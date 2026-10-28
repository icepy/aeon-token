#!/usr/bin/env python3
"""arxiv-radar 扫描器。vM

vM = vL + 饱和词的「raw 命中最新发布日期」。
     原来审计只记 raw 计数不记日期分布，于是「seen 饱和」和「话题降温」字面一模一样
     （第十一轮实测：`embodied AI` raw=21/新收=0，无法判断话题是否还活着）。
     加一列 maxpub 即可分辨，且零额外请求 —— 不需要跑 days:180 对照。
vL = vK + dry-run 写自己的快照 out.dry.json。
vK = vJ + 两个零覆盖的相邻簇（human demonstration / hand-object）。

用法:
    python3 skills/arxiv-radar/scan.py "days:30"
    python3 skills/arxiv-radar/scan.py "dry-run days:90"
    python3 skills/arxiv-radar/scan.py "check:verifiable training"   # check: 必须是最后一个 token

var token（空格分隔，可组合）:
    dry-run         跳过 notify、不写 seen / hits；out.json 不覆盖，改写 out.dry.json
    days:N          窗口天数，默认 30
    names           词表整个换成 memory/universe-names.txt
    check:<词>      只量这个词（7/30/60/90 四档 total + 已见重叠 + 领域命中），跑完退出
    notify:script   让脚本自己发通知（默认**不发**，见下）

通知归谁：正文归模型，不归脚本。
  脚本只会写机械列表（英文标题 + 原始查询串）；翻译和「按簇分组」都是判断。
  所以默认不发，由模型覆写 output/arxiv/report.md 为中文后再发一次。
  `notify:script` 是兜底（人手动跑、或模型那轮没跟上时）。

产物（文件名固定）:
    output/arxiv/out.json     全部幸存者（非 dry-run；每条含 window）
    output/arxiv/out.dry.json 全部幸存者（dry-run；空数组不许覆盖上一轮真快照）
    output/arxiv/audit.log    审计（同时打到 stdout）
    output/arxiv/report.md    通知正文（脚本写机械版，模型覆写中文版）
    memory/arxiv-seen.json    非 dry-run 才写
    memory/arxiv-hits.tsv     非 dry-run 才追加，**列序固定：日期 / 裸 id / 名字 / 窗口**
                              「窗口」= 该行被发现时的窗口天数；>30 即补历史口径（填洞），
                              不代表当天有新叙事。2026-10-26 之前的旧行只有 3 列，
                              第 4 列缺失 = 未知（含第九轮那批 60d 补历史）。

失败必须能与「零命中」区分：查询失败重试 3 次（429 单独退避），仍失败进「未测到」；
连续 3 个词全失败 → 熔断，剩余词进「未尝试」。两者都不是零命中。
"""
import json, os, re, subprocess, sys, time
import urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone

VERSION = "vM"

OUTD = "output/arxiv"
OUT, OUTDRY = OUTD + "/out.json", OUTD + "/out.dry.json"
AUD, REPORT = OUTD + "/audit.log", OUTD + "/report.md"
SEEN = "memory/arxiv-seen.json"
HITS = "memory/arxiv-hits.tsv"
NAMES_FILE = "memory/universe-names.txt"
NOTIFY_TOP = 30
MAX_RESULTS = 100
MAXPAGES = 3
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}totalResults"

ATTEMPTS = 3
TIMEOUT = 45
RETRY_BUDGET = 900
RETRY_SPENT = [0.0]
RETRY_COOLDOWN = 20
RETRY_ATTEMPTS = 4
PREFLIGHT_ATTEMPTS = 2
PREFLIGHT_TIMEOUT = 25
CONSEC_FAIL_LIMIT = 3
REQUEST_GAP = 3

# ── var ───────────────────────────────────────────────────────────
var = sys.argv[1] if len(sys.argv) > 1 else ""

# check: 必须整体提取 —— var.split() 会把 "check:consensus protocol" 切成两个 token，
# 静默去量 ti:"consensus"。这是最贵的一类 bug：量出来了，量的是另一个词。
m = re.search(r"(?:^|\s)check:(.+)$", var)
CHECK = m.group(1).strip() if m else ""
if m:
    var = var[:m.start()].strip()

DRY, DAYS, NAMES_MODE, SEND, UNKNOWN = False, 30, False, False, []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "names":
        NAMES_MODE = True
    elif tok == "notify:script":
        SEND = True
    elif tok.startswith("days:"):
        DAYS = int(tok.split(":", 1)[1] or 30)
    elif tok:
        UNKNOWN.append(tok)

T0 = time.time()
# 窗口 > 30 = 补历史口径（填历史洞），推送与审计都要标出来，别被读成方向升温
BACKFILL = DAYS > 30
BACK_TAG = "（补历史口径）" if BACKFILL else ""

# ── 词表：`#` 开头是注释。写「持仓依赖的机制」，不是持仓的名字 ──────
# 只查 ti:（标题）—— 标题是作者自己的定位，摘要里什么都有。
# 带 cat: 约束的写法是精度手段：carrier 已经不太筛了，词必须自己扛精度。
TERMS = [t.strip() for t in """
# ── 可验证计算 / 证明系统 ──
verifiable inference
verifiable computation
verifiable training
auditable training
proof of training
proof-of-useful-work
light client
zero-knowledge
# ── 链上机制 ──
ti:"consensus" AND cat:cs.DC
data availability sampling
restaking
# vH：liquid staking 四档全 0（写法问题，不是没货）→ 换单词；
#     但单词撞 'stakes'（LLM high-stakes 论文，精度 1/9）→ 加 cat 约束，污染挡在词上。
ti:"staking" AND (cat:cs.CR OR cat:cs.DC OR cat:q-fin.GN)
cat:cs.CR AND ti:"MEV"
automated market maker
# vH：ti:"Robinhood Chain" 四档全 0 → 换 RWA（90d=2，两篇都是 RWA 代币化）
RWA
# ── 具身 / 机器人数据（主战场）──
embodied data
robot manipulation data
robot data
embodied AI
ti:"data engine" AND cat:cs.RO
ti:"human data" AND cat:cs.RO
ti:"egocentric" AND cat:cs.RO
ti:"data generation" AND cat:cs.RO
# vK 新增：不是 egocentric 的同义写法，是零覆盖的相邻簇。
#   实证 90d total=20 而已见 1/20（19 篇从没报过）、7d=2 会日常开火；前 3 条标题全在域内。
ti:"human demonstration" AND cat:cs.RO
# vK 新增：同上。90d total=9 而已见 **0/9** —— 与现有 24 词零重叠；7d=3。
ti:"hand-object" AND cat:cs.RO
# ── 持仓依赖的机制 ──
ti:"EIP-1559"
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

# 三档动作梯子的中间一格：换写法 → 降级为低频 → 删词。
# 跨窗全零 ≥2 轮、同义写法已量完且无新增的词放这里；审计里单独归类，不进「可考虑删词」。
LOW_FREQ = {
    # 第十一轮结清：`ti:"verifiable training"` 全期仅 9 篇、最近一篇 2026-06-12；
    # `ti:"verifiable fine-tuning"` 全期 2 篇；`all:"verifiable training"` 90d 28 篇
    # 但抽样 12 条全是 RLVR 语义（不是「训练过程可证明」）。
    # → 不是死词，也不是缺同义词；真实写法已被 `proof of training` 覆盖。
    # **不要再加 verifiable 变体**；下一个候选是 `attestation` 类，但要先 check: 量。
    "verifiable training",
}

if NAMES_MODE and os.path.exists(NAMES_FILE):
    TERMS = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

known = []
if os.path.exists(NAMES_FILE):
    known = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

# 跨窗档 = 所有比本轮窗口更宽的档。比窗口窄的档等于重复量同一件事。
CROSS_WINDOWS = tuple(d for d in (30, 60, 90) if d > DAYS)
CROSS_EMPTY = not CROSS_WINDOWS      # days>=90 时没有更宽档，跨窗结论不存在

# ── carrier ───────────────────────────────────────────────────────
# carrier 必须按词分域 —— 一组链上词会把「具身/机器人」整簇误杀。
CARRIER_BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
                "production", "open-source", "released", "blockchain", "network",
                "token", "incentive", "marketplace", "validator", "miner"]
CARRIER_ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
                 "simulator", "dataset", "datasets", "real-world", "embodied",
                 "sensor", "egocentric", "demonstration", "vla"]
# 追加 ledger 系：MEV 论文常写 "distributed ledger" / "block creator"，
# 实证 2608.13271 全文无一词命中旧 6 词而被静默丢弃。
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher",
                  "ledger", "ledgers", "block creator", "block builder",
                  "block proposer", "transaction ordering", "on-chain",
                  "state transition"]
# ★ vG 新增，纯增量：BASE 是 github 的部署词汇，arxiv 理论论文不写这些。
#   实证 60 天里 6 篇新 ZK 论文因缺这些词被静默丢弃。默认 carrier 换成它。
#   注：此后连续四轮 carrier 丢 0 —— 已退化成空转，但「零假阴」本身有价值，
#   在没量到假阳之前不要收紧。
CARRIER_CRYPTO = CARRIER_BASE + [
    "proof", "proofs", "circuit", "circuits", "snark", "starks", "stark",
    "verifier", "verifiers", "verification", "verify", "commitment", "commitments",
    "signature", "signatures", "cryptograph", "cryptographic", "prover", "provers",
    "witness", "polynomial", "hash", "hashing", "merkle",
    "node", "nodes", "broadcast", "broadcasting", "round", "rounds", "replica",
    "replicas", "leader", "leaders", "committee", "quorum", "byzantine",
    "adversary", "adversarial", "fault", "faulty", "finality", "fork",
    "transaction", "transactions", "block", "blocks", "shard", "sharding",
    "epoch", "slashing", "stake", "staker", "stakers", "delegat", "reward",
    "training", "model", "models", "inference", "audit", "auditing",
]
CARRIER_BY_TERM = {
    "embodied data": CARRIER_ROBOT,
    "robot manipulation data": CARRIER_ROBOT,
    "robot data": CARRIER_ROBOT,
    "embodied AI": CARRIER_ROBOT,
    'ti:"data engine" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"human data" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"egocentric" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"data generation" AND cat:cs.RO': CARRIER_ROBOT,
    # vK：与上面 4 条同类，走 CARRIER_ROBOT，不落到默认的 crypto carrier
    'ti:"human demonstration" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"hand-object" AND cat:cs.RO': CARRIER_ROBOT,
    "automated market maker": CARRIER_BASE + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_BASE + CARRIER_MARKET,
}

CARRIER_FALLBACK = []

def carrier_for(term, q=""):
    """取这个词实际会用的 carrier 表。term 精确命中 → q 精确命中 → 短名兜底
    （反查映射键的短形 / 查询形）→ 默认表。与 absorb() 取表方式完全一致。"""
    if term in CARRIER_BY_TERM:
        return CARRIER_BY_TERM[term]
    if q in CARRIER_BY_TERM:
        return CARRIER_BY_TERM[q]
    for t, c in CARRIER_BY_TERM.items():
        if short_term(t) == term or q_of(t) == q:
            if term not in CARRIER_FALLBACK:
                CARRIER_FALLBACK.append(term)
            return c
    return CARRIER_CRYPTO


def carrier_label(carrier):
    """表名，只用于审计打印。CARRIER_ROBOT / CARRIER_CRYPTO 是模块级单例，
    身份比较即可；market 那两个值是即时拼的 list，落 else。"""
    if carrier is CARRIER_ROBOT:
        return "robot"
    if carrier is CARRIER_CRYPTO:
        return "crypto"
    return "base+market"

# 只对 title 判，且只留这两个：benchmark 是论文自称，不该丢
EXCL = ["survey", "tutorial"]
STOP = set("""a an the on of in for with from and or to at by as is are was were
towards toward via using based scalable efficient large language model models
learning deep neural network networks system systems new novel study analysis
empirical measurement framework approach method methods data theory practice
case real world beyond not all end how what why when where which that this""".split())

# 名字形状判据的辅助黑名单：这些词大写开头也是普通词，不是项目名
NAME_STOP = set("""the a an on of in for with from and or to at by as is are was were
towards toward via using based novel new study analysis survey benchmark learning
deep zero data model models system systems framework approach method methods
verifiable verified trusted efficient scalable towards paper""".split())

now = datetime.now(timezone.utc)
WD = "一二三四五六日"

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

# ── 取回（带重试 + 重试可见）─────────────────────────────────────
def arxiv_get(url, attempts=ATTEMPTS, timeout=TIMEOUT, tag=""):
    """返回 (root, err)。root 为 None 即失败 —— 失败必须能与「零命中」区分。

    旧写法单次 urlopen 异常即 continue，把 429 读成真零，是 16/24 静默失败的成因。
    退避时往 stderr 打一行，否则和「卡住」长得一样。
    """
    last = ""
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return ET.fromstring(r.read()), ""
        except urllib.error.HTTPError as he:
            last = "HTTP %s" % he.code
            if he.code not in (429, 500, 502, 503, 504):
                return None, last            # 4xx 重试无用
            wait = min(10 * (i + 1), 25)
        except Exception as ex:
            last = str(ex)[:90]
            wait = min(5 * (i + 1), 20)
        if i < attempts - 1:
            if RETRY_SPENT[0] >= RETRY_BUDGET:
                return None, last + "（重试预算用尽）"
            print("  ↻ %s 重试 %d/%d（%s，等 %ds）"
                  % (tag or "query", i + 1, attempts, last, wait),
                  file=sys.stderr, flush=True)
            time.sleep(wait)
            RETRY_SPENT[0] += wait
    return None, last

def preflight():
    """一条最小的带窗请求：arXiv 侧不可用就别让 26 个词去撞。"""
    p = {"search_query": "all:electron AND submittedDate:[%s TO %s]"
         % ((now - timedelta(days=max(DAYS, 1))).strftime("%Y%m%d%H%M"),
            now.strftime("%Y%m%d%H%M")),
         "start": 0, "max_results": 1}
    root, err = arxiv_get(API + "?" + urllib.parse.urlencode(p),
                          attempts=PREFLIGHT_ATTEMPTS, timeout=PREFLIGHT_TIMEOUT,
                          tag="preflight")
    return root is not None, err

def q_of(term):
    """纯词自动包 ti:；已经带字段/布尔/括号的原样用（写全形，别指望自动补）。"""
    if term.startswith(("cat:", "ti:", "abs:", "all:", "(")):
        return term
    if re.search(r"\b(AND|OR|NOT)\b", term):
        return term
    if NAMES_MODE:
        return ('ti:"%s" AND (cat:cs.CR OR cat:cs.CE OR cat:cs.GT OR cat:cs.DC '
                'OR cat:q-fin.CP OR cat:q-fin.GN)' % term)
    return 'ti:"%s"' % term

def fetch_term(term, d=None, start=0, attempts=ATTEMPTS, tag=""):
    d = d or DAYS
    p = {"search_query": "(%s) AND submittedDate:[%s TO %s]"
         % (q_of(term), (now - timedelta(days=d)).strftime("%Y%m%d%H%M"),
            now.strftime("%Y%m%d%H%M")),
         "start": start, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    return arxiv_get(API + "?" + urllib.parse.urlencode(p),
                     attempts=attempts, tag=tag or "%s %dd" % (short_term(term), d))

def total_of(q, d, attempts=3):
    """只量 total_count。失败返回 (-1, [])。"""
    p = {"search_query": "(%s) AND submittedDate:[%s TO %s]"
         % (q, (now - timedelta(days=d)).strftime("%Y%m%d%H%M"),
            now.strftime("%Y%m%d%H%M")),
         "start": 0, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root, err = arxiv_get(API + "?" + urllib.parse.urlencode(p),
                          attempts=attempts, tag="cross:%dd" % d)
    if root is None:
        return -1, []
    node = root.find(OPENSEARCH)
    return (int(node.text) if node is not None and node.text else 0), \
        root.findall("a:entry", NS)

def short_term(t):
    """把查询串剥成能读的短形：ti:"staking" AND (cat:…) → staking"""
    s = t.replace('ti:"', "").replace('"', "")
    s = re.sub(r"\s+AND\s+\(?cat:[^)]*\)?", "", s)
    s = re.sub(r"cat:[A-Za-z.\-]+ AND ", "", s)
    return re.sub(r"\s+", " ", s).strip(" ()") or t

# ── 名字 ──────────────────────────────────────────────────────────
def looks_like_name(w):
    """项目名的形状，不是「大写开头的英文词」。

    旧写法取标题里第一个不在 STOP 的大写词，必然吐垃圾：
    "Verifiable Computation with Trusted ..." → `Verifiable`（而它就在标题里重复了一遍）。
    宁可返回空（下游退回标题），也不要错名字（会污染 hits.tsv 的名字列）。
    """
    if len(w) < 3 or len(w) > 22:
        return False
    if w.lower() in NAME_STOP:
        return False
    if w.isupper() and any(c.isalpha() for c in w):
        return True                      # 全大写缩写：PEARL / FLORA / XMAQUINA
    if any(c.isdigit() for c in w):
        return True                      # 含数字：EIP-1559 / GPT-4
    if "-" in w:
        return False                     # On-Chain / End-to-End 这类短语
    return any(c.isupper() for c in w[1:])   # 内部有大写：SocialCoAct / SkillWeaver

def guess_name(title, summ, known):
    for n in known:
        if re.search(r"\b%s\b" % re.escape(n), title + " " + summ, re.I):
            return n
    m = re.search(r"\b([A-Z][A-Za-z0-9\-]{2,})(?:'s|’s)\b", title + " " + summ)
    if m and looks_like_name(m.group(1)):
        return m.group(1)
    for w in re.findall(r"\b[A-Za-z][A-Za-z0-9\-]*\b", title):
        if looks_like_name(w):
            return w
    return ""

# ── check 模式 ────────────────────────────────────────────────────
def do_check():
    q = q_of(CHECK)
    print("候选词: %r" % CHECK)
    print("查询  : %s" % q)
    print("已在词表: %s" % ("是" if CHECK in TERMS else "否"))
    if UNKNOWN:
        print("⚠️ 未识别 token（check: 必须在最后）: %s" % " ".join(UNKNOWN))
    # 只在「像是被截断」时报。CHECK 不在词表是常态（正在评估的候选词），
    # 而「不在词表 + 含空格」几乎每次都成立，等于没提示。
    if CHECK not in TERMS and any(t.startswith(CHECK + " ") for t in TERMS):
        print("⚠️ 不在词表，但像是词表某条的截断 —— 确认 check: 是最后一个 token")
    print()
    carrier = carrier_for(CHECK, q)          # q = q_of(CHECK) 该函数开头已有
    print("carrier 表: %s%s" % (carrier_label(carrier),
                                "（短名兜底命中）" if CHECK in CARRIER_FALLBACK else ""))
    print("窗口   total  已见/100  领域命中  前 3 条标题")
    for d in (7, 30, 60, 90):
        tot, ents = total_of(q, d)
        if tot < 0:
            print("%4dd   查询失败" % d)
            continue
        ids = [e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0] for e in ents]
        old = sum(1 for i in ids if i in seen)
        dom = 0
        for e in ents:
            blob = (" ".join(e.find("a:title", NS).text.split()) + " " +
                    " ".join(e.find("a:summary", NS).text.split())).lower()
            if any(c in blob for c in carrier):
                dom += 1
        print("%4dd   %5d  %5s/%-3d  %3s/%-3d   %s"
              % (d, tot, old, len(ids), dom, len(ents),
                 " ｜ ".join(" ".join(e.find("a:title", NS).text.split())[:52]
                             for e in ents[:3])))
        time.sleep(REQUEST_GAP)
    print()
    print("读法: 已见/100 低 = 能带来新条目；领域命中低 = 会污染。"
          "领域命中用该词实际使用的 carrier 表算，偏乐观 30-50%，真精度靠前 3 条标题人眼读。")
    sys.exit(0)

# ── 扫描 ──────────────────────────────────────────────────────────
out, raw, newest = [], 0, ""
drop = {"seen_mem": 0, "seen_dup": 0, "excl": 0, "carrier": 0, "fail": 0}
hit_ids = {}          # run 内判重；不要直接写 seen，否则跨词命中只记第一个词
per_term = {}
raw_term = {}
raw_maxpub = {}       # vM：每个词原始命中的最新发布日期 —— 分辨「seen 饱和」与「话题降温」
failed_t = []
skipped_t = []
fail_reason = {}
cross = {}            # 零命中词的跨窗 total_count；-1 = 该档查询失败
dropped = {"excl": [], "carrier": []}   # 丢掉的名字 —— 审计里唯一能看见误杀的地方
DROPPED_CAP = 200

def absorb(root, term):
    """把一次成功取回的结果吃进 out/raw/drop。返回该次取回条数。"""
    global raw, newest
    n = 0
    carrier = carrier_for(term)
    for e in root.findall("a:entry", NS):
        n += 1
        raw += 1
        raw_term[term] = raw_term.get(term, 0) + 1
        # 去掉版本后缀：v2 不该被当新命中重报
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        pub = e.find("a:published", NS).text[:10]
        if pub > newest:
            newest = pub
        # vM：记该词原始命中的最新发布日期（含已被 seen 吸收的那些 —— 正是要看的）
        if pub > raw_maxpub.get(term, ""):
            raw_maxpub[term] = pub
        if aid in seen:
            drop["seen_mem"] += 1
            continue
        if aid in hit_ids:
            hit_ids[aid]["terms"].append(term)
            drop["seen_dup"] += 1
            continue
        if any(x in title.lower() for x in EXCL):
            drop["excl"] += 1
            if len(dropped["excl"]) < DROPPED_CAP:
                dropped["excl"].append((pub, title[:72]))
            continue
        if not any(c in blob for c in carrier):
            drop["carrier"] += 1
            if len(dropped["carrier"]) < DROPPED_CAP:
                dropped["carrier"].append(
                    (term, carrier_label(carrier), pub, title[:72]))
            continue
        # vI：裸 id 进记录 —— hits.tsv 的键必须和 labels.tsv 同构，否则 join 不上
        # vJ：window 进记录 —— 区分「当天新发现」和「补历史填洞」
        rec = {"id": aid, "term": term, "terms": [term], "window": DAYS,
               "name": guess_name(title, summ, known),
               "title": title, "published": pub, "link": "https://arxiv.org/abs/%s" % aid,
               "carrier": next(c for c in carrier if c in blob)}
        out.append(rec)
        hit_ids[aid] = rec
        per_term[term] = per_term.get(term, 0) + 1
    return n

def scan_term(term, attempts=ATTEMPTS, tag=""):
    """取尽一个词的全部页。返回 (条数, 失败原因或"")。"""
    n, page = 0, 0
    while page < MAXPAGES:
        root, err = fetch_term(term, start=page * MAX_RESULTS, attempts=attempts, tag=tag)
        if root is None:
            return n, err
        c = absorb(root, term)
        n += c
        page += 1
        if c < MAX_RESULTS:
            break
    return n, ""

def cross_probe(term):
    """窗口内零命中 → 跨更宽的档量真实 total_count，别把「窗口太短」读成「真零」。"""
    if raw_term.get(term, 0) == 0 and term not in failed_t:
        for d in CROSS_WINDOWS:
            cross.setdefault(term, {})[d] = total_of(q_of(term), d)[0]
            time.sleep(REQUEST_GAP)

# ── 预检 ──────────────────────────────────────────────────────────
ok, perr = preflight()
if not ok:
    print("🛑 preflight 失败: %s" % perr, file=sys.stderr)
    L = ["arxiv-radar %s · preflight 失败 · 窗口 %d 天%s" % (VERSION, DAYS, BACK_TAG),
         "原因: %s" % perr,
         "未测到（试过但失败）: 全部 %d 词" % len(TERMS),
         "未尝试（熔断跳过）: 0",
         "判据: arXiv 侧降级，不是词的问题，别据此改词表。"]
    os.makedirs(OUTD, exist_ok=True)
    open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print("STATUS: ARXIV_RADAR_DEGRADED · 原始 0 · 幸存 0 · 总耗时 %.0fs"
          % (time.time() - T0))
    sys.exit(0)

if CHECK:
    do_check()

# ── 主循环 ────────────────────────────────────────────────────────
consec = 0
for i, term in enumerate(TERMS):
    raw_term.setdefault(term, 0)
    per_term.setdefault(term, 0)
    n, err = scan_term(term, tag="%s %dd" % (short_term(term), DAYS))
    if err:
        print("! %s: %s" % (term, err), file=sys.stderr, flush=True)
        drop["fail"] += 1
        fail_reason[term] = err
        if n == 0:
            failed_t.append(term)
            consec += 1
        else:
            consec = 0
    else:
        consec = 0
    if consec >= CONSEC_FAIL_LIMIT:
        skipped_t = list(TERMS[i + 1:])
        print("🛑 连续 %d 个词全失败 → 判定 arXiv 侧降级，跳过剩余 %d 个词"
              % (consec, len(skipped_t)), file=sys.stderr, flush=True)
        break
    time.sleep(REQUEST_GAP)

# 补扫：429 是成簇的，冷却后单独重试。放主循环之外（立刻重试时 API 还在不高兴）。
rescued = []
if failed_t:
    print("… 冷却 %ds 后补扫 %d 个失败词" % (RETRY_COOLDOWN, len(failed_t)),
          file=sys.stderr, flush=True)
    time.sleep(RETRY_COOLDOWN)
    for term in list(failed_t):
        n, err = scan_term(term, attempts=RETRY_ATTEMPTS,
                           tag="%s 补扫" % short_term(term))
        if err:
            fail_reason[term] = err
            continue
        failed_t.remove(term)
        rescued.append(term)

# 零命中词 → 跨窗量
for term in TERMS:
    if term not in skipped_t:
        cross_probe(term)

# ── 分类（六类分开记；计数单位是「词」，漏斗的单位是「条」）──────────
zero_t = [t for t in TERMS if t not in failed_t and t not in skipped_t
          and raw_term.get(t, 0) == 0 and t not in LOW_FREQ]
lf_t = [t for t in TERMS if t in LOW_FREQ and t not in skipped_t
        and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and per_term.get(t, 0) == 0]
with_new = [t for t in TERMS if per_term.get(t, 0) > 0]

short_w, real_w, unk_w, widest_w = [], [], [], []
for t in zero_t:
    if CROSS_EMPTY:
        widest_w.append(t)
        continue
    cs = [cross.get(t, {}).get(d) for d in CROSS_WINDOWS]
    if not cs or any(c is None for c in cs):
        unk_w.append(t)
    elif any(c > 0 for c in cs):
        short_w.append(t)
    else:
        real_w.append(t)

# ── 审计 ──────────────────────────────────────────────────────────
L = ["arxiv-radar %s · 窗口 %d 天%s · 词 %d · 原始 %d · 幸存 %d · var=%r"
     % (VERSION, DAYS, BACK_TAG, len(TERMS), raw, len(out), var),
     "丢弃 seen(记忆)=%d · seen(本轮重复)=%d · EXCL=%d · carrier=%d · 查询失败=%d"
     % (drop["seen_mem"], drop["seen_dup"], drop["excl"], drop["carrier"], drop["fail"])]

if DRY:
    L.append("快照: %s（dry-run 不覆盖 out.json —— out.json 只代表最后一次真跑）" % OUTDRY)

if newest:
    nd = datetime.strptime(newest, "%Y-%m-%d").date()
    lag = (now.date() - nd).days
    if lag <= 2:
        hint = "正常"
    elif lag <= 4 and now.weekday() in (0, 1):
        hint = "周一/周二 + 周末不公告 → 正常节律"
    elif lag <= 4:
        hint = "3-4 天，连续两天不动才算滞后"
    else:
        hint = "⚠️ 偏大 —— 连续两天不动才算真滞后，别急"
    L.append("窗口内最新收录日期: %s（周%s，距今 %d 天）— %s"
             % (newest, WD[nd.weekday()], lag, hint))
else:
    L.append("窗口内最新收录日期: 无")

L.append("六分类（单位=词）: 未测到(试过失败)=%d · 未尝试(熔断跳过)=%d · 窗口内零命中=%d · "
         "低频探针=%d · 全已见(饱和)=%d · 有新增=%d"
         % (len(failed_t), len(skipped_t), len(zero_t), len(lf_t),
            len(saturated), len(with_new)))

unmapped = [t for t in TERMS if t not in CARRIER_BY_TERM] if not NAMES_MODE else []
if unmapped:
    L.append("未配 carrier 表的词 %d 个（走默认 crypto 表，仅登记不报错）: %s"
             % (len(unmapped), " · ".join(short_term(t) for t in unmapped)))

if CARRIER_FALLBACK:
    L.append("   carrier 短名兜底命中 %d 个: %s"
             % (len(CARRIER_FALLBACK), " · ".join(CARRIER_FALLBACK)))

if failed_t:
    L.append("未测到（**不是零命中**）: " + " · ".join(
        "%s(%s)" % (t, fail_reason.get(t, "?")[:28]) for t in failed_t))
if skipped_t:
    L.append("未尝试（熔断跳过，本轮没有数据）: " + " · ".join(skipped_t))
if rescued:
    L.append("补扫救回 %d 个: %s" % (len(rescued), " · ".join(rescued)))

for t in short_w + real_w + unk_w + widest_w:
    if CROSS_EMPTY:
        L.append("   %s: win=%d（无更宽档）" % (t, raw_term.get(t, 0)))
    else:
        L.append("   %s: win=%d %s" % (
            t, raw_term.get(t, 0),
            " ".join("%dd=%s" % (d, cross.get(t, {}).get(d)) for d in CROSS_WINDOWS)))
if short_w:
    L.append("   └ 窗口太短（跨窗有命中）→ **非真零，别删** %d 个: %s"
             % (len(short_w), " · ".join(short_w)))
if real_w:
    L.append("   └ 跨窗皆 0 → **先换写法**（同义写法也 0 才判死词）%d 个: %s"
             % (len(real_w), " · ".join(real_w)))
if unk_w:
    L.append("   └ 跨窗查询失败（存疑，先别删）%d 个: %s" % (len(unk_w), " · ".join(unk_w)))
if widest_w:
    L.append("   └ 已是最宽窗口（%dd），无更宽档可比 → **先换写法**，别直接判死 %d 个: %s"
             % (DAYS, len(widest_w), " · ".join(widest_w)))
if lf_t:
    L.append("低频探针（已降级，别删）: " + " · ".join(lf_t))
if saturated:
    L.append("全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))
    # vM：饱和 ≠ 降温。raw 命中的最新发布日期才是判据 —— 没有这一列，
    #      「话题活着但都被 seen 吃了」和「话题真的停了」字面完全一样。
    L.append("   饱和词 raw 命中的最新发布日期: " + " · ".join(
        "%s=%s" % (t, raw_maxpub.get(t, "?")[5:]) for t in saturated))
    L.append("   读法: 最新发布日期在近 30 天内 → 话题活着，是 seen 饱和（**别删**）；"
             "停在 60 天前 → 才考虑降温，且需再一轮确认")

for k in ("excl", "carrier"):
    if dropped[k]:
        L.append("丢弃名单 %s（前 %d，共 %d）:" % (k, DROPPED_CAP, drop[k]))
        for rec in dropped[k]:
            if len(rec) == 4:
                t_, lab, pub, ti = rec
                L.append("   %s  [%s · %s]  %s" % (pub, lab, short_term(t_), ti))
            else:
                pub, ti = rec
                L.append("   %s  %s" % (pub, ti))

L.append("词表原始/新收: " + " · ".join(
    "%s=%d/%d" % (k, v, per_term.get(k, 0)) for k, v in
    sorted(raw_term.items(), key=lambda x: -x[1])))
for c in out[:25]:
    L.append("  %s [%s] %s%s" % (c["published"], "+".join(c["terms"]), c["title"][:88],
                                 (" · 名字=%s" % c["name"]) if c["name"] else ""))

if not DRY and out:
    L.append("hits 流水: 追加 %d 行（列序 日期/键/名字/窗口，窗口=%d）" % (len(out), DAYS))

if not out and not with_new:
    if drop["excl"] or drop["carrier"]:
        L.append("ℹ️ 本轮 0 幸存，**但不是 seen 吃干了**：有 %d 条穿过了 seen 却全死在过滤器"
                 "（EXCL=%d carrier=%d）—— 名单见上。这 %d 条是唯一未知。"
                 % (drop["excl"] + drop["carrier"], drop["excl"], drop["carrier"],
                    drop["excl"] + drop["carrier"]))
    else:
        L.append("ℹ️ 本轮 0 幸存 = 结构性（全部命中已在 seen 或跨窗），不是故障。")

os.makedirs(OUTD, exist_ok=True)
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ── 落盘 ──────────────────────────────────────────────────────────
# vL：dry-run 写自己的快照。原来 out.json 一起被挡掉，于是同一次跑里
#     audit.log / report.md 是本轮的、out.json 是上一轮的 —— 三种代际。
if DRY:
    json.dump(out, open(OUTDRY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if hit_ids:
        merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
        merged.update(seen)
        json.dump(dict(list(merged.items())[:2000]),   # merged 新的在前，取头
                  open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if out:
        # vI：第二列写裸 id（不是 URL）—— 必须和 labels.tsv 的键同构才能 join
        # vJ：第四列写窗口 —— 补历史的行不该被读成当天新叙事
        old = open(HITS, encoding="utf-8").read() if os.path.exists(HITS) else ""
        with open(HITS, "w", encoding="utf-8") as f:
            f.write(old)
            if old and not old.endswith("\n"):
                f.write("\n")
            for c in out:
                f.write("%s\t%s\t%s\t%d\n" % (now.strftime("%Y-%m-%d"), c["id"],
                                              c["name"] or c["title"][:40], c["window"]))

if out:
    R = ["**arxiv-radar** · 窗口 %d 天%s · 幸存 %d" % (DAYS, BACK_TAG, len(out)), ""]
    for c in out[:NOTIFY_TOP]:
        nm = ("`%s` " % c["name"]) if c["name"] else ""
        R.append("- %s%s [%s] · %s · %s" % (nm, c["title"][:110],
                                            "+".join(c["terms"]), c["published"],
                                            c["link"]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

# ── 通知 ──────────────────────────────────────────────────────────
# 正文归模型：脚本只会拼英文标题 + 原始查询串，翻译和「按簇分组」都是判断。
# 所以默认不发 —— 由模型覆写 report.md 为中文后发一次。两个发送方就是两条推送。
if DRY or not out:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else "零命中"))
elif SEND:
    if os.path.exists("./notify"):
        r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
        print("notify: 已由脚本发送 · %s" % ((r.stdout or r.stderr or "ok").strip()[:160]))
    else:
        print("notify: ./notify 不存在，未发")
else:
    print("notify: **未发** —— 覆写 %s 为中文（按簇分组、带 [方向]），然后：" % REPORT)
    print("        ./notify -f %s" % REPORT)

print("STATUS: %s · 原始 %d · 幸存 %d · 总耗时 %.0fs"
      % ("ARXIV_RADAR_DEGRADED" if skipped_t else "ARXIV_RADAR_OK",
         raw, len(out), time.time() - T0))
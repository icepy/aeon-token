#!/usr/bin/env python3
"""arxiv-radar 扫描器。vH

用法:
    python3 skills/arxiv-radar/scan.py "days:30"
    python3 skills/arxiv-radar/scan.py "dry-run days:60"
    python3 skills/arxiv-radar/scan.py "check:verifiable training"   # check: 必须是最后一个 token

var token（空格分隔，可组合）:
    dry-run      跳过 notify、不写 seen / hits
    days:N       窗口天数，默认 30
    names        词表整个换成 memory/universe-names.txt
    check:<词>   只量这个词（7/30/60/90 四档 total + 已见重叠 + 领域命中），跑完退出

产物（文件名固定）:
    output/arxiv/out.json     全部幸存者
    output/arxiv/audit.log    审计（同时打到 stdout）
    output/arxiv/report.md    通知正文
    memory/arxiv-seen.json    非 dry-run 才写
    memory/arxiv-hits.tsv     非 dry-run 才追加（日期 / 键 / 名字，append-only）

失败必须能与「零命中」区分：查询失败重试 3 次（429 单独退避），仍失败进「未测到」；
连续 3 个词全失败 → 熔断，剩余词进「未尝试」。两者都不是零命中。
"""
import json, os, re, subprocess, sys, time
import urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone

VERSION = "vH"

OUTD = "output/arxiv"
OUT, AUD, REPORT = OUTD + "/out.json", OUTD + "/audit.log", OUTD + "/report.md"
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

DRY, DAYS, NAMES_MODE, UNKNOWN = False, 30, False, []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "names":
        NAMES_MODE = True
    elif tok.startswith("days:"):
        DAYS = int(tok.split(":", 1)[1] or 30)
    elif tok:
        UNKNOWN.append(tok)

T0 = time.time()

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
# ── 持仓依赖的机制 ──
ti:"EIP-1559"
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

# 三档动作梯子的中间一格：换写法 → 降级为低频 → 删词。
# 跨窗全零 ≥2 轮、同义写法还没量完（或量完仍值得留）的词放这里；
# 审计里单独归类，不进「可考虑删词」。
LOW_FREQ = {
    "verifiable training",   # 第四轮跨窗全零；同义写法未量，先降级不删
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
    "automated market maker": CARRIER_BASE + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_BASE + CARRIER_MARKET,
}
DOMAIN = CARRIER_BASE + CARRIER_ROBOT + CARRIER_MARKET
# 只对 title 判，且只留这两个：benchmark 是论文自称，不该丢
EXCL = ["survey", "tutorial"]
STOP = set("""a an the on of in for with from and or to at by as is are was were
towards toward via using based scalable efficient large language model models
learning deep neural network networks system systems new novel study analysis
empirical measurement framework approach method methods data theory practice
case real world beyond not all end how what why when where which that this""".split())

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
    退避时往 stderr 打一行，否则和「卡住」长得一样（你 Ctrl-C 过一次）。
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
    """一条最小的带窗请求：arXiv 侧不可用就别让 24 个词去撞。"""
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

# ── check 模式 ────────────────────────────────────────────────────
def do_check():
    q = q_of(CHECK)
    print("候选词: %r" % CHECK)
    print("查询  : %s" % q)
    print("已在词表: %s" % ("是" if CHECK in TERMS else "否"))
    if UNKNOWN:
        print("⚠️ 未识别 token（check: 必须在最后）: %s" % " ".join(UNKNOWN))
    if CHECK not in TERMS and " " in CHECK:
        print("⚠️ 不在词表且含空格 —— 先确认没有第二个词被切出去")
    print()
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
            if any(c in blob for c in DOMAIN):
                dom += 1
        print("%4dd   %5d  %5s/%-3d  %3s/%-3d   %s"
              % (d, tot, old, len(ids), dom, len(ents),
                 " ｜ ".join(" ".join(e.find("a:title", NS).text.split())[:52]
                             for e in ents[:3])))
        time.sleep(REQUEST_GAP)
    print()
    print("读法: 已见/100 低 = 能带来新条目；领域命中低 = 会污染。"
          "领域命中用 DOMAIN 词算，偏乐观 30-50%，真精度靠前 3 条标题人眼读。")
    sys.exit(0)

# ── 扫描 ──────────────────────────────────────────────────────────
out, raw, newest = [], 0, ""
drop = {"seen_mem": 0, "seen_dup": 0, "excl": 0, "carrier": 0, "fail": 0}
hit_ids = {}          # run 内判重；不要直接写 seen，否则跨词命中只记第一个词
per_term = {}
raw_term = {}
failed_t = []
skipped_t = []
fail_reason = {}
cross = {}            # 零命中词的跨窗 total_count；-1 = 该档查询失败
dropped = {"excl": [], "carrier": []}   # 丢掉的名字 —— 审计里唯一能看见误杀的地方
DROPPED_CAP = 12

def absorb(root, term):
    """把一次成功取回的结果吃进 out/raw/drop。返回该次取回条数。"""
    global raw, newest
    n = 0
    carrier = CARRIER_BY_TERM.get(term, CARRIER_CRYPTO)
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
                dropped["carrier"].append((pub, title[:72]))
            continue
        rec = {"term": term, "terms": [term], "name": guess_name(title, summ, known),
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

def guess_name(title, summ, known):
    for n in known:
        if re.search(r"\b%s\b" % re.escape(n), title + " " + summ, re.I):
            return n
    m = re.search(r"\b([A-Z][A-Za-z0-9\-]{2,})(?:'s|’s)\b", title + " " + summ)
    if m:
        return m.group(1)
    for w in re.findall(r"\b[A-Z][A-Za-z0-9\-]{2,}\b", title):
        if w.lower() not in STOP:
            return w
    return ""

# ── 预检 ──────────────────────────────────────────────────────────
ok, perr = preflight()
if not ok:
    print("🛑 preflight 失败: %s" % perr, file=sys.stderr)
    L = ["arxiv-radar %s · preflight 失败 · 窗口 %d 天" % (VERSION, DAYS),
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

# ── 分类（六类分开记）─────────────────────────────────────────────
zero_t = [t for t in TERMS if t not in failed_t and t not in skipped_t
          and raw_term.get(t, 0) == 0 and t not in LOW_FREQ]
lf_t = [t for t in TERMS if t in LOW_FREQ and t not in skipped_t
        and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and per_term.get(t, 0) == 0]
with_new = [t for t in TERMS if per_term.get(t, 0) > 0]

short_w, real_w, unk_w = [], [], []
for t in zero_t:
    cs = [cross.get(t, {}).get(d) for d in CROSS_WINDOWS]
    if not cs or any(c is None for c in cs):
        unk_w.append(t)
    elif any(c > 0 for c in cs):
        short_w.append(t)
    else:
        real_w.append(t)

# ── 审计 ──────────────────────────────────────────────────────────
L = ["arxiv-radar %s · 窗口 %d 天 · 词 %d · 原始 %d · 幸存 %d · var=%r"
     % (VERSION, DAYS, len(TERMS), raw, len(out), var),
     "丢弃 seen(记忆)=%d · seen(本轮重复)=%d · EXCL=%d · carrier=%d · 查询失败=%d"
     % (drop["seen_mem"], drop["seen_dup"], drop["excl"], drop["carrier"], drop["fail"])]

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

L.append("六分类: 未测到(试过失败)=%d · 未尝试(熔断跳过)=%d · 窗口内零命中=%d · "
         "低频探针=%d · 全已见(饱和)=%d · 有新增=%d"
         % (len(failed_t), len(skipped_t), len(zero_t), len(lf_t),
            len(saturated), len(with_new)))

if failed_t:
    L.append("未测到（**不是零命中**）: " + " · ".join(
        "%s(%s)" % (t, fail_reason.get(t, "?")[:28]) for t in failed_t))
if skipped_t:
    L.append("未尝试（熔断跳过，本轮没有数据）: " + " · ".join(skipped_t))
if rescued:
    L.append("补扫救回 %d 个: %s" % (len(rescued), " · ".join(rescued)))

for t in short_w + real_w + unk_w:
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
if lf_t:
    L.append("低频探针（已降级，别删）: " + " · ".join(lf_t))
if saturated:
    L.append("全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))

for k in ("excl", "carrier"):
    if dropped[k]:
        L.append("丢弃名单 %s（前 %d）:" % (k, DROPPED_CAP))
        for pub, ti in dropped[k]:
            L.append("   %s  %s" % (pub, ti))

L.append("词表原始/新收: " + " · ".join(
    "%s=%d/%d" % (k, v, per_term.get(k, 0)) for k, v in
    sorted(raw_term.items(), key=lambda x: -x[1])))
for c in out[:25]:
    L.append("  %s [%s] %s" % (c["published"], "+".join(c["terms"]), c["title"][:88]))

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
if not DRY:
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if hit_ids:
        merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
        merged.update(seen)
        json.dump(dict(list(merged.items())[:2000]),   # merged 新的在前，取头
                  open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if out:
        old = open(HITS, encoding="utf-8").read() if os.path.exists(HITS) else ""
        with open(HITS, "w", encoding="utf-8") as f:
            f.write(old)
            if old and not old.endswith("\n"):
                f.write("\n")
            for c in out:
                f.write("%s\t%s\t%s\n" % (now.strftime("%Y-%m-%d"), c["link"],
                                          c["name"] or c["title"][:40]))

if out:
    R = ["**arxiv-radar** · 窗口 %d 天 · 幸存 %d" % (DAYS, len(out)), ""]
    for c in out[:NOTIFY_TOP]:
        nm = ("`%s` " % c["name"]) if c["name"] else ""
        R.append("- %s%s [%s] · %s" % (nm, c["title"][:110],
                                       "+".join(c["terms"]), c["link"]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

if not DRY and out and os.path.exists("./notify"):
    r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
    print("notify: %s" % ((r.stdout or r.stderr or "ok").strip()[:200]))
else:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else "零命中"))

print("STATUS: %s · 原始 %d · 幸存 %d · 总耗时 %.0fs"
      % ("ARXIV_RADAR_DEGRADED" if skipped_t else "ARXIV_RADAR_OK",
         raw, len(out), time.time() - T0))
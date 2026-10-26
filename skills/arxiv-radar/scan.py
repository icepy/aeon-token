#!/usr/bin/env python3
"""arxiv-radar 扫描器（静态文件 —— 模型只调用，不重写）。

用法:
    python3 skills/arxiv-radar/scan.py "days:30"
    python3 skills/arxiv-radar/scan.py "dry-run days:60"
    python3 skills/arxiv-radar/scan.py 'check:ti:"consensus" AND cat:cs.DC'
    python3 skills/arxiv-radar/scan.py "names"        # 机制/名字反查模式

var token（空格分隔，可组合）:
    dry-run        跳过 notify、不写 seen/hits
    days:N         窗口天数，默认 30
    names          词表整个换成 memory/universe-names.txt
    notify:script  由脚本自己发通知（默认：脚本只写 report.md，模型覆写成中文后发）
    check:<词>     只量这一个词，不扫描。**必须放在整串最后** ——
                   内部按空格切 token，多词项只有放最后才能被完整取出
                   （放中间会把 "check:consensus protocol" 切成 check:consensus + protocol，
                   静默量成另一个词）。

产物（文件名固定，别改成 radar2.json）:
    output/arxiv/out.json      全部幸存者
    output/arxiv/audit.log     审计（同时打到 stdout；降级收场也写）
    output/arxiv/report.md     通知正文（脚本写机械版 → 模型覆写成中文）
    memory/arxiv-seen.json     非 dry-run 才写
    memory/arxiv-hits.tsv      命中流水，append-only，非 dry-run 才写（3 列：日期/键/名字）
    memory/arxiv-labels.tsv    方向标签，append-only，**模型写**（键 \\t 方向，无表头）

arXiv 侧会整段降级（read timeout 与 429 交替、整批全挂、约 10 分钟自恢复）。
降级期里重试**是在加码**，所以三层：preflight → 熔断 → 补扫。

失败绝不能读成零命中：total=0 是词/写法的问题（arXiv 答了），read timeout / 429 是
arXiv 侧的问题（它没答），跟词无关。

零命中 ≠「可考虑删词」：跨窗档 = (30,60,90) 中所有 > DAYS 的值，全部为 0 时判词是
「**先用 check: 换同义写法**」—— arXiv 的 ti: 是词干化短语匹配，0 命中多半是写法不对。
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone

VERSION = "vH"

OUTD = "output/arxiv"
OUT, AUD, REPORT = OUTD + "/out.json", OUTD + "/audit.log", OUTD + "/report.md"
SEEN = "memory/arxiv-seen.json"
HITS = "memory/arxiv-hits.tsv"
LABELS = "memory/arxiv-labels.tsv"
NAMES_FILE = "memory/universe-names.txt"
NOTIFY_TOP = 30
MAX_RESULTS = 100
# https 直连：http 会先吃一个 301（实测 0.3s/请求），而且平白依赖重定向跟随。
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}totalResults"
DOMAIN = None      # check 模式用：三个 carrier 域的并集

ATTEMPTS = 2
RETRY_ATTEMPTS = 4
RETRY_COOLDOWN = 20
PREFLIGHT_ATTEMPTS = 2
PREFLIGHT_TIMEOUT = 25     # 实测 arXiv 冷启动首条要 7.2s
CONSEC_FAIL_LIMIT = 3
TIMEOUT = 45
RETRY_BUDGET = 900
RETRY_SPENT = [0.0]

# ── var ───────────────────────────────────────────────────────────
var = sys.argv[1] if len(sys.argv) > 1 else ""

DRY, DAYS, NAMES_MODE, CHECK, SEND, UNKNOWN = False, 30, False, "", False, []

# check: 必须先按「到串尾」提取，再解析其余 token。放最后是约定。
mchk = re.search(r"(?:^|\s)check:(.+)$", var)
if mchk:
    CHECK = mchk.group(1).strip()
    var = (var[:mchk.start()] + var[mchk.end():]).strip()

for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "names":
        NAMES_MODE = True
    elif tok == "notify:script":
        SEND = True
    elif tok.startswith("days:"):
        DAYS = int(tok.split(":", 1)[1] or 30)
    else:
        UNKNOWN.append(tok)

CROSS_WINDOWS = tuple(d for d in (30, 60, 90) if d > DAYS)

T0 = time.time()

# ── 词表：`#` 开头是注释。写「持仓依赖的机制」，不是持仓的名字 ──────
# 裸串（不带 ti:/cat: 前缀）会被包成 ti:"…" 短语。多词 = 连续短语。
TERMS = [t.strip() for t in """
proof-of-useful-work
verifiable inference
light client
proof of training
# vH: `verifiable computation` 替 `proof of learning`。探针 90d=1、已见 0/1、一条精确
#     新论文（TEE + 链上数字）；而 `proof of learning` 四档全 0、换写法也是 0。
verifiable computation
# vH: 保留但降级 —— 同语义已被 `proof of training`(raw=1) / `auditable training`(raw=3) 覆盖。
verifiable training
auditable training
data availability sampling
restaking
automated market maker
ti:"consensus" AND cat:cs.DC
cat:cs.CR AND ti:"MEV"
# vH: 加 cat: 约束。裸 `staking` 的词干会撞 LLM「high-stakes decision」——8/9 条是垃圾；
#     约束后领域命中 1/1 但极稀（90d=1 且已见 1/1）。**精确的空槽，留着当哨兵，别指望它产出。**
#     另三个已量过、别再 probe：`proof-of-stake` 90d=1 已见 / `proof of inference` 四档全 0。
ti:"staking" AND (cat:cs.CR OR cat:cs.DC OR cat:q-fin.GN)
embodied data
robot manipulation data
robot data
embodied AI
zero-knowledge
# ── 机器人数据基础设施（2026-10-25 新增）：旧 4 词只认「embodied AI / robot data」，
#    对同期标题含 data 的机器人论文召回 0/88。这 4 条带 cat:cs.RO 约束，实测精度 23/27。
ti:"data engine" AND cat:cs.RO
ti:"human data" AND cat:cs.RO
ti:"egocentric" AND cat:cs.RO
ti:"data generation" AND cat:cs.RO
# ── 持仓依赖的机制 ──
ti:"EIP-1559"
RWA
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

if NAMES_MODE and os.path.exists(NAMES_FILE):
    TERMS = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

known = []
if os.path.exists(NAMES_FILE):
    known = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

# ── carrier ───────────────────────────────────────────────────────
# carrier 必须按词分域 —— 一组链上词会把「具身/机器人」整簇误杀。
CARRIER_BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
                "production", "open-source", "released", "blockchain", "network",
                "token", "incentive", "marketplace", "validator", "miner"]
CARRIER_ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
                 "simulator", "dataset", "datasets", "real-world", "embodied",
                 "sensor", "egocentric", "demonstration", "vla"]
# 追加 ledger 系：MEV 论文常写 "distributed ledger" / "block creator"。
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
    "automated market maker": CARRIER_CRYPTO + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_CRYPTO + CARRIER_MARKET,
}
DOMAIN = CARRIER_CRYPTO + CARRIER_ROBOT + CARRIER_MARKET
# 只对 title 判，且只留这两个：benchmark 是论文自称，不该丢
EXCL = ["survey", "tutorial"]
STOP = set("""a an the on of in for with from and or to at by as is are was were
towards toward via using based scalable efficient large language model models
learning deep neural network networks system systems new novel study analysis
empirical measurement framework approach method methods data theory practice
case real world beyond not all end how what why when where which that this""".split())

now = datetime.now(timezone.utc)
win = f"[{(now - timedelta(days=DAYS)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

def write_audit(lines):
    os.makedirs(OUTD, exist_ok=True)
    open(AUD, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)

# ── 取回（带重试 + 可见）──────────────────────────────────────────
def arxiv_get(url, attempts=None, timeout=TIMEOUT, tag=""):
    """返回 (root, err)。root 为 None 即失败。

    每次退避打一行 stderr：不然「在退避」和「卡死了」长得一模一样（实测被 Ctrl-C 过）。
    """
    attempts = attempts or ATTEMPTS
    last = ""
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return ET.fromstring(r.read()), ""
        except urllib.error.HTTPError as he:
            last = "HTTP %s" % he.code
            if he.code not in (429, 500, 502, 503, 504):
                return None, last            # 4xx 重试无用，立刻返回
            wait = min(10 * (i + 1), 25)
        except Exception as ex:
            last = str(ex)[:90]
            wait = min(5 * (i + 1), 20)
        if i < attempts - 1:
            if RETRY_SPENT[0] >= RETRY_BUDGET:
                return None, last + "（重试预算用尽）"
            print("  ↻ %s 重试 %d/%d（%s，等 %ds）"
                  % (tag or "?", i + 1, attempts, last, wait), file=sys.stderr)
            time.sleep(wait)
            RETRY_SPENT[0] += wait
    return None, last

def q_of(term):
    if term.startswith(("cat:", "ti:", "abs:", "all:")):
        return term
    if NAMES_MODE:
        return (f'ti:"{term}" AND (cat:cs.CR OR cat:cs.CE OR cat:cs.GT OR cat:cs.DC '
                'OR cat:q-fin.CP OR cat:q-fin.GN)')
    return f'ti:"{term}"'

def total_of(q, d, n=None, tag="", attempts=RETRY_ATTEMPTS, timeout=TIMEOUT):
    """返回 (totalResults, entries)。失败返回 (-1, [])。"""
    since = (now - timedelta(days=d)).strftime("%Y%m%d%H%M")
    p = {"search_query": f"({q}) AND submittedDate:[{since} TO {now:%Y%m%d%H%M}]",
         "start": 0, "max_results": n or MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root, _ = arxiv_get(API + "?" + urllib.parse.urlencode(p),
                        attempts=attempts, timeout=timeout, tag=tag)
    if root is None:
        return -1, []
    node = root.find(OPENSEARCH)
    return (int(node.text) if node is not None and node.text else 0), \
           root.findall("a:entry", NS)

def fetch_term(term, attempts=None):
    q = q_of(term)
    p = {"search_query": f"({q}) AND submittedDate:{win}",
         "start": 0, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root, err = arxiv_get(API + "?" + urllib.parse.urlencode(p),
                          attempts=attempts, tag=term)
    return q, root, err

# ── preflight ────────────────────────────────────────────────────
pf_ok, pf_err = True, ""
pf_tot, _ = total_of("all:electron", DAYS, 1, tag="preflight",
                     attempts=PREFLIGHT_ATTEMPTS, timeout=PREFLIGHT_TIMEOUT)
if pf_tot < 0:
    pf_ok, pf_err = False, pf_err or "preflight 请求失败"

if not pf_ok:
    write_audit(["[%s] preflight 失败 —— arXiv 侧不可用，未扫描" % VERSION,
                 "查询  : all:electron（窗口 %dd，max_results=1）" % DAYS,
                 "耗时  %.0fs（含重试 %.0fs）" % (time.time() - T0, RETRY_SPENT[0]),
                 "",
                 "读法: 这是**API 侧**的问题，跟词表无关 —— 一个词都没试过，",
                 "     所以既不是「零命中」也不是「词不行」。隔 10–30 分钟再跑。",
                 "     total=0 才是词的问题；read timeout / 429 是 arXiv 的问题。"])
    print("STATUS: ARXIV_RADAR_DEGRADED · preflight 失败（arXiv 侧不可用）· 未尝试 %d"
          % len(TERMS))
    sys.exit(0)

# ── check 模式 ───────────────────────────────────────────────────
if CHECK:
    q = q_of(CHECK)
    print("候选词: %r" % CHECK)
    print("查询  : %s" % q)
    print("已在词表: %s" % ("是" if CHECK in TERMS else "否"))
    if UNKNOWN:
        print("⚠️ 未识别 token（会被忽略）: " + " · ".join(UNKNOWN))
    print()
    print("窗口   total  已见/100  领域命中  前 3 条标题")
    for d in (7, 30, 60, 90):
        print("  … 量 %dd" % d, flush=True)
        tot, ents = total_of(q, d, tag="check:%dd" % d)
        if tot < 0:
            print("%4dd  查询失败" % d, flush=True)
            continue
        cap = min(tot, MAX_RESULTS)
        seen_n = dom_n = 0
        titles = []
        for e in ents[:MAX_RESULTS]:
            aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
            title = " ".join(e.find("a:title", NS).text.split())
            summ = " ".join(e.find("a:summary", NS).text.split())
            if aid in seen:
                seen_n += 1
            if any(c in (title + " " + summ).lower() for c in DOMAIN):
                dom_n += 1
            if len(titles) < 3:
                titles.append(title)
        print("%4dd %7d %10s %10s" % (d, tot, "%d/%d" % (seen_n, cap),
                                      "%d/%d" % (dom_n, cap)), flush=True)
        for t in titles:
            print("        · %s" % t[:72], flush=True)
        time.sleep(3)
    print()
    print("读法: 重叠度低 = 带来新条目；领域命中低 = 会污染；total 太小 = 稀有词。")
    print("     ti: 是**词干化短语匹配**（非子串精确）—— 前 3 条标题里找不到该词是正常的。")
    print("     四档全 0 = 换写法；换了写法仍全 0 = 这个名字没有 arxiv 足迹。")
    sys.exit(0)

def guess_name(title, summ, known):
    for n in known:
        if re.search(rf"\b{re.escape(n)}\b", title + " " + summ, re.I):
            return n
    m = re.search(r"\b([A-Z][A-Za-z0-9\-]{2,})(?:'s|\u2019s)\b", title + " " + summ)
    if m:
        return m.group(1)
    for w in re.findall(r"\b[A-Z][A-Za-z0-9\-]{2,}\b", title):
        if w.lower() not in STOP:
            return w
    return ""

def short_term(t):
    """查询串剥成能读的短形：ti:"consensus" AND cat:cs.DC → consensus"""
    t = t.replace('ti:"', "").replace('"', "")
    t = re.sub(r"\s+AND\s+cat:cs\.\w+", "", t)
    t = re.sub(r"^cat:cs\.\w+\s+AND\s+", "", t)
    return t.strip()

out, raw, newest = [], 0, ""
drop = {"seen_mem": 0, "seen_dup": 0, "excl": 0, "carrier": 0, "fail": 0}
hit_ids = {}          # run 内判重；不要直接写 seen，否则跨词命中只记第一个词
per_term = {}
raw_term = {}
failed_t = []
skipped_t = []
fail_reason = {}
cross = {}            # 零命中词的跨窗 total_count；-1 = 该档查询失败
dropped = {"excl": [], "carrier": []}   # 丢掉的名字 —— 索引封顶期这是唯一未知量
DROPPED_CAP = 12

def absorb(root, term):
    """把一次成功取回的结果吃进 out/raw/drop。返回该词原始条数。

    抽成函数是为了让补扫复用同一段逻辑，不必写第二遍。
    """
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
               "title": title, "published": pub, "link": f"https://arxiv.org/abs/{aid}",
               "carrier": next(c for c in carrier if c in blob)}
        out.append(rec)
        hit_ids[aid] = rec
        per_term[term] = per_term.get(term, 0) + 1
    return n

def cross_probe(term, q):
    """窗口内零命中 → 跨更宽的档量真实 total_count，避免把「窗口太短」读成「真零」。"""
    if raw_term.get(term, 0) == 0:
        for d in CROSS_WINDOWS:
            cross.setdefault(term, {})[d] = total_of(q, d, 1, tag="cross:%s" % term)[0]
            time.sleep(3)

# ── 主循环（带熔断）──────────────────────────────────────────────
consec = 0
for idx, term in enumerate(TERMS):
    q, root, err = fetch_term(term)
    if root is None:
        print(f"! {term}: {err}", file=sys.stderr)
        drop["fail"] += 1
        failed_t.append(term)
        fail_reason[term] = err
        consec += 1
        if consec >= CONSEC_FAIL_LIMIT:
            skipped_t = list(TERMS[idx + 1:])
            print("⚠️ 连续 %d 个词全失败 → 判定 arXiv 侧降级，跳过剩余 %d 个词"
                  % (consec, len(skipped_t)), file=sys.stderr)
            break
        time.sleep(3)
        continue
    consec = 0
    absorb(root, term)
    cross_probe(term, q)
    time.sleep(3)

# ── 补扫：失败词一次性重试，跑在主循环之外（429 是成簇的，立刻重试没用）────
rescued = 0
if failed_t:
    print("↻ 补扫 %d 个失败词（先等 %ds 让 API 缓一下）: %s"
          % (len(failed_t), RETRY_COOLDOWN, " · ".join(failed_t)), file=sys.stderr)
    time.sleep(RETRY_COOLDOWN)
    still = []
    for term in list(failed_t):
        q, root, err = fetch_term(term, attempts=RETRY_ATTEMPTS)
        if root is None:
            fail_reason[term] = err + "（补扫仍失败）"
            still.append(term)
            continue
        rescued += 1
        drop["fail"] -= 1
        absorb(root, term)
        cross_probe(term, q)
        time.sleep(3)
    failed_t = still

out.sort(key=lambda c: c["published"], reverse=True)
T_RUN = time.time() - T0

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

truly_zero = [t for t in TERMS if t not in failed_t and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and per_term.get(t, 0) == 0]
with_new = [t for t in TERMS if per_term.get(t, 0) > 0]

WD = "一二三四五六日"
lag, wd, hint = -1, "?", "?"
if newest:
    nd = datetime.strptime(newest, "%Y-%m-%d")
    lag = (now.date() - nd.date()).days
    wd = "周" + WD[nd.weekday()]
    hint = ("正常（周末不公告；周一/周二看到 3–4 天属节律）" if lag <= 4
            else "偏大，先怀疑索引滞后，不是零命中")

L = ["[%s] 扫 %d 词 | 窗口 %s | 原始 %d | 幸存 %d | var=%r"
     % (VERSION, len(TERMS), win, raw, len(out), var),
     "丢弃 seen(记忆)=%d seen(本轮重复)=%d excl=%d carrier=%d 首次失败=%d"
     % (drop["seen_mem"], drop["seen_dup"], drop["excl"], drop["carrier"], drop["fail"]),
     "词表六分类 —— 未测到(试过失败) %d / 未尝试(熔断跳过) %d / 窗口内零命中 %d / "
     "全已见(饱和) %d / 有新增 %d"
     % (len(failed_t), len(skipped_t), len(truly_zero), len(saturated), len(with_new)),
     "跨窗档 %s（只取 > %dd 的档；等宽档是 win 列的副本，不重复量）"
     % (("·".join("%dd" % d for d in CROSS_WINDOWS) or "无"), DAYS),
     "耗时 扫描 %.0fs（含重试 %.0fs）· 补扫救回 %d · 总 %.0fs"
     % (T_RUN, RETRY_SPENT[0], rescued, time.time() - T0),
     "窗口内最新收录日期: %s（%s，距今 %d 天）→ %s"
     % (newest or "(无)", wd, lag, hint)]

if UNKNOWN:
    L.append("⚠️ 未识别 var token（会被静默忽略）: " + " · ".join(UNKNOWN))
if failed_t:
    L.append("⚠️ 未测到（试过、失败 —— **不是零命中**）: "
             + " · ".join("%s(%s)" % (t, fail_reason.get(t, "?")) for t in failed_t))
if skipped_t:
    L.append("⚠️ 未尝试（熔断跳过 —— 一个词都没试过）: " + " · ".join(skipped_t))
if truly_zero:
    L.append("⚠️ 窗口内零命中 %d 个 —— 已跨窗量 total_count（win=%dd / %s）："
             % (len(truly_zero), DAYS, " / ".join("%dd" % d for d in CROSS_WINDOWS) or "无"))
    short, real, unk = [], [], []
    for t in truly_zero:
        c = cross.get(t) or {}
        vals = " ".join("%dd=%s" % (d, c.get(d)) for d in CROSS_WINDOWS)
        if any(c.get(d) is None for d in CROSS_WINDOWS):
            unk.append(t); verdict = "跨窗查询失败（存疑，先别删）"
        elif any((c.get(d) or 0) > 0 for d in CROSS_WINDOWS):
            short.append(t); verdict = "窗口太短 → 非真零，别删"
        else:
            real.append(t); verdict = "跨窗皆 0 → **先用 check: 换同义写法**；连写法都 0 才是死词"
        L.append("   %s: win=0 %s → %s" % (t, vals, verdict))
    L.append("   └ 小结: 窗口太短 %d · 真零 %d · 跨窗失败 %d"
             % (len(short), len(real), len(unk)))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))
for k, label in (("carrier", "carrier 无命中"), ("excl", "EXCL 命中")):
    if dropped[k]:
        L.append("ℹ️ %s 丢弃 %d 条（**误杀只能在这里看见**）:" % (label, drop[k]))
        for pub, t in dropped[k][:8]:
            L.append("   %s %s" % (pub, t))
L.append("词表原始/新收: " + " · ".join(
    "%s=%d/%d" % (k, v, per_term.get(k, 0)) for k, v in
    sorted(raw_term.items(), key=lambda x: -x[1])))
for c in out[:25]:
    L.append("  %s [%s] %s" % (c["published"], "+".join(c["terms"]), c["title"][:85]))
if not out and not with_new:
    if drop["excl"] or drop["carrier"]:
        L.append("ℹ️ 本轮 0 幸存，但**不是 seen 吃干了**：有 %d 条穿过了 seen 却全死在过滤器"
                 "（excl=%d carrier=%d）—— 名单见上，这 %d 条是唯一未知。"
                 % (drop["excl"] + drop["carrier"], drop["excl"], drop["carrier"],
                    drop["excl"] + drop["carrier"]))
    else:
        L.append("ℹ️ 本轮 0 幸存 = 结构性（全部命中已在 seen）。不是故障。")

write_audit(L)

# ── 落盘 / 通知 ───────────────────────────────────────────────────
if not DRY and hit_ids:
    merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
    merged.update(seen)
    # 保新不保旧：merged 是「新的在前」，截尾会留最旧 → 最近看到的论文掉出 seen、下轮重报
    json.dump(dict(list(merged.items())[:2000]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 命中流水：append-only。out.json 每轮被覆盖，这是唯一的历史。
# 日期用报告日期（不是 published）—— 滞后要按「通道点亮那天」算。
if not DRY and out:
    fresh = not os.path.exists(HITS)
    with open(HITS, "a", encoding="utf-8") as f:
        if fresh:
            f.write("日期\t键\t名字\t方向\n")
        for c in out:
            f.write("%s\t%s\t%s\t\n"
                    % (now.strftime("%Y-%m-%d"), c["link"].split("/abs/")[-1],
                       (c["name"] or c["title"])[:60].replace("\t", " ")))

# 机械备用稿（已去噪：不重复名字、term 剥成短形、多词用 / 拼）。模型覆写成中文后发。
if out:
    R = ["**arxiv-radar** · 窗口 %d 天 · 幸存 %d" % (DAYS, len(out)), ""]
    for c in out[:NOTIFY_TOP]:
        t, nm = c["title"], c["name"]
        if nm and t.lower().startswith(nm.lower()):
            t = t[len(nm):].lstrip(" :—-·")
        R.append("- %s%s [%s] · %s"
                 % (("`%s` " % nm) if nm else "", t,
                    "/".join(short_term(x) for x in c["terms"]), c["link"]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

# 通知正文归模型：脚本不会翻译英文标题，也不会「按簇分组」。
# 默认不发 —— 模型覆写 REPORT 为中文后自己发。notify:script 走降级路径。
if DRY or not out:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else "零命中"))
elif SEND:
    if os.path.exists("./notify"):
        r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
        print("notify: 已由脚本发出 · %s"
              % ((r.stdout or r.stderr or "ok").strip()[:200]))
    else:
        print("notify: 跳过（没有 ./notify）")
else:
    print("notify: 待模型覆写 output/arxiv/report.md 后自行发出")
print("STATUS: ARXIV_RADAR_OK · 原始 %d · 幸存 %d · 总耗时 %.0fs"
      % (raw, len(out), time.time() - T0))
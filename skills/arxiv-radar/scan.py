#!/usr/bin/env python3
"""arxiv-radar 扫描器。vF

var token（空格分隔，可组合）:
    dry-run      跳过 notify、不写 seen、不写 hits
    days:N       窗口天数，默认 30
    names        词表整个换成 memory/universe-names.txt
    check:<词>   **必须放最后**，其后全部内容（含空格）都是词。只量这个词
                 （7/30/60/90 四档 total + 已见重叠 + 领域命中），跑完退出
    notify:script  让脚本自己发通知（默认不发，见下）

arXiv 侧会整段降级（实证：`read operation timed out` 与 `HTTP 429` 交替出现，
整批请求全挂，约 10 分钟后自行恢复）。降级期里重试**是在加码**，所以三层：

  1) preflight：开跑前一条最小带窗请求。失败就直接收场，不让 24 个词去撞墙。
  2) 熔断：主循环连续 CONSEC_FAIL_LIMIT 个词全失败 → 停手，剩余词记「未尝试」。
     **「试过失败」和「没试过」必须分开记** —— 前者是空洞，后者是没数据。
  3) 补扫：只在主循环跑完后做一次（隔 RETRY_COOLDOWN 秒、4 次尝试）。

失败绝不能读成零命中：total=0 是词/写法的问题（arXiv 答了，答案是"没有"），
read timeout / 429 是 arXiv 侧的问题（arXiv 没答），跟词无关。

check: 不能靠 var.split() 解析 —— 它按空格切，`check:consensus protocol` 会被切成
"check:consensus" + "protocol"，静默地量成 ti:"consensus"（实测踩过）。
check 模式回显「查询」和「已在词表」两行，用来一眼发现量错了词。
stdout 进管道会块缓冲，实时进度一律打 stderr；表格本身已加 flush。

零命中 ≠「可考虑删词」：跨窗档 = (30,60,90) 中所有 > DAYS 的值，全部为 0 时判词是
「**先用 check: 换同义写法**」—— arXiv 的 ti: 是词干化短语匹配，0 命中多半是写法不对。

产物（文件名固定，别改成 radar2.json）:
    output/arxiv/out.json      全部幸存者
    output/arxiv/audit.log     审计（同时打到 stdout；降级收场也写）
    output/arxiv/report.md     通知正文（脚本写机械版 → 模型覆写成中文）
    memory/arxiv-seen.json     非 dry-run 才写
    memory/arxiv-hits.tsv      命中流水，append-only，非 dry-run 才写（3 列：日期/键/名字）
    memory/arxiv-labels.tsv    方向标签，append-only，**模型写**（键 \\t 方向，无表头）
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone

VERSION = "vF"

OUTD = "output/arxiv"
OUT, AUD, REPORT = OUTD + "/out.json", OUTD + "/audit.log", OUTD + "/report.md"
SEEN = "memory/arxiv-seen.json"
HITS = "memory/arxiv-hits.tsv"
LABELS = "memory/arxiv-labels.tsv"
NAMES_FILE = "memory/universe-names.txt"
NOTIFY_TOP = 30
MAX_RESULTS = 100
# https 直连：http 会先吃一个 301（实测 0.3s/请求，一轮 ~40 请求白花约 12 秒），
# 而且平白依赖 urlopen 的重定向跟随。
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}totalResults"
DOMAIN = None      # check 模式用：三个 carrier 域的并集

ATTEMPTS = 2
RETRY_ATTEMPTS = 4
RETRY_COOLDOWN = 20
PREFLIGHT_ATTEMPTS = 2
PREFLIGHT_TIMEOUT = 25     # 实测 arXiv 冷启动首条要 7.2s，别卡太紧
CONSEC_FAIL_LIMIT = 3
TIMEOUT = 45
RETRY_BUDGET = 900
RETRY_SPENT = [0.0]

# ── var ───────────────────────────────────────────────────────────
var = sys.argv[1] if len(sys.argv) > 1 else ""

DRY, DAYS, NAMES_MODE, CHECK, SEND, UNKNOWN = False, 30, False, "", False, []

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
TERMS = [t.strip() for t in """
proof-of-useful-work
verifiable inference
light client
proof of training
proof of learning
verifiable training
auditable training
data availability sampling
restaking
automated market maker
# ── 共识：2026-10-26 换写法。原 `consensus protocol` 实测 30d=0 / 60d=4
#    （低于 30d 窗的检测下限 → 永远不响）；`consensus mechanism` 四档全 0。
#    改测 ti:"consensus" AND cat:cs.DC：30d=6 / 60d=18 / 90d=27，
#    领域命中 6/6 · 17/18 · 26/27（≈100%），已见仅 0/6 · 4/18。
#    宽 4.5 倍、精度不掉 —— 「有词 ≠ 有召回」的第二例，修法是换写法不是加窗口。
ti:"consensus" AND cat:cs.DC
cat:cs.CR AND ti:"MEV"
liquid staking
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
ti:"Robinhood Chain"
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

if NAMES_MODE and os.path.exists(NAMES_FILE):
    TERMS = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

known = []
if os.path.exists(NAMES_FILE):
    known = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

CARRIER_BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
                "production", "open-source", "released", "blockchain", "network",
                "token", "incentive", "marketplace", "validator", "miner"]
CARRIER_ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
                 "simulator", "dataset", "datasets", "real-world", "embodied",
                 "sensor", "egocentric", "demonstration", "vla"]
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher",
                  "ledger", "ledgers", "block creator", "block builder",
                  "block proposer", "transaction ordering", "on-chain",
                  "state transition"]
CARRIER_BY_TERM = {
    "embodied data": CARRIER_ROBOT,
    "robot manipulation data": CARRIER_ROBOT,
    "robot data": CARRIER_ROBOT,
    "embodied AI": CARRIER_ROBOT,
    'ti:"data engine" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"human data" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"egocentric" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"data generation" AND cat:cs.RO': CARRIER_ROBOT,
    'ti:"consensus" AND cat:cs.DC': CARRIER_BASE,
    "automated market maker": CARRIER_BASE + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_BASE + CARRIER_MARKET,
}
DOMAIN = CARRIER_BASE + CARRIER_ROBOT + CARRIER_MARKET
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

def arxiv_get(url, attempts=None, timeout=TIMEOUT, tag=""):
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
                  % (tag or "?", i + 1, attempts, last, wait),
                  file=sys.stderr, flush=True)
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

def total_of(q, d, n=None, tag="", attempts=None, timeout=TIMEOUT):
    """(totalResults, entries)。total=-1 表示**查询失败**，不是 0。"""
    w = f"[{(now - timedelta(days=d)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"
    p = {"search_query": f"({q}) AND submittedDate:{w}", "start": 0,
         "max_results": n or MAX_RESULTS,
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
        print("  … 量 %dd" % d, file=sys.stderr, flush=True)
        tot, ents = total_of(q, d, tag="check:%dd" % d)
        if tot < 0:
            print("%4dd  查询失败" % d, flush=True)
            if d == 7:
                print("  ⚠️ 首个窗口就全失败 → 判定 arXiv 侧降级，剩余窗口跳过",
                      file=sys.stderr, flush=True)
                break
            continue
        ins = sum(1 for e in ents
                  if e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0] in seen)
        dom = sum(1 for e in ents
                  if any(c in (" ".join(e.find("a:title", NS).text.split()) + " " +
                               " ".join(e.find("a:summary", NS).text.split())).lower()
                         for c in DOMAIN))
        print("%4dd  %5d  %8d/%d  %8d/%d" % (d, tot, ins, len(ents), dom, len(ents)),
              flush=True)
        for e in ents[:3]:
            print("        · " + " ".join(e.find("a:title", NS).text.split())[:78],
                  flush=True)
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
hit_ids = {}
per_term = {}
raw_term = {}
failed_t = []
fail_reason = {}
cross = {}
dropped = {"excl": [], "carrier": []}
DROPPED_CAP = 12

def absorb(root, term):
    global raw, newest
    n = 0
    carrier = CARRIER_BY_TERM.get(term, CARRIER_BASE)
    for e in root.findall("a:entry", NS):
        n += 1
        raw += 1
        raw_term[term] = raw_term.get(term, 0) + 1
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
    if raw_term.get(term, 0) == 0:
        for d in CROSS_WINDOWS:
            cross.setdefault(term, {})[d] = total_of(q, d, 1, tag="cross:%dd" % d)[0]
            time.sleep(3)

# ── 主循环（重试 2 次快速脱身；连续失败则熔断）──────────────────
attempted = 0
consec_fail = 0
tripped = False

for term in TERMS:
    attempted += 1
    q, root, err = fetch_term(term)
    if root is None:
        drop["fail"] += 1
        failed_t.append(term)
        fail_reason[term] = err
        consec_fail += 1
        if consec_fail >= CONSEC_FAIL_LIMIT and attempted < len(TERMS):
            tripped = True
            print("⚠️ 连续 %d 个词全失败 → 判定 arXiv 侧降级，跳过剩余 %d 个词"
                  % (consec_fail, len(TERMS) - attempted),
                  file=sys.stderr, flush=True)
            break
        time.sleep(3)
        continue
    consec_fail = 0
    absorb(root, term)
    cross_probe(term, q)
    time.sleep(3)

skipped_t = TERMS[attempted:] if tripped else []

rescued = 0
if failed_t:
    print("↻ 补扫 %d 个失败词（先等 %ds）: %s"
          % (len(failed_t), RETRY_COOLDOWN, " · ".join(failed_t)), file=sys.stderr)
    time.sleep(RETRY_COOLDOWN)
    for term in list(failed_t):
        q, root, err = fetch_term(term, attempts=RETRY_ATTEMPTS)
        if root is None:
            fail_reason[term] = err + "（补扫仍失败）"
            time.sleep(3)
            continue
        failed_t.remove(term)
        fail_reason.pop(term, None)
        rescued += 1
        absorb(root, term)
        cross_probe(term, q)
        time.sleep(3)
    print("↻ 补扫结束：救回 %d · 仍失败 %d" % (rescued, len(failed_t)),
          file=sys.stderr, flush=True)

out.sort(key=lambda c: c["published"], reverse=True)
T_RUN = time.time() - T0

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

attempted_t = TERMS[:attempted]
truly_zero = [t for t in attempted_t if t not in failed_t and raw_term.get(t, 0) == 0]
saturated = [t for t in attempted_t if raw_term.get(t, 0) > 0 and per_term.get(t, 0) == 0]
with_new = [t for t in attempted_t if per_term.get(t, 0) > 0]

cz_short, cz_real, cz_unk = [], [], []
for t in truly_zero:
    c = cross.get(t) or {}
    vals = [c.get(d) for d in CROSS_WINDOWS]
    if any(v in (None, -1) for v in vals):
        cz_unk.append(t)
    elif any((v or 0) > 0 for v in vals):
        cz_short.append(t)
    else:
        cz_real.append(t)

CW_TXT = "/".join("%dd" % d for d in CROSS_WINDOWS) or "(无跨窗档)"

L = ["[%s] 扫 %d 词 | 窗口 %s | 原始 %d | 幸存 %d | var=%r"
     % (VERSION, len(TERMS), win, raw, len(out), var),
     "丢弃 seen(记忆)=%d seen(本轮重复)=%d excl=%d carrier=%d 首次失败=%d"
     % (drop["seen_mem"], drop["seen_dup"], drop["excl"], drop["carrier"], drop["fail"]),
     "词表六分类 —— 未测到(试过失败) %d / 未尝试(熔断跳过) %d / 窗口内零命中 %d / "
     "全已见(饱和) %d / 有新增 %d"
     % (len(failed_t), len(skipped_t), len(truly_zero), len(saturated), len(with_new)),
     "跨窗档 %s（只取 > %dd 的档；等宽档是 win 列的副本，不重复量）" % (CW_TXT, DAYS),
     "耗时 扫描 %.0fs（含重试 %.0fs）· 补扫救回 %d · 总 %.0fs"
     % (T_RUN, RETRY_SPENT[0], rescued, time.time() - T0)]

WD = "一二三四五六日"
if newest:
    try:
        nd = datetime.strptime(newest, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        lag = (now - nd).days
        hint = ("正常（周末不公告；周一/周二看到 3–4 天属节律）"
                if lag >= 3 and now.weekday() <= 1 else
                "正常" if lag <= 2 else
                "偏大 —— **周中出现 3 天以上才该去查 arXiv status**")
        L.append("窗口内最新收录日期: %s（周%s，距今 %d 天）→ %s"
                 % (newest, WD[nd.weekday()], lag, hint))
    except Exception:
        L.append("窗口内最新收录日期: %s" % newest)
else:
    L.append("窗口内最新收录日期: (无)")

if UNKNOWN:
    L.append("⚠️ 未识别 var token（会被静默忽略）: " + " · ".join(UNKNOWN))
if tripped:
    L.append("🛑 **熔断**：连续 %d 个词全失败 → 判定 arXiv 侧降级，停手。" % CONSEC_FAIL_LIMIT)
if failed_t:
    L.append("⚠️ 未测到 %d 个（主循环 %d 次 + 补扫 %d 次后仍失败，**不是零命中**）: %s"
             % (len(failed_t), ATTEMPTS, RETRY_ATTEMPTS, " · ".join(failed_t)))
    L.append("   └ 这 %d 个词的窗口是空洞，别按零读。原因: %s"
             % (len(failed_t),
                " · ".join("%s=%s" % (t, fail_reason.get(t, "?")) for t in failed_t[:6])))
if skipped_t:
    L.append("⚠️ 未尝试 %d 个（熔断后没轮到，**连试都没试**）: %s"
             % (len(skipped_t), " · ".join(skipped_t)))
if truly_zero:
    if not CROSS_WINDOWS:
        L.append("⚠️ 窗口内零命中 %d 个（无更宽档可退，按真零读）: %s"
                 % (len(truly_zero), " · ".join(truly_zero)))
    else:
        L.append("⚠️ 窗口内零命中 %d 个 —— 已跨窗量 total_count（win=%dd / %s）："
                 % (len(truly_zero), DAYS, CW_TXT))
        for t in truly_zero:
            c = cross.get(t) or {}
            body = " ".join("%dd=%s" % (d, c.get(d)) for d in CROSS_WINDOWS)
            v = ("跨窗查询失败 → 存疑，别删" if t in cz_unk else
                 "窗口太短 → 非真零，别删" if t in cz_short else
                 "跨窗皆 0 → **先用 check: 换同义写法**；连写法都 0 才是死词")
            L.append("   %s: win=%d %s → %s" % (t, raw_term.get(t, 0), body, v))
        L.append("   └ 小结: 窗口太短 %d · 真零 %d · 跨窗失败 %d"
                 % (len(cz_short), len(cz_real), len(cz_unk)))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))

for k, label in (("carrier", "carrier 无命中"), ("excl", "EXCL 命中")):
    if dropped[k]:
        L.append("ℹ️ %s 丢弃 %d 条，前 %d 条:"
                 % (label, drop[k], min(len(dropped[k]), 8)))
        for pub, t in dropped[k][:8]:
            L.append("   %s  %s" % (pub, t))

L.append("词表原始/新收: " + " · ".join(
    "%s=%d/%d" % (k, v, per_term.get(k, 0)) for k, v in
    sorted(raw_term.items(), key=lambda x: -x[1])))
for c in out[:25]:
    L.append("  %s [%s] %s" % (c["published"], "+".join(c["terms"]), c["title"][:85]))

if not out and not with_new and not skipped_t:
    leak = drop["excl"] + drop["carrier"]
    if leak:
        L.append("ℹ️ 本轮 0 幸存，但**不是 seen 吃干了**：有 %d 条穿过了 seen 却全死在过滤器"
                 "（excl=%d carrier=%d）—— 名单见上，这 %d 条是本轮唯一未知量。"
                 % (leak, drop["excl"], drop["carrier"], leak))
    else:
        L.append("ℹ️ 本轮 0 幸存 = 结构性（命中全部已在 seen），不是故障。")

try:
    keys = set()
    if os.path.exists(HITS):
        for i, ln in enumerate(open(HITS, encoding="utf-8")):
            if i == 0:
                continue
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 2 and p[1]:
                keys.add(p[1])
    lab = set()
    if os.path.exists(LABELS):
        for ln in open(LABELS, encoding="utf-8"):
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 2 and p[1]:
                lab.add(p[0])
    if keys - lab:
        L.append("ℹ️ 未打方向标签 %d 条（`?` 也算已打；比对层会先补）: %s"
                 % (len(keys - lab), " · ".join(sorted(keys - lab)[:8])))
except Exception:
    pass

write_audit(L)

# ── 落盘 / 通知 ───────────────────────────────────────────────────
if not DRY and hit_ids:
    merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
    merged.update(seen)
    json.dump(dict(list(merged.items())[:2000]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if not DRY and out:
    fresh = not os.path.exists(HITS)
    need_nl = False
    if not fresh and os.path.getsize(HITS):
        with open(HITS, "rb") as fh:
            fh.seek(-1, 2)
            need_nl = fh.read(1) != b"\n"
    with open(HITS, "a", encoding="utf-8") as f:
        if fresh:
            f.write("日期\t键\t名字\n")
        elif need_nl:
            f.write("\n")
        for c in out:
            f.write("%s\t%s\t%s\n"
                    % (now.strftime("%Y-%m-%d"), c["link"].split("/abs/")[-1],
                       (c["name"] or c["title"])[:60].replace("\t", " ")))

if out:
    R = ["**arxiv-radar** · 窗口 %d 天 · 幸存 %d" % (DAYS, len(out)), ""]
    for c in out[:NOTIFY_TOP]:
        t, nm = c["title"], c["name"]
        if nm and t.lower().startswith(nm.lower()):
            t = t[len(nm):].lstrip(" :—-·")
        R.append("- %s%s [%s] · %s"
                 % (("`%s` " % nm) if nm else "", t, short_term(c["term"]), c["link"]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

if DRY or not out:
    print("notify: 跳过（%s）%s"
          % ("dry-run" if DRY else "零命中",
             " —— report.md 未覆写，仍是上一轮内容" if not DRY and not out else ""))
elif SEND:
    if os.path.exists("./notify"):
        r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
        print("notify: 已由脚本发出 · %s" % ((r.stdout or r.stderr or "ok").strip()[:180]))
    else:
        print("notify: ./notify 不存在")
else:
    print("notify: **未发** —— 用 Write 覆写 %s 为中文（按簇分组、每行带 [方向]）后：" % REPORT)
    print("        ./notify -f %s" % REPORT)
    print("        改不了就直接发机械版（已去噪），**别不发**。")

if tripped or failed_t:
    print("STATUS: ARXIV_RADAR_DEGRADED · 原始 %d · 幸存 %d · 未测到 %d · 未尝试 %d · "
          "总耗时 %.0fs" % (raw, len(out), len(failed_t), len(skipped_t), time.time() - T0))
else:
    print("STATUS: ARXIV_RADAR_OK · 原始 %d · 幸存 %d · 补扫救回 %d · 总耗时 %.0fs"
          % (raw, len(out), rescued, time.time() - T0))
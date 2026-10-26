#!/usr/bin/env python3
"""arxiv-radar 扫描器。

var token（空格分隔，可组合）:
    dry-run      跳过 notify、不写 seen、不写 hits
    days:N       窗口天数，默认 30
    names        词表整个换成 memory/universe-names.txt
    check:<词>   只量这个词（7/30/60/90 四档 total + 已见重叠 + 领域命中），跑完退出
    notify:script  让脚本自己发通知（默认不发，见下）

查询失败会重试 3 次（429 单独退避）；仍失败则进「未测到」分类，
**绝不能被读成零命中** —— 旧写法单次 urlopen 异常即 continue，是 66.7% 静默失败的原因。

零命中 ≠「可考虑删词」：脚本对**窗口内零命中**的词自动跨窗量 opensearch:totalResults，
跨窗档 = (30,60,90) 中所有 > DAYS 的值（窄窗制造假零，必须回退到更宽的窗）。
只有全部跨窗档都为 0 才判真零；跨窗查询本身失败（-1）单独归为「存疑」，不按真零读。

窗口只决定成本与冗余，不决定语义 —— 30d 是生产口径（arxiv 索引滞后 ~5 天，
7d 窗只剩 2 天余量）；days:60 是改词表/改 carrier 时的补历史诊断窗。

通知归属：正文归**模型**。脚本不会翻译英文标题，也不会"按簇分组"，
所以默认只写 output/arxiv/report.md 的机械列表，由模型覆写成中文后发。
无人值守场景用 notify:script 走降级路径。

产物（文件名固定，别改成 radar2.json）:
    output/arxiv/out.json      全部幸存者
    output/arxiv/audit.log     审计（同时打到 stdout）
    output/arxiv/report.md     通知正文（脚本写机械版 → 模型覆写成中文）
    memory/arxiv-seen.json     非 dry-run 才写
    memory/arxiv-hits.tsv      命中流水，append-only，非 dry-run 才写（3 列：日期/键/名字）
    memory/arxiv-labels.tsv    方向标签，append-only，**模型写**（键 \\t 方向，无表头）
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/arxiv"
OUT, AUD, REPORT = OUTD + "/out.json", OUTD + "/audit.log", OUTD + "/report.md"
SEEN = "memory/arxiv-seen.json"
HITS = "memory/arxiv-hits.tsv"
LABELS = "memory/arxiv-labels.tsv"
NAMES_FILE = "memory/universe-names.txt"
NOTIFY_TOP = 30
MAX_RESULTS = 100
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}totalResults"
DOMAIN = None      # check 模式用：三个 carrier 域的并集

# 失败重试。arXiv 限速是 1 req/3s，主循环本来就 sleep 3s，重试只在异常时叠加。
ATTEMPTS = 3
TIMEOUT = 45       # 实测补扫用 45s 才把 16 个失败词全捞回来
RETRY_BUDGET = 600 # 全轮重试总预算（秒）；超了就不再重试，直接标未测到
RETRY_SPENT = [0.0]

# ── var ───────────────────────────────────────────────────────────
var = sys.argv[1] if len(sys.argv) > 1 else ""
DRY, DAYS, NAMES_MODE, CHECK, SEND, UNKNOWN = False, 30, False, "", False, []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "names":
        NAMES_MODE = True
    elif tok == "notify:script":
        SEND = True
    elif tok.startswith("days:"):
        DAYS = int(tok.split(":", 1)[1] or 30)
    elif tok.startswith("check:"):
        CHECK = tok.split(":", 1)[1].strip()
    else:
        UNKNOWN.append(tok)

# 跨窗档必须严格大于 DAYS —— 否则那一档就是 win 列的副本，白花请求还假装是两个证据。
# days:30 → (60, 90) · days:60 → (90,) · days:90+ → ()（退化成窗口内判真零）
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
consensus protocol
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
win = f"[{(now - timedelta(days=DAYS)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

# ── 取回（带重试）────────────────────────────────────────────────
def arxiv_get(url, timeout=TIMEOUT):
    """返回 (root, err)。root 为 None 即失败 —— 失败必须能与「零命中」区分。"""
    last = ""
    for i in range(ATTEMPTS):
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
        if i < ATTEMPTS - 1:
            if RETRY_SPENT[0] >= RETRY_BUDGET:
                return None, last + "（重试预算用尽）"
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

def total_of(q, d, n=None):
    """(totalResults, entries)。total=-1 表示**查询失败**，不是 0。"""
    w = f"[{(now - timedelta(days=d)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"
    p = {"search_query": f"({q}) AND submittedDate:{w}", "start": 0,
         "max_results": n or MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root, _ = arxiv_get(API + "?" + urllib.parse.urlencode(p))
    if root is None:
        return -1, []
    node = root.find(OPENSEARCH)
    return (int(node.text) if node is not None and node.text else 0), \
           root.findall("a:entry", NS)

# ── check 模式：加词前量两个口径，量完退出 ────────────────────────
if CHECK:
    q = q_of(CHECK)
    print("候选词: %r" % CHECK)
    print("查询  : %s" % q)
    print("已在词表: %s" % ("是" if CHECK in TERMS else "否"))
    print()
    print("窗口   total  已见/100  领域命中  前 3 条标题")
    for d in (7, 30, 60, 90):
        tot, ents = total_of(q, d)
        if tot < 0:
            print("%4dd  查询失败" % d); time.sleep(3); continue
        ins = sum(1 for e in ents
                  if e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0] in seen)
        dom = sum(1 for e in ents
                  if any(c in (" ".join(e.find("a:title", NS).text.split()) + " " +
                               " ".join(e.find("a:summary", NS).text.split())).lower()
                         for c in DOMAIN))
        print("%4dd  %5d  %8d/%d  %8d/%d" % (d, tot, ins, len(ents), dom, len(ents)))
        for e in ents[:3]:
            print("        · " + " ".join(e.find("a:title", NS).text.split())[:78])
        time.sleep(3)
    print()
    print("读法: 重叠度低 = 带来新条目；领域命中低 = 会污染；total 太小 = 稀有词。")
    print("     四档全 0 = 写法可能不对，换写法再量。")
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
    """把查询串剥成能读的短形：ti:"egocentric" AND cat:cs.RO → egocentric"""
    t = t.replace('ti:"', "").replace('"', "")
    t = t.replace(" AND cat:cs.RO", "").replace("cat:cs.CR AND ", "")
    return t.strip()

out, raw, newest = [], 0, ""
drop = {"seen": 0, "excl": 0, "carrier": 0, "fail": 0}
hit_ids = {}          # run 内判重；不要直接写 seen，否则跨词命中只记第一个词
per_term = {}
raw_term = {}
failed_t = []
fail_reason = {}
cross = {}            # 零命中词的跨窗 total_count；-1 = 该档查询失败

for term in TERMS:
    carrier = CARRIER_BY_TERM.get(term, CARRIER_BASE)
    q = q_of(term)

    p = {"search_query": f"({q}) AND submittedDate:{win}",
         "start": 0, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root, err = arxiv_get(API + "?" + urllib.parse.urlencode(p))
    if root is None:
        print(f"! {term}: {err}", file=sys.stderr)
        drop["fail"] += 1
        failed_t.append(term)
        fail_reason[term] = err
        time.sleep(3)
        continue

    for e in root.findall("a:entry", NS):
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
            drop["seen"] += 1
            continue
        if aid in hit_ids:
            hit_ids[aid]["terms"].append(term)
            drop["seen"] += 1
            continue
        if any(x in title.lower() for x in EXCL):
            drop["excl"] += 1
            continue
        if not any(c in blob for c in carrier):
            drop["carrier"] += 1
            continue
        rec = {"term": term, "terms": [term], "name": guess_name(title, summ, known),
               "title": title, "published": pub, "link": f"https://arxiv.org/abs/{aid}",
               "carrier": next(c for c in carrier if c in blob)}
        out.append(rec)
        hit_ids[aid] = rec
        per_term[term] = per_term.get(term, 0) + 1

    # 窗口内零命中 → 跨更宽的档量真实 total_count，避免把「窗口太短」读成「真零」
    if raw_term.get(term, 0) == 0:
        for d in CROSS_WINDOWS:
            cross.setdefault(term, {})[d] = total_of(q, d, 1)[0]
            time.sleep(3)
    time.sleep(3)

out.sort(key=lambda c: c["published"], reverse=True)
T_RUN = time.time() - T0

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

truly_zero = [t for t in TERMS if t not in failed_t and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and per_term.get(t, 0) == 0]
with_new = [t for t in TERMS if per_term.get(t, 0) > 0]

# 跨窗分类。**-1 是查询失败，不能按 0 读** —— 否则跨窗本身成了新的假删来源。
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

L = ["扫 %d 词 | 窗口 %s | 原始 %d | 幸存 %d | var=%r"
     % (len(TERMS), win, raw, len(out), var),
     "丢弃 seen=%d excl=%d carrier=%d fail=%d"
     % (drop["seen"], drop["excl"], drop["carrier"], drop["fail"]),
     "词表五分类 —— 未测到(查询失败) %d / 窗口内零命中 %d / 全已见(饱和) %d / 有新增 %d"
     % (len(failed_t), len(truly_zero), len(saturated), len(with_new)),
     "窗口内最新收录日期: %s   ← 比今天早 3 天以上即索引滞后，不是零命中"
     % (newest or "(无)"),
     "跨窗档 %s（只取 > %dd 的档；等宽档是 win 列的副本，不重复量）"
     % (CW_TXT, DAYS),
     "耗时 扫描 %.0fs（含重试 %.0fs）· 总 %.0fs"
     % (T_RUN, RETRY_SPENT[0], time.time() - T0)]
if UNKNOWN:
    L.append("⚠️ 未识别 var token（会被静默忽略）: " + " · ".join(UNKNOWN))
if failed_t:
    L.append("⚠️ 未测到 %d 个（重试 %d 次后仍失败，**不是零命中**）: %s"
             % (len(failed_t), ATTEMPTS, " · ".join(failed_t)))
    L.append("   └ **本轮结论不完整**：这 %d 个词的窗口是空洞，别按零读。原因: %s"
             % (len(failed_t),
                " · ".join("%s=%s" % (t, fail_reason.get(t, "?")) for t in failed_t[:6])))
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
                 "真零（%s 皆 0）→ 可考虑删词" % CW_TXT)
            L.append("   %s: win=%d %s → %s" % (t, raw_term.get(t, 0), body, v))
        L.append("   └ 小结: 窗口太短 %d · 真零 %d · 跨窗失败 %d"
                 % (len(cz_short), len(cz_real), len(cz_unk)))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))
L.append("词表原始/新收: " + " · ".join(
    "%s=%d/%d" % (k, v, per_term.get(k, 0)) for k, v in
    sorted(raw_term.items(), key=lambda x: -x[1])))
for c in out[:25]:
    L.append("  %s [%s] %s" % (c["published"], "+".join(c["terms"]), c["title"][:85]))

# 标签覆盖自检：hits 有、labels 没有的 → 比对层会补，但空洞要可见（`?` 也算已打）
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

open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ── 落盘 / 通知 ───────────────────────────────────────────────────
if not DRY and hit_ids:
    merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-2000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 命中流水：append-only，3 列（方向归 labels.tsv，一列一个 owner）。
# 日期用报告日期（不是 published）—— 滞后要按「通道点亮那天」算。
# 追加前先补换行：上一次写入若没以 \n 结尾，两行会粘连（实证过，1 行 4 字段）。
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

# 机械备用稿（已去噪：不重复名字、term 剥成短形）。模型覆写成中文后发。
if out:
    R = ["**arxiv-radar** · 窗口 %d 天 · 幸存 %d" % (DAYS, len(out)), ""]
    for c in out[:NOTIFY_TOP]:
        t, nm = c["title"], c["name"]
        if nm and t.lower().startswith(nm.lower()):
            t = t[len(nm):].lstrip(" :—-·")
        R.append("- %s%s [%s] · %s"
                 % (("`%s` " % nm) if nm else "", t, short_term(c["term"]), c["link"]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

# 通知正文归模型：脚本不会翻译英文标题，也不会"按簇分组"。
# 默认不发 —— 模型覆写 REPORT 为中文后自己发。notify:script 走降级路径。
if DRY or not out:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else "零命中"))
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
print("STATUS: ARXIV_RADAR_OK · 原始 %d · 幸存 %d · 未测到 %d · 总耗时 %.0fs"
      % (raw, len(out), len(failed_t), time.time() - T0))
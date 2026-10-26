#!/usr/bin/env python3
"""arxiv-radar 扫描器（静态文件 —— 模型只调用，不重写）。

用法:
    python3 skills/arxiv-radar/scan.py "days:30"
    python3 skills/arxiv-radar/scan.py "names"           # 机制/名字反查模式
    python3 skills/arxiv-radar/scan.py "check:world model"  # 量候选词两个口径后退出

var token（空格分隔，可组合）:
    dry-run        跳过 notify、不写 seen、不写 hits
    days:N         窗口天数，默认 30
    names          词表整个换成 memory/universe-names.txt
    check:<词>      只量这个词，跑完退出
    notify:script  让脚本自己发通知（默认不发，见下）

通知归属：正文归**模型**。脚本不会翻译英文标题，也不会"按簇分组"，
所以默认只写 output/arxiv/report.md 的机械备用稿（已去噪，能读），
由模型用 Write 工具覆写成中文（按簇分组、簇标题带方向标签）后发。
无人值守场景用 notify:script 走降级路径。

产物（文件名固定，别改成 radar2.json）:
    output/arxiv/out.json       全部幸存者
    output/arxiv/audit.log      审计（同时打到 stdout）
    output/arxiv/report.md      通知正文（脚本写机械备用稿 → 模型覆写成中文）
    memory/arxiv-seen.json      非 dry-run 才写
    memory/arxiv-hits.tsv       命中流水，append-only，非 dry-run 才写
    memory/arxiv-labels.tsv     方向标签，append-only，**模型写**（键 \\t 方向）
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
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

# ── check 模式：加词前量两个口径，量完退出 ────────────────────────
def q_of(term):
    if term.startswith(("cat:", "ti:", "abs:", "all:")):
        return term
    if NAMES_MODE:
        return (f'ti:"{term}" AND (cat:cs.CR OR cat:cs.CE OR cat:cs.GT OR cat:cs.DC '
                'OR cat:q-fin.CP OR cat:q-fin.GN)')
    return f'ti:"{term}"'

def total_of(q, d):
    """返回 (total_count, entries)。失败返回 (-1, [])。"""
    since = (now - timedelta(days=d)).strftime("%Y%m%d%H%M")
    p = {"search_query": f"({q}) AND submittedDate:[{since} TO {now:%Y%m%d%H%M}]",
         "start": 0, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    try:
        with urllib.request.urlopen(API + "?" + urllib.parse.urlencode(p),
                                    timeout=20) as r:
            root = ET.fromstring(r.read())
    except Exception:
        return -1, []
    node = root.find(OPENSEARCH)
    return (int(node.text) if node is not None and node.text else 0), root.findall("a:entry", NS)

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

for term in TERMS:
    carrier = CARRIER_BY_TERM.get(term, CARRIER_BASE)
    q = q_of(term)

    p = {"search_query": f"({q}) AND submittedDate:{win}",
         "start": 0, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    url = API + "?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            root = ET.fromstring(r.read())
    except Exception as ex:
        print(f"! {term}: {ex}", file=sys.stderr)
        drop["fail"] += 1
        failed_t.append(term)
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
    time.sleep(3)

out.sort(key=lambda c: c["published"], reverse=True)
T_RUN = time.time() - T0

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

truly_zero = [t for t in TERMS if t not in failed_t and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and per_term.get(t, 0) == 0]
with_new = [t for t in TERMS if per_term.get(t, 0) > 0]

# ── 跨窗复量（只对真零词，只补比本轮窗口更宽的档）────────────────
# 7d ⊂ 30d ⊂ 60d：窗口 30 时 7d 被蕴含，只补 60d；窗口 7 时补 30d/60d。
# 目的：把「真零」和「废词」分开 —— 索引滞后 5 天时，窄窗会把稀有词系统性读成零。
XW = [d for d in (7, 30, 60) if d > DAYS]
xwin = {t: {} for t in truly_zero}
for term in truly_zero:
    q = q_of(term)
    for d in XW:
        tot, _ = total_of(q, d)
        xwin[term][d] = tot
        time.sleep(3)

# ── 标签覆盖自检：hits 里有、labels 里没有的条数 ──────────────────
unlabeled = []
if os.path.exists(HITS):
    hkeys = set()
    for i, ln in enumerate(open(HITS, encoding="utf-8")):
        if i == 0:
            continue
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 2 and p[1]:
            hkeys.add(p[1])
    lkeys = set()
    if os.path.exists(LABELS):
        for ln in open(LABELS, encoding="utf-8"):
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 2 and p[1]:
                lkeys.add(p[0])
    unlabeled = sorted(hkeys - lkeys)

L = ["扫 %d 词 | 窗口 %s | 原始 %d | 幸存 %d | var=%r"
     % (len(TERMS), win, raw, len(out), var),
     "丢弃 seen=%d excl=%d carrier=%d fail=%d"
     % (drop["seen"], drop["excl"], drop["carrier"], drop["fail"]),
     "词表四分类 —— 查询失败 %d / 真零 %d / 全已见(饱和) %d / 有新增 %d"
     % (len(failed_t), len(truly_zero), len(saturated), len(with_new)),
     "窗口内最新收录日期: %s   ← 比今天早 3 天以上即索引滞后，实测已到 5 天"
     % (newest or "(无)"),
     "耗时 %.0fs" % T_RUN]
if UNKNOWN:
    L.append("⚠️ 未识别 var token（会被静默忽略）: " + " · ".join(UNKNOWN))
if failed_t:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(failed_t))
if truly_zero:
    if not XW:
        L.append("⚠️ 真零命中（本轮 %dd total=0，无更宽档可补）: %s"
                 % (DAYS, " · ".join(truly_zero)))
    else:
        L.append("⚠️ 真零命中（本轮 %dd total=0）—— 跨窗 %s 复量："
                 % (DAYS, "/".join("%dd" % d for d in XW)))
        for t in truly_zero:
            L.append("   %s: win=%d %s" % (
                t, raw_term.get(t, 0),
                " ".join("%dd=%s" % (d, xwin[t].get(d, -1)) for d in XW)))
        alive = [t for t in truly_zero if any(xwin[t].get(d, 0) > 0 for d in XW)]
        unk = [t for t in truly_zero if t not in alive
               and any(xwin[t].get(d, -1) < 0 for d in XW)]
        real = [t for t in truly_zero if t not in alive and t not in unk]
        if alive:
            L.append("   └ 跨窗有命中（活的，**别删**）%d 个: %s"
                     % (len(alive), " · ".join(alive)))
        if real:
            L.append("   └ 跨窗全零（第 1 轮；第 2 轮仍全零 → 降级为低频，不删）%d 个: %s"
                     % (len(real), " · ".join(real)))
        if unk:
            L.append("   └ 跨窗查询失败（存疑，先别删）%d 个: %s"
                     % (len(unk), " · ".join(unk)))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))
L.append("词表原始/新收: " + " · ".join(
    "%s=%d/%d" % (k, v, per_term.get(k, 0)) for k, v in
    sorted(raw_term.items(), key=lambda x: -x[1])))
if unlabeled:
    L.append("ℹ️ 未打方向标签 %d 条（写进 %s：键\\t方向）: %s"
             % (len(unlabeled), LABELS, " · ".join(unlabeled[:8])
                + (" …" if len(unlabeled) > 8 else "")))
for c in out[:25]:
    L.append("  %s [%s] %s" % (c["published"], "+".join(c["terms"]), c["title"][:85]))

open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ── 落盘 / 通知 ───────────────────────────────────────────────────
if not DRY and hit_ids:
    merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-2000:]),
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
    print("notify: **未发** —— 用 Write 覆写 %s 为中文（按簇分组）后：" % REPORT)
    print("        ./notify -f %s" % REPORT)
    print("        改不了就直接发机械版（已去噪），**别不发**。")
print("STATUS: ARXIV_RADAR_OK · 原始 %d · 幸存 %d · 总耗时 %.0fs"
      % (raw, len(out), time.time() - T0))
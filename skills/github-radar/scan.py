#!/usr/bin/env python3
"""github-radar 扫描器（静态文件 —— 模型只调用，不重写）。

用法:
    python3 skills/github-radar/scan.py "dry-run days:60"

var token（空格分隔，可组合）:
    dry-run   跳过 notify、不写 seen
    days:N    扫描窗口，默认 30
    min:N     star 地板，默认 0
    chk:N     核验门槛（仅在幸存数超 CHK_CAP 时启用），默认 5

产物（文件名固定，别改成 scan10.py / audit10.log）:
    output/ghradar/out.json       全部幸存者
    output/ghradar/audit.log      审计（同时打到 stdout）
    output/ghradar/report.md      通知正文
    memory/github-seen.json       非 dry-run 才写
    memory/github-candidates.md   非 dry-run 才追加
"""
import json, os, subprocess, sys, threading, time
import urllib.error, urllib.parse, urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"
OUT, AUD, REPORT = OUTD + "/out.json", OUTD + "/audit.log", OUTD + "/report.md"
SEEN = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

CHK_CAP = 2000         # 幸存数 <= 这个值 → 全量核验，一个不漏
PER_TERM_CAP = 40      # 只在超上限时才启用（超上限时按词保底）
REPORT_COMMITS = 5
NOTIFY_TOP = 30
MAXPAGE = 3
SITE_SUFFIX = (".github.io", "-page", "-site", "-website", "-homepage", "-showcase")
SCAFFOLD_MIN = 3
SEARCH_MIN_GAP = 2.1   # search 限速 30/min，两次搜索之间至少隔这么久
VERIFY_WORKERS = 8     # 核验并发（core quota 5000/h，与 search 是独立池）
VERIFY_BUDGET = 900    # 核验墙钟预算（秒）；超预算的标 unverified，不违反「全量」

# ── 词表：`#` 开头是注释 ──────────────────────────────────────────
TERMS = [t.strip() for t in """
# ── AI / 机器人（主战场）──
embodied data
robot manipulation
robot dataset
teleoperation
sim2real
sim-to-real
world model
world action model
# vla → 全称：实测双赢（污染 22%→1.4%，且 138/205 是旧口径从没抓到的新仓）
vision language action
# jepa 保留缩写：换全称损失 94.6%；且这一簇 ★0 与 commits 反相关，必须按 commits 读
jepa
egocentric
robotics data engine
# ── 加密（顺带）──
verifiable inference
proof of useful work
data availability
restaking
intent-based
maximal extractable value
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

NEG_BY_TERM = {
    "jepa": ["jepang", "jepara", "jepan"],
    "vla": ["vlan", "vlad", "vladimir", "vladislav", "vladoss"],
}

CARRIER_BY_TERM = {
    "world model": ["embodied", "robot", "vla", "manipulation", "sim2real",
                    "sim-to-real", "teleop", "egocentric", "action", "policy",
                    "rlbench", "lerobot"],
    "data availability": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                          "rollup", "celestia", "modular", "da layer", "zk"],
    "intent-based": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                     "solver", "swap", "defi", "amm", "wallet"],
}

EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]

# ── var ───────────────────────────────────────────────────────────
var = sys.argv[1] if len(sys.argv) > 1 else ""
DRY, DAYS, MIN, CHK, UNKNOWN = False, 30, 0, 5, []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok.startswith("days:"):
        DAYS = int(tok.split(":", 1)[1] or 30)
    elif tok.startswith("min:"):
        MIN = int(tok.split(":", 1)[1] or 0)
    elif tok.startswith("chk:"):
        CHK = int(tok.split(":", 1)[1] or 5)
    else:
        UNKNOWN.append(tok)

T0 = time.time()
farms = set()
if os.path.exists(FARMS):
    for l in open(FARMS, encoding="utf-8"):
        k = l.split("#")[0].strip().lower()
        if k:
            farms.add(k)

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

now = datetime.now(timezone.utc)
NWIN = 3
step = DAYS / NWIN
WINS = ["%s..%s" % ((now - timedelta(days=step * (i + 1))).strftime("%Y-%m-%d"),
                    (now - timedelta(days=step * i)).strftime("%Y-%m-%d"))
        for i in range(NWIN)]

GH_LOCK = threading.Lock()
GH = [True]
gh_lost = [False]

def gh_get(path):
    """先走 gh api（认证），掉线才降级未认证 urllib。429 与 409 必须分开。"""
    last = ""
    if GH[0]:
        for i in range(3):
            try:
                r = subprocess.run(["gh", "api", path], capture_output=True,
                                   text=True, timeout=45)
                if r.returncode == 0 and r.stdout.strip():
                    return json.loads(r.stdout), None
                last = r.stderr.strip()
                if ("rate limit" in last.lower() or "429" in last
                        or "403" in last or "secondary" in last.lower()):
                    time.sleep(5 * (i + 1)); continue
                break
            except Exception as ex:
                last = str(ex); time.sleep(3)
        with GH_LOCK:
            if GH[0]:
                print("  ! gh api 放弃: %s" % last[:140], file=sys.stderr)
                GH[0] = False; gh_lost[0] = True
    for i in range(2):
        try:
            req = urllib.request.Request("https://api.github.com/" + path, headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "aeon-github-radar"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp), None
        except urllib.error.HTTPError as he:
            last = "HTTP %s" % he.code
            if he.code in (403, 429):
                time.sleep(8 * (i + 1)); continue
            return None, last
        except Exception as ex:
            last = str(ex); time.sleep(3)
    return None, last

_last_search = [0.0]
def search(q, page=1):
    gap = SEARCH_MIN_GAP - (time.time() - _last_search[0])
    if gap > 0:
        time.sleep(gap)
    _last_search[0] = time.time()
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100", "page": str(page)})
    return gh_get("search/repositories?" + qs)

def commits_since(rid, days):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    return (len(data) if isinstance(data, list) else None), "ok"

# ── 扫描 ──────────────────────────────────────────────────────────
out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "neg": 0, "pages": 0, "farm": 0, "fail": 0}
hit, qfail, cov = {}, [], {}
raw_term, new_term = {}, {}
page_dropped, neg_dropped = [], []

for term in TERMS:
    total, got, failed = 0, 0, False
    raw_term[term] = 0; new_term[term] = 0
    neg = NEG_BY_TERM.get(term, [])
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        for page in range(1, MAXPAGE + 1):
            res, err = search(q, page)
            if res is None:
                print("! %s @%s p%d: %s" % (term, w, page, err), file=sys.stderr)
                drop["fail"] += 1; failed = True; break
            if page == 1:
                total += res.get("total_count", 0)
            items = res.get("items", [])
            got += len(items); raw_term[term] += len(items)
            for it in items:
                raw += 1
                rid = it["full_name"]
                owner = (it.get("owner") or {}).get("login", "")
                short = rid.split("/")[-1]
                if rid in seen:
                    drop["seen"] += 1; continue
                if rid in hit:
                    hit[rid]["terms"].append(term); drop["seen"] += 1; continue
                if it.get("archived"):
                    drop["archived"] += 1; continue
                lang = it.get("language")
                lowall = (rid + " " + (it.get("description") or "")).lower()
                if neg and any(x in lowall for x in neg):
                    drop["neg"] += 1; neg_dropped.append(rid); continue
                size_kb = it.get("size", 0)
                # 站点仓：按后缀**无条件**丢 —— 体量不是判据（304MB 静态站照样是站）
                if short.lower().endswith(SITE_SUFFIX):
                    drop["pages"] += 1
                    page_dropped.append((rid, size_kb)); continue
                # 同名仓：可能是真代码仓（UniWAM/UniWAM），也可能是个人主页
                if (short.lower() == owner.lower() and size_kb < 300
                        and not lang):
                    drop["pages"] += 1
                    page_dropped.append((rid, size_kb)); continue
                desc = (it.get("description") or "").strip()
                if len(desc) < 25:
                    drop["short_desc"] += 1; continue
                if any(x in lowall for x in EXCL):
                    drop["excl"] += 1; continue
                need = CARRIER_BY_TERM.get(term)
                if need and not any(c in desc.lower() for c in need):
                    drop["carrier"] += 1; continue
                if owner.lower() in farms:
                    drop["farm"] += 1; continue
                out.append({"term": term, "terms": [term], "repo": rid,
                            "owner": owner, "url": it["html_url"],
                            "stars": it.get("stargazers_count", 0),
                            "created": (it.get("created_at") or "")[:10],
                            "topics": it.get("topics", [])[:6],
                            "size_kb": size_kb, "language": lang,
                            "desc": " ".join(desc.split())[:140]})
                hit[rid] = out[-1]; new_term[term] += 1
            if len(items) < 100:
                break
    if failed and not got:
        qfail.append(term)
    if total:
        cov[term] = round(100.0 * got / total, 1)

T_SEARCH = time.time() - T0

# ── 共享脚手架：owner 黑名单抓不到 ──
byname = {}
for c in out:
    byname.setdefault(c["repo"].split("/")[-1].lower(), []).append(c)
scaffold = []
for nm, lst in byname.items():
    if len({c["owner"] for c in lst}) >= SCAFFOLD_MIN:
        pref, n = Counter(c["desc"][:80] for c in lst).most_common(1)[0]
        if n >= SCAFFOLD_MIN:
            for c in lst:
                if c["desc"][:80] == pref:
                    c["scaffold"] = True; scaffold.append(c["repo"])
out = [c for c in out if not c.get("scaffold")]

# ── 核验：幸存数不超上限就**全量**；并发 + 墙钟预算 ──
if len(out) <= CHK_CAP:
    todo = list(out)
    verify_mode = "全量"
else:
    pick = {}
    for c in out:
        if c["stars"] >= CHK:
            pick[c["repo"]] = c
    by_term = {}
    for c in out:
        by_term.setdefault(c["term"], []).append(c)
    for t, lst in by_term.items():
        lst.sort(key=lambda c: (-c["stars"], c["created"]))
        for c in lst[:PER_TERM_CAP]:
            pick[c["repo"]] = c
    todo = list(pick.values())[:CHK_CAP]
    verify_mode = "抽样(超上限)"

DEADLINE = time.time() + VERIFY_BUDGET

def verify_one(c):
    if time.time() > DEADLINE:
        c["unverified"] = True
        return
    n30, st = commits_since(c["repo"], 30)
    if st == "empty":
        c["maybe_empty"] = True; return
    if st != "ok":
        c["unverified"] = True; return
    c["commits_30d"] = n30
    if n30 >= 100:
        c["commits_30d_ge"] = True
    if n30 == 0:
        c["stale"] = True; return
    n7, st7 = commits_since(c["repo"], 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 >= 100:
            c["commits_7d_ge"] = True
        if n7 == 0:
            c["burst_only"] = True
    if not c.get("language"):
        c["no_lang"] = True

T_V0 = time.time()
with ThreadPoolExecutor(max_workers=VERIFY_WORKERS) as ex:
    list(ex.map(verify_one, todo))
T_VERIFY = time.time() - T_V0

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["owner_repos"] = owner_n[c["owner"]]

def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty"))

rep = sorted([c for c in out if reportable(c)],
             key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"], -c["stars"]))

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def fmt(c):
    return "%s ★%d 30d=%s%s 7d=%s%s" % (
        c["repo"], c["stars"],
        "≥100" if c.get("commits_30d_ge") else c.get("commits_30d"),
        " [爆完即停]" if c.get("burst_only") else "",
        "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
        "" if c.get("language") else " [无language]")

failed_t = list(qfail)
truly_zero = [t for t in TERMS if t not in qfail and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and new_term.get(t, 0) == 0]
with_new = [t for t in TERMS if new_term.get(t, 0) > 0]

L = ["扫 %d 词 × %d 窗 × %d 页 | 原始 %d | 幸存 %d | 报告级 %d | var=%r"
     % (len(TERMS), NWIN, MAXPAGE, raw, len(out), len(rep), var),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d neg=%d "
     "pages=%d scaffold=%d farm=%d fail=%d"
     % (drop["seen"], drop["excl"], drop["archived"], drop["short_desc"],
        drop["carrier"], drop["neg"], drop["pages"], len(scaffold),
        drop["farm"], drop["fail"]),
     "核验 %d/%d (%.1f%%) · 模式 %s · 黑名单 %d owner"
     % (len(todo), len(out), 100.0 * len(todo) / max(len(out), 1),
        verify_mode, len(farms)),
     "词表四分类 —— 查询失败 %d / 真零 %d / 全已见(饱和) %d / 有新增 %d"
     % (len(failed_t), len(truly_zero), len(saturated), len(with_new)),
     "耗时 搜索 %.0fs · 核验 %.0fs · 总 %.0fs"
     % (T_SEARCH, T_VERIFY, time.time() - T0)]
if UNKNOWN:
    L.append("⚠️ 未识别 var token（会被静默忽略）: " + " · ".join(UNKNOWN))
if failed_t:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(failed_t))
if truly_zero:
    L.append("⚠️ 真零命中（total=0，可考虑删词）: " + " · ".join(truly_zero))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))
L.append("词表返回/新收: " + " · ".join(
    "%s=%d/%d" % (t, raw_term.get(t, 0), new_term.get(t, 0)) for t in
    sorted(TERMS, key=lambda x: -raw_term.get(x, 0))))
if gh_lost[0]:
    L.append("⚠️ gh 认证已丢失，降级未认证 —— 本轮完整性存疑")
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % kv for kv in low.items()))
if scaffold:
    L.append("ℹ️ 共享脚手架（同短名跨≥%d owner 且 desc 前缀同）%d 个: %s"
             % (SCAFFOLD_MIN, len(scaffold), " · ".join(scaffold[:12])))
if neg_dropped:
    L.append("ℹ️ 被 NEG 规则丢弃 %d 个: %s" % (len(neg_dropped),
                                              " · ".join(neg_dropped[:12])))
if page_dropped:
    L.append("ℹ️ 被 pages 规则丢弃 %d 个: %s"
             % (len(page_dropped), " · ".join("%s(%dKB)" % p for p in page_dropped[:12])))
vt = Counter(c["term"] for c in todo)
L.append("逐词核验数: " + " · ".join("%s=%d" % (k, vt.get(k, 0)) for k in
                                     sorted(TERMS, key=lambda x: -vt.get(x, 0))))
uv = [c["repo"] for c in todo if c.get("unverified")]
if uv:
    L.append("⚠️ 未核验（限速或超预算，勿当空仓）%d: %s" % (len(uv), " · ".join(uv[:12])))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）%d: %s" % (len(stale), " · ".join(stale[:15])))
burst = [c["repo"] for c in todo if c.get("burst_only")]
if burst:
    L.append("⚠️ 爆完即停（30d 有量 / 7d 归零）%d: %s"
             % (len(burst), " · ".join(burst[:15])))
nol = [c["repo"] for c in todo if c.get("no_lang")]
if nol:
    L.append("⚠️ 无 language 字段（疑似非代码仓）%d: %s"
             % (len(nol), " · ".join(nol[:12])))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（409）: " + " · ".join(empty))
cand = {o: n for o, n in owner_n.items() if n >= 3}
if cand:
    L.append("ℹ️ 候选农场（owner≥3，需人工判）: " +
             " · ".join("%s=%d" % kv for kv in cand.items()))
for c in rep[:25]:
    L.append("  " + fmt(c))

open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ── 落盘 / 通知 ───────────────────────────────────────────────────
stamp = now.strftime("%Y-%m-%d")
if not DRY and hit:
    merged = {k: stamp for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-8000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            f.write("- [%s](%s) ★%d · 30d=%s 7d=%s%s · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"],
                       "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
                       "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
                       " [爆完即停]" if c.get("burst_only") else "",
                       c["term"], c["desc"][:100]))

if rep:
    R = ["**github-radar** · 窗口 %d 天 · 报告级 %d · 7d 活跃 %d"
         % (DAYS, len(rep), sum(1 for c in rep if c.get("commits_7d"))), ""]
    for c in rep[:NOTIFY_TOP]:
        R.append("- [%s](%s) ★%d · 30d=%s 7d=%s%s · `%s` · %s"
                 % (c["repo"], c["url"], c["stars"],
                    "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
                    "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
                    " [爆完即停]" if c.get("burst_only") else "",
                    c["term"], c["desc"][:100]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

if not DRY and rep and os.path.exists("./notify"):
    r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
    print("notify: %s" % ((r.stdout or r.stderr or "ok").strip()[:200]))
else:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else "报告级 0"))
print("STATUS: GITHUB_RADAR_OK · 幸存 %d · 报告级 %d · 总耗时 %.0fs"
      % (len(out), len(rep), time.time() - T0))
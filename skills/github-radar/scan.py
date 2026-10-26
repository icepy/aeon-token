#!/usr/bin/env python3
"""github-radar 扫描器（静态文件 —— 模型只调用，不重写）。

用法:
    python3 skills/github-radar/scan.py "days:30"
    python3 skills/github-radar/scan.py "days:30 probe"      # 额外跑专名簇反查

var token（空格分隔，可组合）:
    dry-run   跳过 notify、不写 seen、**不覆盖 out.json**（改写 out.dry.json）
    days:N    扫描窗口，默认 30
    min:N     star 地板，默认 0
    chk:N     核验门槛（仅在幸存数超 CHK_CAP 时启用），默认 5
    probe     对种子仓名 token 做反查，找词表漏掉的专名簇

产物（文件名固定，别改成 scan13.py / audit13.log）:
    output/ghradar/out.json       全部幸存者（非 dry-run）
    output/ghradar/out.dry.json   全部幸存者（dry-run；空数组不许覆盖上一轮真快照）
    output/ghradar/audit.log      审计（同时打到 stdout）
    output/ghradar/report.md      通知正文
    output/ghradar/clusters.json  probe 时**必定重写**（空也写，好区分"没跑"和"跑了没货"）
    memory/github-seen.json       非 dry-run 才写
    memory/github-candidates.md   非 dry-run 才追加
"""
import json, os, re, subprocess, sys, threading, time
import urllib.error, urllib.parse, urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"
OUT, OUT_DRY = OUTD + "/out.json", OUTD + "/out.dry.json"
AUD, REPORT = OUTD + "/audit.log", OUTD + "/report.md"
CLUSTERS = OUTD + "/clusters.json"
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
SEARCH_MIN_GAP = 2.1   # search 限速 30/min
VERIFY_WORKERS = 6     # 核验并发（core quota 5000/h，但并发太高会触发二级限流）
VERIFY_BUDGET = 900    # 核验墙钟预算（秒）；超预算的标 unverified
PROBE_TOP = 12         # probe: 取报告级前 N 个的仓名 token 作候选
PROBE_MAXTOK = 20      # probe: 最多反查多少个 token
PROBE_MAX_TOTAL = 600  # probe: 反查 total 超过这个 → 判为通用词，不是专名
PROBE_SEED_TARGET = 36 # probe: 种子仓数量目标（报告级 → 幸存 → 丢弃堆，依次补足）

# 根目录里有这些 = 真代码仓（用来否掉"页形态"）
CODE_SKELETON = {"src", "tests", "test", "pyproject.toml", "package.json",
                 "cargo.toml", "contracts", "crates", "app", "lib", "makefile",
                 "setup.py", "requirements.txt", "cmake", "go.mod", "build.gradle"}
# 反查时不该当专名的通用 token
STOPWORDS = set("""world model models data robot robots learning sim sim2real agent
agents lab labs ai repo code page site github io project paper papers reproduce
reproduction experiments experiment baseline baselines implementation demo
official release training framework system systems control policy""".split())

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
DRY, DAYS, MIN, CHK, PROBE, UNKNOWN = False, 30, 0, 5, False, []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "probe":
        PROBE = True
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
FULLWIN = "%s..%s" % ((now - timedelta(days=DAYS)).strftime("%Y-%m-%d"),
                      now.strftime("%Y-%m-%d"))

GH_LOCK = threading.Lock()
GH_COOLDOWN = 60           # gh 掉线后的冷却秒数；到期自动重试，不再整轮放弃
GH_DOWN_UNTIL = [0.0]
gh_lost = [False]

def gh_alive():
    return time.time() >= GH_DOWN_UNTIL[0]

def gh_down(reason):
    with GH_LOCK:
        GH_DOWN_UNTIL[0] = time.time() + GH_COOLDOWN
        if not gh_lost[0]:
            print("  ! gh api 放弃: %s" % reason[:140], file=sys.stderr)
            gh_lost[0] = True

def gh_get(path):
    """先走 gh api（认证）；失败则冷却 GH_COOLDOWN 秒后自动回来。
    429（限速）与 409（真空仓）必须分开；404 不该拖垮认证态。"""
    last = ""
    if gh_alive():
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
        if "404" not in last and "Not Found" not in last:
            gh_down(last)
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
        "neg": 0, "pages": 0, "pages_root": 0, "farm": 0, "fail": 0}
hit, qfail, cov = {}, [], {}
raw_term, new_term, seen_term = {}, {}, {}
page_dropped, neg_dropped, root_dropped = [], [], []
# carrier / short_desc 丢掉的仓 —— probe 的第三顺位种子（活仓常躺在这里）
drop_names = []
DROP_NAMES_CAP = 400

for term in TERMS:
    total, got, failed = 0, 0, False
    raw_term[term] = 0; new_term[term] = 0; seen_term[term] = 0
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
                    drop["seen"] += 1; seen_term[term] += 1; continue
                if rid in hit:
                    hit[rid]["terms"].append(term)
                    drop["seen"] += 1; seen_term[term] += 1; continue
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
                    drop["short_desc"] += 1
                    if len(drop_names) < DROP_NAMES_CAP:
                        drop_names.append((it.get("pushed_at") or "", rid))
                    continue
                if any(x in lowall for x in EXCL):
                    drop["excl"] += 1; continue
                need = CARRIER_BY_TERM.get(term)
                if need and not any(c in desc.lower() for c in need):
                    drop["carrier"] += 1
                    if len(drop_names) < DROP_NAMES_CAP:
                        drop_names.append((it.get("pushed_at") or "", rid))
                    continue
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

# ── pages 根目录规则（三次独立复现后固化）──
# index.html + .nojekyll 且根目录无任何代码骨架 → 页。体积不做豁免。
def is_page_repo(rid):
    data, _ = gh_get("repos/%s/contents" % rid)
    if not isinstance(data, list):
        return False
    names = {str(x.get("name", "")).lower() for x in data}
    return ("index.html" in names and ".nojekyll" in names
            and not (names & CODE_SKELETON))

if out:
    # 4 路：并发太高会把 gh 打成二级限流
    with ThreadPoolExecutor(max_workers=4) as ex:
        flags = list(ex.map(is_page_repo, [c["repo"] for c in out]))
    kept = []
    for c, isp in zip(out, flags):
        if isp:
            drop["pages_root"] += 1; root_dropped.append(c["repo"])
        else:
            kept.append(c)
    out = kept

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
        c["unverified"] = True; return
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
# dry-run 不覆盖 out.json —— 否则一次 0 幸存就会把上一轮的真快照写成 "[]"
SNAP = OUT_DRY if DRY else OUT
json.dump(out, open(SNAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── probe：反查找词表漏掉的专名簇 ──
# 种子池必须是「报告级 → 幸存 → 丢弃堆最新」三级补足。只看报告级会在幸存 0 时整段空转
# （第十三轮实证：活仓全躺在丢弃堆里，而 probe 因为 rep=0 完全没跑）。
# 顺序必须是「先反查、再排序」—— 按 token 在种子里出现几次排会漏掉
# SuperMimic（它只出现 1 次，被 capstone/recall 这类通用词挤掉）。
# 专名判据：反查 total 小 + owner 密度高 + 簇内有高 commit 仓。
cluster_report = []
probe_stat = {"rep": 0, "out": 0, "drop": 0, "tok": 0, "done": 0, "seeds": 0}
if PROBE:
    seeds = []
    for tag, src in (("rep", rep), ("out", out),
                     ("drop", [r for _, r in sorted(drop_names, reverse=True)])):
        n0 = len(seeds)
        for it in src:
            rid = it["repo"] if isinstance(it, dict) else it
            if rid not in seeds:
                seeds.append(rid)
            if len(seeds) >= PROBE_SEED_TARGET:
                break
        probe_stat[tag] = len(seeds) - n0
        if len(seeds) >= PROBE_SEED_TARGET:
            break
    probe_stat["seeds"] = len(seeds)
    toks = []
    for rid in seeds:
        for tk in re.split(r"[-_./]", rid.split("/")[-1].lower()):
            if (len(tk) >= 4 and tk not in STOPWORDS
                    and not tk.isdigit() and tk not in toks):
                toks.append(tk)
    probe_stat["tok"] = len(toks)
    in_out = {c["repo"] for c in out}
    for tk in toks[:PROBE_MAXTOK]:
        res, err = search('"%s" in:name,description created:%s fork:false'
                          % (tk, FULLWIN))
        if res is None:
            continue
        total = res.get("total_count", 0)
        items = res.get("items", [])
        owners = {(i.get("owner") or {}).get("login", "") for i in items}
        hot = []
        for i in items[:8]:
            n30, st = commits_since(i["full_name"], 30)
            if st == "ok" and n30 and n30 >= REPORT_COMMITS:
                n7, _ = commits_since(i["full_name"], 7)
                hot.append({"repo": i["full_name"],
                            "stars": i.get("stargazers_count", 0),
                            "commits_30d": n30, "commits_7d": n7})
        hot.sort(key=lambda x: (-(x["commits_7d"] or 0), -x["commits_30d"]))
        cluster_report.append({
            "token": tk, "total": total, "owners": len(owners),
            "generic": total > PROBE_MAX_TOTAL,
            "not_in_out": sum(1 for i in items if i["full_name"] not in in_out),
            "hot": hot[:8]})
        probe_stat["done"] += 1
    # 专名优先：非通用词 → 簇内活跃仓多 → owner 密度高
    cluster_report.sort(key=lambda x: (x["generic"], -len(x["hot"]), -x["owners"]))
    # **无条件重写** —— 空数组也要写，否则上一轮的 clusters.json 会冒充本轮结果
    json.dump(cluster_report, open(CLUSTERS, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

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
sat_seen = [t for t in saturated if seen_term.get(t, 0) > 0]
sat_loss = [t for t in saturated if seen_term.get(t, 0) == 0]

L = ["扫 %d 词 × %d 窗 × %d 页 | 原始 %d | 幸存 %d | 报告级 %d | var=%r"
     % (len(TERMS), NWIN, MAXPAGE, raw, len(out), len(rep), var),
     "快照 %s%s" % (SNAP, "（dry-run 不覆盖 out.json）" if DRY else ""),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d neg=%d "
     "pages=%d pages_root=%d scaffold=%d farm=%d fail=%d"
     % (drop["seen"], drop["excl"], drop["archived"], drop["short_desc"],
        drop["carrier"], drop["neg"], drop["pages"], drop["pages_root"],
        len(scaffold), drop["farm"], drop["fail"]),
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
    # 「饱和」这个标签本身是混的：new_term 只在全部过滤器跑完之后才自增，
    # 所以「被 carrier/short_desc 丢光」和「真被 seen 吸收」会落进同一类。必须拆开。
    L.append("ℹ️ 饱和（raw>0 且 0 新增）%d —— 其中真被 seen 吸收 %d 个（**别删**）: %s"
             % (len(saturated), len(sat_seen),
                " · ".join("%s(raw=%d seen=%d)" % (t, raw_term[t], seen_term[t])
                           for t in sat_seen)))
    if sat_loss:
        L.append("   └ 全是过滤损耗 %d 个（seen=0，**不是饱和**，别按饱和读）: %s"
                 % (len(sat_loss), " · ".join("%s(raw=%d)" % (t, raw_term[t])
                                              for t in sat_loss)))
L.append("词表返回/新收/已见: " + " · ".join(
    "%s=%d/%d/%d" % (t, raw_term.get(t, 0), new_term.get(t, 0), seen_term.get(t, 0))
    for t in sorted(TERMS, key=lambda x: -raw_term.get(x, 0))))
if gh_lost[0]:
    L.append("⚠️ gh 认证曾掉线（已按 %ds 冷却自动重试）—— 核验完整性存疑" % GH_COOLDOWN)
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
    L.append("ℹ️ 被 pages 后缀规则丢弃 %d 个: %s"
             % (len(page_dropped), " · ".join("%s(%dKB)" % p for p in page_dropped[:12])))
if root_dropped:
    L.append("ℹ️ 被 pages 根目录规则丢弃 %d 个（index.html+.nojekyll 且无代码骨架）: %s"
             % (len(root_dropped), " · ".join(root_dropped[:12])))
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
if PROBE:
    L.append("ℹ️ probe 种子 %d（报告级 %d / 幸存 %d / 丢弃堆 %d）→ 候选 token %d → "
             "已反查 %d · clusters.json 已重写（空也写）"
             % (probe_stat["seeds"], probe_stat["rep"], probe_stat["out"],
                probe_stat["drop"], probe_stat["tok"], probe_stat["done"]))
    if not probe_stat["seeds"]:
        L.append("   ⚠️ 种子为 0 —— 本轮 probe 无从反查，不是「没有簇」")
    else:
        L.append("ℹ️ probe 反查 —— 专名候选（total≤%d）:" % PROBE_MAX_TOTAL)
        for cl in [c for c in cluster_report if not c["generic"]][:8]:
            L.append("  `%s` total=%d owners=%d 未在幸存者=%d | %s"
                     % (cl["token"], cl["total"], cl["owners"], cl["not_in_out"],
                        " · ".join("%s(%s/%s)" % (h["repo"], h["commits_30d"],
                                                  h["commits_7d"]) for h in cl["hot"][:4])))
        gen = [c for c in cluster_report if c["generic"]][:5]
        if gen:
            L.append("  （通用词，反查噪声）: " + " · ".join(
                "%s(total=%d)" % (c["token"], c["total"]) for c in gen))
for c in rep[:25]:
    L.append("  " + fmt(c))

open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ── 落盘 / 通知 ───────────────────────────────────────────────────
stamp = now.strftime("%Y-%m-%d")
if not DRY and hit:
    merged = {k: stamp for k in hit}
    merged.update(seen)
    # 保留**新**条目：merged 的顺序是「本轮新命中 → 旧 seen」，
    # 原来取 [-8000:] 保留的是尾部旧条目，超 8000 会先把新命中挤掉。
    json.dump(dict(list(merged.items())[:8000]),
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
#!/usr/bin/env python3
"""github-radar 第六轮扫描。

相对 SKILL.md 原版的三处已知缺陷修复（第 4/5 轮日志已实证）：
  1) pages 规则：只在「名字像页 且 size<300KB 且无 language」时丢（原版只看名字+size，
     误杀 UniWAM/UniWAM ★135/20 提交、dextacwam/DexTacWAM ★24/26）。
  2) terms 聚合：多词命中时保留全部 term（原版只记首个，系统性压低 world action model）。
  3) 核验上限：CHK_CAP 可调（原版 250 对 1,200 幸存只有 8.9% 覆盖率，报告级被低估 ~4×）。

用法：DRY=1 DAYS=60 MIN=0 CHK=5 CAP=250 python3 -I output/ghradar/scan6.py
"""
import json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"; OUT = OUTD + "/out6.json"; AUD = OUTD + "/audit6.log"
SEEN = "memory/github-seen.json"; CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

DRY = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 60)   # 本轮 var=days:60
MIN = int(os.environ.get("MIN") or 0)
CHK = int(os.environ.get("CHK") or 5)
CHK_CAP = int(os.environ.get("CAP") or 250)
REPORT_COMMITS = 5

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
vla
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
print("窗口: %s" % " | ".join(WINS), file=sys.stderr)

GH = True
def gh_get(path):
    global GH
    last = ""
    if GH:
        for i in range(3):
            try:
                r = subprocess.run(["gh", "api", path], capture_output=True,
                                   text=True, timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    return json.loads(r.stdout), None
                last = r.stderr.strip()
                if ("rate limit" in last.lower() or "429" in last
                        or "403" in last or "secondary" in last.lower()):
                    time.sleep(5 * (i + 1)); continue
                break
            except Exception as ex:
                last = str(ex); time.sleep(3)
        print("  ! gh api 放弃: %s" % last[:140], file=sys.stderr)
        GH = False
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

def search(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100"})
    return gh_get("search/repositories?" + qs)

def commits_30d(rid):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    return (len(data) if isinstance(data, list) else None), "ok"

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "pages": 0, "farm": 0, "fail": 0}
qfail, cov, per_term = [], {}, {}
by_rid = {}
page_dropped = []
carrier_dropped = defaultdict(list)

for term in TERMS:
    total, got, failed = 0, 0, False
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        res, err = search(q)
        if res is None:
            print("! %s @%s: %s" % (term, w, err), file=sys.stderr)
            drop["fail"] += 1; failed = True; time.sleep(10); continue
        total += res.get("total_count", 0)
        items = res.get("items", [])
        got += len(items)
        for it in items:
            raw += 1
            rid = it["full_name"]
            owner = (it.get("owner") or {}).get("login", "")
            short = rid.split("/")[-1]
            if rid in seen:
                drop["seen"] += 1; continue
            if rid in by_rid:
                # 修复②：保留全部命中词，不再只记首个
                if term not in by_rid[rid]["terms"]:
                    by_rid[rid]["terms"].append(term)
                drop["seen"] += 1; continue
            if it.get("archived"):
                drop["archived"] += 1; continue
            size_kb = it.get("size", 0)
            # 修复①：name-like-page 且 小体量 且 无语言 三者同时成立才丢
            if ((short.endswith(".github.io") or short.lower() == owner.lower())
                    and size_kb < 300 and not it.get("language")):
                drop["pages"] += 1
                page_dropped.append((rid, size_kb, it.get("language")))
                continue
            desc = (it.get("description") or "").strip()
            if len(desc) < 25:
                drop["short_desc"] += 1; continue
            if any(x in desc.lower() for x in EXCL):
                drop["excl"] += 1; continue
            need = CARRIER_BY_TERM.get(term)
            if need and not any(c in desc.lower() for c in need):
                drop["carrier"] += 1
                carrier_dropped[term].append(rid)
                continue
            if owner.lower() in farms:
                drop["farm"] += 1; continue
            rec = {"term": term, "terms": [term], "repo": rid,
                   "owner": owner, "url": it["html_url"],
                   "stars": it.get("stargazers_count", 0),
                   "created": (it.get("created_at") or "")[:10],
                   "pushed": (it.get("pushed_at") or "")[:10],
                   "lang": it.get("language"),
                   "topics": it.get("topics", [])[:6],
                   "size_kb": size_kb,
                   "desc": " ".join(desc.split())[:140]}
            out.append(rec); by_rid[rid] = rec
        time.sleep(3 if GH else 8)   # search 限速 30/min，3s 间隔才安全
    if failed and not got:
        qfail.append(term)
    per_term[term] = sum(1 for c in out if term in c["terms"])
    if total:
        cov[term] = (round(100.0 * got / total, 1), total, got)

# ── 核验 ──
out.sort(key=lambda c: -c["stars"])
todo = [c for c in out if c["stars"] >= CHK]
if len(todo) < CHK_CAP:
    todo += sorted([c for c in out if c["stars"] < CHK],
                   key=lambda c: c["created"], reverse=True)[:CHK_CAP - len(todo)]
print("核验 %d 仓…" % len(todo), file=sys.stderr)
for i, c in enumerate(todo):
    n, st = commits_30d(c["repo"])
    if st == "ok":
        c["commits_30d"] = n
        if n == 0:
            c["stale"] = True
    elif st == "empty":
        c["maybe_empty"] = True
    else:
        c["unverified"] = True
    if i % 50 == 49:
        print("  %d/%d" % (i + 1, len(todo)), file=sys.stderr)

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["owner_repos"] = owner_n[c["owner"]]

def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty"))

rep = sorted([c for c in out if reportable(c)],
             key=lambda c: (-c["commits_30d"], -c["stars"]))

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L = ["扫 %d 词 × %d 窗 | 原始 %d | 幸存 %d | 报告级 %d"
     % (len(TERMS), NWIN, raw, len(out), len(rep)),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d pages=%d farm=%d fail=%d"
     % (drop["seen"], drop["excl"], drop["archived"], drop["short_desc"],
        drop["carrier"], drop["pages"], drop["farm"], drop["fail"]),
     "核验 %d（★>=%d 全部 + 最新补齐，上限 %d）| 幸存未核验 %d"
     % (len(todo), CHK, CHK_CAP, len(out) - len(todo)),
     "黑名单载入 %d 个 owner: %s" % (len(farms), " · ".join(sorted(farms))),
     "词表命中(全 term): " + " · ".join("%s=%d" % (k, v) for k, v in
                                        sorted(per_term.items(), key=lambda x: -x[1]))]
low = {k: v for k, v in cov.items() if v[0] < 50}
if low:
    L.append("⚠️ 覆盖率 <50%（绝对数不可引用）: " + " · ".join(
        "%s=%.1f%%(%d/%d)" % (k, v[0], v[2], v[1]) for k, v in low.items()))
if qfail:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(qfail))
zero = [k for k, v in per_term.items() if v == 0 and k not in qfail]
if zero:
    L.append("⚠️ 真零命中: " + " · ".join(zero))
if page_dropped:
    L.append("ℹ️ 被 pages 规则丢弃 %d 个: %s" % (len(page_dropped),
             " · ".join("%s(%dKB,%s)" % p for p in page_dropped[:15])))
if carrier_dropped:
    L.append("ℹ️ carrier 丢弃按词: " + " · ".join(
        "%s=%d" % (k, len(v)) for k, v in sorted(carrier_dropped.items(),
                                                 key=lambda x: -len(x[1]))))
uv = [c["repo"] for c in todo if c.get("unverified")]
if uv:
    L.append("⚠️ 未核验（限速，勿当空仓）%d 个: %s" % (len(uv), " · ".join(uv[:15])))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交 %d 个（star 在骗人）: %s" % (len(stale), " · ".join(stale)))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（409，只有 description）: " + " · ".join(empty))
cand = {o: n for o, n in owner_n.items() if n >= 3}
if cand:
    L.append("ℹ️ 候选农场（owner≥3，需人工判，非判决）: " +
             " · ".join("%s=%d" % kv for kv in cand.items()))
capped = [c["repo"] for c in todo if c.get("commits_30d") == 100]
if capped:
    L.append("ℹ️ commits_30d=100 是 per_page 上限（实为 ≥100）%d 个: %s"
             % (len(capped), " · ".join(capped)))
for c in rep[:30]:
    L.append("  %s [%s] %s ★%d commits30d=%d size=%dKB lang=%s"
             % (c["created"], "/".join(c["terms"]), c["repo"], c["stars"],
                c["commits_30d"], c["size_kb"], c["lang"]))
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

if not DRY and by_rid:
    stamp = now.strftime("%Y-%m-%d")
    merged = {k: stamp for k in by_rid}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-5000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            f.write("- [%s](%s) ★%d · %dd提交 · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"], c["commits_30d"],
                       "/".join(c["terms"]), c["desc"][:100]))

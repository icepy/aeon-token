#!/usr/bin/env python3
"""github-radar 扫描。脚本自己写 output/ghradar/ —— shell 重定向会被权限层拦。"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"; OUT = OUTD + "/out.json"; AUD = OUTD + "/audit.log"
SEEN  = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 0)
CHK  = int(os.environ.get("CHK") or 5)   # 核验门槛：★>=CHK 全部核验
CHK_CAP = 250                            # 核验总上限，防跑飞
REPORT_COMMITS = 5                       # 报告级：30 天提交数下限

# ── 词表。`#` 开头是注释。改词只改这一段 ──
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

# 脏词必须配 carrier（须与本行词同现才算命中）。
# 判据是 carrier **之后**的精度，不是原始噪声率。
CARRIER_BY_TERM = {
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
    farms = {l.strip().lower() for l in open(FARMS, encoding="utf-8")
             if l.strip() and not l.startswith("#")}

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

GH = True
def gh_get(path):
    global GH
    if GH:
        try:
            r = subprocess.run(["gh", "api", path], capture_output=True,
                               text=True, timeout=45)
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout), "gh"
            print("  ! gh api 失败 rc=%s: %s" % (r.returncode, r.stderr.strip()[:140]),
                  file=sys.stderr); GH = False
        except Exception as ex:
            print("  ! gh 不可用: %s" % ex, file=sys.stderr); GH = False
    req = urllib.request.Request("https://api.github.com/" + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "aeon-github-radar"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp), "anon"

def search(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100"})
    return gh_get("search/repositories?" + qs)

def commits_30d(rid):
    """判真伪只看这个。空仓 409 → None。"""
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    try:
        d, _ = gh_get("repos/%s/commits?%s" % (rid, qs))
        return len(d) if isinstance(d, list) else None
    except Exception:
        return None

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "farm": 0, "fail": 0}
hit, qfail, cov, per_term = {}, [], {}, {}

for term in TERMS:
    total, got, failed = 0, 0, False
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        try:
            res, src = search(q)
        except Exception as ex:
            print("! %s @%s: %s" % (term, w, ex), file=sys.stderr)
            drop["fail"] += 1; failed = True; time.sleep(7); continue
        total += res.get("total_count", 0)
        items = res.get("items", [])
        got += len(items)
        for it in items:
            raw += 1
            rid = it["full_name"]
            owner = (it.get("owner") or {}).get("login", "")
            if rid in seen:
                drop["seen"] += 1; continue
            if rid in hit:
                hit[rid]["terms"].append(term); drop["seen"] += 1; continue
            if it.get("archived"):
                drop["archived"] += 1; continue
            desc = (it.get("description") or "").strip()
            if len(desc) < 25:
                drop["short_desc"] += 1; continue
            if any(x in desc.lower() for x in EXCL):
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
                        "desc": " ".join(desc.split())[:140]})
            hit[rid] = out[-1]
        time.sleep(2 if src == "gh" else 7)
    if failed and not got:
        qfail.append(term)
    per_term[term] = len([c for c in out if c["term"] == term])
    if total:
        cov[term] = round(100.0 * got / total, 1)

# ── 核验：按 star 分桶，不是按创建时间 ──
# 先全部 ★>=CHK（高信号），再补创建最新的，直到上限。
out.sort(key=lambda c: -c["stars"])
todo = [c for c in out if c["stars"] >= CHK]
if len(todo) < CHK_CAP:
    rest = sorted([c for c in out if c["stars"] < CHK],
                  key=lambda c: c["created"], reverse=True)
    todo += rest[:CHK_CAP - len(todo)]
for c in todo:
    n = commits_30d(c["repo"])
    c["commits_30d"] = n
    if n == 0:
        c["stale"] = True
    if n is None:
        c["maybe_empty"] = True

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["farm_hit"] = owner_n[c["owner"]]

# ── 报告级：核验过 + 还在写 + 不农场 + 不空仓 ──
def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty")
            and not c.get("farm_hit"))

rep = [c for c in out if reportable(c)]
rep.sort(key=lambda c: (-c["commits_30d"], -c["stars"]))

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L = ["扫 %d 词 × %d 窗 | 原始 %d | 幸存 %d | 报告级 %d" % (
        len(TERMS), NWIN, raw, len(out), len(rep)),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d farm=%d fail=%d"
        % (drop["seen"], drop["excl"], drop["archived"], drop["short_desc"],
           drop["carrier"], drop["farm"], drop["fail"]),
     "核验 %d 个（★>=%d 全部 + 最新补齐，上限 %d）"
        % (len(todo), CHK, CHK_CAP),
     "词表命中: " + " · ".join("%s=%d" % (k, v) for k, v in
        sorted(per_term.items(), key=lambda x: -x[1]))]
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % (k, v) for k, v in low.items()))
if qfail:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(qfail))
zero = [k for k, v in per_term.items() if v == 0 and k not in qfail]
if zero:
    L.append("⚠️ 真零命中: " + " · ".join(zero))
fh = {o: n for o, n in owner_n.items() if n >= 3}
if fh:
    L.append("⚠️ 疑似仓库农场（待入黑名单）: " + " · ".join(
        "%s=%d" % kv for kv in fh.items()))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）: " + " · ".join(stale))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（只有 description）: " + " · ".join(empty))
for c in rep[:25]:
    L.append("  %s [%s] %s ★%d commits30d=%d"
             % (c["created"], c["term"], c["repo"], c["stars"], c["commits_30d"]))
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

if not DRY and hit:
    stamp = now.strftime("%Y-%m-%d")
    merged = {k: stamp for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-5000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            f.write("- [%s](%s) ★%d · %dd提交 · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"], c["commits_30d"],
                       c["term"], c["desc"][:100]))

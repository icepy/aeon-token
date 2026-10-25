#!/usr/bin/env python3
"""github-radar 扫描（加固版）。

与 skills/github-radar/SKILL.md 的 scan.py 逻辑一致：同样的 TERMS / EXCL /
CARRIER / star 分桶 / commits_30d 判真伪。只修三处纯工程缺陷，不动任何筛选判据：

1. **不再回落到未认证 urllib。** 原实现在 gh 返回非 0 时 `GH=False` 永久切换，
   而未认证搜索是 10/min —— 一撞限速就整轮降级，且把「限速」写成「空仓」。
   现在遇到 rate limit 就退避重试，等同一次查询。
2. **搜索按 1/3.2s 节流**（30/min 限额下留安全余量）。
3. **commits 查询区分「真 409 空仓」与「取数失败」。** 只有 409/404 才标
   maybe_empty；限速或网络错误标 unverified，不进报告级也不进空仓名单。
"""
import json, os, re, subprocess, sys, time, urllib.parse
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"; OUT = OUTD + "/out.json"; AUD = OUTD + "/audit.log"
SEEN  = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 0)
CHK  = int(os.environ.get("CHK") or 5)
CHK_CAP = 250
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

STATS = Counter()


def gh_api(path, retries=4):
    """返回 (data, http_status, err)。退避重试，绝不静默降级。"""
    for attempt in range(retries):
        r = subprocess.run(["gh", "api", path], capture_output=True,
                           text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout), 200, None
        err = (r.stderr or "").strip()
        # 409 空仓 / 404 不存在 —— 是真实答案，不重试
        if re.search(r"(409|404|Git Repository is empty|Not Found)", err):
            return None, (409 if "409" in err or "empty" in err else 404), err
        if "rate limit" in err.lower() or "429" in err:
            wait = 25 * (attempt + 1)
            STATS["ratelimit_retry"] += 1
            print("   ~ ratelimit, sleep %ds (%s)" % (wait, path[:60]),
                  file=sys.stderr)
            time.sleep(wait)
            continue
        STATS["api_other_err"] += 1
        time.sleep(4 * (attempt + 1))
    return None, -1, "exhausted retries"


def search(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100"})
    d, st, err = gh_api("search/repositories?" + qs)
    return d, st, err


def commits_30d(rid):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    d, st, err = gh_api("repos/%s/commits?%s" % (rid, qs))
    if d is None:
        return None, ("empty" if st == 409 else "missing" if st == 404
                      else "unverified")
    return (len(d) if isinstance(d, list) else None), "ok"


out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "farm": 0, "fail": 0}
hit, qfail, cov, per_term = {}, [], {}, {}

for term in TERMS:
    total, got, failed = 0, 0, False
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        res, st, err = search(q)
        time.sleep(3.2)          # 30/min 限额下留余量
        if res is None:
            print("! %s @%s: http=%s %s" % (term, w, st, (err or "")[:100]),
                  file=sys.stderr)
            drop["fail"] += 1; failed = True; continue
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
                        "size_kb": it.get("size", 0),
                        "desc": " ".join(desc.split())[:140]})
            hit[rid] = out[-1]
    if failed and not got:
        qfail.append(term)
    per_term[term] = len([c for c in out if c["term"] == term])
    if total:
        cov[term] = round(100.0 * got / total, 1)

# ── 核验：按 star 分桶 ──
out.sort(key=lambda c: -c["stars"])
todo = [c for c in out if c["stars"] >= CHK]
if len(todo) < CHK_CAP:
    rest = sorted([c for c in out if c["stars"] < CHK],
                  key=lambda c: c["created"], reverse=True)
    todo += rest[:CHK_CAP - len(todo)]
for i, c in enumerate(todo):
    n, why = commits_30d(c["repo"])
    c["commits_30d"] = n
    c["verify"] = why
    if n == 0:
        c["stale"] = True
    if why in ("empty", "missing"):
        c["maybe_empty"] = True
    if why == "unverified":
        c["unverified"] = True
    if i % 25 == 0:
        time.sleep(0.4)

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["farm_hit"] = owner_n[c["owner"]]


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
     "核验 %d 个（★>=%d 全部 + 最新补齐，上限 %d）| 空仓 %d · 未验成 %d · 限速重试 %d"
        % (len(todo), CHK, CHK_CAP,
           sum(1 for c in todo if c.get("maybe_empty")),
           sum(1 for c in todo if c.get("unverified")),
           STATS["ratelimit_retry"]),
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
unv = [c["repo"] for c in todo if c.get("unverified")]
if unv:
    L.append("⚠️ 提交数未验成（不计入报告/空仓）: " + " · ".join(unv[:20]) +
             (" …+%d" % (len(unv) - 20) if len(unv) > 20 else ""))
for c in rep[:30]:
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

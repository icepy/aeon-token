#!/usr/bin/env python3
"""WAM 簇第六轮全量翻页（无窗口切片），并核验 30 天提交。"""
import json, subprocess, sys, time, urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
SINCE = "2026-08-26"

def gh(path):
    for i in range(4):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        e = r.stderr.strip()
        if "rate limit" in e.lower() or "403" in e or "429" in e or "secondary" in e.lower():
            time.sleep(6 * (i + 1)); continue
        print("! %s -> %s" % (path[:80], e[:120]), file=sys.stderr)
        return None
    return None

def paginate(q):
    items, page = [], 1
    while page <= 10:
        qs = urllib.parse.urlencode({"q": q, "per_page": "100", "page": str(page),
                                     "sort": "created", "order": "asc"})
        d = gh("search/repositories?" + qs)
        if d is None:
            break
        batch = d.get("items", [])
        items += batch
        if len(batch) < 100:
            break
        page += 1
        time.sleep(3)
    return items

q = '"world action model" in:name,description created:>=%s fork:false' % SINCE
its = paginate(q)
print("total_items=%d" % len(its), file=sys.stderr)

def wk(d):
    y, m, dd = map(int, d.split("-"))
    return datetime(y, m, dd).isocalendar()[1]

weeks = {}
owners = {}
recs = []
for it in its:
    rid = it["full_name"]
    c = (it.get("created_at") or "")[:10]
    w = "W%02d" % wk(c)
    weeks[w] = weeks.get(w, 0) + 1
    o = (it.get("owner") or {}).get("login", "").lower()
    owners[o] = owners.get(o, 0) + 1
    recs.append({"repo": rid, "stars": it.get("stargazers_count", 0),
                 "created": c, "week": w,
                 "pushed": (it.get("pushed_at") or "")[:10],
                 "size_kb": it.get("size", 0),
                 "lang": it.get("language"),
                 "desc": " ".join((it.get("description") or "").split())[:120]})

order = ["W%d" % i for i in range(35, 44)]
print("严格词表 %d 仓 / %d owner" % (len(recs), len(owners)))
print("逐周: " + " · ".join("%s=%d" % (w, weeks.get(w, 0)) for w in order))
print("10 月新建: %d" % len([r for r in recs if r["created"] >= "2026-10-01"]))
multi = {o: n for o, n in owners.items() if n >= 2}
print("owner>=2: %d 个 -> %s" % (len(multi), multi))

# 只核验 ★>=10 或 10 月新建的（节流 search 之外的 core 配额足够）
targets = [r for r in recs if r["stars"] >= 10 or r["created"] >= "2026-10-01"]
print("核验 %d 仓…" % len(targets), file=sys.stderr)
since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
for i, r in enumerate(targets):
    qs = urllib.parse.urlencode({"since": since, "per_page": "100"})
    d = gh("repos/%s/commits?%s" % (r["repo"], qs))
    if isinstance(d, list):
        r["commits_30d"] = len(d)
    else:
        r["commits_30d"] = None
    if i % 40 == 39:
        print("  %d/%d" % (i + 1, len(targets)), file=sys.stderr)
    time.sleep(0.4)

json.dump(recs, open("output/ghradar/wam6.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump({"weeks": weeks, "total": len(recs), "owners": len(owners),
           "multi_owner": multi}, open("output/ghradar/wam6_weeks.json", "w",
                                       encoding="utf-8"), ensure_ascii=False, indent=1)

print("\n★>=10 按提交数:")
for r in sorted([x for x in recs if x["stars"] >= 10],
                key=lambda x: -(x.get("commits_30d") or 0)):
    print("  %-45s ★%-5d 30d=%-4s created=%s pushed=%s" %
          (r["repo"], r["stars"], r.get("commits_30d"), r["created"], r["pushed"]))

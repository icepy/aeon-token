#!/usr/bin/env python3
"""复核 84→99 的差异：同窗口分段 vs 全量翻页，并验证 wam in:name 的子串污染。"""
import json, subprocess, time, urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)

def gh(path):
    for i in range(4):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        if "rate limit" in r.stderr.lower():
            time.sleep(6 * (i + 1)); continue
        return None
    return None

def search(q, cap=10):
    items, page, total = [], 1, 0
    while page <= cap:
        qs = urllib.parse.urlencode({"q": q, "sort": "created", "order": "desc",
                                     "per_page": "100", "page": str(page)})
        d = gh("search/repositories?" + qs)
        if not d:
            break
        total = d.get("total_count", 0)
        got = d.get("items", [])
        items += got
        if len(got) < 100:
            break
        page += 1; time.sleep(2.5)
    return items, total

# ① 全量（无窗口）
full, tot = search('"world action model" in:name,description created:>=2026-08-26 fork:false')
print("① 全量 created:>=2026-08-26 → total=%d 实取=%d" % (tot, len(full)))

# ② 三段窗口（= scan.py 口径），窗口边界用 created:A..B
WINS = ["2026-08-26..2026-09-15", "2026-09-15..2026-10-05", "2026-10-05..2026-10-25"]
seen, wsum = {}, 0
for w in WINS:
    it, t = search('"world action model" in:name,description created:%s fork:false stars:>=0' % w)
    wsum += t
    for x in it:
        seen[x["full_name"]] = x
    print("   窗 %s → total=%d 取=%d" % (w, t, len(it)))
print("② 三段合计 total=%d 去重后=%d" % (wsum, len(seen)))

a = set(x["full_name"] for x in full)
b = set(seen)
print("③ 差异：全量有而窗口无 %d 个 → %s" % (len(a - b), sorted(a - b)[:10]))
print("   窗口有而全量无 %d 个 → %s" % (len(b - a), sorted(b - a)[:10]))

# ④ 子串污染验证
it, t = search("wam in:name created:>=2026-08-26 fork:false", cap=3)
print("\n④ wam in:name total=%d（前 15 个名字看是否子串误中）" % t)
for x in it[:15]:
    print("   %-52s" % x["full_name"])

json.dump(sorted(a | b), open("output/ghradar/wam5_names.json", "w"), indent=1)

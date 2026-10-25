#!/usr/bin/env python3
"""汇总本轮覆盖率：total_count 合计 vs 实取。"""
import json, subprocess, urllib.parse, time
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
DAYS, NWIN = 60, 3
step = DAYS / NWIN
WINS = [f"{(now - timedelta(days=step*(i+1))):%Y-%m-%d}..{(now - timedelta(days=step*i)):%Y-%m-%d}"
        for i in range(NWIN)]
TERMS = ["embodied data", "robot manipulation", "robot dataset", "teleoperation",
         "sim2real", "sim-to-real", "world model", "world action model", "vla",
         "jepa", "egocentric", "verifiable inference", "proof of useful work",
         "data availability", "restaking", "intent-based", "maximal extractable value"]

tot_all = got_all = 0
rows = []
for t in TERMS:
    tot = got = 0
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=0' % (t, w)
        qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                     "per_page": "100", "page": "1"})
        r = subprocess.run(["gh", "api", "search/repositories?" + qs],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            continue
        d = json.loads(r.stdout)
        tot += d.get("total_count", 0)
        got += len(d.get("items", []))
        time.sleep(2)
    rows.append((t, tot, got, 100.0 * got / tot if tot else 0))
    tot_all += tot; got_all += got

for t, tot, got, p in sorted(rows, key=lambda x: x[3]):
    print("%-26s total=%-6d sampled=%-4d cov=%5.1f%%" % (t, tot, got, p))
print("\n合计 total=%d sampled=%d cov=%.1f%%" % (tot_all, got_all, 100.0*got_all/tot_all))

#!/usr/bin/env python3
"""补充探针（非官方词表）：arxiv-radar 那边 20 篇里 11 篇是「具身数据引擎」，
这里查同一主题在代码侧有没有对应物。结果单列，不混进正式词表统计。"""
import json, subprocess, time, urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
def gh(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100", "page": "1"})
    r = subprocess.run(["gh", "api", "search/repositories?" + qs],
                       capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout) if r.returncode == 0 else None

PROBES = [
    "embodied data engine",
    "robot data engine",
    "synthetic robot data",
    "robot data generation",
    "data flywheel robot",
    "teleoperation dataset",
]
for p in PROBES:
    q = '"%s" in:name,description created:>2026-09-25 fork:false' % p
    res = gh(q)
    if not res:
        print("%-24s FAIL" % p); continue
    items = res.get("items", [])
    print("\n-- %-22s total=%-4d sampled=%d" % (p, res.get("total_count", 0), len(items)))
    for it in items[:12]:
        print("   %4d ★ %-10s %-46s %s" % (
            it.get("stargazers_count", 0), (it.get("created_at") or "")[:10],
            it["full_name"], (it.get("description") or "")[:72]))
    time.sleep(3)

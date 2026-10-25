#!/usr/bin/env python3
"""WAM 84 vs 99 的成因诊断：查询稳定性 + 窗口边界 + 创建日期分布。"""
import json, subprocess, time, urllib.parse
from collections import Counter
from datetime import datetime

def gh(path):
    for i in range(4):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        if "rate limit" in r.stderr.lower():
            time.sleep(6 * (i + 1)); continue
        return None
    return None

def q(expr, cap=3):
    items, page = [], 1
    total = 0
    while page <= cap:
        qs = urllib.parse.urlencode({"q": expr, "sort": "created", "order": "desc",
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
    return total, items

BASE = '"world action model" in:name,description fork:false'
print("== A. 同一查询连跑两次（检验 total_count 稳定性）==")
for i in range(2):
    t, _ = q(BASE + " created:>=2026-08-26")
    print("  第 %d 次 total=%d" % (i + 1, t))
    time.sleep(3)

print("\n== B. 不同起点边界 ==")
for s in ("2026-08-25", "2026-08-26", "2026-08-27"):
    t, _ = q(BASE + " created:>=%s" % s)
    print("  created:>=%s → total=%d" % (s, t)); time.sleep(3)

print("\n== C. 上一轮可能的窗口（10-24 口径）==")
for w in ("2026-08-25..2026-10-24", "2026-08-26..2026-10-25"):
    t, _ = q(BASE + " created:%s" % w)
    print("  created:%s → total=%d" % (w, t)); time.sleep(3)

print("\n== D. 99 个的创建日期分布（看增量是否扎堆在近期）==")
t, items = q(BASE + " created:>=2026-08-26", cap=1)
d = Counter(x["created_at"][:10] for x in items)
print("  total=%d 实取=%d" % (t, len(items)))
for k in sorted(d):
    print("   %s %d" % (k, d[k]))

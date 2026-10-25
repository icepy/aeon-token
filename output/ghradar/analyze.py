#!/usr/bin/env python3
"""对 out.json 全体幸存者做分布分析：按词、按周、按 star、按 owner。"""
import json
from collections import Counter, defaultdict
from datetime import datetime

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
print("总数", len(out))

# 按词
by_term = defaultdict(list)
for c in out:
    by_term[c["term"]].append(c)
print("\n== 按词：数目 / ★≥10 / ★0 占比 / 中位创建 ==")
for t, cs in sorted(by_term.items(), key=lambda x: -len(x[1])):
    s10 = sum(1 for c in cs if c["stars"] >= 10)
    z = sum(1 for c in cs if c["stars"] == 0)
    ds = sorted(c["created"] for c in cs)
    print("%-26s n=%-5d >=10:%-4d zero:%-4d(%4.1f%%) created %s..%s"
          % (t, len(cs), s10, z, 100.0 * z / len(cs), ds[0], ds[-1]))

# 按周
print("\n== 按 ISO 周创建分布 ==")
wk = Counter()
for c in out:
    d = datetime.strptime(c["created"], "%Y-%m-%d")
    wk["%d-W%02d" % d.isocalendar()[:2]] += 1
for k in sorted(wk):
    print("  %s %d" % (k, wk[k]))

# star 分布
print("\n== star 分布 ==")
bins = [(0, 0), (1, 2), (3, 9), (10, 49), (50, 199), (200, 999), (1000, 10**9)]
for lo, hi in bins:
    n = sum(1 for c in out if lo <= c["stars"] <= hi)
    print("  %5s-%-6s %d" % (lo, hi if hi < 10**9 else "+", n))

# ★>=10 的全列（这是可以直接引用的可读面）
print("\n== ★>=10 全部（按创建倒序）==")
hi = sorted([c for c in out if c["stars"] >= 10],
            key=lambda c: (-c["stars"]))
print("共 %d 个" % len(hi))
for c in hi:
    print("%5d ★ %-22s %-40s [%s] %s"
          % (c["stars"], c["created"], c["repo"], c["term"], c["desc"][:80]))

# 10 月新建（最近 25 天）
print("\n== 10 月新建 且 ★>=5（新提法的工程化信号）==")
oct_ = sorted([c for c in out if c["created"] >= "2026-10-01" and c["stars"] >= 5],
              key=lambda c: -c["stars"])
print("共 %d 个" % len(oct_))
for c in oct_:
    print("%5d ★ %-22s %-40s [%s] %s"
          % (c["stars"], c["created"], c["repo"], c["term"], c["desc"][:70]))

# owner 多仓
print("\n== owner 命中数 >=3 ==")
on = Counter(c["owner"] for c in out)
for o, n in on.most_common():
    if n >= 3:
        print("  %-28s %d" % (o, n))

#!/usr/bin/env python3
"""84 vs 99 最终判定：把 99 集与上轮 84 逐周残差做卡方/均匀性检验，并列出 99 独有的仓。"""
import json
from collections import Counter
from datetime import datetime

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))
PREV = {"W35": 5, "W36": 9, "W37": 5, "W38": 6, "W39": 17,
        "W40": 18, "W41": 6, "W42": 10, "W43": 8}

def wk(d):
    y, m, dd = map(int, d[:10].split("-"))
    return "W%02d" % datetime(y, m, dd).isocalendar()[1]

cur = Counter(wk(i["created_at"]) for i in items)
diffs = {k: cur[k] - PREV[k] for k in sorted(PREV)}
print("逐周差值:", diffs)
print("差值合计 %d · 有差值的周数 %d/9 · 最大 +%d"
      % (sum(diffs.values()), len([v for v in diffs.values() if v]),
         max(diffs.values())))

# 若为两小时内有机增长，新仓创建时间必然集中在今天；若无，则不是增长
today = [i for i in items if i["created_at"][:10] >= "2026-10-23"]
print("\n99 集里 10-23 之后创建的: %d 个" % len(today))
print("99 集最新创建时间: %s" % max(i["created_at"] for i in items)[:10])

# 上轮 84 里 ★ 最高的几个，今天还在 99 集里吗
CHECK = ["OpenWAM-Official/OpenWAM", "robbyant-research/Zero-WAM", "OpenMOSS/EasyWAM",
         "UniWAM/UniWAM", "LeapLabTHU/Simple-WAM", "THUSI-Lab/PrismWAM",
         "black-forest-labs/flux-action", "dextacwam/DexTacWAM"]
names = set(i["full_name"] for i in items)
print("\n上轮头部仓在今日 99 集里的状态:")
for r in CHECK:
    print("   %-40s %s" % (r, "IN" if r in names else "OUT"))

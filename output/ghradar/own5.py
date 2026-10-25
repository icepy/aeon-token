#!/usr/bin/env python3
"""99 集的 owner 集中度 + 与上轮 79 owner 的对照。"""
import json
from collections import Counter

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))
owners = Counter(i["full_name"].split("/")[0] for i in items)
print("99 仓 · %d owner" % len(owners))
multi = {o: n for o, n in owners.items() if n >= 2}
print("owner 有 ≥2 仓: %d 个 → %s" % (len(multi), multi))

# 上一轮 79 owner / 84 仓
print("\n上轮: 84 仓 / 79 owner（5 个 owner 有 ≥2 仓）")
print("本轮: %d 仓 / %d owner（%d 个 owner 有 ≥2 仓）" % (len(items), len(owners), len(multi)))

#!/usr/bin/env python3
"""验证 ghio+selfname+shortdesc 口径（恰好 84）是否复现上轮按周曲线。"""
import json
from collections import Counter
from datetime import datetime

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))

def drop(i):
    o, s = i["full_name"].split("/")
    sl = s.lower()
    return (sl.endswith(".github.io") or sl == o.lower()
            or len((i.get("description") or "").strip()) < 25)

kept = [i for i in items if not drop(i)]
def wk(d):
    y, m, dd = map(int, d[:10].split("-"))
    return "W%02d" % datetime(y, m, dd).isocalendar()[1]

w = Counter(wk(i["created_at"]) for i in kept)
owners = set((i.get("owner") or {}).get("login", "") for i in items)  # 需 owner 字段
print("口径 ghio+selfname+shortdesc → %d 仓" % len(kept))
prev = {"W35": 5, "W36": 9, "W37": 5, "W38": 6, "W39": 17, "W40": 18, "W41": 6, "W42": 10, "W43": 8}
print("%-5s %5s %5s %s" % ("周", "上轮", "本轮", "差"))
for k in sorted(prev):
    print("%-5s %5d %5d %+d" % (k, prev[k], w[k], w[k] - prev[k]))
print("合计 上轮 %d · 本轮 %d" % (sum(prev.values()), len(kept)))

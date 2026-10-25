#!/usr/bin/env python3
"""99 vs 84 归因：项目页 / 站点类仓库是否被上一轮剔除。按周对齐。"""
import json
from collections import Counter
from datetime import datetime

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))
print("全量 99 个")

def is_page(it):
    r = it["full_name"]
    short, owner = r.split("/")[-1], r.split("/")[0]
    s = short.lower()
    return (s.endswith(".github.io") or s.lower() == owner.lower()
            or s.endswith("-page") or s.endswith("-project") or s.endswith("-website")
            or s.endswith("projectpage") or s.startswith("www."))

pages = [it for it in items if is_page(it)]
code = [it for it in items if not is_page(it)]
print("项目页/站点类 %d · 代码仓 %d" % (len(pages), len(code)))

def wk(d):
    y, m, dd = map(int, d[:10].split("-"))
    return "W%02d" % datetime(y, m, dd).isocalendar()[1]

for label, grp in (("全量 99", items), ("剔项目页", code)):
    w = Counter(wk(i["created_at"]) for i in grp)
    ks = sorted(w)
    print("%-10s %3d 仓 · %s" % (label, len(grp), " · ".join("%s=%d" % (k, w[k]) for k in ks)))

prev = {"W35": 5, "W36": 9, "W37": 5, "W38": 6, "W39": 17, "W40": 18, "W41": 6, "W42": 10, "W43": 8}
w_all = Counter(wk(i["created_at"]) for i in items)
w_code = Counter(wk(i["created_at"]) for i in code)
print("\n%-6s %6s %8s %8s %8s" % ("周", "上轮", "本轮全量", "剔页后", "剔页-上轮"))
for k in sorted(prev):
    print("%-6s %6d %8d %8d %+8d" % (k, prev[k], w_all[k], w_code[k], w_code[k] - prev[k]))

print("\n项目页/站点清单（%d）:" % len(pages))
for it in sorted(pages, key=lambda x: -x["stargazers_count"]):
    print("  ★%-5d %-10s %s" % (it["stargazers_count"], it["created_at"][:10], it["full_name"]))

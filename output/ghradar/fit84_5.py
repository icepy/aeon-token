#!/usr/bin/env python3
"""找出哪种过滤口径能把 99 变成 84：逐条试，看哪个组合命中。"""
import json
from itertools import combinations

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))

def f_ghio(i):
    return i["full_name"].split("/")[-1].lower().endswith(".github.io")

def f_selfname(i):
    o, s = i["full_name"].split("/")
    return s.lower() == o.lower()

def f_pageword(i):
    s = i["full_name"].split("/")[-1].lower()
    return any(s.endswith(x) for x in ("-page", "-project", "-website", "projectpage"))

def f_shortdesc(i):
    return len((i.get("description") or "").strip()) < 25

def f_nodesc(i):
    return not (i.get("description") or "").strip()

FILTERS = {"ghio": f_ghio, "selfname": f_selfname, "pageword": f_pageword,
           "shortdesc": f_shortdesc, "nodesc": f_nodesc}

print("基线 99")
for name, f in FILTERS.items():
    print("  单独剔 %-10s → %d" % (name, len([i for i in items if not f(i)])))

print("\n组合：")
for r in range(1, 4):
    for combo in combinations(FILTERS, r):
        n = len([i for i in items if not any(FILTERS[c](i) for c in combo)])
        if 80 <= n <= 88:
            print("  剔 %-34s → %d" % ("+".join(combo), n))

print("\n最接近 84 的组合逐仓核对：")
best = ("ghio", "selfname", "pageword")
kept = [i for i in items if not any(FILTERS[c](i) for c in best)]
print("  %s → %d 仓" % ("+".join(best), len(kept)))
print("\n  被这三条剔除的 %d 个：" % (99 - len(kept)))
for i in items:
    if any(FILTERS[c](i) for c in best):
        print("    ★%-5d %s" % (i["stargazers_count"], i["full_name"]))

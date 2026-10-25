#!/usr/bin/env python3
"""判定哪一条属性过滤能把 99 精确降为 84，且逐周等于上轮 5/9/5/6/17/18/6/10/8。"""
import json
from collections import Counter
from datetime import datetime
from itertools import combinations

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))
PREV = {"W35": 5, "W36": 9, "W37": 5, "W38": 6, "W39": 17,
        "W40": 18, "W41": 6, "W42": 10, "W43": 8}

def wk(d):
    y, m, dd = map(int, d[:10].split("-"))
    return "W%02d" % datetime(y, m, dd).isocalendar()[1]

def curve(grp):
    w = Counter(wk(i["created_at"]) for i in grp)
    return {k: w[k] for k in sorted(PREV)}

print("99 集逐周:", curve(items))
print("合计", len(items))
print("★0 有 %d 个" % len([i for i in items if i["stargazers_count"] == 0]))
print("★<2 有 %d 个" % len([i for i in items if i["stargazers_count"] < 2]))
print("pushed_at 早于 09-25 有 %d 个" % len([i for i in items
      if (i.get("pushed_at") or "")[:10] < "2026-09-25"]))

CANDS = {
    "★>=1": lambda i: i["stargazers_count"] >= 1,
    "★>=2": lambda i: i["stargazers_count"] >= 2,
    "★>=3": lambda i: i["stargazers_count"] >= 3,
    "有 description": lambda i: bool((i.get("description") or "").strip()),
    "非 page 词": lambda i: not any(i["full_name"].split("/")[-1].lower().endswith(x)
                                    for x in ("-page", "-project", "-website", "projectpage")),
    "非 github.io": lambda i: not i["full_name"].lower().endswith(".github.io"),
    "非 selfname": lambda i: i["full_name"].split("/")[-1].lower() != i["full_name"].split("/")[0].lower(),
    "非 fork": lambda i: True,
}
for name, f in CANDS.items():
    g = [i for i in items if f(i)]
    c = curve(g)
    match = "✅ 逐周吻合" if c == PREV else ""
    print("%-16s → %2d 仓 %s %s" % (name, len(g), c, match))

print("\n组合搜索（找 84 且逐周完全吻合）:")
best = None
for r in (2, 3):
    for combo in combinations(CANDS, r):
        g = [i for i in items if all(CANDS[c](i) for c in combo)]
        if len(g) == 84:
            c = curve(g)
            print("  %-34s → 84 %s %s" % ("+".join(combo), c,
                                          "✅" if c == PREV else ""))
            if c == PREV:
                best = combo
print("\n完全吻合口径:", best)

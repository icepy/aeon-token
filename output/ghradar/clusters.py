#!/usr/bin/env python3
"""三件事：
1. WAM / world-model 簇的按周走势（对比今晨 run2 的 W35..W43 曲线）
2. 加密侧全量（小词可读面）
3. 新提法命名扩散：10 月新建里 name 含 WAM/world 的工程化变体
"""
import json, re
from collections import Counter, defaultdict
from datetime import datetime

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))

def wk(s):
    return "%d-W%02d" % datetime.strptime(s, "%Y-%m-%d").isocalendar()[:2]

def iscode(c):
    d = c["desc"].lower()
    return not (".github.io" in d or "project page" in d
                or d.startswith("a curated") or "awesome" in c["repo"].lower())

print("== world action model 簇：按周（代码仓 / 全部）==")
wam = [c for c in out if c["term"] == "world action model" or "wam" in c["repo"].lower()]
cw, aw = Counter(), Counter()
for c in wam:
    aw[wk(c["created"])] += 1
    if iscode(c):
        cw[wk(c["created"])] += 1
for k in sorted(aw):
    print("  %s  代码仓 %2d   全部 %2d" % (k, cw.get(k, 0), aw[k]))
print("  合计 %d 仓 / %d owner；10 月新建 %d" % (
    len(wam), len({c["owner"] for c in wam}),
    sum(1 for c in wam if c["created"] >= "2026-10-01")))

print("\n== world model 簇：按周（代码仓）==")
wm = [c for c in out if c["term"] == "world model"]
cwm = Counter(wk(c["created"]) for c in wm if iscode(c))
for k in sorted(cwm):
    print("  %s  代码仓 %3d" % (k, cwm[k]))
print("  合计 %d 仓 / %d owner" % (len(wm), len({c["owner"] for c in wm})))

print("\n== 加密侧全量（6 个小词，全部列出）==")
CRY = ["verifiable inference", "proof of useful work", "data availability",
       "restaking", "intent-based", "maximal extractable value"]
for t in CRY:
    cs = [c for c in out if c["term"] == t]
    print("\n-- %s（%d）--" % (t, len(cs)))
    for c in sorted(cs, key=lambda x: -x["stars"]):
        print("   %3d ★ %s %-46s %s" % (c["stars"], c["created"], c["repo"], c["desc"][:75]))

print("\n== 10 月新建：name 含 wam 的工程化变体（提法扩散证据）==")
nam = [c for c in out if c["created"] >= "2026-10-01" and "wam" in c["repo"].lower()]
print("共 %d 个" % len(nam))
for c in sorted(nam, key=lambda x: x["created"]):
    print("   %s  %4d ★  %-44s %s" % (c["created"], c["stars"], c["repo"], c["desc"][:62]))

print("\n== ★0 但不该被 star 率埋没的：10 月新建 + 高提交 == 需人工看 ==")

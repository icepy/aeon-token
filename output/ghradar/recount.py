#!/usr/bin/env python3
"""校正：WAM 簇的两种口径（严格词表 vs 词表∪name含wam）。"""
import json
from collections import Counter
from datetime import datetime
out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
def wk(s): return "%d-W%02d" % datetime.strptime(s, "%Y-%m-%d").isocalendar()[:2]

strict = [c for c in out if c["term"] == "world action model"]
byname = [c for c in out if "wam" in c["repo"].lower()]
union = {c["repo"]: c for c in strict + byname}
print("严格词表 world action model: %d 仓 / %d owner" % (len(strict), len({c["owner"] for c in strict})))
print("name 含 wam 的任何仓:        %d" % len(byname))
print("并集:                        %d 仓 / %d owner" % (len(union), len({c["owner"] for c in union.values()})))
print("并集中 10 月新建:            %d" % sum(1 for c in union.values() if c["created"] >= "2026-10-01"))

print("\n严格口径按周:")
cw = Counter(wk(c["created"]) for c in strict)
for k in sorted(cw): print("  %s %d" % (k, cw[k]))

# owner 多仓
print("\n严格口径 owner 分布（>=2）:")
on = Counter(c["owner"] for c in strict)
print("  多仓 owner 数:", sum(1 for v in on.values() if v >= 2), "/", len(on))

# 机器人 vs 加密
CRY = {"verifiable inference","proof of useful work","data availability","restaking","intent-based","maximal extractable value"}
print("\n机器人侧 %d · 加密侧 %d" % (
    sum(1 for c in out if c["term"] not in CRY), sum(1 for c in out if c["term"] in CRY)))

#!/usr/bin/env python3
"""Round-8 analysis: contamination delta, term yields, cluster coverage, agent fingerprint."""
import json
import os
import re
import subprocess
import time
from collections import Counter, defaultdict

OUTD = "output/ghradar"
out = json.load(open(OUTD + "/out8.json", encoding="utf-8"))
terms = json.load(open(OUTD + "/terms8.json", encoding="utf-8"))

print("=" * 70)
print("A. 缩写 → 全称：污染是否真的清掉")
print("=" * 70)

# 第七轮 NEG 词表：vla 撞 vlan/vlad*；jepa 撞 jepang/jepara/jepan
VLA_NEG = ["vlan", "vlad", "vladimir", "vladislav", "vladoss"]
JEPA_NEG = ["jepang", "jepara", "jepan"]

def contaminated(repos, negs):
    hits = []
    for c in repos:
        blob = (c["repo"] + " " + c["desc"]).lower()
        if any(n in blob for n in negs):
            hits.append(c["repo"])
    return hits

vla_set = [c for c in out if c["term"] == "vision language action"]
jepa_set = [c for c in out if c["term"] == "joint embedding predictive"]

cv = contaminated(vla_set, VLA_NEG)
cj = contaminated(jepa_set, JEPA_NEG)
print("vision language action: 幸存 %d，残留污染 %d (%.1f%%) %s"
      % (len(vla_set), len(cv), 100.0 * len(cv) / max(1, len(vla_set)), cv[:6]))
print("joint embedding predictive: 幸存 %d，残留污染 %d (%.1f%%) %s"
      % (len(jepa_set), len(cj), 100.0 * len(cj) / max(1, len(jepa_set)), cj[:6]))
print("对照 第七轮：vla 22.0% 污染 · jepa 14.5%")

def rep_of(lst):
    return [c for c in lst if c.get("commits_30d") is not None
            and c["commits_30d"] >= 5 and not c.get("stale")
            and not c.get("maybe_empty")]

print("  vla 全称口径：存活仓 %d / 报告级 %d" % (len(vla_set), len(rep_of(vla_set))))
print("  jepa 全称口径：存活仓 %d / 报告级 %d" % (len(jepa_set), len(rep_of(jepa_set))))

print()
print("=" * 70)
print("B. 逐词产出（新收 vs 报告级）")
print("=" * 70)
by = defaultdict(list)
for c in out:
    by[c["term"]].append(c)
rows = []
for t in terms["terms"]:
    lst = by.get(t, [])
    rows.append((t, terms["new_term"].get(t, 0), len(lst), len(rep_of(lst)),
                 len([c for c in lst if c.get("commits_7d", 0) > 0])))
rows.sort(key=lambda r: -r[3])
print("%-30s %6s %6s %8s %6s" % ("term", "新收", "幸存", "报告级", "7d活"))
for t, nw, sv, rp, a7 in rows:
    print("%-30s %6d %6d %8d %6d" % (t, nw, sv, rp, a7))

print()
print("=" * 70)
print("C. 全量核验总览")
print("=" * 70)
ver = [c for c in out if c.get("commits_30d") is not None]
rep = rep_of(out)
print("幸存 %d · 已核验 %d (%.1f%%) · 报告级 %d (%.1f%%) · 7d 活跃 %d (%.1f%%)"
      % (len(out), len(ver), 100.0 * len(ver) / len(out), len(rep),
         100.0 * len(rep) / len(ver),
         len([c for c in ver if c.get("commits_7d", 0) > 0]),
         100.0 * len([c for c in ver if c.get("commits_7d", 0) > 0]) / len(ver)))
print("30d 零提交 %d (%.1f%%) · 爆完即停 %d / %d 报告级 (%.1f%%)"
      % (len([c for c in ver if c.get("stale")]),
         100.0 * len([c for c in ver if c.get("stale")]) / len(ver),
         len([c for c in rep if c.get("burst_only")]), len(rep),
         100.0 * len([c for c in rep if c.get("burst_only")]) / max(1, len(rep))))
print("空仓 409 %d · 未核验 %d · 撞 30d 上限(≥100) %d · 撞 7d 上限 %d"
      % (len([c for c in out if c.get("maybe_empty")]),
         len([c for c in out if c.get("unverified")]),
         len([c for c in ver if c.get("commits_30d_ge")]),
         len([c for c in ver if c.get("commits_7d_ge")])))

print()
print("=" * 70)
print("D. 加密 vs 机器人（对齐完整度后比较）")
print("=" * 70)
CRY = {"verifiable inference", "proof of useful work", "data availability",
       "restaking", "intent-based", "maximal extractable value"}
cry = [c for c in out if c["term"] in CRY]
rob = [c for c in out if c["term"] not in CRY]
for name, lst in (("加密", cry), ("机器人/AI", rob)):
    v = [c for c in lst if c.get("commits_30d") is not None]
    r = rep_of(lst)
    a7 = [c for c in r if c.get("commits_7d", 0) > 0]
    print("%-10s 幸存 %3d · 核验 %3d (%.0f%%) · 报告级 %3d (%.1f%%) · 7d活 %2d (%.0f%%)"
          % (name, len(lst), len(v), 100.0 * len(v) / max(1, len(lst)),
             len(r), 100.0 * len(r) / max(1, len(v)),
             len(a7), 100.0 * len(a7) / max(1, len(r))))

print()
print("=" * 70)
print("E. 报告级全表（按 7d 排序）")
print("=" * 70)
for c in rep:
    print("%-52s ★%-5d 30d=%-4s 7d=%-4s %-28s %s"
          % (c["repo"][:52], c["stars"],
             "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
             "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
             c["term"], c["created"]))

#!/usr/bin/env python3
"""第七轮汇总：两批全量核验合并后的规范数字。"""
import json, re
from collections import Counter

def clean(c):
    blob = ((c["repo"].split("/")[-1]) + " " + (c.get("desc") or "")).lower()
    if c["term"] == "vla" and re.search(
            r"\bvlan\b|intervlan|vlan-|_vlan|vlan_|\bvlad|\bvlaria|\bvlak|"
            r"vpn|router|switch|dhcp|packet.tracer|networking|subnet", blob):
        return False
    if c["term"] == "jepa" and re.search(
            r"jepang|jepara|bahasa|kuis|undangan|pernikahan|kotoba", blob):
        return False
    s = c["repo"].split("/")[-1]
    if s.endswith(".github.io") and c["size_kb"] < 300:
        return False
    return True

CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}

a = json.load(open("output/ghradar/full7.json", encoding="utf-8"))
b = json.load(open("output/ghradar/full7b.json", encoding="utf-8"))
allr = a + b
ok = [c for c in allr if c.get("q_status") == "ok"]

print("合并：幸存 %d（r6 %d + r7 新增 %d），核验 ok=%d，失败=%d"
      % (len(allr), len(a), len(b), len(ok), len(allr) - len(ok)))

rep = [c for c in ok if c["commits_30d"] >= 5]
repc = [c for c in rep if clean(c)]
repca = [c for c in repc if c.get("commits_7d", 0) >= 1]
print("≥5 提交/30d: %d (%.1f%%) → 剔污染 %d (%.1f%%) → 其中 7d 活跃 %d (%.1f%%)"
      % (len(rep), 100.0 * len(rep) / len(ok),
         len(repc), 100.0 * len(repc) / len(ok),
         len(repca), 100.0 * len(repca) / len(ok)))

print("7d 活跃（全部）: %d (%.1f%%)"
      % (len([c for c in ok if c.get("commits_7d", 0) >= 1]),
         100.0 * len([c for c in ok if c.get("commits_7d", 0) >= 1]) / len(ok)))

for d, lab in ((CRYPTO, "crypto"), (None, "robot")):
    xs = [c for c in ok if (c["term"] in CRYPTO) == (d is not None)]
    r = [c for c in xs if c["commits_30d"] >= 5]
    rc = [c for c in r if clean(c)]
    ra = [c for c in rc if c.get("commits_7d", 0) >= 1]
    print("[%s] 核验 %d | ≥5提交 %d | clean %d | clean且7d活跃 %d"
          % (lab, len(xs), len(r), len(rc), len(ra)))

print("\n30d=100 撞顶（下限）: %d" % len([c for c in ok if c["commits_30d"] == 100]))
print("30d 零提交: %d (%.1f%%)"
      % (len([c for c in ok if c["commits_30d"] == 0]),
         100.0 * len([c for c in ok if c["commits_30d"] == 0]) / len(ok)))

# 爆完即停，只在 clean 报告级里算
burst = [c for c in repc if c.get("commits_7d", 0) == 0]
print("爆完即停（clean 报告级里 7d=0）: %d / %d = %.1f%%"
      % (len(burst), len(repc), 100.0 * len(burst) / len(repc)))

# 按词 clean 报告级
print("\n按词 clean 报告级（≥5提交 30d）:")
pc = Counter(c["term"] for c in repc)
for t, n in pc.most_common():
    tot = len([c for c in ok if c["term"] == t])
    print("  %-24s %4d / %4d" % (t, n, tot))

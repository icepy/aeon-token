#!/usr/bin/env python3
"""scan 幸存集 vs 全量口径的 WAM 差异归因：pages / seen / carrier / desc。"""
import json

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
wam = [c for c in out if c["term"] == "world action model"]
names = set(c["repo"] for c in wam)
full = set(json.load(open("output/ghradar/wam5_names.json", encoding="utf-8")))

print("scan 幸存 WAM %d（10 月新建 %d）· 全量口径 names %d"
      % (len(wam), len([c for c in wam if c["created"] >= "2026-10-01"]), len(full)))
missing = sorted(full - names)
print("全量有、scan 幸存集无: %d" % len(missing))
for r in missing:
    print("   %s" % r)

print("\nscan 有、全量无: %d" % len(names - full))
for r in sorted(names - full):
    print("   %s" % r)

#!/usr/bin/env python3
"""OpenMakerProjects 为何「仍在」：查它是否真的进了幸存集。"""
import json

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
hit = [c for c in out if "openmaker" in c["owner"].lower()]
print("幸存集里 openmaker 相关: %d" % len(hit))
for c in hit:
    print("   %s ★%d" % (c["repo"], c["stars"]))
keys = ["maxamin", "nirholas", "openmakerprojects"]
print("\n大小写匹配测试:")
for c in out[:0]:
    pass
owners = set(c["owner"] for c in out)
print("  'OpenMakerProjects' 在 owners 里:", "OpenMakerProjects" in owners)
print("  'openmakerprojects' 小写是否出现在任何 owner:",
      any(o.lower() == "openmakerprojects" for o in owners))

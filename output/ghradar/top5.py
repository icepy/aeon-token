#!/usr/bin/env python3
"""报告素材：净报告级 top、新面孔、加密侧。"""
import json

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
rep = [c for c in out if (c.get("commits_30d") or 0) >= 5
       and not c.get("stale") and not c.get("maybe_empty")]
LISTS = {"YanjieZe/agent-real2sim2real", "ShuaixinHuang/awesome-robotics",
         "futakw/Awesome-Physical-AI-Safety", "benchflow-ai/awesome-embodied-agents"}
NONEMB = {"cooperwooley/diamond-cs2-v2", "khelverskovp/atom-jepa", "Tanpig-X/PDE-JEPA"}
clean = [c for c in rep if c["repo"] not in LISTS and c["repo"] not in NONEMB]

print("== 净报告级 top 20（按提交）==")
for c in sorted(clean, key=lambda x: (-x["commits_30d"], -x["stars"]))[:20]:
    cap = "+" if c["commits_30d"] == 100 else ""
    print("%-10s ★%-5d c30=%-4s%s %-46s %s" % (c["created"], c["stars"],
          c["commits_30d"], cap, c["repo"], c["desc"][:60]))

print("\n== ★>=50 且活（净集）==")
for c in sorted([c for c in clean if c["stars"] >= 50], key=lambda x: -x["stars"]):
    print("★%-5d c30=%-4s %-10s %-46s %s" % (c["stars"], c["commits_30d"],
          c["created"], c["repo"], c["desc"][:50]))

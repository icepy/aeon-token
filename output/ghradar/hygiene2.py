#!/usr/bin/env python3
"""收紧后的语义误中判据：只剔 name 明确的列表仓 / 项目页。"""
import json, re
from collections import Counter

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))

def is_list(c):
    name = c["repo"].split("/")[-1].lower()
    d = c["desc"].lower()
    if re.search(r"awesome|paper-list|project-?page|-page$|\.github\.io$|"
                 r"paper list|reading list", name):
        return "name"
    if re.match(r"^(a |an )?(curated|awesome) ", d) or "curated list" in d \
       or "curated collection" in d or "bibliography" in d \
       or d.startswith("a curated"):
        return "desc"
    return None

lists = [(c, is_list(c)) for c in out if is_list(c)]
print("== 明确的列表/项目页仓: %d ==" % len(lists))
for c, why in sorted(lists, key=lambda x: -(x[0].get("commits_30d") or 0)):
    if c.get("commits_30d") is not None:
        print("   %-46s ★%-4d commits=%s (%s)" % (
            c["repo"], c["stars"], c["commits_30d"], why))
bad = {c["repo"] for c, _ in lists}

# 另两类单独的语义误中（人工判定，附理由）
MISMATCH = {
    "pengqianhan/campus-world-model": "奥克兰大学 3D 校园地图，非 world model",
    "ABC12345anouys/EvoBot": "LIBERO 任务 agent，desc 自述 no world model",
    "Sarim-MBZUAI/advsim2real": "web agent 提示注入，非机器人 sim2real",
    "khelverskovp/atom-jepa": "3D 原子系统 JEPA，非具身/视觉",
    "Tanpig-X/PDE-JEPA": "偏微分方程 latent 动力学",
    "ostertagmatthieu-dev/saac-jepa": "CNC 机床迁移，非机器人",
    "aselimc/jepa.cpp": "JEPA 的 CPU 推理移植",
    "bilemond/JANUS": "AI 自主科研 agent，非具身",
    "ManfredCh/ai-security-universe": "AI 安全综述",
    "hanfeny7/world-pose-fall-intelligence": "跌倒检测 showcase",
    "ImYangC7/AutoGUIWorld": "GUI agent 的视觉世界模型",
    "Jimntu/GameDirector_code": "游戏玩法世界模型",
}
excl = bad | set(MISMATCH)
print("\n== 另加人工判定语义误中 %d ==" % len(MISMATCH))
for k, v in MISMATCH.items():
    print("   %-44s %s" % (k, v))

def ok(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= 5
            and not c.get("stale") and not c.get("maybe_empty")
            and not c.get("farm_hit") and c["repo"] not in excl)

rep = sorted([c for c in out if ok(c)],
             key=lambda c: (-c["commits_30d"], -c["stars"]))
print("\n== 最终报告级: %d ==" % len(rep))
for t, n in Counter(c["term"] for c in rep).most_common():
    print("   %-22s %d" % (t, n))

print("\n== 提交数（≥100 记为 100+）==")
for c in rep:
    tag = "100+" if c["commits_30d"] == 100 else str(c["commits_30d"])
    print("%-46s ★%-4d %-5s %s" % (c["repo"], c["stars"], tag, c["created"]))

json.dump([c["repo"] for c in rep], open("output/ghradar/final_repos.json", "w"),
          ensure_ascii=False, indent=1)

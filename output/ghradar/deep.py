#!/usr/bin/env python3
"""覆盖率 + 本轮相对历史的新面孔 + 结构性偏差检查。"""
import json
from collections import Counter

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
final = set(json.load(open("output/ghradar/final_repos.json")))

# ── 覆盖率（用 audit 里的 per-term 与 total_count 复算）──
# audit 已给出 <50% 的词，这里只报整体
print("== 覆盖率 ==")
print("  world model 21.4% · vla 7.9% · jepa 44.3%  <- audit 报的 3 个不合格词")

# ── 观察窗偏差：报告级按创建周的衰减 ──
print("\n== 观察窗偏差检查：报告级（≥5 提交/30d）按创建周 ==")
def iso_w(d):
    from datetime import datetime
    return datetime.strptime(d, "%Y-%m-%d").isocalendar()[1]
rep = [c for c in out if c["repo"] in final]
wk_all = Counter(iso_w(c["created"]) for c in out)
wk_rep = Counter(iso_w(c["created"]) for c in rep)
for w in sorted(wk_rep):
    tot = wk_all.get(w, 0)
    print("  W%d: 幸存 %3d / 报告级 %3d (%.0f%%)" % (
        w, tot, wk_rep[w], 100.0 * wk_rep[w] / max(tot, 1)))
print("  ⚠️ 新仓观察窗短 —— W42/W43 的仓没有足够时间累积 5 次提交，")
print("     所以「新仓报告级数下降」不能读成「热度下降」。")

# ── 本轮新面孔：10 月建 + 报告级 + 不在历史日志提到的名单里 ──
HIST = {
    "OpenInterpretability/ekbasis", "clipspark/multiworldbench",
    "video-db/RoboPeek", "cvlab-kaist/ME-World", "QinnyuLan/SONIC_unitree_h2",
    "Iunacy/HAND", "ShuhongLL/RawVLA", "NVIDIA/Flora",
    "THUSI-Lab/PrismWAM", "OpenWAM-Official/OpenWAM", "OpenMOSS/EasyWAM",
    "UniWAM/UniWAM", "Gen-Verse/RSI-Anything", "TencentARC/WorldCrafter",
    "CuboiLeo/SuperMimic-Reproduced", "robosimstudio/robosimstudio",
    "Ropedia/ropedia-w0", "vearl-verified-compute/vearl",
    "Gen-Verse/JEPA-Anything", "robbyant-research/Zero-WAM",
    "buaacyw/code-world-model", "black-forest-labs/flux-action",
    "cocacola-lab/Recursia", "iitimii/SmolWAM",
}
new_faces = [c for c in rep if c["created"] >= "2026-10-01"
             and c["repo"] not in HIST]
new_faces.sort(key=lambda c: (-c["commits_30d"], -c["stars"]))
print("\n== 10 月新建 · 报告级 · 历史未提过: %d ==" % len(new_faces))
for c in new_faces:
    print("%-46s ★%-4d %3dd [%s] %s" % (
        c["repo"], c["stars"], c["commits_30d"], c["term"], c["desc"][:70]))

# ── ★0 但有真实提交（新建仓铁律的正向证据）──
z = [c for c in rep if c["stars"] == 0]
print("\n== ★0 但报告级（新建仓必然 ★0–2 的实证）: %d ==" % len(z))
for c in sorted(z, key=lambda x: -x["commits_30d"]):
    print("%-46s %3dd %s" % (c["repo"], c["commits_30d"], c["created"]))

# ── 同一 owner 多仓（非黑名单的）──
own = Counter(c["owner"] for c in out)
multi = {o: n for o, n in own.items() if n >= 3}
print("\n== owner ≥3 仓（farm 候选）: %d 个 ==" % len(multi))
for o, n in sorted(multi.items(), key=lambda x: -x[1]):
    rs = [c["repo"] for c in out if c["owner"] == o]
    print("  %-28s %d 仓: %s" % (o, n, ", ".join(r.split("/")[-1] for r in rs)[:110]))

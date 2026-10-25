#!/usr/bin/env python3
"""本轮 top 新面孔的结构抽验：语言 / size / fork / 提交 / pushed。"""
import json, subprocess, sys

repos = sys.argv[1:] or [
    "ShuhongLL/RawVLA", "QinnyuLan/SONIC_unitree_h2", "Iunacy/HAND",
    "ZJU-OmniAI/VLA-Rolling", "LogosIntelligenceLab/TIDE",
    "cvlab-kaist/ME-World", "video-db/RoboPeek", "dundysm/occlubench",
    "Dicomsky/StairVLA", "91CHD/embodied-data-lab", "NVIDIA/Flora",
    "Ropedia/ropedia-w0", "cocacola-lab/Recursia", "THUSI-Lab/PrismWAM",
    "OpenPhoenix-Team/Phoenix-MWA", "TianhengW/PatchWAM", "gwenzhang/OSWAM",
    "ZGCA-HMI-Lab/DiffWAM", "LambdaHumanoid/openlambda", "ssj9596/Atomic-WAM",
]
print("%-44s %-12s %8s %4s %5s %-6s %-11s" % ("repo", "lang", "sizeKB", "★", "f?" , "comms", "pushed"))
print("-" * 104)
for r in repos:
    d = subprocess.run(["gh", "api", "repos/" + r], capture_output=True, text=True)
    if d.returncode != 0:
        print("%-44s  ERR %s" % (r, d.stderr.strip()[:40])); continue
    j = json.loads(d.stdout)
    c = subprocess.run(["gh", "api", "repos/%s/commits?per_page=1" % r],
                       capture_output=True, text=True)
    n = "?"
    if c.returncode == 0 and c.stdout.strip():
        try:
            n = len(json.loads(c.stdout))
        except Exception:
            pass
    print("%-44s %-12s %8d %4d %5s %-6s %-11s" % (
        r, (j.get("language") or "-")[:12], (j.get("size") or 0),
        j.get("stargazers_count", 0), "Y" if j.get("fork") else "n",
        n, (j.get("pushed_at") or "")[:10]))

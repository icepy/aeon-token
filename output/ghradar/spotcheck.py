#!/usr/bin/env python3
"""本轮 top 新面孔的结构抽验。"""
import json, subprocess

repos = [
    "OpenInterpretability/ekbasis",
    "kaarelkaarelson/lingbot-world-v2-realtime",
    "clipspark/multiworldbench",
    "ruyue0001/trace2env",
    "video-db/RoboPeek",
    "TencentARC/Multics",
    "seohongpark/ocbench",
    "DexForce/UNITAS",
    "LeapLabTHU/Simple-WAM",
    "NVIDIA/Flora",
    "ABC12345anouys/EvoBot",
    "rokbenko/quackd",
    "vearl-verified-compute/vearl",
]
print("%-46s %-10s %8s %4s %5s %6s %-11s" % (
    "repo", "lang", "sizeKB", "★", "fork", "cmts", "pushed"))
print("-" * 100)
for r in repos:
    d = subprocess.run(["gh", "api", "repos/" + r], capture_output=True, text=True)
    if d.returncode != 0:
        print("%-46s ERR" % r); continue
    j = json.loads(d.stdout)
    c = subprocess.run(["gh", "api", "repos/%s/commits?per_page=100" % r],
                       capture_output=True, text=True)
    n = len(json.loads(c.stdout)) if c.returncode == 0 and c.stdout.strip() else -1
    print("%-46s %-10s %8d %4d %5d %6d %-11s" % (
        r, j.get("language") or "-", j.get("size", 0),
        j.get("stargazers_count", 0), j.get("forks_count", 0), n,
        (j.get("pushed_at") or "")[:10]))

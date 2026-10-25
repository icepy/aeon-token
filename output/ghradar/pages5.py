#!/usr/bin/env python3
"""pages 规则误杀检查：被 selfname / pageword 丢掉的仓，实际是什么。"""
import json, subprocess

REPOS = ["UniWAM/UniWAM", "dextacwam/DexTacWAM", "kf953741/kf953741",
         "iitimii/SmolWAM", "wa-jepa/wa-jepa.github.io",
         "SII-Ferenas/ProWAM-page", "Prism-WAM/prism-wam.github.io"]

print("%-40s %-12s %7s %5s %-11s %s" % ("repo", "lang", "sizeKB", "★", "pushed", "desc"))
print("-" * 110)
for r in REPOS:
    d = subprocess.run(["gh", "api", "repos/" + r], capture_output=True, text=True)
    if d.returncode != 0:
        print("%-40s ERR" % r); continue
    j = json.loads(d.stdout)
    print("%-40s %-12s %7d %5d %-11s %s" % (
        r, (j.get("language") or "-")[:12], j.get("size") or 0,
        j.get("stargazers_count", 0), (j.get("pushed_at") or "")[:10],
        (j.get("description") or "-")[:52]))

# UniWAM 是不是真代码仓（有无 releases / topics）
d = subprocess.run(["gh", "api", "repos/UniWAM/UniWAM/contents"], capture_output=True, text=True)
if d.returncode == 0:
    print("\nUniWAM 根目录: " + ", ".join(x["name"] for x in json.loads(d.stdout)[:15]))

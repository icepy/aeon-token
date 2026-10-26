#!/usr/bin/env python3
"""github-radar 第十轮：根目录形态 + agent 指纹 + 覆盖率。

判据 10：「高提交数」和「是代码仓」在同一排序里无法区分 —— 必须看根目录。
判据 11：根目录 AGENTS.md / CLAUDE.md / .clinerules = 「单人 + agent」指纹。
"""
import json
import subprocess
import time

d = json.load(open("output/ghradar/out10.json", encoding="utf-8"))
d.sort(key=lambda c: (-(c.get("commits_7d") or 0), -(c.get("commits_30d") or 0)))

CODE_SIGNS = ("src", "tests", "pyproject.toml", "requirements.txt", "package.json",
              "Cargo.toml", "go.mod", "CMakeLists.txt", "configs", "Dockerfile",
              "Assets", "ProjectSettings", "scripts")
SITE_ONLY = ("index.html", ".nojekyll")


def tree(repo):
    for i in range(3):
        r = subprocess.run(["gh", "api", "repos/%s/contents/" % repo, "--jq",
                            "map(.name)|join(\" \")"],
                           capture_output=True, text=True, timeout=45)
        if r.returncode == 0:
            return r.stdout.strip()
        time.sleep(6 * (i + 1))
    return ""


print("%-52s %-10s %-16s %s" % ("repo", "lang", "flags", "root"))
rows = []
for c in d:
    names = tree(c["repo"])
    low = names.lower().split()
    flags = []
    for f in ("agents.md", "claude.md", ".clinerules", ".cursorrules"):
        if f in low:
            flags.append(f)
    if all(x in low for x in SITE_ONLY) and not any(
            x.lower() in low for x in CODE_SIGNS):
        flags.append("SITE-ONLY")
    c["root"] = names
    c["flags"] = flags
    rows.append(c)
    print("%-52s %-10s %-16s %s" % (
        c["repo"][:52], str(c.get("language"))[:10],
        ",".join(flags) or "-", names[:70]))
    time.sleep(0.6)

rep = [c for c in rows if (c.get("commits_30d") or 0) >= 5]
site_only = [c for c in rep if "SITE-ONLY" in c["flags"]]
print("\n报告级 %d，其中 纯静态站 %d: %s" % (
    len(rep), len(site_only), [c["repo"] for c in site_only]))
print("报告级 含 agent 指纹 %d: %s" % (
    len([c for c in rep if any("AGENTS" in f or "CLAUDE" in f or "clinerules" in f
                               for f in c["flags"])]),
    [(c["repo"], c["flags"]) for c in rep
     if any("AGENTS" in f or "CLAUDE" in f or "clinerules" in f for f in c["flags"])]))

json.dump(rows, open("output/ghradar/tree10.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

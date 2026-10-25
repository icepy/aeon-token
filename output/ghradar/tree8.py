#!/usr/bin/env python3
"""Round-8: agent fingerprint (AGENTS.md/CLAUDE.md/.clinerules) + root tree shape."""
import json
import subprocess
import time

OUTD = "output/ghradar"
out = json.load(open(OUTD + "/out8.json", encoding="utf-8"))
rep = [c for c in out if c.get("commits_30d") is not None and c["commits_30d"] >= 5
       and not c.get("stale") and not c.get("maybe_empty")]
rep.sort(key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"]))

AGENT_FILES = {"AGENTS.md", "CLAUDE.md", ".clinerules", "GEMINI.md"}


def tree(rid):
    r = subprocess.run(["gh", "api", "repos/%s/contents" % rid],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    try:
        return [x["path"] for x in json.loads(r.stdout)]
    except Exception:
        return None


print("检查报告级 %d 个仓的根目录形态与 agent 指纹" % len(rep))
print()
res = []
for c in rep:
    t = tree(c["repo"])
    time.sleep(0.15)
    if t is None:
        res.append((c, "ERR", []))
        continue
    low = {p.lower() for p in t}
    has_agent = bool(low & {a.lower() for a in AGENT_FILES})
    # 代码形态：有 src/ contracts/ crates/ train/ 等，或根目录有 >=2 个 .py/.rs/.ts
    code_dirs = {"src", "contracts", "crates", "train", "training", "models",
                 "inference", "scripts", "lib", "app", "packages", "solver",
                 "programs", "tests", "eval"}
    has_code_dir = bool(low & code_dirs)
    code_files = [p for p in low if p.endswith((".py", ".rs", ".ts", ".js", ".go",
                                                ".sol", ".cpp", ".c", ".cu", ".ipynb"))]
    # 页面形态：index.html + 无代码目录
    is_page = ("index.html" in low) and not has_code_dir and len(code_files) <= 1
    tag = "PAGE" if is_page else ("AGENT" if has_agent else "")
    res.append((c, tag, t))

print("%-52s %-5s %-6s %s" % ("repo", "7d", "标签", "根目录"))
print("-" * 110)
for c, tag, t in res:
    shown = ",".join(t[:9])
    print("%-52s %-5s %-6s %s" % (
        c["repo"][:52], c.get("commits_7d", "-"), tag or "-", shown[:60]))

agents = [c["repo"] for c, tag, _ in res if tag == "AGENT"]
pages = [c["repo"] for c, tag, _ in res if tag == "PAGE"]
errs = [c["repo"] for c, tag, _ in res if tag == "ERR"]
print()
print("agent 指纹 (AGENTS.md/CLAUDE.md/.clinerules): %d / %d = %.1f%% :: %s"
      % (len(agents), len(rep), 100.0 * len(agents) / len(rep), agents))
print("页面形态 (index.html 无代码目录): %d / %d :: %s" % (len(pages), len(rep), pages))
print("tree 取失败: %d :: %s" % (len(errs), errs))

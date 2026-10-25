#!/usr/bin/env python3
"""pages 规则误杀量化：被 selfname / pageword 丢掉的仓，有几个是真代码仓且活跃。"""
import json, subprocess, time

items = json.load(open("output/ghradar/wam5.json", encoding="utf-8"))

def kind(i):
    o, s = i["full_name"].split("/")
    sl = s.lower()
    if sl.endswith(".github.io") or sl.startswith("www."):
        return "github.io"
    if sl == o.lower():
        return "selfname"
    if any(sl.endswith(x) for x in ("-page", "-project", "-website", "projectpage")):
        return "pageword"
    return "keep"

dropped = [i for i in items if kind(i) != "keep"]
print("99 中被 pages 族规则丢弃 %d" % len(dropped))

def c30(rid):
    qs = "commits?since=2026-09-25T00:00:00Z&per_page=100"
    d = subprocess.run(["gh", "api", "repos/%s/%s" % (rid, qs)],
                       capture_output=True, text=True)
    if d.returncode != 0:
        return None
    try:
        v = json.loads(d.stdout)
        return len(v) if isinstance(v, list) else None
    except Exception:
        return None

print("\n%-46s %-10s %5s %6s %s" % ("repo", "规则", "★", "c30", "语言"))
print("-" * 92)
real = []
for i in dropped:
    d = subprocess.run(["gh", "api", "repos/" + i["full_name"]],
                       capture_output=True, text=True)
    lang, size = "-", 0
    if d.returncode == 0:
        j = json.loads(d.stdout)
        lang, size = (j.get("language") or "-"), (j.get("size") or 0)
    n = c30(i["full_name"]); time.sleep(1.2)
    print("%-46s %-10s %5d %6s %s" % (i["full_name"], kind(i),
          i["stargazers_count"], n if n is not None else "?", lang))
    if lang not in ("-", "HTML") and (n or 0) >= 5:
        real.append((i["full_name"], lang, size, n))

print("\n🔴 误杀（真代码 + ≥5 提交/30d）%d 个:" % len(real))
for r in real:
    print("   %-40s %-10s %6dKB c30=%d" % r)

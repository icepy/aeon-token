#!/usr/bin/env python3
"""报告级 89 个的人工卫生检查：列表仓 / 项目页 / 语义误中 / 农场残留。"""
import json

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
rep = [c for c in out if (c.get("commits_30d") or 0) >= 5
       and not c.get("stale") and not c.get("maybe_empty")]

LISTY = ("awesome", "bibliography", "list of", "curated", "paper list",
         "reading list", "collection of", "papers on", "recent papers")
print("== 疑似列表 / 综述仓（名字或 desc 含列表词）==")
for c in rep:
    s = (c["repo"] + " " + c["desc"]).lower()
    if any(k in s for k in LISTY):
        print("  c30=%-4d ★%-5d %-52s %s" % (c["commits_30d"], c["stars"], c["repo"], c["desc"][:70]))

print("\n== 报告级里非具身的语义误中候选 ==")
NONEMB = ("cs2", "counter-strike", "game", "financial", "finance", "分子",
          "molecule", "atomistic", "pde", "partial differential", "gui",
          "自駕", "driving", "campus map", "climate", "weather")
for c in rep:
    s = (c["repo"] + " " + c["desc"]).lower()
    if any(k in s for k in NONEMB):
        print("  c30=%-4d ★%-5d %-48s [%s] %s" % (c["commits_30d"], c["stars"],
              c["repo"], c["term"], c["desc"][:62]))

print("\n== 农场候选 owner 名下仍在报告级的仓（需逐个判）==")
for c in rep:
    if c.get("owner_repos"):
        print("  c30=%-4d ★%-5d owner=%-24s %-44s %s" % (c["commits_30d"], c["stars"],
              c["owner"], c["repo"], c["desc"][:50]))

print("\n== commits=100 撞顶（真值 >=100）==")
print("  " + " · ".join(c["repo"] for c in rep if c["commits_30d"] == 100))

print("\n报告级 %d · 10 月新建 %d · ★>=50 %d"
      % (len(rep), len([c for c in rep if c["created"] >= "2026-10-01"]),
         len([c for c in rep if c["stars"] >= 50])))

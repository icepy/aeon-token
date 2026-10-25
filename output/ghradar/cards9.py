#!/usr/bin/env python3
"""修正 scan.py 追加的预核验候选段落：scan 在核验前就写了报告级 20 条，
全量核验后实为 77。用 out9full.json 重建本节，并标出真正新增（vs 第八轮快照）。"""
import json

CARDS = "memory/github-candidates.md"
cur = json.load(open("output/ghradar/out9full.json", encoding="utf-8"))
prev = {c["repo"] for c in json.load(open("output/ghradar/out8.json",
                                          encoding="utf-8"))}
ver = [c for c in cur if c.get("commits_30d") is not None]
rep = sorted([c for c in ver if c["commits_30d"] >= 5 and not c.get("stale")],
             key=lambda c: (-(c.get("commits_7d") or 0), -c["commits_30d"],
                            -c["stars"]))

lines = open(CARDS, encoding="utf-8").read().split("\n")
keep = []
for l in lines:
    if l.startswith("## 2026-10-25 · github-radar（报告级 20）"):
        break
    keep.append(l)
while keep and not keep[-1].strip():
    keep.pop()

keep.append("")
keep.append("## 2026-10-25 · github-radar 第九轮（报告级 %d · 全量核验 230/234，"
            "真正新增 26）" % len(rep))
keep.append("")
keep.append("> 60 天窗 · 18 词 · 原始 3,461 → 幸存 234。核验 230/234 = 98.3%。"
            "★ 只测发布时传播，commits 才测「现在还在写」。"
            "标 `[新]` = 不在第八轮快照内（第八轮 dry-run 未落 seen，"
            "本轮 169/234 是重复回捞）。")
keep.append("")
for c in rep:
    tag = "" if c["repo"] in prev else " `[新]`"
    keep.append("- [%s](%s) ★%d · 30d=%s 7d=%s%s · `%s`%s · %s"
                % (c["repo"], c["url"], c["stars"],
                   "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
                   "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
                   " [爆完即停]" if c.get("burst_only") else "",
                   c["term"], tag, c["desc"][:100]))

open(CARDS, "w", encoding="utf-8").write("\n".join(keep) + "\n")
print("rewrote %s: %d report-level entries, %d new"
      % (CARDS, len(rep), sum(1 for c in rep if c["repo"] not in prev)))

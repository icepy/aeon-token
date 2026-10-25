#!/usr/bin/env python3
"""读 output/ghradar/out.json，按方向词分组出报告级仓库，并做跨轮对照。

不做判断，只做归类：仓库 / 一句话 / 链接 / star / 30 天提交数。
"""
import json, os
from collections import defaultdict, Counter

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))

rep = [c for c in out
       if c.get("commits_30d") is not None and c["commits_30d"] >= 5
       and not c.get("stale") and not c.get("maybe_empty")
       and not c.get("farm_hit")]
rep.sort(key=lambda c: (-c["commits_30d"], -c["stars"]))

by_term = defaultdict(list)
for c in rep:
    by_term[c["term"]].append(c)

print("=== 报告级 %d，按方向词 ===" % len(rep))
for term, cs in sorted(by_term.items(), key=lambda kv: -len(kv[1])):
    print("\n## %s  (%d)" % (term, len(cs)))
    for c in cs:
        print("- %s ★%d · %dd提交 · %s · %s"
              % (c["repo"], c["stars"], c["commits_30d"], c["created"],
                 c["desc"][:110]))
        print("  %s" % c["url"])

print("\n=== 本轮最活跃 15（跨词）===")
for c in rep[:15]:
    print("%-46s ★%-5d %3dd  [%s] %s"
          % (c["repo"], c["stars"], c["commits_30d"], c["term"], c["created"]))

# 加密侧单列（顺带通道）
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
cr = [c for c in out if c["term"] in CRYPTO]
cr_rep = [c for c in rep if c["term"] in CRYPTO]
print("\n=== 加密侧：命中 %d，报告级 %d ===" % (len(cr), len(cr_rep)))
for c in sorted(cr, key=lambda x: -(x.get("commits_30d") or -1))[:20]:
    print("%-46s ★%-4d commits30d=%s [%s] %s"
          % (c["repo"], c["stars"], c.get("commits_30d"), c["term"],
             (c.get("verify") or "")))

# 10 月新仓（窗口最关键的一段）
oct_new = [c for c in rep if c["created"] >= "2026-10-01"]
print("\n=== 10 月新建且报告级: %d ===" % len(oct_new))
for c in oct_new[:25]:
    print("%-46s ★%-4d %3dd [%s] %s"
          % (c["repo"], c["stars"], c["commits_30d"], c["term"], c["created"]))

# star vs commits 背离（star 在骗人的正向面）
hi_star = [c for c in out if c["stars"] >= 100]
print("\n=== ★>=100 的仓: %d，其中 30d<5 提交 %d ===" % (
    len(hi_star), sum(1 for c in hi_star
                      if (c.get("commits_30d") or 0) < 5)))
for c in sorted(hi_star, key=lambda x: -x["stars"])[:15]:
    print("%-46s ★%-5d commits30d=%s [%s]"
          % (c["repo"], c["stars"], c.get("commits_30d"), c["term"]))

# WAM 簇（沿用上轮口径）
wam = [c for c in out if "wam" in c["repo"].lower()
       or "world action model" in c["desc"].lower()
       or "world-action model" in c["desc"].lower()
       or c["term"] == "world action model"]
print("\n=== WAM 簇: %d 仓 / %d owner ===" % (len(wam), len({c["owner"] for c in wam})))
alive = [c for c in wam if (c.get("commits_30d") or 0) >= 5]
print("其中报告级 %d" % len(alive))
for c in sorted(alive, key=lambda x: -x["commits_30d"])[:15]:
    print("%-46s ★%-4d %3dd %s" % (c["repo"], c["stars"], c["commits_30d"], c["created"]))

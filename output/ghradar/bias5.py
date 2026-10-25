#!/usr/bin/env python3
"""核验覆盖率偏差量化：★<5 的仓只核验了 8.9%，但其中 27.7% 是活的。"""
import json
from collections import Counter

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
low = [c for c in out if c["stars"] < 5]
lv = [c for c in low if c.get("commits_30d") is not None]
lu = [c for c in low if c.get("commits_30d") is None]
alive = [c for c in lv if c["commits_30d"] >= 5]

print("★<5 幸存 %d · 已核验 %d (%.1f%%) · 未核验 %d"
      % (len(low), len(lv), 100.0 * len(lv) / len(low), len(lu)))
print("已核验里 >=5 提交: %d (%.1f%%)" % (len(alive), 100.0 * len(alive) / len(lv)))

rate = len(alive) / len(lv)
print("\n外推：若未核验的 %d 个同率，还有 ~%d 个活仓没被看见"
      % (len(lu), round(rate * len(lu))))
print("当前报告级 %d → 潜在 ~%d（≈ %.1f 倍）"
      % (len([c for c in out if (c.get("commits_30d") or 0) >= 5]),
         len([c for c in out if (c.get("commits_30d") or 0) >= 5]) + round(rate * len(lu)),
         (len([c for c in out if (c.get("commits_30d") or 0) >= 5]) + rate * len(lu))
         / len([c for c in out if (c.get("commits_30d") or 0) >= 5])))

print("\n⚠️ 但已核验的 ★<5 是按「创建最新」挑的，有偏：")
print("  已核验 created 中位 %s · 未核验中位 %s"
      % (sorted(c["created"] for c in lv)[len(lv) // 2],
         sorted(c["created"] for c in lu)[len(lu) // 2]))
print("  已核验 10 月新建 %d/%d · 未核验 10 月新建 %d/%d"
      % (len([c for c in lv if c["created"] >= "2026-10-01"]), len(lv),
         len([c for c in lu if c["created"] >= "2026-10-01"]), len(lu)))
print("\n  → 外推是上界，不是点估计：新仓更容易还在写代码。")

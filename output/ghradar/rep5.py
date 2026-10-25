#!/usr/bin/env python3
"""第 5 轮可读面：报告级分组 + 高信号分层 + WAM 簇复核。"""
import json, re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
print("幸存 %d" % len(out))

def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= 5
            and not c.get("stale") and not c.get("maybe_empty"))

rep = [c for c in out if reportable(c)]
print("报告级 %d\n" % len(rep))

# ── 按词分组 ──
by = defaultdict(list)
for c in rep:
    for t in c.get("terms") or [c["term"]]:
        by[t].append(c)
print("== 报告级按词 ==")
for t, v in sorted(by.items(), key=lambda x: -len(x[1])):
    print("  %-26s %d" % (t, len(v)))

# ── 全局 top（按提交，撞顶的 100 单列）──
print("\n== 报告级按 30d 提交 top40 ==")
for c in sorted(rep, key=lambda x: (-x["commits_30d"], -x["stars"]))[:40]:
    cap = " (≥100)" if c["commits_30d"] == 100 else ""
    print("  c30=%-4d%s ★%-5d %-10s %-48s %s"
          % (c["commits_30d"], cap, c["stars"], c["created"], c["repo"], c["desc"][:70]))

# ── 10 月新建 ──
YOUNG = "2026-10-01"
print("\n== 10 月新建的报告级 ==")
sel = sorted([c for c in rep if c["created"] >= YOUNG],
             key=lambda x: (-x["commits_30d"], -x["stars"]))
print("%d 个" % len(sel))
for c in sel:
    print("  c30=%-4d ★%-5d %-10s %-48s [%s]" % (c["commits_30d"], c["stars"],
          c["created"], c["repo"], c["term"]))

# ── star 领先代码 ──
print("\n== ★>=50 但 30d 提交 <5（star 在骗人）==")
lazy = [c for c in out if c["stars"] >= 50 and not reportable(c)]
for c in sorted(lazy, key=lambda x: -x["stars"])[:25]:
    st = c.get("commits_30d")
    print("  ★%-5d c30=%-5s %-48s" % (c["stars"], st if st is not None else "?",
                                       c["repo"]))

# ── 加密侧全量 ──
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
cr = [c for c in out if c["term"] in CRYPTO]
print("\n== 加密侧（6 词）全量 %d，报告级 %d ==" % (len(cr), len([c for c in cr if reportable(c)])))
print("  ★0 占 %d" % len([c for c in cr if c["stars"] == 0]))
for c in sorted([c for c in cr if (c.get("commits_30d") or 0) > 0],
                key=lambda x: -x["commits_30d"])[:20]:
    print("  c30=%-4d ★%-4d %-10s %-44s [%s] %s"
          % (c["commits_30d"], c["stars"], c["created"], c["repo"], c["term"], c["desc"][:50]))

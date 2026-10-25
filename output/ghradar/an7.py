#!/usr/bin/env python3
"""第七轮分析：全量核验后的真实报告级、7 天活跃度、以及抽样偏差的量化。"""
import json
from collections import Counter
from datetime import datetime

full = json.load(open("output/ghradar/full7.json", encoding="utf-8"))
old = {c["repo"]: c for c in json.load(open("output/ghradar/out6.json", encoding="utf-8"))}

ok = [c for c in full if c.get("q_status") == "ok"]
bad = [c for c in full if c.get("q_status") != "ok"]

print("=" * 70)
print("全量核验 %d 仓：ok=%d  失败=%d" % (len(full), len(ok), len(bad)))
if bad:
    print("  失败原因: " + " · ".join("%s=%d" % kv for kv in
          Counter(c["q_status"] for c in bad).most_common()))

# ── 报告级（≥5 提交/30d）全量 ──
rep = [c for c in ok if c["commits_30d"] >= 5]
print("\n≥5 提交/30d（报告级）: %d / %d = %.1f%%"
      % (len(rep), len(ok), 100.0 * len(rep) / len(ok)))

# ── 活跃（≥1 提交/7d）──
act = [c for c in ok if c.get("commits_7d", 0) >= 1]
print("≥1 提交/7d（现在还在写）: %d / %d = %.1f%%"
      % (len(act), len(ok), 100.0 * len(act) / len(ok)))

# ── 爆完即停（只在报告级里算：30d≥5 且 7d=0）──
burst = [c for c in rep if c.get("commits_7d", 0) == 0]
print("爆完即停（30d≥5 但 7d=0）: %d / %d = %.1f%%"
      % (len(burst), len(rep), 100.0 * len(burst) / max(len(rep), 1)))
stale = [c for c in ok if c.get("stale")]
print("30d 零提交（star 在骗人）: %d" % len(stale))

# ── 30d 分布 ──
def bucket(n):
    if n == 0: return "0"
    if n < 5: return "1-4"
    if n < 10: return "5-9"
    if n < 20: return "10-19"
    if n < 50: return "20-49"
    if n < 100: return "50-99"
    return "100(上限)"
print("\n30d 提交分布: " + " · ".join(
    "%s=%d" % (k, v) for k, v in
    Counter(bucket(c["commits_30d"]) for c in ok).most_common()))

# ── 抽样偏差：第六轮核验过的 281 个 vs 本轮全量 ──
print("\n" + "=" * 70)
print("抽样偏差量化（第六轮只验了 20%，本轮补齐）")
v6 = [c for c in full if c["repo"] in old and old[c["repo"]].get("commits_30d") is not None]
print("第六轮已验: %d" % len(v6))
if v6:
    r6 = [c for c in v6 if c["commits_30d"] >= 5]
    print("  其中 ≥5 提交: %d (%.1f%%)" % (len(r6), 100.0 * len(r6) / len(v6)))
nv = [c for c in ok if c["repo"] not in {x["repo"] for x in v6}]
print("第六轮未验（本轮首次）: %d" % len(nv))
if nv:
    rn = [c for c in nv if c["commits_30d"] >= 5]
    print("  其中 ≥5 提交: %d (%.1f%%)" % (len(rn), 100.0 * len(rn) / len(nv)))
    an = [c for c in nv if c.get("commits_7d", 0) >= 1]
    print("  其中 7d 活跃: %d (%.1f%%)" % (len(an), 100.0 * len(an) / len(nv)))
    print("\n  ★<5 且被前六轮漏掉的活仓（≥5 提交/30d）TOP 25:")
    for c in sorted(rn, key=lambda c: -c.get("commits_7d", 0))[:25]:
        print("    %s [%s] ★%d 30d=%d 7d=%d %s"
              % (c["repo"], c["term"], c["stars"], c["commits_30d"],
                 c.get("commits_7d", -1), c.get("lang", "")))

# ── 按域拆分 ──
print("\n" + "=" * 70)
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
def dom(c):
    return "crypto" if c["term"] in CRYPTO else "robot"
for d in ("robot", "crypto"):
    xs = [c for c in ok if dom(c) == d]
    if not xs: continue
    r = [c for c in xs if c["commits_30d"] >= 5]
    a = [c for c in xs if c.get("commits_7d", 0) >= 1]
    b = [c for c in xs if c.get("burst_only")]
    print("\n[%s] 核验 %d | ≥5提交 %d (%.1f%%) | 7d活跃 %d (%.1f%%) | 爆完即停 %d"
          % (d, len(xs), len(r), 100.0 * len(r) / len(xs),
             len(a), 100.0 * len(a) / len(xs), len(b)))

print("\n[robot] 7d 活跃 TOP 30:")
for c in sorted([c for c in ok if dom(c) == "robot" and c.get("commits_7d", 0) >= 1],
                key=lambda c: -c["commits_7d"])[:30]:
    print("  %s ★%d 30d=%d 7d=%d [%s] %s"
          % (c["repo"], c["stars"], c["commits_30d"], c["commits_7d"],
             c["term"], c.get("lang", "")))

print("\n[crypto] 7d 活跃全部:")
for c in sorted([c for c in ok if dom(c) == "crypto" and c.get("commits_7d", 0) >= 1],
                key=lambda c: -c["commits_7d"]):
    print("  %s ★%d 30d=%d 7d=%d [%s] %s"
          % (c["repo"], c["stars"], c["commits_30d"], c["commits_7d"],
             c["term"], c.get("lang", "")))

print("\n[crypto] ≥5 提交/30d 但 7d=0（爆完即停）:")
for c in sorted([c for c in ok if dom(c) == "crypto" and c["commits_30d"] >= 5
                 and c.get("commits_7d", 0) == 0], key=lambda c: -c["commits_30d"]):
    print("  %s ★%d 30d=%d 7d=0 [%s]"
          % (c["repo"], c["stars"], c["commits_30d"], c["term"]))

# ── 撞 per_page 上限 ──
cap = [c["repo"] for c in ok if c["commits_30d"] == 100]
print("\ncommits_30d=100（per_page 上限，实为 ≥100）%d 个: %s"
      % (len(cap), " · ".join(cap)))
cap7 = [c["repo"] for c in ok if c.get("commits_7d") == 100]
if cap7:
    print("commits_7d=100（上限）%d 个: %s" % (len(cap7), " · ".join(cap7)))

#!/usr/bin/env python3
"""Regenerate audit8.log from the final out8.json (post full-verification)."""
import json
from collections import Counter

OUTD = "output/ghradar"
out = json.load(open(OUTD + "/out8.json", encoding="utf-8"))
t = json.load(open(OUTD + "/terms8.json", encoding="utf-8"))
TERMS = t["terms"]
raw_term, new_term, cov, totals = (t["raw_term"], t["new_term"], t["cov"],
                                   t["total_by_term"])

ver = [c for c in out if c.get("commits_30d") is not None]
rep = sorted([c for c in ver if c["commits_30d"] >= 5 and not c.get("stale")
              and not c.get("maybe_empty")],
             key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"], -c["stars"]))

truly_zero = [x for x in TERMS if raw_term.get(x, 0) == 0]
saturated = [x for x in TERMS if raw_term.get(x, 0) > 0 and new_term.get(x, 0) == 0]
with_new = [x for x in TERMS if new_term.get(x, 0) > 0]

L = ["扫 %d 词 × %d 窗 × %d 页 | 原始 %d | 幸存 %d | 报告级 %d"
     % (len(TERMS), 3, t["maxpage"], sum(raw_term.values()), len(out), len(rep)),
     "核验 %d / %d = %.1f%%（全量，非抽样）· 未核验 %d · 空仓(409) %d"
     % (len(ver), len(out), 100.0 * len(ver) / len(out),
        len([c for c in out if c.get("unverified")]),
        len([c for c in out if c.get("maybe_empty")])),
     "词表四分类 —— 查询失败 0 / 真零 %d / 全已见(饱和) %d / 有新增 %d"
     % (len(truly_zero), len(saturated), len(with_new))]
if truly_zero:
    L.append("⚠️ 真零命中（total=0，可考虑删词）: " + " · ".join(truly_zero))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d/total=%d)" % (x, raw_term[x], totals.get(x, 0)) for x in saturated))
L.append("词表返回/新收: " + " · ".join(
    "%s=%d/%d" % (x, raw_term.get(x, 0), new_term.get(x, 0)) for x in
    sorted(TERMS, key=lambda y: -raw_term.get(y, 0))))
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % kv for kv in low.items()))

stale = [c["repo"] for c in ver if c.get("stale")]
burst = [c["repo"] for c in ver if c.get("burst_only")]
nol = [c["repo"] for c in ver if c.get("no_lang")]
L.append("⚠️ 30 天零提交（star 在骗人）%d: %s" % (len(stale), " · ".join(stale[:20])))
L.append("⚠️ 爆完即停（30d 有量 / 7d 归零）%d: %s" % (len(burst), " · ".join(burst[:20])))
L.append("⚠️ 无 language 字段（疑似非代码仓）%d: %s" % (len(nol), " · ".join(nol[:20])))
L.append("ℹ️ 撞 30d per_page 上限（≥100，是下限不是真值）: %s"
         % (" · ".join(c["repo"] for c in ver if c.get("commits_30d_ge")) or "无"))
L.append("⚠️ 共享脚手架簇 jepa-world-model-from-scratch ×8 owner（同 desc + 同 commit msg）")
for c in rep:
    L.append("  %s ★%d 30d=%s%s 7d=%s [%s] %s" % (
        c["repo"], c["stars"],
        "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
        " [爆完即停]" if c.get("burst_only") else "",
        "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
        c["term"], c["created"]))
open(OUTD + "/audit8.log", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L[:12]))
print("... (%d 行写入 audit8.log)" % len(L))

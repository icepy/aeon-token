#!/usr/bin/env python3
"""本轮数据卫生 + 结构分析（只统计，不判断）。"""
import json, re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))

# ── 1. 上限截断 ──
capped = [c for c in out if c.get("commits_30d") == 100]
print("== 提交数撞 per_page=100 上限: %d 个（实为 ≥100，不可当精确值）==" % len(capped))
for c in capped:
    print("   %-46s ★%-4d [%s]" % (c["repo"], c["stars"], c["term"]))

# ── 2. 语义误中：awesome/论文列表/非代码 ──
LIST_PAT = re.compile(r"awesome|curated|bibliography|papers on|reading list|"
                      r"project page|recent papers|collection of", re.I)
NOTCODE = re.compile(r"unofficial 3d map|no rl / vla / world model", re.I)
lists = []
for c in out:
    d = c["desc"]
    name = c["repo"].split("/")[-1]
    if LIST_PAT.search(d) or LIST_PAT.search(name) or NOTCODE.search(d):
        lists.append(c)
print("\n== 语义误中（列表类/非代码），%d 个 ==" % len(lists))
for c in sorted(lists, key=lambda x: -(x.get("commits_30d") or 0)):
    print("   %-46s ★%-4d %sd commits=%s" % (
        c["repo"], c["stars"],
        "列表" if LIST_PAT.search(c["desc"]) or LIST_PAT.search(c["repo"].split("/")[-1]) else "非码",
        c.get("commits_30d")))

bad = {c["repo"] for c in lists}

def ok(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= 5
            and not c.get("stale") and not c.get("maybe_empty")
            and not c.get("farm_hit") and c["repo"] not in bad)

rep = sorted([c for c in out if ok(c)],
             key=lambda c: (-c["commits_30d"], -c["stars"]))
print("\n== 剔除后报告级: %d（原 96）==" % len(rep))

# ── 3. 严格 WAM 周曲线 ──
now = datetime.now(timezone.utc)
def iso_w(d):
    return datetime.strptime(d, "%Y-%m-%d").isocalendar()[1]

strict = [c for c in out if c["term"] == "world action model"]
loose = [c for c in out
         if c["term"] == "world action model"
         or re.search(r"wam", c["repo"].split("/")[-1], re.I)
         or re.search(r"world[- ]action model", c["desc"], re.I)]
print("\n== WAM：严格词表 %d 仓 / %d owner ｜ 放宽(WAM in name 或 desc) %d 仓 / %d owner ==" % (
    len(strict), len({c['owner'] for c in strict}),
    len(loose), len({c['owner'] for c in loose})))
wk = Counter(iso_w(c["created"]) for c in strict if c["created"] >= "2026-08-26")
print("   严格词表按 ISO 周:", " · ".join("W%d=%d" % (k, wk[k]) for k in sorted(wk)))
oct_strict = [c for c in strict if c["created"] >= "2026-10-01"]
oct_alive = [c for c in oct_strict if ok(c)]
print("   10 月新建 %d，其中报告级 %d" % (len(oct_strict), len(oct_alive)))

# ── 4. star vs commits 背离（★>=100）──
hs = [c for c in out if c["stars"] >= 100]
print("\n== ★>=100: %d 仓｜30d<5 提交 %d 个（%.0f%%）｜30d=0 %d 个 ==" % (
    len(hs), sum(1 for c in hs if (c.get("commits_30d") or 0) < 5),
    100.0 * sum(1 for c in hs if (c.get("commits_30d") or 0) < 5) / max(len(hs), 1),
    sum(1 for c in hs if c.get("commits_30d") == 0)))

# ── 5. 加密侧 ──
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
cr = [c for c in out if c["term"] in CRYPTO]
print("\n== 加密侧：命中 %d｜★0 占 %d｜★>=10 %d｜报告级 %d ==" % (
    len(cr), sum(1 for c in cr if c["stars"] == 0),
    sum(1 for c in cr if c["stars"] >= 10), len([c for c in cr if ok(c)])))
for c in sorted(cr, key=lambda x: (-(x.get("commits_30d") or -1), -x["stars"]))[:14]:
    print("   %-44s ★%-3d commits=%s %s" % (
        c["repo"], c["stars"], c.get("commits_30d"),
        "已验" if c.get("commits_30d") is not None else "未验(非核验桶)"))

# ── 6. 按创建周的报告级曲线（机器人侧整体）──
rb = [c for c in rep if c["term"] not in CRYPTO]
wk2 = Counter(iso_w(c["created"]) for c in rb)
print("\n== 报告级（机器人侧）%d 仓，按创建 ISO 周 ==" % len(rb))
print("   " + " · ".join("W%d=%d" % (k, wk2[k]) for k in sorted(wk2)))

# ── 7. 分方向词最终计数 ──
print("\n== 最终报告级，按词 ==")
for t, n in Counter(c["term"] for c in rep).most_common():
    print("   %-24s %d" % (t, n))

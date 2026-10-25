#!/usr/bin/env python3
"""Round-8 deep checks: vla/jepa overlap, semantic mis-hits, same-name clusters."""
import json
import subprocess
import time
from collections import Counter, defaultdict

OUTD = "output/ghradar"
out = json.load(open(OUTD + "/out8.json", encoding="utf-8"))
seen = json.load(open("memory/github-seen.json", encoding="utf-8"))

print("=" * 72)
print("F. vla 缩写词 vs 全称：是重叠还是互补？")
print("=" * 72)
# 60d total for each form (already measured): vla=3696, vision language action=205
print("60d 总仓数:  \"vla\"=3696  |  \"vision language action\"=205")
vla_full = [c for c in out if c["term"] == "vision language action"]
print("幸存 %d（全部为新收，round 7 的 vla 结果已在 seen 里）" % len(vla_full))
print("=> 两个口径高度不重叠：全称 205 个里 138 个是 `vla` 从没抓到过的")
print("   原因：仓库名常是 smolvla / InfraVLA / TernaVLA 这种合成词，")
print("   描述里写全称但从不写独立的 vla token；GitHub 搜索按词切分，两边打不中对方。")

print()
print("=" * 72)
print("G. jepa 全称口径的代价 —— 缩写才是术语本身")
print("=" * 72)
jepa_full = [c for c in out if c["term"] == "joint embedding predictive"]
print("本轮 \"joint embedding predictive\" 60d total=35，幸存 %d" % len(jepa_full))
# 从 seen 里数 round 1-7 抓到的 jepa 仓（never deleted, 但 seen 只有名字）
# 直接查当前 jepa 口径总量
import urllib.parse
q = '"jepa" in:name,description created:2026-08-26..2026-10-25 fork:false stars:>=0'
r = subprocess.run(["gh", "api", "search/repositories?" +
                    urllib.parse.urlencode({"q": q, "per_page": "1"})],
                   capture_output=True, text=True)
tot = json.loads(r.stdout).get("total_count") if r.returncode == 0 else "?"
print("对照 \"jepa\" 60d total=%s" % tot)
print("=> 全称口径丢掉约 %s/%s 的仓（%.1f%% 损失）。JEPA 是 LeCun 家族的固定缩写，"
      % ("?" if tot == "?" else int(tot) - 35, tot,
         100.0 * (int(tot) - 35) / int(tot) if tot not in ("?", 0) else 0))
print("   仓库名一律写成 jepa-*，几乎没人把全称写进 name/description。")
print("=> 结论：vla 该换成全称（污染 22%→1.4% 且产出变多）；")
print("   jepa 必须保留缩写 + NEG，换全称等于退订 96% 的该赛道。")

print()
print("=" * 72)
print("H. 语义误中（高提交 ≠ 代码仓）—— 报告级里的可疑仓")
print("=" * 72)
sus = [c for c in out if c.get("commits_30d") is not None and c["commits_30d"] >= 5
       and not c.get("stale")]
SUSPECT = ["page", "website", "site", "awesome", "blog", "docs", "portfolio",
           "homepage", "demo", "landing"]
hits = [c for c in sus if any(s in c["repo"].lower() for s in SUSPECT)]
for c in hits:
    print("  %-50s ★%-4d 30d=%-4s lang=%-10s %s"
          % (c["repo"][:50], c["stars"], c["commits_30d"], c["language"], c["desc"][:60]))
print("  共 %d 个可疑" % len(hits))

print()
print("=" * 72)
print("I. 同名簇（不同 owner 但仓库名同构）—— 农场/课程的第二形态")
print("=" * 72)
byname = defaultdict(list)
for c in out:
    byname[c["repo"].split("/")[-1].lower()].append(c)
dups = {k: v for k, v in byname.items() if len(v) >= 2}
for k, v in sorted(dups.items(), key=lambda x: -len(x[1])):
    print("  [%d] %s" % (len(v), k))
    for c in v:
        print("       %-46s ★%-3d 30d=%-4s 7d=%-4s %s"
              % (c["repo"][:46], c["stars"], c.get("commits_30d", "-"),
                 c.get("commits_7d", "-"), c["created"]))

print()
print("=" * 72)
print("J. EXCL 只查 description 不查 name —— 漏洞实锤")
print("=" * 72)
EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]
leak = [c for c in out if any(x in c["repo"].lower().split("/")[-1] for x in EXCL)
        and not any(x in c["desc"].lower() for x in EXCL)]
for c in leak:
    print("  %-52s 30d=%-4s  名含禁词但 desc 没有 → 漏网"
          % (c["repo"][:52], c.get("commits_30d", "-")))
print("  共 %d 个漏网" % len(leak))

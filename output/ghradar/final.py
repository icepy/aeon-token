#!/usr/bin/env python3
"""最终可读面：10 月新建 + 提交>=10（真在写）+ 剔噪。"""
import json
from datetime import datetime

res = json.load(open("output/ghradar/highsig.json", encoding="utf-8"))
print("高信号集 %d 个" % len(res))

# 逐条人工判过噪的（term 命中但语义不符）
NOISE = {
    "pengqianhan/campus-world-model",      # 奥克兰大学 3D 校园地图
    "Sarim-MBZUAI/advsim2real",            # web agent 提示注入，非机器人 sim2real
    "fin-ai-lab/tfwm",                     # 金融世界模型（不是具身）
}
YOUNG = "2026-10-01"
print("\n== 10 月新建 + 30d 提交>=10（真在写的工程仓）==")
sel = [c for c in res if c["created"] >= YOUNG and isinstance(c["c30"], int)
       and c["c30"] >= 10 and c["repo"] not in NOISE]
sel.sort(key=lambda c: -c["c30"])
print("%d 个\n" % len(sel))
for c in sel:
    print("  c30=%-4s ★%-5d %-24s %-50s %s"
          % (c["c30"], c["stars"], c["created"], c["repo"], c["desc"][:88]))

print("\n== 10月新建 + ★>=20 但提交<10（star 领先代码）==")
lazy = [c for c in res if c["created"] >= YOUNG and c["stars"] >= 20
        and isinstance(c["c30"], int) and c["c30"] < 10]
for c in sorted(lazy, key=lambda x: -x["stars"]):
    print("  ★%-5d c30=%-3s %-48s %s" % (c["stars"], c["c30"], c["repo"], c["desc"][:70]))

print("\n== 提交数被 per_page=100 截断的仓（c30==100，真值 >=100）==")
for c in [x for x in res if x["c30"] == 100]:
    print("  ★%-5d %-50s %s" % (c["stars"], c["repo"], c["desc"][:70]))

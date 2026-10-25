#!/usr/bin/env python3
"""报告级 89 的人工卫生剔除后净数 + 具身侧分层。"""
import json
from collections import Counter
from datetime import datetime

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
rep = [c for c in out if (c.get("commits_30d") or 0) >= 5
       and not c.get("stale") and not c.get("maybe_empty")]

LISTS = {"YanjieZe/agent-real2sim2real", "ShuaixinHuang/awesome-robotics",
         "futakw/Awesome-Physical-AI-Safety", "benchflow-ai/awesome-embodied-agents"}
NONEMB = {"cooperwooley/diamond-cs2-v2", "khelverskovp/atom-jepa",
          "Tanpig-X/PDE-JEPA"}
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}

clean = [c for c in rep if c["repo"] not in LISTS and c["repo"] not in NONEMB]
print("报告级 %d → 净 %d（剔列表 %d / 非具身 %d）"
      % (len(rep), len(clean),
         len([c for c in rep if c["repo"] in LISTS]),
         len([c for c in rep if c["repo"] in NONEMB])))

emb = [c for c in clean if c["term"] not in CRYPTO]
print("净集里具身侧 %d · 加密侧 %d" % (len(emb), len(clean) - len(emb)))

def wk(d):
    y, m, dd = map(int, d.split("-"))
    return "W%02d" % datetime(y, m, dd).isocalendar()[1]

w = Counter(wk(c["created"]) for c in emb)
print("\n净具身侧按创建周: " + " · ".join("%s=%d" % (k, w[k]) for k in sorted(w)))
print("owner 数 %d · 10 月新建 %d" % (len(set(c["owner"] for c in emb)),
                                    len([c for c in emb if c["created"] >= "2026-10-01"])))
print("\ncommits 分层: >=50 %d · 20-49 %d · 5-19 %d"
      % (len([c for c in emb if c["commits_30d"] >= 50]),
         len([c for c in emb if 20 <= c["commits_30d"] < 50]),
         len([c for c in emb if 5 <= c["commits_30d"] < 20])))

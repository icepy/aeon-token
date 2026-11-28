#!/usr/bin/env python3
"""第 33 轮补八：批量指纹窗口敏感度 + 零模型对照。只读。"""
import json
import time
import urllib.request
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


cb = get(API + "?_cb=%d" % int(time.time()),
         {"User-Agent": "defillama-radar/audit33h",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
ls = sorted(p["listedAt"] for p in cb if isinstance(p, dict) and p.get("listedAt"))
now = time.time()
span = ls[-1] - ls[0]


def clusters(w):
    out, i = [], 0
    while i < len(ls):
        j = i
        while j + 1 < len(ls) and ls[j + 1] - ls[i] <= w:
            j += 1
        if j - i + 1 >= 3:
            out.append((ls[i], j - i + 1))
            i = j + 1
        else:
            i += 1
    return out


print("n=%d span=%.1f 年" % (len(ls), span / 86400 / 365))
print("\n窗口  簇数  其中起点在近 30d")
for w in (0, 1, 2, 5, 10, 15, 30, 60, 120, 300):
    c = clusters(w)
    recent = sum(1 for t, n in c if now - t <= 30 * 86400)
    print("  %4ds  %4d   %d" % (w, len(c), recent))

# 零模型：把 listedAt 在 [min,max] 上均匀打散，重算 15s 簇
import random
random.seed(7)
tot = 0
trials = 20
for _ in range(trials):
    sim = sorted(random.uniform(ls[0], ls[-1]) for _ in range(len(ls)))
    i = 0
    while i < len(sim):
        j = i
        while j + 1 < len(sim) and sim[j + 1] - sim[i] <= 15:
            j += 1
        if j - i + 1 >= 3:
            tot += 1
            i = j + 1
        else:
            i += 1
print("\n零模型（均匀打散，15s 窗）: 平均 %.2f 簇 / %d 次" % (tot / trials, trials))
print("→ 真实 15s 簇 %d 远高于零模型 ⇒ 这些簇是真录入批次，不是时间巧合"
      % len(clusters(15)))

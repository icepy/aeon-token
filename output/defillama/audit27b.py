#!/usr/bin/env python3
"""第 27 轮补充审计：listedAt 逐日直方图 + 全量 TVL 外部曲线对照。只读。"""
import json
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


cb = get(API + "?_cb=%d" % int(time.time()),
         {"User-Agent": "defillama-radar/audit27b",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})

now = time.time()
print("== listedAt 逐日（UTC，近 14 日）==")
day = Counter()
for p in cb:
    if isinstance(p, dict) and p.get("listedAt"):
        d = datetime.fromtimestamp(p["listedAt"], timezone.utc).strftime("%m-%d")
        day[d] += 1
for d in sorted(day)[-14:]:
    print("  %s n=%d" % (d, day[d]))

print("\n== 窗口滑移核对 ==")
for w in (7, 8, 30):
    print("  近 %dd: %d" % (w, sum(1 for p in cb if isinstance(p, dict)
                                 and p.get("listedAt") and now - p["listedAt"] <= w * 86400)))

print("\n== 全量 TVL 外部曲线 ==")
try:
    h = get("https://api.llama.fi/v2/historicalChainTvl",
            {"User-Agent": "defillama-radar/audit27b"})
    for row in h[-6:]:
        print("  %s  $%.2fB" % (datetime.fromtimestamp(row["date"], timezone.utc)
                                .strftime("%Y-%m-%d"), row["tvl"] / 1e9))
    if len(h) >= 2:
        a, b = h[-2]["tvl"], h[-1]["tvl"]
        print("  最近一日 %.2f%%" % (100.0 * (b / a - 1)))
except Exception as ex:
    print("  失败: %s" % str(ex)[:120])

print("\n== 空链 ⟺ dummy 两向 ==")
empty = [p for p in cb if isinstance(p, dict) and not (p.get("chains") or []) and p.get("id")]
dummy = [p for p in cb if isinstance(p, dict) and p.get("module") == "dummy.js"]
se, sd = {str(p.get("id")) for p in empty}, {str(p.get("id")) for p in dummy}
print("空链 %d · dummy %d · 空链\\dummy %s · dummy\\空链 %s"
      % (len(se), len(sd), sorted(se - sd), sorted(sd - se)))
print("空链中 tvl 非空 %d" % sum(1 for p in empty if p.get("tvl")))

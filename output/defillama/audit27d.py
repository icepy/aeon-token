#!/usr/bin/env python3
"""第 27 轮补三：两源 delta 符号分歧核对 + 30d 滚出核对。只读。"""
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
         {"User-Agent": "defillama-radar/audit27d",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
now = time.time()
print("now_utc=%s" % datetime.fromtimestamp(now, timezone.utc).isoformat())

print("\n== 30d 滚出核对 ==")
day = Counter(int((now - p["listedAt"]) // 86400)
              for p in cb if isinstance(p, dict) and p.get("listedAt"))
for d in (29, 30, 31, 32):
    print("  第 %d 天前 n=%d" % (d, day[d]))
print("  7d 滚出桶(第 7 天前) n=%d" % day[7])

print("\n== 两源 TVL ==")
tot = sum(p.get("tvl") or 0 for p in cb if isinstance(p, dict))
print("/protocols 求和 $%.2fB" % (tot / 1e9))
h = get("https://api.llama.fi/v2/historicalChainTvl",
        {"User-Agent": "defillama-radar/audit27d"})
for row in h[-4:]:
    print("  chainTvl %s $%.2fB" % (datetime.fromtimestamp(row["date"], timezone.utc)
                                    .strftime("%Y-%m-%d"), row["tvl"] / 1e9))
last = h[-1]
print("  比值 %.2fx（快照 vs 最新日桶，只比 delta 不比绝对值）"
      % (tot / last["tvl"]))
print("  日桶最新点距 now 约 %.1fh" % ((now - last["date"]) / 3600))

print("\n== 空链 net 变化候选（tvl 从 None 变有值）==")
print("  tvl=None 计数 %d" % sum(1 for p in cb if isinstance(p, dict) and p.get("tvl") is None))
print("  listedAt 缺失 %d" % sum(1 for p in cb if isinstance(p, dict) and not p.get("listedAt")))

#!/usr/bin/env python3
"""第 27 轮补二：按时间戳排序的 listedAt 直方图 + 未来日期检查。只读。"""
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
         {"User-Agent": "defillama-radar/audit27c",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})

now = time.time()
# 按"距今天数"分桶，负数=未来
buckets = Counter()
future = []
for p in cb:
    if not isinstance(p, dict) or not p.get("listedAt"):
        continue
    la = p["listedAt"]
    d = int((now - la) // 86400)
    buckets[d] += 1
    if la > now:
        future.append((str(p.get("id")), p.get("name"), la))

print("== 距今天数桶（前 20）==")
for d in sorted(buckets)[:20]:
    label = "未来(%.1fh)" % (-d * 24 - 0) if d < 0 else "第 %d 天前" % d
    print("  %-14s n=%d" % (label, buckets[d]))

print("\n== 未来日期条目 %d 条 ==" % len(future))
for f in sorted(future, key=lambda x: -x[2])[:15]:
    print("  %s %s → %s" % (f[0], f[1],
                            datetime.fromtimestamp(f[2], timezone.utc).isoformat()))

print("\n== 7/8/9 日窗口 ==")
for w in (6, 7, 8, 9, 30):
    print("  近 %dd: %d" % (w, sum(1 for p in cb if isinstance(p, dict)
                                 and p.get("listedAt") and now - p["listedAt"] <= w * 86400)))

print("\n== 时间跨度边界 ==")
las = sorted(p["listedAt"] for p in cb if isinstance(p, dict) and p.get("listedAt"))
print("最早 %s" % datetime.fromtimestamp(las[0], timezone.utc).isoformat())
print("最晚 %s" % datetime.fromtimestamp(las[-1], timezone.utc).isoformat())
print("已登记总 %d" % len(las))

#!/usr/bin/env python3
"""第 33 轮补三：30d 窗口为何 265→246，逐日定位滑出。只读。"""
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
         {"User-Agent": "defillama-radar/audit33c",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
now = time.time()
la = [p["listedAt"] for p in cb if isinstance(p, dict) and p.get("listedAt")]
day = Counter(datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in la)

cut = now - 30 * 86400
print("30d 边界 = %s" % datetime.fromtimestamp(cut, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
print("本轮读数: 7d=%d 30d=%d 90d=%d"
      % (sum(1 for t in la if now - t <= 7 * 86400),
         sum(1 for t in la if now - t <= 30 * 86400),
         sum(1 for t in la if now - t <= 90 * 86400)))

print("\n== 边界附近逐日：当日总数 / 仍在 30d 窗内 ==")
for d in ("2026-10-24", "2026-10-25", "2026-10-26", "2026-10-27",
          "2026-10-28", "2026-10-29", "2026-10-30"):
    tot = day.get(d, 0)
    inw = sum(1 for t in la
              if datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") == d
              and now - t <= 30 * 86400)
    print("  %s  当日=%2d  窗内=%2d" % (d, tot, inw))

print("\n== 龄段切片 ==")
for lo, hi in ((7, 8), (30, 31), (89, 90)):
    print("  (%dd, %dd] = %d" % (lo, hi, sum(1 for t in la if lo * 86400 < now - t <= hi * 86400)))

print("\n== 7d 边界逐日 ==")
for d in ("2026-11-20", "2026-11-21", "2026-11-22"):
    tot = day.get(d, 0)
    inw = sum(1 for t in la
              if datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") == d
              and now - t <= 7 * 86400)
    print("  %s  当日=%2d  窗内=%2d" % (d, tot, inw))

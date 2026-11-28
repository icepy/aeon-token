#!/usr/bin/env python3
"""第 33 轮补九：90d 窗 986→987 的配平 + 10s/15s 簇跳变来源。只读。"""
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
         {"User-Agent": "defillama-radar/audit33i",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
ls = sorted(p["listedAt"] for p in cb if isinstance(p, dict) and p.get("listedAt"))
now = time.time()

print("== 90d 边界配平 ==")
for lo in (89, 90, 91, 92):
    print("  龄 (89d, %dd] = %d" % (lo, sum(1 for t in ls if 89 * 86400 < now - t <= lo * 86400)))
print("  90d 窗内 = %d（上轮报 986，+5 新增应得 991）"
      % sum(1 for t in ls if now - t <= 90 * 86400))
c = Counter(datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in ls)
for d in ("2026-08-28", "2026-08-29", "2026-08-30", "2026-08-31", "2026-09-01"):
    print("  %s 当日登记=%d" % (d, c.get(d, 0)))

print("\n== 10s → 15s 簇数跳变来源（91 → 172）==")
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
c10 = {t: n for t, n in clusters(10)}
c15 = clusters(15)
extra = [(t, n) for t, n in c15 if t not in c10]
print("15s 窗新增 %d 簇：" % len(extra))
for t, n in sorted(extra, key=lambda x: -x[1])[:8]:
    print("  %s n=%d" % (datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), n))
print("  15s 簇总条目 %d / 全体 %d = %.1f%%"
      % (sum(n for _, n in c15), len(ls), 100.0 * sum(n for _, n in c15) / len(ls)))

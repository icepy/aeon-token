#!/usr/bin/env python3
"""第 27 轮补四：日桶回溯修订取证。只读。"""
import json
import urllib.request
from datetime import datetime, timezone

API = "https://api.llama.fi/v2/historicalChainTvl"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


h = get(API, {"User-Agent": "defillama-radar/audit27e"})
byday = {datetime.fromtimestamp(r["date"], timezone.utc).strftime("%Y-%m-%d"): r["tvl"]
         for r in h}
for d in ("2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19",
          "2026-11-20", "2026-11-21"):
    v = byday.get(d)
    print("%s  $%.2fB" % (d, v / 1e9) if v else "%s  缺失" % d)

print("\n== 与第 26 轮日志读数对照 ==")
prev = {"2026-11-18": 71.32, "2026-11-19": 70.30, "2026-11-20": 66.61}
for d, pv in prev.items():
    v = byday.get(d, 0) / 1e9
    print("%s 上轮 %0.2fB → 本轮 %0.2fB  修订 %+.2f%%" % (d, pv, v, 100.0 * (v / pv - 1)))

print("\n== 上轮『最近一日』重算 ==")
a = byday["2026-11-19"]
for d in ("2026-11-20", "2026-11-21"):
    print("%s 对 11-19: %+.2f%%" % (d, 100.0 * (byday[d] / a - 1)))

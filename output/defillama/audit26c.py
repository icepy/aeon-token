#!/usr/bin/env python3
"""分辨 −3.77% 是全市场行情还是本份 payload 口径。只读，一次请求。"""
import json
import urllib.request
from datetime import datetime, timezone

req = urllib.request.Request("https://api.llama.fi/v2/historicalChainTvl",
                             headers={"User-Agent": "defillama-radar/audit26c",
                                      "Cache-Control": "no-cache"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
print("点数 %d" % len(raw))
for pt in raw[-6:]:
    print("  %s  $%.2fB"
          % (datetime.fromtimestamp(pt["date"], timezone.utc).strftime("%Y-%m-%d %H:%M"),
             pt["tvl"] / 1e9))
a, b = raw[-2]["tvl"], raw[-1]["tvl"]
print("最近一日变化: %.2f%%" % (100.0 * (b / a - 1)))
if len(raw) >= 4:
    print("三日前→今日: %.2f%%" % (100.0 * (raw[-1]["tvl"] / raw[-4]["tvl"] - 1)))

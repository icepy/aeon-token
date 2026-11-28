#!/usr/bin/env python3
"""第 33 轮补十：滑窗计数 vs 极大连续段计数 —— 证明前者会把一个长批次切碎。只读。"""
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
         {"User-Agent": "defillama-radar/audit33j",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
ls = sorted(p["listedAt"] for p in cb if isinstance(p, dict) and p.get("listedAt"))
now = time.time()

def runs(gap):
    """极大连续段：相邻间隔 <= gap 就并入同段。"""
    out, cur = [], [ls[0]]
    for t in ls[1:]:
        if t - cur[-1] <= gap:
            cur.append(t)
        else:
            out.append(cur)
            cur = [t]
    out.append(cur)
    return [r for r in out if len(r) >= 3]


print("== 极大连续段（相邻 <= gap）==")
for g in (0, 15, 60, 300):
    rs = runs(g)
    print("  gap=%4ds  段数=%3d  总条目=%4d  最大段=%d"
          % (g, len(rs), sum(len(r) for r in rs), max(len(r) for r in rs)))
    for r in sorted(rs, key=lambda r: -len(r))[:3]:
        print("       %s n=%d 跨 %.0fs"
              % (datetime.fromtimestamp(r[0], timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 len(r), r[-1] - r[0]))
    print("       其中起点在近 30d: %d"
          % sum(1 for r in rs if now - r[0] <= 30 * 86400))

print("\n== 10-08 那一段逐条 ==")
seg = sorted(p for p in cb if isinstance(p, dict) and p.get("listedAt")
             and abs(p["listedAt"] - 1791504000) < 3600)
print("2027? 条数=%d" % len(seg))
seg2 = sorted(((p["listedAt"], str(p.get("id")), p.get("name")) for p in cb
               if isinstance(p, dict) and p.get("listedAt")
               and datetime.fromtimestamp(p["listedAt"], timezone.utc).strftime("%Y-%m-%d") == "2026-10-08"),
              key=lambda x: x[0])
print("2026-10-08 当日 %d 条，跨度 %.0f 分钟" % (len(seg2), (seg2[-1][0] - seg2[0][0]) / 60.0))
gaps = [seg2[i][0] - seg2[i - 1][0] for i in range(1, len(seg2))]
print("相邻间隔：max=%ds 中位=%ds  <=15s 的对数=%d/%d"
      % (max(gaps), sorted(gaps)[len(gaps) // 2],
         sum(1 for g in gaps if g <= 15), len(gaps)))

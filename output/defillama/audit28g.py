#!/usr/bin/env python3
"""第 33 轮补七：02:21 批量指纹窗口普查（"同秒≥3" 规则是否低报）。只读。"""
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
         {"User-Agent": "defillama-radar/audit33g",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
lo, hi = 1795746000, 1795747200   # 02:20:00Z – 02:40:00Z on 11-27
rows = sorted(((p.get("listedAt"), p) for p in cb
               if isinstance(p, dict) and p.get("listedAt")
               and lo <= p["listedAt"] <= hi), key=lambda x: x[0])
print("02:20–02:40Z 窗口内全量条目 %d 条（含已在 seen 的老条目）:" % len(rows))
for t, p in rows:
    pid = str(p.get("id"))
    st = seen.get(pid) or {}
    print("  %s %s %-24s parent=%-24s cat=%-18s tvl=%-12s chains=%-22s seen_first=%s"
          % (datetime.fromtimestamp(t, timezone.utc).strftime("%H:%M:%S"), pid,
             (p.get("name") or "")[:24], (p.get("parentProtocol") or "-")[:24],
             (p.get("category") or "-")[:18], p.get("tvl"), str(p.get("chains")),
             st.get("first", "<未入库>")))

print("\n== 全量里 ±15s 滑窗内 ≥3 条的簇（新判据试探）==")
ls = sorted(p["listedAt"] for p in cb if isinstance(p, dict) and p.get("listedAt"))
clusters = []
i = 0
while i < len(ls):
    j = i
    while j + 1 < len(ls) and ls[j + 1] - ls[i] <= 15:
        j += 1
    if j - i + 1 >= 3:
        clusters.append((ls[i], j - i + 1))
        i = j + 1
    else:
        i += 1
print("簇数 = %d（同秒≥3 口径为 31）" % len(clusters))
for t, n in clusters[-6:]:
    print("  %s n=%d" % (datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), n))

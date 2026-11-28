#!/usr/bin/env python3
"""第 33 轮补五：Hyperliquid Builder 全量 240→241 而 30d 不动 —— 查是否老条目补 tags。只读。"""
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
         {"User-Agent": "defillama-radar/audit33e",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
now = time.time()
rows = [p for p in cb if isinstance(p, dict) and "Hyperliquid Builder" in (p.get("tags") or [])]
print("Hyperliquid Builder 全量 = %d" % len(rows))
aged = []
for p in rows:
    la = p.get("listedAt")
    age = (now - la) / 86400.0 if la else None
    aged.append((age, str(p.get("id")), p.get("name"), la, p.get("tvl")))
print("\n龄在 25–100 天的条目（30d 不动而 90d 动的解释候选）:")
for age, i, nm, la, tvl in sorted((a for a in aged if a[0] is not None)):
    if 20 <= age <= 100:
        print("  %s %-34s 龄 %.1fd  listedAt=%s  tvl=%s"
              % (i, nm, age, datetime.fromtimestamp(la, timezone.utc).strftime("%Y-%m-%d"), tvl))
print("\n无 listedAt 的条数 = %d" % sum(1 for a in aged if a[0] is None))
print("龄 >100d 条数 = %d" % sum(1 for a in aged if a[0] is not None and a[0] > 100))

# 全量 tags 覆盖变化线索：有 tags 的条目里 listedAt 缺失情况
tagged = [p for p in cb if isinstance(p, dict) and p.get("tags")]
print("\n全量有 tags=%d，其中 listedAt 缺失=%d"
      % (len(tagged), sum(1 for p in tagged if not p.get("listedAt"))))
# 最近 90d 内按日 计数，看是否有单日簇可解释 +1
from collections import Counter
c = Counter(datetime.fromtimestamp(p["listedAt"], timezone.utc).strftime("%Y-%m-%d")
            for p in rows if p.get("listedAt") and now - p["listedAt"] <= 90 * 86400)
print("90d 内逐日（仅非零）: %s" % dict(sorted(c.items())))

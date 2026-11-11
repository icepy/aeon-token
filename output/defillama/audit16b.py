#!/usr/bin/env python3
"""第 16 轮补充核查：9382 缺口、Elysium 簇、listedAt 滞后。只读。"""
import json, urllib.request
from datetime import datetime, timezone
from collections import Counter

API = "https://api.llama.fi/protocols"
CHAINS = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
          "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"]
req = urllib.request.Request(API, headers={"User-Agent": "dl-audit16b"})
with urllib.request.urlopen(req, timeout=60) as r:
    pay = json.loads(r.read().decode("utf-8"))
by = {str(p.get("id")): p for p in pay if isinstance(p, dict) and p.get("id")}

print("=== 9382 是否存在 ===")
print("9382 in payload:", "9382" in by)
print("9381 / 9383 存在:", "9381" in by, "9383" in by)

print("\n=== 9373 listedAt 与上轮快照的关系 ===")
p = by.get("9373", {})
print("9373 listedAt =", p.get("listedAt"),
      datetime.fromtimestamp(p["listedAt"], tz=timezone.utc).isoformat() if p.get("listedAt") else "")
print("上轮 payload last-modified = 2026-11-09T23:38:34Z（上一轮记录）")

print("\n=== 全部链名频次（用于看 Elysium 是否成簇）===")
c = Counter()
for q in by.values():
    for ch in (q.get("chains") or []):
        c[ch] += 1
for ch, n in c.most_common(40):
    mark = " [白名单]" if ch in CHAINS else ""
    print("  %-28s %4d%s" % (ch, n, mark))

print("\n=== Elysium 相关条目全量 ===")
ely = [(str(q.get("id")), q.get("name"), q.get("chains"), q.get("tvl"),
        q.get("parentProtocol"), q.get("listedAt"))
       for q in by.values()
       if any("elysium" in str(x).lower() for x in (q.get("chains") or []))
       or "elysium" in str(q.get("address") or "").lower()]
ely.sort(key=lambda x: int(x[0]) if x[0].isdigit() else -1)
for e in ely:
    print("  id=%s %-28s chains=%s tvl=%s parent=%s listedAt=%s" % e)

print("\n=== 描述提到 Elysium 但 chains 为空 ===")
for q in by.values():
    d = (q.get("description") or "")
    if "elysium" in d.lower() and not (q.get("chains") or []):
        print("  id=%s %-24s tvl=%s listedAt=%s" % (q.get("id"), q.get("name"), q.get("tvl"), q.get("listedAt")))

print("\n=== 描述提到 Robinhood Chain 但 chains 为空 ===")
for q in by.values():
    d = (q.get("description") or "") + " " + (q.get("url") or "")
    if "robinhood" in d.lower() and not (q.get("chains") or []):
        print("  id=%s %-24s tvl=%s listedAt=%s" % (q.get("id"), q.get("name"), q.get("tvl"), q.get("listedAt")))

print("\n=== 15 条新增的 listedAt 排序 ===")
new = ["9373","9374","9375","9376","9377","9378","9379","9380","9381","9383","9384","9385","9386","9387","9388"]
rows = [(i, by[i].get("listedAt"), by[i].get("name")) for i in new if i in by]
rows.sort(key=lambda x: x[1])
prev = None
for i, t, n in rows:
    dt = "初始" if prev is None else "+%ds" % (t - prev)
    print("  %s %s %-26s %s" % (i, datetime.fromtimestamp(t, tz=timezone.utc).strftime("%H:%M:%SZ"), n, dt))
    prev = t

#!/usr/bin/env python3
"""第 33 轮补四：两向差集、dummy.js 校验、tags 流、空链结构、Pear 家族。只读。"""
import json
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"
NEW = ["9524", "9525", "9526", "9527", "9528"]


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


cb = get(API + "?_cb=%d" % int(time.time()),
         {"User-Agent": "defillama-radar/audit33d",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
now = time.time()

raw_ids = {str(p.get("id")) for p in cb if isinstance(p, dict) and p.get("id")}
print("== 两向差集 ==")
print("only_raw=%s" % sorted(raw_ids - set(seen)))
print("only_seen=%s" % sorted(set(seen) - raw_ids))
print("raw=%d seen=%d 交集=%d" % (len(raw_ids), len(seen), len(raw_ids & set(seen))))

cm = {str(p.get("id")): p for p in cb if isinstance(p, dict) and p.get("id")}
print("\n== 新增 5 条的 module / tvlCodePath（dummy 校验）==")
for i in NEW:
    p = cm.get(i, {})
    print("  %s %-22s module=%-28s tvlCodePath=%-32s tvl=%s chains=%s"
          % (i, p.get("name"), p.get("module"), p.get("tvlCodePath"),
             p.get("tvl"), p.get("chains")))

print("\n== 空链 ⟺ tvl=None 校验 ==")
empty = [p for p in cb if isinstance(p, dict) and not (p.get("chains") or [])]
print("空链=%d · 空链且tvl=None=%d · 空链且tvl非空=%d"
      % (len(empty), sum(1 for p in empty if p.get("tvl") is None),
         sum(1 for p in empty if p.get("tvl") is not None)))
print("空链且 module=dummy.js=%d"
      % sum(1 for p in empty if (p.get("module") or "").endswith("dummy.js")))
nonempty_none = [p for p in cb if isinstance(p, dict) and (p.get("chains") or [])
                 and p.get("tvl") is None]
print("非空链但 tvl=None=%d 例: %s"
      % (len(nonempty_none), [(str(p.get("id")), p.get("name")) for p in nonempty_none[:4]]))

print("\n== tags 流（唯一入口）==")
tagged = [p for p in cb if isinstance(p, dict) and p.get("tags")]
print("全量有 tags=%d" % len(tagged))
for tag in ("Hyperliquid Builder", "Polymarket Builder"):
    rows = [p for p in tagged if tag in (p.get("tags") or [])]
    def cnt(days):
        return sum(1 for p in rows if p.get("listedAt") and now - p["listedAt"] <= days * 86400)
    print("  %-22s 全量=%d 7d=%d 30d=%d 90d=%d  Interface=%d 空链=%d tvl非空=%d"
          % (tag, len(rows), cnt(7), cnt(30), cnt(90),
             sum(1 for p in rows if p.get("category") == "Interface"),
             sum(1 for p in rows if not (p.get("chains") or [])),
             sum(1 for p in rows if p.get("tvl") is not None)))
    for p in rows:
        if p.get("tvl") is not None:
            print("     tvl 非空: %s %s $%.0f" % (p.get("id"), p.get("name"), p["tvl"]))

print("\n== Pear 家族全量 ==")
for p in cb:
    if isinstance(p, dict) and (p.get("parentProtocol") or "") == "parent#pear-protocol":
        print("  %s %-20s cat=%-16s tvl=%-14s chains=%s listedAt=%s"
              % (p.get("id"), p.get("name"), p.get("category"), p.get("tvl"),
                 p.get("chains"),
                 datetime.fromtimestamp(p["listedAt"], timezone.utc).strftime("%Y-%m-%d")
                 if p.get("listedAt") else "-"))

print("\n== 链命中数 vs 新增（老条目补 chains 校验）==")
CHAINS = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
          "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"]
for c in CHAINS:
    n = sum(1 for p in cb if isinstance(p, dict) and c in (p.get("chains") or []))
    print("  %-18s %d" % (c, n))

print("\n== 新增 5 条是否在清单内 ==")
names = [l.strip() for l in open("memory/defillama-names.txt", encoding="utf-8")
         if l.strip() and not l.startswith("#")]
for i in NEW:
    nm = (cm.get(i, {}).get("name") or "")
    print("  %s %-24s in_names=%s" % (i, nm, any(k.lower() in nm.lower() for k in names)))

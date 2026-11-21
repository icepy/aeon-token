#!/usr/bin/env python3
"""日精度 listedAt 的 4 条是谁 + 空链/dummy 的计数核对。只读。"""
import json
import urllib.request
from datetime import datetime, timezone

req = urllib.request.Request("https://api.llama.fi/protocols?_cb=d26b",
                             headers={"User-Agent": "defillama-radar/audit26b",
                                      "Cache-Control": "no-cache"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
print("n=%d" % len(raw))

print("== listedAt 恰为 UTC 整日 ==")
for p in raw:
    if not isinstance(p, dict):
        continue
    la = p.get("listedAt")
    if la and la % 86400 == 0:
        print("  %s · %s · %s · cat=%s · chains=%s · tvl=%s · module=%s"
              % (p.get("id"), p.get("name"),
                 datetime.fromtimestamp(la, timezone.utc).strftime("%Y-%m-%d"),
                 p.get("category"), p.get("chains"), p.get("tvl"), p.get("module")))

print("\n== 空链 vs dummy 两向 ==")
empty = {str(p.get("id")) for p in raw if isinstance(p, dict)
         and p.get("id") and not (p.get("chains") or [])}
dummy = {str(p.get("id")) for p in raw if isinstance(p, dict)
         and p.get("id") and p.get("module") == "dummy.js"}
print("empty=%d dummy=%d equal=%s only_empty=%s only_dummy=%s"
      % (len(empty), len(dummy), empty == dummy,
         sorted(empty - dummy)[:5], sorted(dummy - empty)[:5]))

print("\n== 新增 6 条的 misrep / wrongLiquidity / audits ==")
for i in ["9480", "9481", "9482", "9483", "9484", "9485"]:
    p = next((x for x in raw if str(x.get("id")) == i), {})
    print("  %s %s · misrep=%s · wrongLiq=%s · audits=%s · audit_links=%s"
          % (i, p.get("name"), p.get("misrepresentedTokens"), p.get("wrongLiquidity"),
             p.get("audits"), p.get("audit_links")))

print("\n== 全量 TVL 头部 15（看 −$16.7B 是否来自单条）==")
rows = sorted([p for p in raw if isinstance(p, dict) and p.get("tvl")],
              key=lambda p: -p["tvl"])[:15]
for p in rows:
    print("  %-28s $%.1fB · %s" % (p.get("name"), p["tvl"] / 1e9, p.get("category")))

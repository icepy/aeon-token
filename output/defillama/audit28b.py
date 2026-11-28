#!/usr/bin/env python3
"""第 33 轮补：日桶直方图（与上轮同口径 12 个 1 日桶）+ 被挡桶 TVL 合计。只读。"""
import json
import time
import urllib.request
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"
NEW = ["9524", "9525", "9526", "9527", "9528"]


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


cb, hc = get(API + "?_cb=%d" % int(time.time()),
             {"User-Agent": "defillama-radar/audit33b",
              "Cache-Control": "no-cache", "Pragma": "no-cache"})
now = int(time.time())
listed = [p for p in cb if isinstance(p, dict) and p.get("listedAt")]

DAY = 86400
hist = [0] * 12
for p in listed:
    age = now - p["listedAt"]
    if 0 <= age < 12 * DAY:
        hist[age // DAY] += 1
print("12 个 1 日桶（第 0 桶=最近 24h）: %s" % hist)
print("7d=%d 30d=%d 90d=%d"
      % (sum(hist), sum(1 for p in listed if 0 <= now - p["listedAt"] < 30 * DAY),
         sum(1 for p in listed if 0 <= now - p["listedAt"] < 90 * DAY)))
print("上轮读数: [7,9,9,4,5,3,6,5,4,11,5,5] → 7d=43 30d=265 90d=986")

print("\n== 被挡 4 条 TVL 合计 vs 可报 ==")
cm = {str(p.get("id")): p for p in cb if isinstance(p, dict) and p.get("id")}
dropids = ["9524", "9525", "9526", "9527"]
tot = 0
for i in dropids:
    p = cm.get(i, {})
    v = p.get("tvl")
    print("  %s %s tvl=%s" % (i, p.get("name"), v))
    if isinstance(v, (int, float)):
        tot += v
print("被挡合计 tvl 非空加总 = $%.2f" % tot)
rep = cm.get("9528", {}).get("tvl") or 0
print("可报合计 = $%.2f  比值 %.1fx" % (rep, (tot / rep) if rep else 0))

print("\n== Pear Vaults 与 pear-protocol 同族 ==")
for p in cb:
    if not isinstance(p, dict):
        continue
    pp = p.get("parentProtocol") or ""
    if "pear" in pp.lower() or "pear" in (p.get("slug") or "").lower():
        print("  %s · %s · parent=%s · cat=%s · tvl=%s · chains=%s"
              % (p.get("id"), p.get("name"), pp, p.get("category"),
                 p.get("tvl"), p.get("chains")))

print("\n== 9524/9525/9526 同窗（12s）+ 是否同 parent 家族 ==")
for i in NEW[:3]:
    p = cm.get(i, {})
    print("  %s %s parent=%s cat=%s tvl=%s" % (i, p.get("name"), p.get("parentProtocol"),
                                              p.get("category"), p.get("tvl")))

print("\n== Stoxes.fun 附加字段 ==")
p = cm.get("9528", {})
for k in ("id", "name", "slug", "symbol", "gecko_id", "address", "url", "audits",
          "listedAt", "category", "chains", "tvl", "mcap", "methodology", "forkedFrom"):
    if k in p:
        print("  %s = %r" % (k, p[k]))
print("  keys=%s" % sorted(p.keys()))

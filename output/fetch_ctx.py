#!/usr/bin/env python3
"""Fetch VIRTUAL pairs + ETH price from DexScreener."""
import json
import urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "aeon-price-alert/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
data = get("https://api.dexscreener.com/latest/dex/tokens/" + VIRTUAL)
pairs = data.get("pairs") or []
print("virtual_pairs=%d" % len(pairs))
base = [p for p in pairs if p.get("chainId") == "base"]
base.sort(key=lambda p: ((p.get("liquidity") or {}).get("usd") or 0), reverse=True)
for p in base[:6]:
    print(json.dumps({
        "pair": p.get("pairAddress"),
        "dex": p.get("dexId"),
        "b": (p.get("baseToken") or {}).get("symbol"),
        "q": (p.get("quoteToken") or {}).get("symbol"),
        "priceUsd": p.get("priceUsd"),
        "h1": (p.get("priceChange") or {}).get("h1"),
        "h24": (p.get("priceChange") or {}).get("h24"),
        "liq": (p.get("liquidity") or {}).get("usd"),
        "vol24": (p.get("volume") or {}).get("h24"),
    }))

print("---ETH---")
d2 = get("https://api.dexscreener.com/latest/dex/search?q=WETH%20USDC")
pp = [p for p in (d2.get("pairs") or []) if p.get("chainId") == "base"]
pp.sort(key=lambda p: ((p.get("liquidity") or {}).get("usd") or 0), reverse=True)
for p in pp[:4]:
    print(json.dumps({
        "pair": p.get("pairAddress"),
        "dex": p.get("dexId"),
        "b": (p.get("baseToken") or {}).get("symbol"),
        "q": (p.get("quoteToken") or {}).get("symbol"),
        "priceUsd": p.get("priceUsd"),
        "h1": (p.get("priceChange") or {}).get("h1"),
        "liq": (p.get("liquidity") or {}).get("usd"),
    }))

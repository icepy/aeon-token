#!/usr/bin/env python3
"""Fetch DEUS pairs from DexScreener and print the deepest base-chain pool."""
import json
import urllib.request

CONTRACT = "0x940A319B75861014A220D9c6c144d108552B089B"
CHAIN = "base"
URL = "https://api.dexscreener.com/latest/dex/tokens/" + CONTRACT

req = urllib.request.Request(URL, headers={"User-Agent": "aeon-price-alert/1.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    body = r.read().decode("utf-8")

data = json.loads(body)
pairs = data.get("pairs") or []
print("total_pairs=%d" % len(pairs))

base_pairs = [p for p in pairs if p.get("chainId") == CHAIN]
print("base_pairs=%d" % len(base_pairs))
pool = base_pairs if base_pairs else pairs

def liq(p):
    return ((p.get("liquidity") or {}).get("usd") or 0)

pool.sort(key=liq, reverse=True)
rows = []
for p in pool:
    rows.append({
        "dexId": p.get("dexId"),
        "pairAddress": p.get("pairAddress"),
        "base": (p.get("baseToken") or {}).get("symbol"),
        "quote": (p.get("quoteToken") or {}).get("symbol"),
        "priceUsd": p.get("priceUsd"),
        "h1": (p.get("priceChange") or {}).get("h1"),
        "h6": (p.get("priceChange") or {}).get("h6"),
        "h24": (p.get("priceChange") or {}).get("h24"),
        "liq_usd": liq(p),
        "vol_24h": (p.get("volume") or {}).get("h24"),
        "url": p.get("url"),
    })

print(json.dumps(rows, indent=2))
print("---DEEPEST---")
print(json.dumps(rows[0], indent=2))

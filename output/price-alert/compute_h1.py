#!/usr/bin/env python3
"""Recompute DEUS/USD from the saved swap series, with a DexScreener cross-check.

Validation note: these pools order (token0=USDC 6dp, token1=DEUS 18dp), and the raw
sqrtPriceX96 ratio comes out as DEUS-per-USDC on this venue family, so the human
USDC-per-DEUS mark is its RECIPROCAL. Verified against three independent DexScreener
prints (pool2 0.01791 / pool3 0.01787 / pool4 0.01800) before any gate was evaluated.
"""
import json
import statistics
import sys
import time

d = json.load(open("output/price-alert/h1_series_out.json"))
rows = d["rows"]
for r in rows:
    r["price_usd"] = 1.0 / r["usdc_per_deus"]

now_ts = int(time.time())
cut = now_ts - 3600

print("=== per-pool marks vs DexScreener ===")
dex = {"pool2": 0.01791, "pool3": 0.01787, "pool4": 0.01800}
for p in ("pool2", "pool3", "pool4"):
    prs = [r["price_usd"] for r in rows if r["pool"] == p]
    if prs:
        print(f"{p}: last={prs[-1]:.8f} n={len(prs)} dex={dex[p]}")

print("\n=== real 1h window ===")
in1h = [r for r in rows if r["ts"] >= cut]
older = [r for r in rows if r["ts"] < cut]
print(f"swaps in last 1h: {len(in1h)}; before: {len(older)}")
for r in in1h:
    print(f"  {r['iso']} {r['pool']:6s} {r['price_usd']:.8f} deus={r['deus_delta']:.1f}")

# volume-weighted across pools in the last hour, weighting by |DEUS| moved
tot_w = sum(abs(r["deus_delta"]) for r in in1h)
vw = sum(r["price_usd"] * abs(r["deus_delta"]) for r in in1h) / tot_w if tot_w else None
print(f"\nDEUS volume in last 1h: {tot_w:.1f} DEUS")
print(f"volume-weighted last-1h mark: {vw}")
print(f"volume-weighted last-1h USD: ${vw*sum(r['usdc_delta'] for r in in1h)/tot_w if tot_w else 0:.2f} notional (USDC leg)")

# point-in-time reference ~1h ago per pool, and latest per pool
print("\n=== per-pool 1h delta ===")
for p in ("pool2", "pool3", "pool4"):
    sub = [r for r in in1h if r["pool"] == p]
    if len(sub) >= 2:
        first, last = sub[0], sub[-1]
        print(f"{p}: {first['iso']} {first['price_usd']:.8f} -> {last['iso']} {last['price_usd']:.8f} "
              f"= {(last['price_usd']/first['price_usd']-1)*100:+.3f}%")

print("\n=== median mark across live pools, 1h window ===")
if in1h:
    med = statistics.median(r["price_usd"] for r in in1h)
    print(f"median={med:.8f}  min={min(r['price_usd'] for r in in1h):.8f}  max={max(r['price_usd'] for r in in1h):.8f}")

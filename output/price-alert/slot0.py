#!/usr/bin/env python3
"""Read the TRUE mark of the Aerodrome Slipstream CL pool from slot0 (sqrtPriceX96 + tick).

Reserve-ratio marks are only exact for constant-product pools. Slipstream is concentrated
liquidity, so the canonical price is sqrtPriceX96^2, not token1/token0 balance ratio.
"""
import json
import sys
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
DEEP_POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SLOT0 = "0x3850c7bd"  # slot0() -> (sqrtPriceX96, tick, observationIndex, ...)


def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(f"rpc error: {out['error']}")
            return out["result"]
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def words(data):
    h = data[2:] if data.startswith("0x") else data
    return [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]


if __name__ == "__main__":
    raw = rpc("eth_call", [{"to": DEEP_POOL, "data": SLOT0}, "latest"])
    w = words(raw)
    sqrtP = w[0]
    tick = w[1]
    if tick >= 2**255:
        tick -= 2**256
    # both tokens are 18 decimals, so raw price == human price
    price_token1_per_token0 = (sqrtP / 2**96) ** 2
    print(json.dumps({
        "pool": DEEP_POOL,
        "slot0_raw_words": len(w),
        "sqrtPriceX96": str(sqrtP),
        "tick": tick,
        "price_token1_per_token0_slot0": price_token1_per_token0,
        "note": "token1/token0 as the pool orders them; identify which side is DEUS from reserves",
        "raw": raw[:200],
    }, indent=1))

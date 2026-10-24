#!/usr/bin/env python3
"""Compute a REAL 1h DEUS/USD move from the three live DEUS/USDC pools, with timestamps.

These pools are Uniswap-V3-style and actually trade. The deepest pool (Aerodrome classic,
DEUS/VIRTUAL) has printed zero swaps for hours, so it cannot supply h1.
Each swap's sqrtPriceX96 gives an exact post-trade marginal price in USDC per DEUS.
"""
import json
import sys
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
V3_SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
USDC_DEC, DEUS_DEC = 6, 18

POOLS = {
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": ("pool2", 32861.3),
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": ("pool3", 10707.85),
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": ("pool4", 6128.45),
}


def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def words(data):
    h = data[2:] if data.startswith("0x") else data
    return [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]


def walk(pool, lo, hi):
    out, start = [], lo
    while start <= hi:
        end = min(start + 999, hi)
        out.extend(rpc("eth_getLogs", [{"address": pool, "fromBlock": hex(start),
                                        "toBlock": hex(end), "topics": [V3_SWAP]}]))
        start = end + 1
        time.sleep(0.3)
    return out


if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    rows = []
    for pool, (name, liq) in POOLS.items():
        for lg in walk(pool, lo, hi):
            w = words(lg["data"])
            sqrtP = w[2]
            # token0=USDC(6), token1=DEUS(18): raw t1/t0 then decimals adjust
            usdc_per_deus = (sqrtP / 2**96) ** 2 * 10 ** (USDC_DEC - DEUS_DEC)
            amt0 = w[0] - 2**256 if w[0] >= 2**255 else w[0]
            amt1 = w[1] - 2**256 if w[1] >= 2**255 else w[1]
            rows.append({
                "pool": name, "liq": liq, "block": int(lg["blockNumber"], 16),
                "tx": lg["transactionHash"], "usdc_per_deus": usdc_per_deus,
                "usdc_delta": amt0 / 10**USDC_DEC, "deus_delta": amt1 / 10**DEUS_DEC,
            })
    # timestamps
    seen = {}
    for r in rows:
        b = r["block"]
        if b not in seen:
            blk = rpc("eth_getBlockByNumber", [hex(b), False])
            seen[b] = int(blk["timestamp"], 16)
        r["ts"] = seen[b]
        r["iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(r["ts"]))
    rows.sort(key=lambda r: (r["ts"], r["block"]))
    payload = {"from": lo, "to": hi, "rows": rows}
    with open("output/price-alert/h1_series_out.json", "w") as f:
        json.dump(payload, f, indent=1)
    for r in rows:
        print(f"{r['iso']} {r['pool']:6s} {r['usdc_per_deus']:.6f} usdc={r['usdc_delta']:.2f} deus={r['deus_delta']:.1f} {r['tx'][:14]}")

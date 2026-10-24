#!/usr/bin/env python3
"""Measure a REAL 1h price change for DEUS from the venues that actually traded.

The canonical deepest pool (Aerodrome classic, Solidly) has printed ZERO swaps for hours,
so DexScreener's priceChange.h1 is null. That is an ABSENCE, not a flat reading.
The three smaller DEUS pools are Uniswap-V3-style and DO trade, so decode their
Swap(sender, recipient, amount0, amount1, sqrtPriceX96, liquidity, tick) events
into a DEUS/USD series and compute the true 1h move.

V3 Swap: topic0 = 0xc42079f9..., topics = [sig, sender, recipient],
         data = [amount0, amount1, sqrtPriceX96, liquidity, tick]
Solidly Swap: topic0 = 0xb3e27736..., topics = [sig, sender, to],
         data = [amount0In, amount1In, amount0Out, amount1Out]
"""
import json
import sys
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
V3_SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SLIP_SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"

POOLS = {
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": "pool2",
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": "pool3",
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": "pool4",
    "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa": "deepest",
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


def addr_from_topic(t):
    return "0x" + t[-40:]


def call(pool, sel):
    r = rpc("eth_call", [{"to": pool, "data": sel}, "latest"])
    return "0x" + r[2:].rjust(64, "0")[-40:] if r and r != "0x" else None


def walk(pool, lo, hi):
    logs, start = [], lo
    while start <= hi:
        end = min(start + 499, hi)
        logs.extend(rpc("eth_getLogs", [{"address": pool, "fromBlock": hex(start), "toBlock": hex(end)}]))
        start = end + 1
        time.sleep(0.3)
    return logs


if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    out = {}
    for pool, name in POOLS.items():
        meta = {}
        try:
            meta["token0"] = call(pool, "0x0dfe1681")
            meta["token1"] = call(pool, "0xd21220a7")
        except Exception as e:  # noqa: BLE001
            out[name] = {"pool": pool, "error": f"token probe failed: {e}"}
            continue
        dec0 = int(rpc("eth_call", [{"to": meta["token0"], "data": "0x313ce567"}, "latest"]), 16)
        dec1 = int(rpc("eth_call", [{"to": meta["token1"], "data": "0x313ce567"}, "latest"]), 16)
        meta["dec0"], meta["dec1"] = dec0, dec1
        meta["deus_is"] = "token0" if meta["token0"].lower() == DEUS else (
            "token1" if meta["token1"].lower() == DEUS else "neither")
        meta["virtual_is"] = "token0" if meta["token0"].lower() == VIRTUAL else (
            "token1" if meta["token1"].lower() == VIRTUAL else "neither")

        logs = walk(pool, lo, hi)
        meta["n_logs"] = len(logs)
        swaps = []
        for lg in logs:
            t0 = (lg.get("topics") or [None])[0]
            try:
                bn = int(lg["blockNumber"], 16)
                if t0 == V3_SWAP:
                    w = words(lg["data"])
                    amt0 = w[0] - 2**256 if w[0] >= 2**255 else w[0]
                    amt1 = w[1] - 2**256 if w[1] >= 2**255 else w[1]
                    sqrtP = w[2]
                    # raw token1/token0, decimals-adjusted
                    p = (sqrtP / 2**96) ** 2 * 10 ** (dec0 - dec1)
                    swaps.append({"block": bn, "tx": lg["transactionHash"], "sqrtP": str(sqrtP),
                                  "raw_t1_per_t0": p, "amt0": amt0, "amt1": amt1,
                                  "tick": w[4] - 2**256 if w[4] >= 2**255 else w[4]})
                elif t0 == SLIP_SWAP:
                    w = words(lg["data"])
                    swaps.append({"block": bn, "tx": lg["transactionHash"], "solidly": True,
                                  "amt0In": w[0], "amt1In": w[1],
                                  "amt0Out": w[2], "amt1Out": w[3]})
            except Exception:  # noqa: BLE001
                continue
        meta["n_swaps"] = len(swaps)

        # normalise to DEUS->quote price where possible
        for s in swaps:
            if "raw_t1_per_t0" in s:
                if meta["deus_is"] == "token0":
                    s["quote_per_deus"] = s["raw_t1_per_t0"]
                elif meta["deus_is"] == "token1":
                    s["quote_per_deus"] = 1 / s["raw_t1_per_t0"] if s["raw_t1_per_t0"] else None
                s["quote_sym"] = meta["token1"] if meta["deus_is"] == "token0" else meta["token0"]
        meta["swaps"] = swaps
        out[name] = {"pool": pool, **meta}
    print(json.dumps(out, indent=1))

#!/usr/bin/env python3
"""Scan every DEUS pair contract for its LAST hour of activity, unfiltered by topic0.

Reason: the DEUS venue set mixes two pool ABIs.
  - Aerodrome Slipstream / Uniswap-V3  -> Swap topic0 0xc42079f9... (3 topics, 5 data words)
  - Aerodrome classic (Solidly)        -> Swap topic0 0xb3e27736... (varies)
Filtering only on 0xb3e27736 silently under-reports V3-style pools.
"""
import json
import sys
import time
import urllib.request
from collections import Counter

RPC = "https://base.gateway.tenderly.co"
V3_SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SLIP_SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

POOLS = [
    ("0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa", "aerodrome slipstream DEUS/VIRTUAL — deepest, liq $682k"),
    ("0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b", "aerodrome V3-style — liq $32.9k"),
    ("0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642", "aero — liq $10.7k"),
    ("0x75bc14950Ab093cBd1f80BbbDf458596939180A3", "aerodrome — liq $6.1k"),
]


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
    return []


def walk(pool, lo, hi):
    logs = []
    start = lo
    while start <= hi:
        end = min(start + 499, hi)
        got = rpc("eth_getLogs", [{"address": pool, "fromBlock": hex(start), "toBlock": hex(end)}])
        logs.extend(got)
        start = end + 1
        time.sleep(0.3)
    return logs


if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    out = {}
    for addr, name in POOLS:
        try:
            logs = walk(addr, lo, hi)
        except Exception as e:  # noqa: BLE001
            out[addr] = {"name": name, "error": str(e)}
            continue
        hist = Counter((lg.get("topics") or [None])[0] for lg in logs)
        swaps = [lg for lg in logs if (lg.get("topics") or [None])[0] in (V3_SWAP, SLIP_SWAP)]
        blocks = sorted(int(lg["blockNumber"], 16) for lg in swaps)
        out[addr] = {
            "name": name,
            "total_logs": len(logs),
            "swap_count": len(swaps),
            "swap_topic0": sorted({(lg.get("topics") or [None])[0] for lg in swaps}),
            "histogram": dict(hist),
            "first_swap_block": blocks[0] if blocks else None,
            "last_swap_block": blocks[-1] if blocks else None,
            "swap_txs": [
                {"block": int(lg["blockNumber"], 16), "tx": lg["transactionHash"]}
                for lg in swaps
            ],
        }
    print(json.dumps({"from": lo, "to": hi, "pools": out}, indent=1))

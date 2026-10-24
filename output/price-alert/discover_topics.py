#!/usr/bin/env python3
"""Discover which topic0s actually appear on a pool contract in a block window."""
import json
import sys
import time
import urllib.request
from collections import Counter

RPC = "https://base.gateway.tenderly.co"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(f"rpc error: {out['error']}")
            return out["result"]
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
    raise last


def collect(pool, lo, hi):
    """Walk windows, collect topic0 histogram. Unfiltered by topic but address-filtered."""
    hist = Counter()
    total = 0
    logs = []
    start = lo
    while start <= hi:
        end = min(start + 499, hi)
        try:
            got = rpc("eth_getLogs", [{"address": pool, "fromBlock": hex(start), "toBlock": hex(end)}])
        except Exception as e:  # noqa: BLE001
            print(f"    [{start}-{end}] FAIL {e}", file=sys.stderr)
            start = end + 1
            continue
        total += len(got)
        for lg in got:
            t0 = (lg.get("topics") or [None])[0]
            hist[t0] += 1
        logs.extend(got)
        start = end + 1
        time.sleep(0.3)
    return total, hist, logs


if __name__ == "__main__":
    pool = sys.argv[1]
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    label = sys.argv[4]
    total, hist, logs = collect(pool, lo, hi)
    print(json.dumps({
        "pool": pool, "label": label, "from": lo, "to": hi,
        "total_logs": total,
        "topic0_histogram": dict(hist),
        "transfer_events": sum(1 for lg in logs if (lg.get("topics") or [None])[0] == TRANSFER),
        "sample": [{"tx": lg["transactionHash"], "block": int(lg["blockNumber"], 16),
                    "topic0": (lg.get("topics") or [None])[0],
                    "n_topics": len(lg.get("topics") or []),
                    "n_data_words": len(lg["data"][2:]) // 64} for lg in logs[:6]],
    }, indent=1))

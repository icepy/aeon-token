#!/usr/bin/env python3
"""Scan Aerodrome Slipstream pools on Base for Swap events in 1000-block windows."""
import json
import sys
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
SWAP_TOPIC0 = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

POOLS = {
    "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa": "deepest DEUS/VIRTUAL (aerodrome slipstream)",
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": "DEUS pool 2 (aerodrome)",
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": "DEUS pool 3 (aero)",
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": "DEUS pool 4 (aerodrome)",
}


def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                RPC, data=body, headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(f"rpc error: {out['error']}")
            return out["result"]
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            print(f"  retry {attempt+1} after {delay}s: {e}", file=sys.stderr)
            time.sleep(delay)
            delay *= 2


def scan(address, lo, hi):
    logs = []
    start = lo
    while start <= hi:
        end = min(start + 999, hi)
        got = rpc(
            "eth_getLogs",
            [
                {
                    "address": address,
                    "fromBlock": hex(start),
                    "toBlock": hex(end),
                    "topics": [SWAP_TOPIC0],
                }
            ],
        )
        logs.extend(got)
        print(
            f"  {address[:10]} [{start}-{end}] -> {len(got)} swaps",
            file=sys.stderr,
        )
        start = end + 1
        time.sleep(0.4)
    return logs


if __name__ == "__main__":
    lo = int(sys.argv[1])
    hi = int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else "window"
    result = {}
    for addr, name in POOLS.items():
        print(f"scanning {name} {addr}", file=sys.stderr)
        lg = scan(addr, lo, hi)
        result[addr] = {"name": name, "count": len(lg), "logs": lg}
    payload = {"label": label, "from": lo, "to": hi, "pools": result}
    out = f"output/price-alert/scan_{label}.json"
    with open(out, "w") as f:
        json.dump(payload, f, indent=1)
    summary = {a: v["count"] for a, v in result.items()}
    print(json.dumps({"label": label, "from": lo, "to": hi, "counts": summary, "out": out}))

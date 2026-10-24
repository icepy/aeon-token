#!/usr/bin/env python3
"""Determine whether the deepest DEUS/VIRTUAL pool is Aerodrome classic (Solidly) or Slipstream."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

CANDIDATES = {
    "getReserves() [solidly]": "0x0902f1ac",
    "stable()": "0x22be3de1",
    "metadata()": "0x392f37e9",
    "decimals()": "0x313ce567",
    "getFee()": "0xced72f87",
    "observationLength()": "0xafb4b2d0",
}


def rpc(method, params, retries=3):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def words(data):
    h = data[2:] if data.startswith("0x") else data
    return [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]


if __name__ == "__main__":
    for name, sel in CANDIDATES.items():
        out = rpc("eth_call", [{"to": POOL, "data": sel}, "latest"])
        if "result" not in out:
            print(f"REV  {name:28s} -> {out['error'].get('message')}")
        else:
            w = words(out["result"])
            print(f"OK   {name:28s} -> {w[:5]}")
        time.sleep(0.2)

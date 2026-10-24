#!/usr/bin/env python3
"""Probe which price-view selector the Aerodrome Slipstream pool actually implements."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

CANDIDATES = {
    "slot0() [univ3]": "0x3850c7bd",
    "globalState() [slipstream]": "0xc19d93fb",
    "fee()": "0xddca3f43",
    "liquidity()": "0x1a686502",
    "token0()": "0x0dfe1681",
    "token1()": "0xd21220a7",
    "tickSpacing()": "0xd0c93a7c",
    "factory()": "0xc45a0155",
    "feeGrowthGlobal0X128()": "0xf3058399",
}


def rpc(method, params, retries=3):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                out = json.loads(r.read())
            return out
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


if __name__ == "__main__":
    for name, sel in CANDIDATES.items():
        out = rpc("eth_call", [{"to": POOL, "data": sel}, "latest"])
        if "result" in out:
            print(f"OK   {name:32s} {sel}  -> {out['result'][:200]}")
        else:
            print(f"REV  {name:32s} {sel}  -> {out['error'].get('message')}")
        time.sleep(0.2)

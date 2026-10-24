#!/usr/bin/env python3
"""Find the deepest pool's TRUE last activity (unfiltered by topic0)."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
LO, HI = 53010000, 53019896


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


if __name__ == "__main__":
    found = []
    start = LO
    while start <= HI:
        end = min(start + 999, HI)
        got = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(start), "toBlock": hex(end)}]) or []
        for lg in got:
            found.append((int(lg["blockNumber"], 16), lg["transactionHash"], lg["topics"][0]))
        start = end + 1
        time.sleep(0.3)
    print(f"unfiltered logs on deepest pool {LO}-{HI}: {len(found)}")
    for f in found[-10:]:
        print(" ", f[0], f[1], f[2][:20])
    if found:
        b = found[-1][0]
        blk = rpc("eth_getBlockByNumber", [hex(b), False])
        print("last activity block", b, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(blk["timestamp"], 16))))

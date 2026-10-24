#!/usr/bin/env python3
"""Lightweight: balance history + code/nonce for the 1h seller (no wide log scan)."""
import json
import time
import urllib.request
import sys

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last = e
            time.sleep(1.0 * (2 ** i))
    raise last

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

SELLER = "0xbd6383c7cbe3ed150f662f70fd4f3a4a1816e13d"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head, flush=True)
print("code=%s" % rpc("eth_getCode", [SELLER, "latest"]), flush=True)
print("nonce=%d" % int(rpc("eth_getTransactionCount", [SELLER, "latest"]), 16), flush=True)
print("eth_wei=%d" % int(rpc("eth_getBalance", [SELLER, "latest"]), 16), flush=True)

pad = "0" * 24 + SELLER[2:].lower()
def bal_at(tok, blk):
    return int(call(tok, "0x70a08231" + pad, hex(blk)), 16) / 1e18

for mins, label in ((0, "now"), (60, "-1h"), (360, "-6h"), (1440, "-24h"),
                    (10080, "-7d"), (43200, "-30d")):
    blk = head - int(mins * 30)
    try:
        print("DEUS %s = %.6f" % (label, bal_at(DEUS, blk)), flush=True)
    except Exception as e:
        print("DEUS %s ERR %s" % (label, e), flush=True)

# xDEUS NFT holdings
try:
    n = int(call(XDEUS, "0x70a08231" + pad), 16)
    print("xdeus_nfts=%d" % n, flush=True)
    for i in range(n):
        data = "0x2f745c59" + pad + format(i, "064x")
        tid = int(call(XDEUS, data), 16)
        print("  xdeus_tokenId[%d]=%d" % (i, tid), flush=True)
except Exception as e:
    print("xdeus ERR %s" % e, flush=True)

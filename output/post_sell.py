#!/usr/bin/env python3
"""Post-sell absorption check: any swaps on the deepest pool after the 52,737 dump?"""
import json
import time
import urllib.request
import datetime

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=5):
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
            time.sleep(0.8 * (2 ** i))
    raise last

def iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.UTC).strftime("%H:%M:%SZ")

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

head = int(rpc("eth_blockNumber", []), 16)
lo = 53028000
logs = []
cur = lo
while cur < head:
    hi = min(cur + 999, head)
    logs.extend(rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(cur), "toBlock": hex(hi),
                                     "topics": [SWAP]}]))
    cur = hi + 1
print("post_sell_swaps=%d  window=%d..%d" % (len(logs), lo, head), flush=True)
for lg in logs:
    w = lg["data"][2:]
    a0i, a1i = int(w[0:64], 16) / 1e18, int(w[64:128], 16) / 1e18
    a0o, a1o = int(w[128:192], 16) / 1e18, int(w[192:256], 16) / 1e18
    blk = int(lg["blockNumber"], 16)
    ts = int(rpc("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16)
    print(json.dumps({"blk": blk, "ts": iso(ts), "deus_in": round(a1i, 3),
                      "deus_out": round(a1o, 3), "virtual_in": round(a0i, 3),
                      "virtual_out": round(a0o, 3)}), flush=True)
print("head_iso=%s" % iso(int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)), flush=True)

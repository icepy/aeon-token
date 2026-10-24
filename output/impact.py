#!/usr/bin/env python3
"""Exact timing + reserve-impact of the 52,737 claim-and-dump; final mark snapshot."""
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

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

def iso(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")

def reserves(blk):
    r = call(DEEP, "0x0902f1ac", hex(blk))
    w = r[2:]
    return int(w[0:64], 16), int(w[64:128], 16)

head = int(rpc("eth_blockNumber", []), 16)
hts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
print("head=%d ts=%s" % (head, iso(hts)), flush=True)

for blk in (53027942, 53027992, 53027993, 53027994, 53028000, head):
    b = rpc("eth_getBlockByNumber", [hex(blk), False])
    print("blk %d %s" % (blk, iso(int(b["timestamp"], 16))), flush=True)

v_before, d_before = reserves(53027992)
v_at, d_at = reserves(53027993)
v_after, d_after = reserves(53028000)
r_b, r_a = v_before / d_before, v_at / d_at
print("ratio before=%.10f at_sell=%.10f (+1blk)=%.10f" % (r_b, r_a, v_after / d_after), flush=True)
print("impact_in_sell_block_pct=%.3f" % ((r_a / r_b - 1) * 100), flush=True)
print("deus_in_pool_before=%d  after=%d  delta=%.2f" % (
    d_before, d_at, (d_at - d_before) / 1e18), flush=True)
print("recovered_pct_after_7blk=%.3f" % ((r_after if False else (v_after / d_after) / r_b - 1) * 100), flush=True)

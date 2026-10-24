#!/usr/bin/env python3
"""Identify distributor 0x20d29c8e and confirm the claim->sell 51s pattern."""
import json
import time
import urllib.request

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

DIST = "0x20d29c8ec7489c600da7e595ce4ae1da11d76fc5"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
DIST2 = "0xd4c450ac"  # partial from notes

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head, flush=True)

code = rpc("eth_getCode", [DIST, "latest"])
print("dist_code_len=%d  prefix=%s" % (len(code), code[:60]), flush=True)

for name, sel in (("name", "0x06fdde03"), ("symbol", "0x95d89b41"),
                  ("owner", "0x8da5cb5b"), ("totalSupply", "0x18160ddd"),
                  ("decimals", "0x313ce567")):
    try:
        r = call(DIST, sel)
        if r and r != "0x":
            if sel in ("0x06fdde03", "0x95d89b41") and len(r) > 130:
                try:
                    ln = int(r[2 + 64:2 + 128], 16)
                    s = bytes.fromhex(r[2 + 128:2 + 128 + ln * 2]).decode("utf-8", "replace")
                    print("%s=%r" % (name, s), flush=True)
                    continue
                except Exception:
                    pass
            print("%s=%s" % (name, r[:130]), flush=True)
    except Exception as e:
        print("%s err %s" % (name, str(e)[:60]), flush=True)

# DEUS balance of distributor
b = int(call(DEUS, "0x70a08231" + "0" * 24 + DIST[2:].lower()), 16) / 1e18
print("dist_deus_balance=%.4f" % b, flush=True)

# Two tx timestamps -> latency
for txh, label in (("0x6ba180bb2856ac13d5", "claim_tx"), ("0xc940253588a057e876", "sell_tx")):
    try:
        # need full hash; look up by prefix is impossible -> use receipt of known full hashes
        pass
    except Exception:
        pass

# use block timestamps
for blk in (53027942, 53027993):
    bb = rpc("eth_getBlockByNumber", [hex(blk), False])
    print("blk %d ts=%d" % (blk, int(bb["timestamp"], 16)), flush=True)

t1 = int(rpc("eth_getBlockByNumber", [hex(53027942), False])["timestamp"], 16)
t2 = int(rpc("eth_getBlockByNumber", [hex(53027993), False])["timestamp"], 16)
print("latency_seconds=%d" % (t2 - t1), flush=True)

# how many distinct recipients did the distributor pay today? sample last 20k blocks
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
padf = "0x" + "0" * 24 + DIST[2:].lower()
lo = head - 20000
rows = []
cur = lo
while cur < head:
    hi = min(cur + 999, head)
    try:
        rows.extend(rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(cur), "toBlock": hex(hi),
                                         "topics": [TRANSFER, padf]}]))
    except Exception:
        pass
    cur = hi + 1
print("dist_outgoing_transfers_20k_blocks=%d" % len(rows), flush=True)
agg = {}
for lg in rows:
    to = "0x" + lg["topics"][2][-40:]
    amt = int(lg["data"][2:], 16) / 1e18
    agg[to] = agg.get(to, 0) + amt
for k, v in sorted(agg.items(), key=lambda x: -x[1])[:12]:
    print("  -> %s  %.2f" % (k, v), flush=True)

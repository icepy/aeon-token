#!/usr/bin/env python3
"""Control test for the zero-swap window + locate the true last swap on the deepest pool.
Lesson: never trust a zero-log window. Point the same filter at a KNOWN-active window,
and also point a deliberately-wrong topic0 at that window to prove discriminative power.
"""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last = e
            time.sleep(1.5 * (2**i))
    raise last

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
WRONG = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75a"

def scan(fromb, tob, topic):
    out = []
    lo = fromb
    while lo <= tob:
        hi = min(lo + 999, tob)
        out.extend(rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo),
                                        "toBlock": hex(hi), "topics": [topic]}]))
        lo = hi + 1
    return out

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head)

# CONTROL: known-active window around the 12:34/12:35Z swaps (blk 53027871 / 53027993)
c_from, c_to = 53027400, 53028000
c = scan(c_from, c_to, SWAP)
print("control_real_topic0_hits=%d (window %d..%d)" % (len(c), c_from, c_to))
w = scan(c_from, c_to, WRONG)
print("control_wrong_topic0_hits=%d" % len(w))
for lg in c:
    print("  ctrl blk=%d tx=%s" % (int(lg["blockNumber"],16), lg["transactionHash"][:18]))

# LAST SWAP: scan backwards in 999-block chunks from head until we find one
found = None
hi = head
scanned = 0
while scanned < 12000:
    lo = hi - 999
    logs = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo),
                                "toBlock": hex(hi), "topics": [SWAP]}])
    scanned += (hi - lo + 1)
    if logs:
        found = (lo, hi, logs[-1], len(logs))
        break
    hi = lo - 1
if found:
    lo, hi2, lg, n = found
    blk = int(lg["blockNumber"], 16)
    print("last_swap_block=%d in chunk %d..%d (chunk had %d swaps)" % (blk, lo, hi2, n))
    print("last_swap_tx=%s" % lg["transactionHash"])
    b = rpc("eth_getBlockByNumber", [hex(blk), False])
    ts = int(b["timestamp"], 16)
    print("last_swap_ts=%d (%s UTC)" % (ts, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))))
    hb = rpc("eth_getBlockByNumber", [hex(head), False])
    hts = int(hb["timestamp"], 16)
    print("quiet_minutes=%.1f" % ((hts - ts)/60.0))
    print("blocks_since=%d" % (head - blk))
else:
    print("NO swap found in last %d blocks" % scanned)

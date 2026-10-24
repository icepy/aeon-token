#!/usr/bin/env python3
"""Escrow Burn events over a block-pinned 24h window, chunked with per-chunk tolerance."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last=None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode())
            if "error" in d: raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last=e; time.sleep(1.2*(2**i))
    raise last

def blk(n):
    return rpc("eth_getBlockByNumber", [hex(n), False])

def ts(n):
    return int(blk(n)["timestamp"],16)

head = int(rpc("eth_blockNumber", []), 16)
hts = ts(head)
print("head=%d ts=%d %s" % (head, hts, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hts))))

# binary search exact 24h block
lo, hi = head - 60000, head
target = hts - 86400
while lo + 1 < hi:
    mid = (lo+hi)//2
    if ts(mid) <= target: lo = mid
    else: hi = mid
b24 = lo
print("24h_block=%d delta=%ds" % (b24, hts - ts(b24)))

ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d6adfabb7cd8caa254de14def35"

logs = []
failed = []
cursor = b24
while cursor < head:
    hi2 = min(cursor + 999, head)
    try:
        got = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(cursor),
                                   "toBlock": hex(hi2), "topics": [BURN]}], retries=2)
        logs.extend(got)
    except Exception as e:
        failed.append((cursor, hi2, str(e)[:60]))
    cursor = hi2 + 1

print("burn_events_24h=%d failed_chunks=%d" % (len(logs), len(failed)))
for f in failed[:5]:
    print("  FAILED", f)
for lg in logs:
    b = int(lg["blockNumber"],16)
    bts = ts(b)
    w = lg["data"][2:]
    amt = int(w[0:64],16)/1e18
    owner = "0x"+lg["topics"][1][-40:]
    tid = int(lg["topics"][2],16)
    print("  blk=%d %s owner=%s tokenId=%d amount=%.4f tx=%s" % (
        b, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(bts)), owner, tid, amt,
        lg["transactionHash"]))

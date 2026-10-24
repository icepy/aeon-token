#!/usr/bin/env python3
"""Decode the two escrow events (Burn n=2, other n=2) from the histogram, with time + full context."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
d = json.load(open("output/escrow_hist.json"))
hist = d["hist"]; samples = d["samples"]

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last=None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                rd = json.loads(r.read().decode())
            if "error" in rd: raise RuntimeError(rd["error"])
            return rd["result"]
        except Exception as e:
            last=e; time.sleep(1.2*(2**i))
    raise last

def blk(n): return rpc("eth_getBlockByNumber", [hex(n), False])
def ts(n): return int(blk(n)["timestamp"],16)

BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
head = int(rpc("eth_blockNumber", []), 16)
hts = ts(head)
lo, hi = head - 60000, head
target = hts - 86400
while lo + 1 < hi:
    mid=(lo+hi)//2
    if ts(mid) <= target: lo = mid
    else: hi = mid
b24 = lo

logs = []
cursor = b24
while cursor < head:
    hi2 = min(cursor+999, head)
    try:
        logs.extend(rpc("eth_getLogs", [{"address":ESCROW,"fromBlock":hex(cursor),
                                         "toBlock":hex(hi2),"topics":[BURN]}], retries=2))
    except Exception: pass
    cursor = hi2+1
print("burn_events_24h=%d" % len(logs))
for lg in logs:
    b = int(lg["blockNumber"],16); bts = ts(b)
    w = lg["data"][2:]
    amt = int(w[0:64],16)/1e18
    tstamp = int(w[64:128],16)
    bal_after = int(w[128:192],16)/1e18
    owner = "0x"+lg["topics"][1][-40:]
    tid = int(lg["topics"][2],16)
    print("  blk=%d %s (%d min ago) owner=%s tokenId=%d amount=%.4f escrowAfter=%.4f tx=%s" % (
        b, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(bts)), (hts-bts)//60,
        owner, tid, amt, bal_after, lg["transactionHash"]))

# other topic0, for completeness
OTHER = "0x7162984403f6c73c8639375d45a9187dfd04602231bd8e587c415718b5f7e5f9"
print("\n-- other event (stake side) 24h --")
ol = []
cursor = b24
while cursor < head:
    hi2 = min(cursor+999, head)
    try:
        ol.extend(rpc("eth_getLogs", [{"address":ESCROW,"fromBlock":hex(cursor),
                                       "toBlock":hex(hi2),"topics":[OTHER]}], retries=2))
    except Exception: pass
    cursor = hi2+1
print("count=%d" % len(ol))
for lg in ol:
    b = int(lg["blockNumber"],16); bts = ts(b)
    w = lg["data"][2:]
    vals = [int(w[i*64:(i+1)*64],16) for i in range(3)]
    print("  blk=%d %s topics=%s data=%s tx=%s" % (
        b, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(bts)),
        [t[-40:] for t in lg["topics"][1:]], vals, lg["transactionHash"][:20]))

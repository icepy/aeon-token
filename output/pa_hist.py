#!/usr/bin/env python3
"""Histogram topic0 on the escrow contract first, then filter with the CORRECT 64-hex hash."""
import json, time, urllib.request, collections

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

def blk(n): return rpc("eth_getBlockByNumber", [hex(n), False])
def ts(n): return int(blk(n)["timestamp"],16)

head = int(rpc("eth_blockNumber", []), 16)
hts = ts(head)
print("head=%d %s" % (head, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hts))))

lo, hi = head - 60000, head
target = hts - 86400
while lo + 1 < hi:
    mid = (lo+hi)//2
    if ts(mid) <= target: lo = mid
    else: hi = mid
b24 = lo
print("24h_block=%d delta=%ds" % (b24, hts - ts(b24)))

ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"

# STEP 1: histogram topic0s by address only (no topic filter) over a 24h window
hist = collections.Counter()
samples = {}
failed = 0
cursor = b24
while cursor < head:
    hi2 = min(cursor + 999, head)
    try:
        got = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(cursor), "toBlock": hex(hi2)}], retries=2)
        for lg in got:
            t0 = lg["topics"][0]
            hist[t0] += 1
            samples.setdefault(t0, lg)
    except Exception:
        failed += 1
    cursor = hi2 + 1

print("failed_chunks=%d total_logs=%d distinct_topic0=%d" % (failed, sum(hist.values()), len(hist)))
for t0, n in hist.most_common():
    lg = samples[t0]
    print("  %s  n=%d  topics=%d datalen=%d tx=%s" % (t0, n, len(lg["topics"]), len(lg["data"])//2, lg["transactionHash"][:14]))

with open("output/escrow_hist.json","w") as f:
    json.dump({"head":head,"b24":b24,"hist":dict(hist),"samples":samples}, f)
print("saved output/escrow_hist.json")

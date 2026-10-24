#!/usr/bin/env python3
"""24h block-pinned deltas: DEUS supply, CLAIM vault, escrow. Plus topic-hash length audit."""
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
                rd = json.loads(r.read().decode())
            if "error" in rd: raise RuntimeError(rd["error"])
            return rd["result"]
        except Exception as e:
            last=e; time.sleep(1.2*(2**i))
    raise last

def calli(to,data,tag="latest"):
    r = rpc("eth_call", [{"to":to,"data":data}, tag])
    return int(r[2:][0:64],16) if r and len(r)>=66 else None
def blk(n): return rpc("eth_getBlockByNumber",[hex(n),False])
def ts(n): return int(blk(n)["timestamp"],16)
def pad(a): return a.lower().replace("0x","").rjust(64,"0")

head = int(rpc("eth_blockNumber", []),16); hts = ts(head)
lo,hi = head-60000, head; target = hts-86400
while lo+1 < hi:
    mid=(lo+hi)//2
    if ts(mid)<=target: lo=mid
    else: hi=mid
b24 = lo
print("head=%d %s" % (head, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hts))))
print("24h_block=%d delta=%ds" % (b24, hts-ts(b24)))

DEUS="0x940a319b75861014a220d9c6c144d108552b089b"
CLAIM="0x5cbf5dfaa5336ce0456e24217e7911365100879a"
ESCROW="0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS="0xe6d5f7439Bc236C40054e2275f765f59343D4431"

def at(tag):
    return {
      "supply": calli(DEUS,"0x18160ddd",tag)/1e18,
      "claim": calli(DEUS,"0x70a08231"+pad(CLAIM),tag)/1e18,
      "escrow": calli(DEUS,"0x70a08231"+pad(ESCROW),tag)/1e18,
      "xdeus": calli(XDEUS,"0x18160ddd",tag),
    }

now = at("latest"); past = at(hex(b24))
print("\nDEUS supply : %.6f -> %.6f  delta=%+.4f" % (past["supply"], now["supply"], now["supply"]-past["supply"]))
print("CLAIM vault : %.4f -> %.4f  delta=%+.4f" % (past["claim"], now["claim"], now["claim"]-past["claim"]))
print("escrow      : %.6f -> %.6f  delta=%+.4f" % (past["escrow"], now["escrow"], now["escrow"]-past["escrow"]))
print("xDEUS       : %d -> %d  delta=%+d" % (past["xdeus"], now["xdeus"], now["xdeus"]-past["xdeus"]))
print("escrow 5%%/day line=%.0f  ratio=%.3fx" % (past["escrow"]*0.05, abs(now["escrow"]-past["escrow"])/(past["escrow"]*0.05)))
print("claim pct of supply=%.2f%%" % (now["claim"]/now["supply"]*100))

print("\n-- topic0 hash length audit --")
stored_burn = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7adfabb7cd8caa254de14def35"
real_burn   = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
for name,h in [("stored",stored_burn),("real_onchain",real_burn)]:
    body = h[2:]
    print("  %-13s len(hex)=%d %s %s" % (name, len(body), "OK" if len(body)==64 else "MALFORMED",
          h if len(body)!=64 else ""))

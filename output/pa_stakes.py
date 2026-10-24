#!/usr/bin/env python3
"""Decode the stake-side event (topic0 0x71629844...) to reconcile escrow 24h balance."""
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

def blk(n): return rpc("eth_getBlockByNumber",[hex(n),False])
def ts(n): return int(blk(n)["timestamp"],16)
def calli(to,data,tag="latest"):
    r = rpc("eth_call",[{"to":to,"data":data},tag])
    return int(r[2:][0:64],16) if r and len(r)>=66 else None
def pad(a): return a.lower().replace("0x","").rjust(64,"0")

ESCROW="0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
DEUS="0x940a319b75861014a220d9c6c144d108552b089b"
STAKE="0x7162984403f6c73c8639375d45a9187dfd04602231bd8e587c415718b5f7e5f9"

head=int(rpc("eth_blockNumber",[]),16); hts=ts(head)
lo,hi=head-60000,head; target=hts-86400
while lo+1<hi:
    mid=(lo+hi)//2
    if ts(mid)<=target: lo=mid
    else: hi=mid
b24=lo
print("head=%d %s | b24=%d" % (head, time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(hts)), b24))

logs=[]
c=b24
while c<head:
    h2=min(c+999,head)
    try:
        logs.extend(rpc("eth_getLogs",[{"address":ESCROW,"fromBlock":hex(c),"toBlock":hex(h2),"topics":[STAKE]}],retries=2))
    except Exception: pass
    c=h2+1
print("stake_events_24h=%d" % len(logs))
tot=0
for lg in logs:
    b=int(lg["blockNumber"],16); bts=ts(b)
    w=lg["data"][2:]
    nwords=len(w)//64
    vals=[int(w[i*64:(i+1)*64],16) for i in range(nwords)]
    sender="0x"+lg["topics"][1][-40:]
    print("  blk=%d %s sender=%s nwords=%d vals=%s tx=%s" % (
        b, time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(bts)), sender, nwords,
        [v/1e18 if v>1e15 else v for v in vals], lg["transactionHash"]))
    if nwords>=1 and vals[0]>1e15: tot+=vals[0]/1e18
print("total_staked_1e18_scale=%.4f" % tot)

# reconciliaton
e24=calli(DEUS,"0x70a08231"+pad(ESCROW),hex(b24))/1e18
en =calli(DEUS,"0x70a08231"+pad(ESCROW),"latest")/1e18
print("\nescrow 24h: %.6f -> %.6f delta=%+.6f" % (e24,en,en-e24))
print("burns: 319562.2265 + 5000.0000 = 324562.2265")
print("implied stakes = %.6f" % (324562.2265 + (en-e24)))

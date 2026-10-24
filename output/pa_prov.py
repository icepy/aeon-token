#!/usr/bin/env python3
"""Provenance of the 02:00:15Z staker 0x8d834919 + gate distances at the current mark."""
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
    r=rpc("eth_call",[{"to":to,"data":data},tag])
    return int(r[2:][0:64],16) if r and len(r)>=66 else None
def pad(a): return a.lower().replace("0x","").rjust(64,"0")
def blk(n): return rpc("eth_getBlockByNumber",[hex(n),False])
def ts(n): return int(blk(n)["timestamp"],16)

head=int(rpc("eth_blockNumber",[]),16); hts=ts(head)
STAKER="0x8d834919956af4f696f729bdcaba61c9f16529f5"
DEUS="0x940a319b75861014a220d9c6c144d108552b089b"
XDEUS="0xe6d5f7439Bc236C40054e2275f765f59343D4431"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

print("head=%d %s" % (head, time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(hts))))
code = rpc("eth_getCode",[STAKER,"latest"])
nonce = rpc("eth_getTransactionCount",[STAKER,"latest"])
bal = calli(DEUS,"0x70a08231"+pad(STAKER))
xnft = calli(XDEUS,"0x70a08231"+pad(STAKER))
eth = rpc("eth_getBalance",[STAKER,"latest"])
print("0x8d834919 code_len=%d nonce=%d deus=%.4f xdeus_nfts=%d eth=%.6f" % (
    len(code), int(nonce,16), bal/1e18, xnft or 0, int(eth,16)/1e18))
print("  code_prefix=%s" % code[:74])

# incoming DEUS transfers in last 30000 blocks (topic1 = from, topic2 = to)
to_topic = "0x" + pad(STAKER)
lo = head - 30000
logs=[]
c=lo
while c<head:
    h2=min(c+999,head)
    try:
        logs.extend(rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(c),"toBlock":hex(h2),
                     "topics":[TRANSFER,None,to_topic]}],retries=2))
    except Exception: pass
    c=h2+1
print("incoming_deus_transfers_last_30000_blk=%d" % len(logs))
for lg in logs[-8:]:
    b=int(lg["blockNumber"],16); bts=ts(b)
    amt=int(lg["data"][2:][0:64],16)/1e18
    frm="0x"+lg["topics"][1][-40:]
    print("  blk=%d %s from=%s amt=%.4f tx=%s" % (
        b, time.strftime("%m-%dT%H:%M:%SZ",time.gmtime(bts)), frm, amt, lg["transactionHash"][:18]))

# gate distances
P = 0.01744603
print("\n-- gate distances at mark $%.8f --" % P)
for t in [0.012,0.025,0.032,0.041]:
    print("  $%-6s %+8.2f%%" % (t, (t/P-1)*100))
print("  ATH $0.06876 %+8.2f%% above current" % ((0.06876/P-1)*100))
print("  current is %.2f%% below ATH" % ((1-P/0.06876)*100))

import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
TR   = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0"*64
_id=[15000]
def rpc(m,p):
    _id[0]+=1
    body=json.dumps({"jsonrpc":"2.0","id":_id[0],"method":m,"params":p}).encode()
    for a in range(6):
        req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=45) as r: j=json.loads(r.read())
            if "error" in j: raise RuntimeError(f"{m}: {j['error']}")
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<5: time.sleep(2+3*a); continue
            raise
def ts(n): return int(rpc("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)

head=int(rpc("eth_blockNumber",[]),16)
lo,hi=53061405,53062305   # 07:09 -> 07:39 window where supply jumped

mints=[]; burns=[]
b=lo
while b<=hi:
    e=min(b+999,hi)
    for lg in rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(b),"toBlock":hex(e),"topics":[TR,ZERO]}]):
        mints.append(lg)
    for lg in rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(b),"toBlock":hex(e),"topics":[TR,None,ZERO]}]):
        burns.append(lg)
    b=e+1

def terr(n): return time.strftime("%m-%d %H:%M:%SZ",time.gmtime(ts(n)))
out_mints=[{"blk":int(l["blockNumber"],16),"iso":terr(int(l["blockNumber"],16)),
            "to":"0x"+l["topics"][2][-40:],"amount":int(l["data"],16)/1e18,
            "tx":l["transactionHash"]} for l in mints]
out_burns=[{"blk":int(l["blockNumber"],16),"iso":terr(int(l["blockNumber"],16)),
            "from":"0x"+l["topics"][1][-40:],"amount":int(l["data"],16)/1e18,
            "tx":l["transactionHash"]} for l in burns]

# control: corrupt topic0
BAD=TR[:-1]+("1" if TR[-1]!="1" else "2")
ctl_t=len(rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(lo),"toBlock":hex(min(lo+999,hi)),"topics":[TR]}]))
ctl_f=len(rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(lo),"toBlock":hex(min(lo+999,hi)),"topics":[BAD]}]))

# classify recipients: EOA vs contract
def code(a):
    return rpc("eth_getCode",[a,hex(head)])

for m in out_mints:
    m["code"]=code(m["to"])[:20]
print(json.dumps({"window":[lo,hi],"mints":out_mints,"burns":out_burns,
  "mint_total":sum(m["amount"] for m in out_mints),
  "burn_total":sum(x["amount"] for x in out_burns),
  "control":{"true":ctl_t,"corrupt":ctl_f}},indent=1))

import json, urllib.request, time
RPC="https://base.gateway.tenderly.co"
DEUS="0x940A319B75861014A220D9c6c144d108552B089B"
TR="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
W="0x42a1647e8a77f8325a7c7bf06096cda477915d39"
_id=[19000]
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
def iso(n): return time.strftime("%m-%d %H:%M:%SZ",time.gmtime(ts(n)))
def code(a,n):
    c=rpc("eth_getCode",[a,hex(n)])
    if c=="0x": return "EOA"
    if c.startswith("0xef0100"): return "EIP7702:"+c[8:48]
    return "CONTRACT:"+c[:10]

head=int(rpc("eth_blockNumber",[]),16)
MINT_BLK=53061481
topic_w="0x"+"0"*24+W[2:].lower()

outs=[]
b=MINT_BLK
while b<=head:
    e=min(b+999,head)
    outs.extend(rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(b),"toBlock":hex(e),"topics":[TR,topic_w]}]))
    b=e+1

# also anything received
ins=[]
b=MINT_BLK
while b<=head:
    e=min(b+999,head)
    ins.extend(rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(b),"toBlock":hex(e),"topics":[TR,None,topic_w]}]))
    b=e+1

rows=[]
for l in outs:
    n=int(l["blockNumber"],16)
    rows.append({"dir":"OUT","blk":n,"iso":iso(n),"other":"0x"+l["topics"][2][-40:],
                 "amount":int(l["data"],16)/1e18,"tx":l["transactionHash"],
                 "other_type":code("0x"+l["topics"][2][-40:],n)})
for l in ins:
    n=int(l["blockNumber"],16)
    rows.append({"dir":"IN","blk":n,"iso":iso(n),"other":"0x"+l["topics"][1][-40:],
                 "amount":int(l["data"],16)/1e18,"tx":l["transactionHash"],
                 "other_type":code("0x"+l["topics"][1][-40:],n)})
rows.sort(key=lambda r:r["blk"])
print(json.dumps({"head":head,"wallet":W,"outs":rows},indent=1))

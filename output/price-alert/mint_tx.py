import json, urllib.request, time
RPC="https://base.gateway.tenderly.co"
TX="0xa83d52f2e9d045ba52355e8b250243635aaa25c0e4a06fc4c91e22026804d68e"
TO="0x42a1647e8a77f8325a7c7bf06096cda477915d39"
DEUS="0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW="0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
_id=[17000]
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
def bal(a,n):
    return int(rpc("eth_call",[{"to":DEUS,"data":"0x70a08231"+"0"*24+a[2:].lower()},hex(n)]),16)/1e18

tx=rpc("eth_getTransactionByHash",[TX])
rc=rpc("eth_getTransactionReceipt",[TX])
blk=int(rc["blockNumber"],16)
print(json.dumps({
 "blk":blk,"iso":time.strftime("%FT%TZ",time.gmtime(ts(blk))),
 "from":tx["from"],"to":tx["to"],"value":int(tx["value"],16),
 "input_selector":tx["input"][:10],"input_len":len(tx["input"]),
 "status":rc["status"],"gasUsed":int(rc["gasUsed"],16),
 "n_logs":len(rc["logs"]),
 "log_addrs":sorted({l["address"] for l in rc["logs"]}),
 "target_code_prefix":rpc("eth_getCode",[TO,hex(blk)])[:80],
 "bal_target_now":bal(TO,int(rpc("eth_blockNumber",[]),16)),
 "bal_target_after":bal(TO,blk),
 "bal_escrow_at_blk":bal(ESCROW,blk),
},indent=1))

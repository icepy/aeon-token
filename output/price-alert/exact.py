import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VP   = "0x529d2863a1521d0b57db028168fdE2E97120017C"
_id=[9000]
def rpc(m,p):
    _id[0]+=1
    body=json.dumps({"jsonrpc":"2.0","id":_id[0],"method":m,"params":p}).encode()
    for a in range(6):
        req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=45) as r: j=json.loads(r.read())
            if "error" in j: raise RuntimeError(j["error"])
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<5: time.sleep(2+3*a); continue
            raise

def ts(n): return int(rpc("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)

head=int(rpc("eth_blockNumber",[]),16); HTS=ts(head)
def find(target):
    lo,hi=head-60000,head
    while int(rpc("eth_getBlockByNumber",[hex(lo),False])["timestamp"],16) > target:
        lo -= 20000
    while lo<hi:
        mid=(lo+hi+1)//2
        if ts(mid)<=target: lo=mid
        else: hi=mid-1
    return lo

def snap(n):
    raw=rpc("eth_call",[{"to":POOL,"data":"0x0902f1ac"},hex(n)])[2:]
    v=int(raw[0:64],16)/1e18; d=int(raw[64:128],16)/1e18
    s=rpc("eth_call",[{"to":VP,"data":"0x3850c7bd"},hex(n)])[2:]
    sp=int(s[0:64],16); pu=(sp/2**96)**2*1e12
    return {"blk":n,"ts":ts(n),"virtual":v,"deus":d,"virt_usd":pu,"ratio":v/d,"mark":(v/d)*pu}

n1=find(HTS-3600); n24=find(HTS-86400)
h=snap(head); a=snap(n1); b=snap(n24)
print(json.dumps({
 "head":{"blk":h["blk"],"ts":h["ts"],"iso":time.strftime("%FT%TZ",time.gmtime(h["ts"])),"mark":h["mark"]},
 "h1":{"blk":a["blk"],"ts":a["ts"],"iso":time.strftime("%FT%TZ",time.gmtime(a["ts"])),"delta_s":HTS-a["ts"],"mark":a["mark"]},
 "h24":{"blk":b["blk"],"ts":b["ts"],"iso":time.strftime("%FT%TZ",time.gmtime(b["ts"])),"delta_s":HTS-b["ts"],"mark":b["mark"]},
 "h1_pct":(h["mark"]/a["mark"]-1)*100,
 "h24_pct":(h["mark"]/b["mark"]-1)*100,
 "legs_1h":{"ratio":(h["ratio"]/a["ratio"]-1)*100,"virtual":(h["virt_usd"]/a["virt_usd"]-1)*100},
 "legs_24h":{"ratio":(h["ratio"]/b["ratio"]-1)*100,"virtual":(h["virt_usd"]/b["virt_usd"]-1)*100},
 "ratio":h["ratio"],"virt_usd":h["virt_usd"],"mark":h["mark"],
 "reserves_head":{"virtual":h["virtual"],"deus":h["deus"]},
},indent=1))

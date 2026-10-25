import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
_id=[13000]
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
def supply(n):
    return int(rpc("eth_call",[{"to":DEUS,"data":"0x18160ddd"},hex(n)]),16)/1e18
def ts(n): return int(rpc("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)

head=int(rpc("eth_blockNumber",[]),16); HTS=ts(head)
def find(t):
    lo,hi=head-60000,head
    while int(rpc("eth_getBlockByNumber",[hex(lo),False])["timestamp"],16)>t: lo-=20000
    while lo<hi:
        mid=(lo+hi+1)//2
        if ts(mid)<=t: lo=mid
        else: hi=mid-1
    return lo

pts=[]
for back in (0, 900, 1800, 3600, 21600, 43200, 64800, 86400, 172800):
    n = head if back==0 else find(HTS-back)
    pts.append({"back_s":back,"blk":n,"ts":ts(n),"iso":time.strftime("%FT%TZ",time.gmtime(ts(n))),"supply":supply(n)})

# also the 07:01Z run's head block, for cross-check against memory's -12373.69
n07=53061213
pts.append({"back_s":"07:01Z_run_head","blk":n07,"ts":ts(n07),"iso":time.strftime("%FT%TZ",time.gmtime(ts(n07))),"supply":supply(n07)})
pts.append({"back_s":"07:01Z_minus_24h","blk":find(ts(n07)-86400),"ts":ts(find(ts(n07)-86400)),"iso":time.strftime("%FT%TZ",time.gmtime(ts(find(ts(n07)-86400)))),"supply":supply(find(ts(n07)-86400))})

for p in pts[:-2]:
    if p["back_s"] not in (0,):
        p["delta_vs_now"]=round(pts[0]["supply"]-p["supply"],6)
print(json.dumps({"head":head,"points":pts},indent=1))

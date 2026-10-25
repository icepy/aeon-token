import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
PREV = {  # from 07:01Z run (memory + state)
 "0x92325e5a": None, "0x4e3ae00e": None, "0x9d1c316f": None, "0xbb0f7533": None,
}
WALLETS = {
 "inventory_sink_0x92325e5a": "0x92325e5a",  # prefix only -> need full addr
}
_ids=[7000]
def rpc(m,p):
    _ids[0]+=1
    body=json.dumps({"jsonrpc":"2.0","id":_ids[0],"method":m,"params":p}).encode()
    for a in range(6):
        req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=45) as r:
                j=json.loads(r.read())
            if "error" in j: raise RuntimeError(j["error"])
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<5: time.sleep(2+3*a); continue
            raise

head=int(rpc("eth_blockNumber",[]),16)

# find full addresses from state's inventory/holder keys
st=json.load(open("memory/topics/price-alert-state.json"))
def walk(o,p=""):
    out=[]
    if isinstance(o,dict):
        for k,v in o.items(): out+=walk(v,p+"/"+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): out+=walk(v,p+f"/{i}")
    else:
        out.append((p,o))
    return out
hits={}
for p,v in walk(st):
    if isinstance(v,str):
        s=v
        for pref in ("0x92325e5a","0x4e3ae00e","0x9d1c316f","0xbb0f7533"):
            if pref in s.lower():
                i=s.lower().index(pref)
                cand=s[i:i+42]
                if len(cand)==42 and all(c in "0123456789abcdefABCDEFx" for c in cand):
                    hits.setdefault(pref,set()).add(cand)

res={}
for pref,addrs in hits.items():
    for a in addrs:
        bal=int(rpc("eth_call",[{"to":DEUS,"data":"0x70a08231"+"0"*24+a[2:].lower()},hex(head)]),16)
        res[a]=round(bal/1e18,8)

print(json.dumps({"head":head,"balances":res,
  "candidates":{k:sorted(v) for k,v in hits.items()}},indent=1))

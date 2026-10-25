import json, urllib.request, time
RPC="https://base.gateway.tenderly.co"
DEUS="0x940A319B75861014A220D9c6c144d108552B089B"
_id=[23000]
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
def bal(a,n):
    return int(rpc("eth_call",[{"to":DEUS,"data":"0x70a08231"+"0"*24+a[2:].lower()},hex(n)]),16)/1e18
def ts(n): return int(rpc("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)

W=[("0x4af20629b81dd0ddef1bbac1b72b4c1594a18f9a",8612.177673333446),
   ("0x393f8accc70a73862ecda51bd3b1395e55631f3b",12951.379476673497),
   ("0x5318d687f24c9bbfc3ac67b27331d96c117e777c",14621.912849993054),
   ("0x380ce63e3368e2dff6ba351647eb9396815ce61e",6970.444099295909),
   ("0xfb4224282a67cff86b7780d408e2c4da840f6c78",11926.293411159739),
   ("0x9be2134e02465ce9b20ce99d6160e9a6a46677ee",7593.334848594693),
   ("0xd50de17126280a31afee93d5e4d830233e19473d",10459.28808898746),
   ("0x3d1aa83e5bf6b3d254e8f56b587b034613529c8e",12694.079551962197)]

head=int(rpc("eth_blockNumber",[]),16)
HTS=ts(head)
def find(t):
    lo,hi=head-60000,head
    while int(rpc("eth_getBlockByNumber",[hex(lo),False])["timestamp"],16)>t: lo-=20000
    while lo<hi:
        mid=(lo+hi+1)//2
        if ts(mid)<=t: lo=mid
        else: hi=mid-1
    return lo
B7=find(HTS-7*86400); B30=find(HTS-30*86400)
PRE=53061480

rows=[]
for a,amt in W:
    pre=bal(a,PRE); now=bal(a,head); d7=bal(a,B7); d30=bal(a,B30)
    rows.append({"w":a[:10],"pre_mint":round(pre,2),"mint":round(amt,2),
                 "now":round(now,2),"d30":round(d30,2),"d7":round(d7,2),
                 "held_before_any":pre>0.01,
                 "delta_now":round(now-pre,2)})
print(json.dumps({"head":head,"blk_7d":B7,"blk_30d":B30,"pre_blk":PRE,
  "sum_pre":round(sum(r["pre_mint"] for r in rows),2),
  "sum_now":round(sum(r["now"] for r in rows),2),
  "sum_d30":round(sum(r["d30"] for r in rows),2),
  "sum_d7":round(sum(r["d7"] for r in rows),2),
  "all_had_balance_before":all(r["held_before_any"] for r in rows),
  "rows":rows},indent=1))

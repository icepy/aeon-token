import json, urllib.request, time, math

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VP   = "0x529d2863a1521d0b57db028168fdE2E97120017C"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
_id=[11000]
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

head=int(rpc("eth_blockNumber",[]),16)
B24=53019978   # ts 86400s before head from exact.py

def esc_bal(n):
    return int(rpc("eth_call",[{"to":DEUS,"data":"0x70a08231"+"0"*24+ESCROW[2:].lower()},hex(n)]),16)/1e18
def supply(n):
    return int(rpc("eth_call",[{"to":DEUS,"data":"0x18160ddd"},hex(n)]),16)/1e18

raw=rpc("eth_call",[{"to":POOL,"data":"0x0902f1ac"},hex(head)])[2:]
V=int(raw[0:64],16)/1e18; D=int(raw[64:128],16)/1e18
s=rpc("eth_call",[{"to":VP,"data":"0x3850c7bd"},hex(head)])[2:]
virt=(int(s[0:64],16)/2**96)**2*1e12
mark=(V/D)*virt
k=V*D

def cost_to(target):
    r = target/virt
    Dn = math.sqrt(k/r); Vn = math.sqrt(k*r)
    deus_out = D-Dn; virt_in = Vn-V
    return {"deus": deus_out, "virtual": virt_in, "usd": virt_in*virt,
            "depth_consumed_pct": (1-Dn/D)*100}

e_now=esc_bal(head); e_24=esc_bal(B24)
s_now=supply(head); s_24=supply(B24)

# xDEUS #1396 owner
try:
    o=rpc("eth_call",[{"to":XDEUS,"data":"0x6352211e"+hex(1396)[2:].rjust(64,"0")},hex(head)])
    owner="0x"+o[-40:]
except Exception as ex:
    owner=f"err: {ex}"

print(json.dumps({
 "head":head,"V":V,"D":D,"virt_usd":virt,"mark":mark,"k":k,
 "level_cost":{f"{t}":cost_to(t) for t in (0.012,0.025,0.032,0.041)},
 "escrow":{"now":e_now,"h24":e_24,"delta":e_now-e_24,"delta_pct":(e_now/e_24-1)*100},
 "supply":{"now":s_now,"h24":s_24,"delta":s_now-s_24},
 "xdeus_1396_owner":owner,
},indent=1))

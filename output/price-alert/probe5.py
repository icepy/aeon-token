#!/usr/bin/env python3
"""Probe 5: fix the V3 orientation (usd_per_deus = 1e12 / p_raw) and get VIRTUAL h24."""
import json, urllib.request

RPC = "https://base.gateway.tenderly.co"
def rpc(m, p):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json","User-Agent":"curl/8.5.0"})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())

def call(to,data):
    d=rpc("eth_call",[{"to":to,"data":data},"latest"]); return d.get("result")

out={}
V3={"0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b":0,
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642":0,
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3":0}
for pool in V3:
    sl=call(pool,"0x3850c7bd")
    sq=int(sl[2:][0:64],16)
    p_raw=(sq/2**96)**2          # token1_raw per token0_raw = DEUS_raw(18) per USDC_raw(6)
    deus_per_usdc = p_raw*1e6/1e18
    V3[pool]={"sqrtPriceX96":str(sq),"deus_per_usdc":round(deus_per_usdc,4),
              "usd_per_deus":round(1/deus_per_usdc,8)}
out["v3_marks"]=V3
vals=sorted(v["usd_per_deus"] for v in V3.values())
out["v3_median"]=vals[len(vals)//2]

# VIRTUAL h24
req=urllib.request.Request("https://api.dexscreener.com/latest/dex/tokens/0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b",
                           headers={"User-Agent":"curl/8.5.0"})
with urllib.request.urlopen(req,timeout=25) as r: d=json.loads(r.read().decode())
rows=[]
for p in d.get("pairs") or []:
    if not p.get("priceUsd"): continue
    rows.append({"dex":p.get("dexId"),"pair":p.get("pairAddress"),
                 "price":float(p["priceUsd"]),
                 "h1":(p.get("priceChange") or {}).get("h1"),
                 "h24":(p.get("priceChange") or {}).get("h24"),
                 "liq":(p.get("liquidity") or {}).get("usd") or 0,
                 "v1h":(p.get("volume") or {}).get("h1") or 0})
rows.sort(key=lambda x:-x["liq"])
out["virtual_top"]=rows[:6]
live=[x for x in rows if x["v1h"]>0]
out["virtual_live_median"]=sorted(x["price"] for x in live)[len(live)//2]
h24s=[x["h24"] for x in live if x["h24"] is not None]
out["virtual_live_median_h24"]=sorted(h24s)[len(h24s)//2] if h24s else None

print(json.dumps(out,indent=2))

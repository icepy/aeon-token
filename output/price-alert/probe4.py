#!/usr/bin/env python3
"""Probe 4: cross-venue mark check, the 16,528 sell origin, the new 10,905 staker, NFT 1396."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

def rpc(method, params, retries=4):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    delay=1; last=None
    for _ in range(retries):
        try:
            req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req,timeout=30) as r: d=json.loads(r.read().decode())
            if "error" in d:
                last=d["error"]; m=json.dumps(d["error"])
                if "-32005" in m or "rate" in m.lower() or "too large" in m.lower():
                    time.sleep(delay); delay*=2; continue
                raise RuntimeError(m)
            return d.get("result")
        except Exception as e:
            last=e; time.sleep(delay); delay*=2
    raise RuntimeError(f"{method}: {last}")

def call(to,data,tag="latest"): return rpc("eth_call",[{"to":to,"data":data},tag])
def hexint(x): return int(x,16) if x and x!="0x" else 0
def pad(a): return "0x"+a[2:].rjust(64,"0")
def s256(h,i):
    s=h[2:] if h.startswith("0x") else h
    return int(s[i*64:(i+1)*64],16)

out={}
head=hexint(rpc("eth_blockNumber",[]))
hb=rpc("eth_getBlockByNumber",[hex(head),False]); head_ts=hexint(hb["timestamp"])
out["head_block"]=head; out["head_ts"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(head_ts))

# --- USDC V3 pools live mark: sqrtPriceX96, token0=USDC(6dp) token1=DEUS(18dp) => invert ---
V3 = {
 "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": "primary USDC venue",
 "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": "USDC venue 2",
 "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": "USDC venue 3",
}
marks={}
for pool,label in V3.items():
    try:
        t0="0x"+call(pool,"0x0dfe1681")[2:][24:64]
        t1="0x"+call(pool,"0xd21220a7")[2:][24:64]
        sl=call(pool,"0x3850c7bd")  # slot0()
        sq=s256(sl,0)
        # price token1/token0 raw = (sqrtPriceX96/2^96)^2
        p_raw=(sq/2**96)**2
        # token0=USDC 6dp, token1=DEUS 18dp: raw = DEUS_raw per USDC_raw
        # USD per DEUS = (1e6/1e18) / p_raw  ... verify orientation below
        usd_per_deus = (1e6/1e18)/p_raw
        liq=hexint(call(pool,"0x1a686502"))/1e18  # liquidity() -> L
        marks[pool]={"label":label,"token0":t0,"token1":t1,"sqrtPriceX96":str(sq),
                     "usd_per_deus":round(usd_per_deus,8),"L":liq}
    except Exception as e:
        marks[pool]={"label":label,"err":str(e)}
out["v3_marks"]={k:v for k,v in marks.items()}
vals=[v["usd_per_deus"] for v in marks.values() if "usd_per_deus" in v]
if vals:
    vals.sort(); out["v3_median_usd_per_deus"]=vals[len(vals)//2]

# --- the 16,528 sell: trace origin of 0x8180513f ---
SELLER="0x8180513f9a155233cfc16e94c82cbcf82966d04d"
try:
    code=rpc("eth_getCode",[SELLER,"latest"]); out["seller_code"]=code[:80]
    nonce=rpc("eth_getTransactionCount",[SELLER,"latest"]); out["seller_nonce"]=hexint(nonce)
    out["seller_deus_balance"]=hexint(call(DEUS,"0x70a08231"+pad(SELLER)[2:]))/1e18
    # incoming DEUS transfers in last 40k blocks
    inc=[]
    s=head-40000
    while s<=head:
        e=min(s+999,head)
        try:
            for l in rpc("eth_getLogs",[{"address":DEUS,"topics":[TRANSFER,None,pad(SELLER)],
                                        "fromBlock":hex(s),"toBlock":hex(e)}]) or []:
                inc.append({"blk":hexint(l["blockNumber"]),"from":"0x"+l["topics"][1][-40:],
                            "deus":round(int(l["data"][2:][0:64],16)/1e18,4)})
        except Exception: pass
        s=e+1
    out["seller_incoming_deus_40k"]=inc[-12:]
    out["seller_incoming_count"]=len(inc)
except Exception as e:
    out["seller_err"]=str(e)

# --- new 10,905 staker ---
NEW_STAKER="0x2c81beef5814dfb9794535c0cca5776a7614c642"
try:
    out["staker_code"]=rpc("eth_getCode",[NEW_STAKER,"latest"])[:80]
    out["staker_nonce"]=hexint(rpc("eth_getTransactionCount",[NEW_STAKER,"latest"]))
    out["staker_deus_bal"]=hexint(call(DEUS,"0x70a08231"+pad(NEW_STAKER)[2:]))/1e18
    out["staker_xdeus_bal"]=hexint(call(XDEUS,"0x70a08231"+pad(NEW_STAKER)[2:]))
    eth=hexint(rpc("eth_getBalance",[NEW_STAKER,"latest"]))/1e18
    out["staker_eth"]=eth
    inc=[]
    s=head-30000
    while s<=head:
        e=min(s+999,head)
        try:
            for l in rpc("eth_getLogs",[{"address":DEUS,"topics":[TRANSFER,None,pad(NEW_STAKER)],
                                        "fromBlock":hex(s),"toBlock":hex(e)}]) or []:
                inc.append({"blk":hexint(l["blockNumber"]),"from":"0x"+l["topics"][1][-40:],
                            "deus":round(int(l["data"][2:][0:64],16)/1e18,4)})
        except Exception: pass
        s=e+1
    out["staker_incoming_deus_30k"]=inc[-10:]
    out["staker_incoming_count"]=len(inc)
except Exception as e:
    out["staker_err"]=str(e)

# --- xDEUS NFT 1396 owner re-check + total supply ---
try:
    bal=hexint(call(XDEUS,"0x70a08231"+pad("0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63")[2:]))
    out["xdeus_bal_0xbb0f7533"]=bal
    if bal>0:
        r=call(XDEUS,"0x2f745c59"+pad("0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63")[2:]+"0"*64)
        out["nft_tokenOfOwnerByIndex_0"]=s256(r,0)
    out["xdeus_totalSupply"]=hexint(call(XDEUS,"0x18160ddd"))
except Exception as e:
    out["xdeus_err"]=str(e)

# --- CLAIM vault 24h net out ---
CLAIM="0x5cbf5dfaa5336ce0456e24217e7911365100879a"
try:
    blk24=52989207
    out["claim_now"]=hexint(call(DEUS,"0x70a08231"+pad(CLAIM)[2:]))/1e18
    out["claim_24h_ago"]=hexint(call(DEUS,"0x70a08231"+pad(CLAIM)[2:],hex(blk24)))/1e18
    out["claim_net_out_24h"]=round(out["claim_24h_ago"]-out["claim_now"],4)
except Exception as e:
    out["claim_err"]=str(e)

# --- DEXScreener deepest pair h1 for the record ---
try:
    req=urllib.request.Request(f"https://api.dexscreener.com/latest/dex/tokens/{DEUS}",headers={"User-Agent":"curl/8.5.0"})
    with urllib.request.urlopen(req,timeout=25) as r: d=json.loads(r.read().decode())
    rows=[{"pair":p.get("pairAddress"),"dex":p.get("dexId"),
           "price":p.get("priceUsd"),"h1":(p.get("priceChange") or {}).get("h1"),
           "h24":(p.get("priceChange") or {}).get("h24"),
           "liq":(p.get("liquidity") or {}).get("usd"),
           "v24":(p.get("volume") or {}).get("h24")} for p in (d.get("pairs") or [])]
    rows.sort(key=lambda x:-(x["liq"] or 0))
    out["dexscreener"]=rows
except Exception as e:
    out["dex_err"]=str(e)

print(json.dumps(out,indent=2))

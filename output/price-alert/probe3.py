#!/usr/bin/env python3
"""Probe 3: attribute the 1h tape (who bought, who sold), and reconcile the escrow delta."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38738796B951CE87B378538b32B3E6Ee3C4C373"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
STAKE_T0 = "0x"  # resolved by probing escrow Deposit/Burn topic set below

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    delay=1; last=None
    for _ in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                last=d["error"]; msg=json.dumps(d["error"])
                if "-32005" in msg or "rate" in msg.lower() or "too large" in msg.lower():
                    time.sleep(delay); delay*=2; continue
                raise RuntimeError(msg)
            return d.get("result")
        except Exception as e:
            last=e; time.sleep(delay); delay*=2
    raise RuntimeError(f"rpc fail {method}: {last}")

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to":to,"data":data}, tag])

def hexint(x): return int(x,16) if x and x!="0x" else 0
def pad(a): return "0x"+a[2:].rjust(64,"0")

out={}
head = hexint(rpc("eth_blockNumber", []))
hb = rpc("eth_getBlockByNumber", [hex(head), False])
head_ts = hexint(hb["timestamp"])

# --- 1) full topic0 histogram on the pool for the 1h window (family sanity) ---
hist={}
s=53030607
while s<=head:
    e=min(s+999, head)
    try:
        for l in rpc("eth_getLogs",[{"address":POOL,"fromBlock":hex(s),"toBlock":hex(e)}]) or []:
            hist[l["topics"][0]] = hist.get(l["topics"][0],0)+1
    except Exception as ex:
        out.setdefault("hist_err",[]).append(str(ex))
    s=e+1
out["pool_topic0_histogram_1h"] = hist

# --- 2) identify sender of every 1h swap via tx.from + DEUS transfer counterparties ---
swaps=[]
s=53030607
while s<=head:
    e=min(s+999,head)
    try:
        swaps.extend(rpc("eth_getLogs",[{"address":POOL,"topics":[SWAP],"fromBlock":hex(s),"toBlock":hex(e)}]) or [])
    except Exception as ex:
        out.setdefault("sw_err",[]).append(str(ex))
    s=e+1
swaps.sort(key=lambda l:(hexint(l["blockNumber"]), hexint(l["logIndex"])))
out["swap_count"] = len(swaps)

# for the biggest swaps, fetch tx.from and the DEUS Transfer legs in that tx
targets = swaps
detail=[]
for l in targets[:40]:
    txh = l["transactionHash"]
    try:
        tx = rpc("eth_getTransactionByHash",[txh])
        rc = rpc("eth_getTransactionReceipt",[txh])
        legs=[]
        for lg in (rc.get("logs") or []):
            if lg["address"].lower()==DEUS.lower() and lg["topics"][0].lower()==TRANSFER:
                frm="0x"+lg["topics"][1][-40:]; to="0x"+lg["topics"][2][-40:]
                amt=int(lg["data"][2:][0:64],16)/1e18
                legs.append({"from":frm,"to":to,"deus":round(amt,4)})
        detail.append({"blk":hexint(l["blockNumber"]),"tx":txh,"from":tx.get("from"),
                       "to":(tx.get("to") or ""),"deus_legs":legs})
    except Exception as ex:
        detail.append({"blk":hexint(l["blockNumber"]),"tx":txh,"err":str(ex)})
out["swap_details"] = detail

# --- 3) escrow: find stake (Transfer into escrow) events in 24h ---
stakes=[]
s=52989207
while s<=head:
    e=min(s+999,head)
    try:
        for l in rpc("eth_getLogs",[{"address":DEUS,"topics":[TRANSFER,None,pad(ESCROW)],
                                     "fromBlock":hex(s),"toBlock":hex(e)}]) or []:
            amt=int(l["data"][2:][0:64],16)/1e18
            ts=None
            stakes.append({"blk":hexint(l["blockNumber"]),"tx":l["transactionHash"],
                           "from":"0x"+l["topics"][1][-40:],"deus":round(amt,6)})
    except Exception as ex:
        out.setdefault("stake_err",[]).append(str(ex))
    s=e+1
out["transfers_into_escrow_24h"]=stakes
out["stake_total_24h"]=round(sum(x["deus"] for x in stakes),6)

# --- 4) escrow current balance + 24h ago (already have) ---
out["escrow_now"]=hexint(call(DEUS,"0x70a08231"+pad(ESCROW)[2:]))/1e18
out["escrow_24h_ago"]=hexint(call(DEUS,"0x70a08231"+pad(ESCROW)[2:],hex(52989207)))/1e18
out["escrow_delta_24h"]=round(out["escrow_now"]-out["escrow_24h_ago"],6)

# --- 5) big-sell counterparty: who is 0x... for the 16,362 sell; check top buyers' balances ---
buyers={}
for d in detail:
    frm=d.get("from")
    if not frm: continue
    buyers.setdefault(frm,{"txs":0,"deus_out":0.0})
    buyers[frm]["txs"]+=1
out["buyer_senders_top"]=sorted(
    [{"addr":k,**v} for k,v in buyers.items()], key=lambda x:-x["txs"])[:10]

print(json.dumps(out, indent=2))

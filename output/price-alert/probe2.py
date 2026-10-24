#!/usr/bin/env python3
"""Probe 2: VIRTUAL/USD leg, per-swap direction in the 1h window, xDEUS NFT check, escrow events."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
BURN_T0 = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    delay = 1; last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                last = d["error"]; msg = json.dumps(d["error"])
                if "-32005" in msg or "rate" in msg.lower() or "too large" in msg.lower():
                    time.sleep(delay); delay *= 2; continue
                raise RuntimeError(msg)
            return d.get("result")
        except Exception as e:
            last = e; time.sleep(delay); delay *= 2
    raise RuntimeError(f"rpc fail {method}: {last}")

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

def hexint(x):
    return int(x,16) if x and x!="0x" else 0

def pad(a): return "0x" + a[2:].rjust(64,"0")

out = {}
head = hexint(rpc("eth_blockNumber", []))
hb = rpc("eth_getBlockByNumber", [hex(head), False])
head_ts = hexint(hb["timestamp"])
out["head_block"] = head
out["head_ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(head_ts))

# ---- VIRTUAL/USD via DexScreener (VIRTUAL token endpoint) ----
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
try:
    req = urllib.request.Request(f"https://api.dexscreener.com/latest/dex/tokens/{VIRTUAL}",
                                 headers={"User-Agent":"curl/8.5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        dv = json.loads(r.read().decode())
    rows = []
    for p in dv.get("pairs") or []:
        try:
            rows.append({
                "dex": p.get("dexId"), "pair": p.get("pairAddress"),
                "priceUsd": float(p["priceUsd"]) if p.get("priceUsd") else None,
                "h1": (p.get("priceChange") or {}).get("h1"),
                "liq": (p.get("liquidity") or {}).get("usd") or 0,
                "v1h": (p.get("volume") or {}).get("h1") or 0,
                "base": (p.get("baseToken") or {}).get("symbol"),
                "quote": (p.get("quoteToken") or {}).get("symbol"),
            })
        except Exception:
            pass
    rows = [x for x in rows if x["priceUsd"]]
    rows.sort(key=lambda x: -x["liq"])
    out["virtual_pairs_top"] = rows[:8]
    # prefer pools that actually traded in the last hour
    live = [x for x in rows if (x["v1h"] or 0) > 0]
    if live:
        out["virtual_live_median"] = sorted(x["priceUsd"] for x in live)[len(live)//2]
        out["virtual_live_n"] = len(live)
    out["virtual_deepest"] = rows[0]["priceUsd"] if rows else None
except Exception as e:
    out["virtual_err"] = str(e)

# ---- per-swap direction in the last 1h ----
blk_1h = 53030607
logs = []
s = blk_1h
while s <= head:
    e = min(s+999, head)
    try:
        logs.extend(rpc("eth_getLogs", [{"address":POOL,"topics":[SWAP],"fromBlock":hex(s),"toBlock":hex(e)}]) or [])
    except Exception as ex:
        out.setdefault("scan_err", []).append(f"{s}-{e}:{ex}")
    s = e+1
logs.sort(key=lambda l: (hexint(l["blockNumber"]), hexint(l["logIndex"])))

# Solidly Sync event gives reserves; use proven approach: read reserves per swap block.
# Simpler and exact: for each swap tx, read pool reserves at block-1 and at block -> direction of DEUS leg.
# That is 2 calls per swap (31 swaps = 62 calls) - acceptable.
cache = {}
def res_at(bn):
    if bn in cache: return cache[bn]
    r = call(POOL, "0x0902f1ac", hex(bn))
    if not r or r=="0x":
        cache[bn]=None; return None
    w = r[2:]
    v = int(w[0:64],16)/1e18; d = int(w[64:128],16)/1e18
    cache[bn]=(v,d); return cache[bn]

swaps = []
for l in logs:
    bn = hexint(l["blockNumber"])
    try:
        a = res_at(bn-1); b = res_at(bn)
        if not a or not b:
            continue
        ddeus = b[1]-a[1]   # + => DEUS into pool => SELL ; - => DEUS out => BUY
        dvirt = b[0]-a[0]
        swaps.append({
            "blk": bn, "tx": l["transactionHash"],
            "deus_delta": round(ddeus,4),
            "virt_delta": round(dvirt,4),
            "side": "sell" if ddeus>0 else ("buy" if ddeus<0 else "flat"),
        })
    except Exception as ex:
        out.setdefault("swap_err", []).append(f"{bn}:{ex}")

buys = [x for x in swaps if x["side"]=="buy"]
sells = [x for x in swaps if x["side"]=="sell"]
out["one_hour_tape"] = {
    "swaps": len(swaps),
    "buys": len(buys), "sells": len(sells),
    "deus_bought_out_of_pool": round(sum(-x["deus_delta"] for x in buys),2),
    "deus_sold_into_pool": round(sum(x["deus_delta"] for x in sells),2),
    "net_deus_into_pool": round(sum(x["deus_delta"] for x in swaps),2),
    "largest_swaps": sorted(swaps, key=lambda x:-abs(x["deus_delta"]))[:6],
}
# when did the revival start?
if swaps:
    first = swaps[0]["blk"]
    fb = rpc("eth_getBlockByNumber", [hex(first), False])
    out["revival_first_swap"] = {
        "block": first,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hexint(fb["timestamp"]))),
        "minutes_quiet_before": round((hexint(fb["timestamp"]) - 1792845333 - 3600 + 3600)/60,1),
    }
    # silence between 12:35:33Z (1792845333) and this first swap
    out["revival_first_swap"]["gap_minutes_from_1235Z"] = round(
        (hexint(fb["timestamp"]) - 1792845333)/60, 1)

# ---- xDEUS: does 0xbb0f7533 still hold NFT 1396? ----
try:
    r = call(XDEUS, "0x70a08231" + pad("0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63")[2:])
    out["xdeus_balance_0xbb0f7533"] = hexint(r)
except Exception as e:
    out["xdeus_err"] = str(e)
out["xdeus_total_supply"] = hexint(call(XDEUS, "0x18160ddd"))

# ---- escrow 24h reconciliation: Burn + Stake events ----
blk_24h = 52989207
burns = []; stakes = []
s = blk_24h
while s <= head:
    e = min(s+999, head)
    try:
        for l in rpc("eth_getLogs", [{"address":ESCROW,"topics":[BURN_T0],"fromBlock":hex(s),"toBlock":hex(e)}]) or []:
            data = l["data"][2:]
            amt = int(data[0:64],16)/1e18
            ts  = int(data[64:128],16)
            burns.append({"blk":hexint(l["blockNumber"]),"tx":l["transactionHash"],
                          "deus":amt,"ts":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(ts))})
    except Exception as ex:
        out.setdefault("escrow_err",[]).append(f"{s}-{e}:{ex}")
    s = e+1
out["escrow_burns_24h"] = burns
out["escrow_burn_total_24h"] = round(sum(b["deus"] for b in burns),6)

print(json.dumps(out, indent=2))

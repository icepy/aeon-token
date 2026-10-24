#!/usr/bin/env python3
"""Narrow checks: router identity + DEUS provenance for the 52,737 sell; trigger + cohort re-verify."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last = e
            time.sleep(1.0 * (2 ** i))
    raise last

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ROUTER = "0x8d8f598c1739e518b871815dd1f20ea3c169c360"
SELL_TX = "0xc940253588a057e876ce409f32198b1c28e41d0a12fc3c769d58818d99863319"
SELL_BLK = 53027993
SELLER = "0xbd6383c7cbe3ed150f662f70fd4f3a4a1816e13d"

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head, flush=True)

print("router_code=%s" % rpc("eth_getCode", [ROUTER, "latest"])[:120], flush=True)

# what is the router? probe common selectors / see if it is a known aggregator
for name, sel in (("owner", "0x8da5cb5b"), ("name", "0x06fdde03"), ("symbol", "0x95d89b41")):
    try:
        r = call(ROUTER, sel)
        if r and r != "0x":
            print("%s=%s" % (name, r[:160]), flush=True)
    except Exception:
        pass

# DEUS transfers in the sell block, to/from the pool & router
print("--- DEUS transfers in sells blocks (53027990..53027996) ---", flush=True)
for blk in range(SELL_BLK - 3, SELL_BLK + 4):
    got = rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(blk), "toBlock": hex(blk),
                               "topics": [TRANSFER]}])
    for lg in got:
        frm = "0x" + lg["topics"][1][-40:]
        to = "0x" + lg["topics"][2][-40:]
        amt = int(lg["data"][2:], 16) / 1e18
        if amt > 500:
            print(json.dumps({"blk": blk, "from": frm, "to": to, "amt": round(amt, 3),
                              "tx": lg["transactionHash"][:18]}), flush=True)

# Was there any escrow Burn (xDEUS NFT) in the last ~12h? -> forward trigger
BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
lo = head - 21600
print("--- escrow burns last ~12h ---", flush=True)
cur = lo
n = 0
while cur < head:
    hi = min(cur + 999, head)
    try:
        got = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(cur), "toBlock": hex(hi),
                                   "topics": [BURN]}])
    except Exception as e:
        got = []
        print("logerr %s" % e, flush=True)
    for lg in got:
        n += 1
        owner = "0x" + lg["topics"][1][-40:]
        tid = int(lg["topics"][2], 16)
        w = lg["data"][2:]
        amt = int(w[0:64], 16) / 1e18
        print(json.dumps({"blk": int(lg["blockNumber"], 16), "owner": owner,
                          "tokenId": tid, "released_deus": round(amt, 3)}), flush=True)
    cur = hi + 1
print("burns_12h=%d" % n, flush=True)

# cohort re-verify
print("--- cohort balances ---", flush=True)
for label, a in (("0x7f6aba75", "0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3"),
                 ("0x6a45ca8b", "0x6a45ca8bb30f396f40721e105e0aa6cabf326657"),
                 ("0xf0a04b07", "0xf0a04b079dcf7b9d92682123ba2e2180109cb650"),
                 ("0xcae798c0", "0xcae798c0c6958df8299df4f13726da433b8ba7ba"),
                 ("0xbb0f7533", "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63")):
    pad = "0" * 24 + a[2:].lower()
    b = int(call(DEUS, "0x70a08231" + pad), 16) / 1e18
    print("%s deus=%.4f" % (label, b), flush=True)

# pending unstake NFT #1396 check
pad = "0" * 24 + "bb0f753321e2b5fd29bd1d14b532f5b54959ae63"
try:
    nft = int(call(XDEUS, "0x70a08231" + pad), 16)
    print("bb0f7533 xdeus_nfts=%d" % nft, flush=True)
    if nft:
        tid = int(call(XDEUS, "0x2f745c59" + pad + format(0, "064x")), 16)
        print("bb0f7533 tokenId[0]=%d" % tid, flush=True)
except Exception as e:
    print("nft err %s" % e, flush=True)

# escrow balance
esc = int(call(DEUS, "0x70a08231" + "0" * 24 + ESCROW[2:].lower()), 16) / 1e18
print("escrow_deus=%.6f" % esc, flush=True)

import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
XDEUS = "0xe6d5f7439bc236c40054e2275f765f59343d4431"
ESCROW = "0xa85a38796b951ce87b378538b32b3e6ee3c4c373"
WATCH = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"
BURN_TOPIC0 = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    for attempt, back in enumerate([1, 2, 4, 8]):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if attempt == 3:
                raise
            time.sleep(back)

def call(to, data, blk=None):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk) if blk else "latest"])

head = int(rpc("eth_blockNumber", []), 16)
head_ts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
print("head", head, iso(head_ts))

# xDEUS totalSupply + balanceOf(watch)
xs = int(call(XDEUS, "0x18160ddd"), 16)
print(f"xDEUS totalSupply (ERC-721): {xs}")
balnft = int(call(XDEUS, "0x70a08231" + WATCH[2:].rjust(64, "0")), 16)
print(f"xDEUS balanceOf(0xbb0f7533) = {balnft}")
try:
    tid = int(call(XDEUS, "0x2f745c59" + WATCH[2:].rjust(64, "0") + "0"*64), 16)  # tokenOfOwnerByIndex
    print(f"  tokenOfOwnerByIndex(0) = {tid}  <-- 1396 means NOT burned yet")
except Exception as e:
    print("  tokenOfOwnerByIndex reverted:", e)

# escrow Burn events over last ~6h in 1000-blk windows
print("\n--- escrow Burn events, last ~6h ---")
found = 0
for w in range(12):
    hi = head - w * 1000
    lo = hi - 999
    try:
        logs = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [BURN_TOPIC0]}])
    except Exception as e:
        print(f"  {lo}-{hi} err {e}"); continue
    for lg in logs:
        found += 1
        bn = int(lg["blockNumber"], 16)
        ts = int(rpc("eth_getBlockByNumber", [hex(bn), False])["timestamp"], 16)
        owner = "0x" + lg["topics"][1][-40:]
        tid_h = int(lg["topics"][2], 16)
        d = lg["data"][2:]
        amt = int(d[0:64], 16) / 1e18
        print(f"  blk {bn} {iso(ts)} owner {owner} tokenId {tid_h} released {amt:,.4f}")
print(f"total burns found: {found}")

# negative control
ctl = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(head-999), "toBlock": hex(head), "topics": ["0x"+"01"*32]}])
print(f"negative control (same window, bogus topic0): {len(ctl)}")

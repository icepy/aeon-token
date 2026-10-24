import json, urllib.request, time, collections

RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abdf50e9722b7ff3d2de2b0d2f2c"

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
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(back)

head = int(rpc("eth_blockNumber", []), 16)
start = head - 1800
print("head", head, "window", start, "->", head)

# topic0 histogram by address only, over the first 1000-block window (family check)
hist = collections.Counter()
for lo in range(start, head + 1, 1000):
    hi = min(lo + 999, head)
    for lg in rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi)}]):
        hist[lg["topics"][0]] += 1
print("topic0 histogram (all logs):")
for t, n in hist.most_common():
    print(f"  {t} {n}")

swaps = []
syncs = []
for lo in range(start, head + 1, 1000):
    hi = min(lo + 999, head)
    for lg in rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [SWAP]}]):
        swaps.append(lg)
    for lg in rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [SYNC]}]):
        syncs.append(lg)

print(f"\nSwap events: {len(swaps)}   Sync events: {len(syncs)}")
if swaps:
    print("first swap blk", int(swaps[0]["blockNumber"], 16), swaps[0]["transactionHash"])
    print("last  swap blk", int(swaps[-1]["blockNumber"], 16), swaps[-1]["transactionHash"])

# decode Solidly Swap: data = amount0In, amount1In, amount0Out, amount1Out (4 words)
# token0 = VIRTUAL, token1 = DEUS
buys = sells = 0
deus_bought = deus_sold = 0.0
for lg in swaps:
    w = lg["data"][2:]
    a0in, a1in, a0out, a1out = (int(w[i:i+64], 16) for i in range(0, 256, 64))
    if a1out > 0:            # DEUS out of pool = buy
        buys += 1
        deus_bought += a1out / 1e18
    if a1in > 0:             # DEUS into pool = sell
        sells += 1
        deus_sold += a1in / 1e18
print(f"buys {buys} ({deus_bought:,.2f} DEUS)   sells {sells} ({deus_sold:,.2f} DEUS)")
print(f"net DEUS into pool: {deus_sold - deus_bought:+,.2f}")

json.dump({"head": head, "start": start, "swaps": len(swaps), "syncs": len(syncs),
           "buys": buys, "sells": sells, "deus_bought": deus_bought, "deus_sold": deus_sold,
           "hist": dict(hist)},
          open("/home/runner/work/aeon-token/aeon-token/output/price-alert/swaps.json", "w"), indent=1)

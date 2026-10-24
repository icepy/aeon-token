import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
TOPIC0 = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
START = 53037783
END = 53039582


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


logs = []
lo = START
while lo <= END:
    hi = min(lo + 999, END)
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getLogs",
            "params": [
                {
                    "address": POOL,
                    "topics": [TOPIC0],
                    "fromBlock": hex(lo),
                    "toBlock": hex(hi),
                }
            ],
        }
    )
    if "error" in r:
        print("ERROR window", lo, hi, r["error"])
        time.sleep(1)
        continue
    logs.extend(r["result"])
    lo = hi + 1

print("swaps", len(logs))
# Solidly Swap: amount0In, amount1Out, amount1In, amount0Out? order per pool - verify via reserve check
buys = 0
sells = 0
deus_out = 0.0
deus_in = 0.0
rows = []
for L in logs:
    d = L["data"][2:]
    w = [int(d[i * 64 : (i + 1) * 64], 16) for i in range(4)]
    # Aerodrome classic Swap event: Swap(sender,to,amount0In,amount1In,amount0Out,amount1Out)?
    # Decode both interpretations, resolve by consistency later
    rows.append({"blk": int(L["blockNumber"], 16), "w": [x / 1e18 for x in w], "tx": L["transactionHash"]})

for r in rows[:5]:
    print(r["blk"], r["w"], r["tx"])
print("total logs", len(rows))
print("first blk", rows[0]["blk"] if rows else None, "last", rows[-1]["blk"] if rows else None)

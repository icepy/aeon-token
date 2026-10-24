import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
TOPIC0 = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def fetch(lo, hi, topics, address=POOL):
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getLogs",
            "params": [
                {"address": address, "topics": topics, "fromBlock": hex(lo), "toBlock": hex(hi)}
            ],
        }
    )
    if "error" in r:
        return None
    return r["result"]


START, END = 53037783, 53039582
logs = []
lo = START
while lo <= END:
    hi = min(lo + 999, END)
    got = fetch(lo, hi, [TOPIC0])
    if got is None:
        print("ERR", lo, hi)
        time.sleep(1)
        continue
    logs.extend(got)
    lo = hi + 1

print("swaps:", len(logs))
buys = sells = 0
deus_bought = deus_sold = 0.0
rows = []
for L in logs:
    d = L["data"][2:]
    w = [int(d[i * 64 : (i + 1) * 64], 16) / 1e18 for i in range(4)]
    a0in, a1in, a0out, a1out = w
    if a1out > 0:
        buys += 1
        deus_bought += a1out
        side = "BUY"
    else:
        sells += 1
        deus_sold += a1in
        side = "SELL"
    rows.append((int(L["blockNumber"], 16), side, a1out if a1out > 0 else a1in, L["transactionHash"]))

for r in rows:
    print(r[0], r[1], round(r[2], 4), r[3])

print()
print("buys", buys, "deus_out", round(deus_bought, 4))
print("sells", sells, "deus_in", round(deus_sold, 4))
print("net deus into pool", round(deus_sold - deus_bought, 4))
print("volume deus", round(deus_sold + deus_bought, 4))

import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
TXS = [
    ("sell_29298", "0x"),  # placeholder, filled from swap scan
]


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SOLIDLY_SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

b = int(rpc("eth_blockNumber", [])["result"], 16)
logs = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(b - 900), "toBlock": hex(b),
                            "topics": [SOLIDLY_SWAP]}])["result"]
print("swaps_last_900", len(logs))

targets = []
for lg in logs:
    d = lg["data"][2:]
    w = [d[i:i + 64] for i in range(0, len(d), 64)]
    a1in, a1out = int(w[1], 16) / 1e18, int(w[3], 16) / 1e18
    if a1in > 5000 or a1out > 5000:
        targets.append((lg["transactionHash"], a1in, a1out))

print("large swaps", len(targets))
for txh, din, dout in targets[:6]:
    tx = rpc("eth_getTransactionByHash", [txh])["result"]
    rc = rpc("eth_getTransactionReceipt", [txh])["result"]
    print("\ntx", txh)
    print("  from", tx["from"], "to", tx["to"])
    print("  selector", tx["input"][:10], "inputlen", len(tx["input"]))
    print("  DEUS in %.3f out %.3f  status %s" % (din, dout, rc["status"]))

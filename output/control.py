import json, subprocess, time
RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
WRONG = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75c"
B1, HEAD = 53041388, 53043188

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p}
                          for i, (m, p) in enumerate(calls)])
    for a in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * 2 ** a); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(1.5 * 2 ** a); continue
        return j
    raise RuntimeError("fail")

lo = 53041900
j = rpc([("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(lo + 40), "topics": [SWAP]}]),
         ("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(lo + 40), "topics": [WRONG]}])])
print("CONTROL right topic0:", len(j[0].get("result", [])), "| one-char-wrong topic0:", len(j[1].get("result", [])))

# topic0 histogram on the pool, address-only, to catch family mismatch
j = rpc([("eth_getLogs", [{"address": DEEP, "fromBlock": hex(HEAD - 900), "toBlock": hex(HEAD)}])])[0]
from collections import Counter
c = Counter(l["topics"][0][:18] for l in j.get("result", []))
print("\ntopic0 histogram (last 900 blocks, address-only):")
for k, v in c.most_common():
    print("  ", k, v)

# the two swap txs
txs = ["0x861538dff0", "0xc850ee0dfb"]
j = rpc([("eth_getLogs", [{"address": DEEP, "fromBlock": hex(53041900), "toBlock": hex(53041940),
                           "topics": [SWAP]}])])[0]
print("\ntx hashes:")
for l in j.get("result", []):
    print("  ", l["transactionHash"])

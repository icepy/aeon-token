import json, subprocess, time
from decimal import Decimal, getcontext
getcontext().prec = 50
RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
B1, HEAD = 53041388, 53043188

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p}
                          for i, (m, p) in enumerate(calls)])
    last = ""
    for a in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        last = out
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * 2 ** a); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(1.5 * 2 ** a); continue
        return j
    raise RuntimeError(last[:300])

logs = []
start = B1
while start <= HEAD:
    end = min(start + 999, HEAD)
    j = rpc([("eth_getLogs", [{"address": DEEP, "fromBlock": hex(start), "toBlock": hex(end),
                               "topics": [SWAP]}])])[0]
    if "error" in j:
        print("ERR", start, end, j["error"]); start = end + 1; continue
    logs += j.get("result", [])
    start = end + 1
    time.sleep(0.6)

print("swap logs 1h:", len(logs))
tot_in = tot_out = Decimal(0)
buys = sells = 0
rows = []
for l in logs:
    d = l["data"][2:]
    w = [int(d[i:i+64], 16) for i in range(0, len(d), 64)]
    # Solidly: amount0In, amount1In, amount0Out, amount1Out (token0=VIRTUAL, token1=DEUS)
    a0i, a1i, a0o, a1o = w[0], w[1], w[2], w[3]
    deus_in = Decimal(a1i) / Decimal(10**18)
    deus_out = Decimal(a1o) / Decimal(10**18)
    if deus_in > 0:
        sells += 1; tot_in += deus_in
    if deus_out > 0:
        buys += 1; tot_out += deus_out
    rows.append((int(l["blockNumber"], 16), l["transactionHash"][:12], float(deus_in), float(deus_out)))

print("buys %d (%.2f DEUS out) | sells %d (%.2f DEUS in)" % (buys, tot_out, sells, tot_in))
print("net DEUS into pool = %.4f" % (tot_in - tot_out))
for r in sorted(rows):
    print("  blk %d %s in=%.2f out=%.2f" % r)

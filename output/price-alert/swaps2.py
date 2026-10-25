import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
_id = [900]

def rpc(method, params):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        j = json.loads(r.read())
    if "error" in j:
        raise RuntimeError(j["error"])
    return j["result"]

def ts(n):
    return int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)

def find(target):
    lo, hi = 53040000, int(rpc("eth_blockNumber", []), 16)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ts(mid) <= target:
            lo = mid
        else:
            hi = mid - 1
    return lo

# window around the 07:14:01Z blockTimestampLast
t = 1792912441
start = find(t - 2400)
end = find(t + 600)
logs = []
b = start
while b <= end:
    e = min(b + 999, end)
    logs.extend(rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(b), "toBlock": hex(e), "topics": [SWAP]}]))
    b = e + 1

rows = []
for lg in logs:
    d = lg["data"][2:]
    a0in, a1in = int(d[0:64], 16) / 1e18, int(d[64:128], 16) / 1e18
    a0out, a1out = int(d[128:192], 16) / 1e18, int(d[192:256], 16) / 1e18
    rows.append({"blk": int(lg["blockNumber"], 16),
                 "iso": datetime.datetime.fromtimestamp(ts(int(lg["blockNumber"], 16)), datetime.UTC).strftime("%H:%M:%SZ"),
                 "virtual_in": round(a0in, 8), "deus_in": round(a1in, 6),
                 "virtual_out": round(a0out, 8), "deus_out": round(a1out, 6),
                 "side": "BUY" if a1out > 0 else "SELL",
                 "deus": round(a1out - a1in, 6), "tx": lg["transactionHash"]})

# control on a block range known to contain a swap
ctl_true = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(start), "toBlock": hex(min(start + 999, end)), "topics": [SWAP]}])
bad = SWAP[:-1] + ("1" if SWAP[-1] != "1" else "2")
ctl_false = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(start), "toBlock": hex(min(start + 999, end)), "topics": [bad]}])

print(json.dumps({"window": [start, end], "n": len(rows), "rows": rows,
                  "ctl_true": len(ctl_true), "ctl_false": len(ctl_false),
                  "now_iso": datetime.datetime.fromtimestamp(ts(int(rpc("eth_blockNumber", []), 16)), datetime.UTC).strftime("%FT%TZ")}, indent=1))

import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
_id = [500]

def rpc(method, params):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        j = json.loads(r.read())
    if "error" in j:
        raise RuntimeError(j["error"])
    return j["result"]

head = int(rpc("eth_blockNumber", []), 16)
start = head - 1800

logs = []
step = 999
b = start
while b <= head:
    e = min(b + step - 1, head)
    part = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(b), "toBlock": hex(e), "topics": [SWAP]}])
    logs.extend(part)
    b = e + 1

# discrimination control: corrupt topic0 last char
bad = SWAP[:-1] + ("1" if SWAP[-1] != "1" else "2")
ctrl = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(head - 999), "toBlock": hex(head), "topics": [bad]}])
ctrl_ok = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(head - 999), "toBlock": hex(head), "topics": [SWAP]}])

ts_cache = {}
def bts(n):
    if n not in ts_cache:
        ts_cache[n] = int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)
    return ts_cache[n]

sv = []
for lg in logs:
    d = lg["data"][2:]
    a0in = int(d[0:64], 16); a1in = int(d[64:128], 16)
    a0out = int(d[128:192], 16); a1out = int(d[192:256], 16)
    # token0 = VIRTUAL, token1 = DEUS
    dv = (a0in - a0out) / 1e18   # + means VIRTUAL into pool = DEUS bought
    dd = (a1in - a1out) / 1e18   # + means DEUS into pool = DEUS sold
    sv.append({"blk": int(lg["blockNumber"], 16), "tx": lg["transactionHash"],
               "ts": bts(int(lg["blockNumber"], 16)),
               "virtual_delta": dv, "deus_delta": dd,
               "side": "BUY_DEUS" if dv > 0 else "SELL_DEUS"})

sv.sort(key=lambda x: x["blk"])
tot_buy = sum(s["deus_delta"] for s in sv if s["deus_delta"] > 0)
tot_sell = sum(-s["deus_delta"] for s in sv if s["deus_delta"] < 0)
print(json.dumps({"head": head, "window": [start, head], "n_swaps": len(sv),
                  "control_hits": len(ctrl), "control_true": len(ctrl_ok),
                  "deus_bought_by_pool": tot_buy, "deus_sold_by_pool": tot_sell,
                  "net_deus_into_pool": tot_buy - tot_sell,
                  "swaps": [{"blk": s["blk"], "iso": datetime.datetime.fromtimestamp(s["ts"], datetime.UTC).isoformat(), "side": s["side"], "deus": round(s["deus_delta"], 6), "virtual": round(s["virtual_delta"], 6), "tx": s["tx"]} for s in sv[-15:]]}, indent=1))

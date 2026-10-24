import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"

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

head = int(rpc("eth_blockNumber", []), 16)
start = head - 1800
syncs = []
for lo in range(start, head + 1, 1000):
    hi = min(lo + 999, head)
    syncs += rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [SYNC]}])

print(f"Sync events (correct topic0): {len(syncs)}")
prev = None
for lg in syncs:
    w = lg["data"][2:]
    v = int(w[0:64], 16) / 1e18
    d = int(w[64:128], 16) / 1e18
    bn = int(lg["blockNumber"], 16)
    blk = rpc("eth_getBlockByNumber", [hex(bn), False])
    ts = int(blk["timestamp"], 16)
    iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
    gap = "" if prev is None else f"  gap {(ts-prev)/60:.1f} min"
    print(f"  blk {bn} {iso} VIRTUAL {v:,.2f} DEUS {d:,.2f} ratio {v/d:.8f}{gap}")
    prev = ts

head_ts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
print("head", head, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(head_ts)))
if syncs:
    last_ts = int(rpc("eth_getBlockByNumber", [syncs[-1]["blockNumber"], False])["timestamp"], 16)
    print(f"minutes since last pool event: {(head_ts-last_ts)/60:.1f}")

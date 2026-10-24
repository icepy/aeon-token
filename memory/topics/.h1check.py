import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


head = int(call("eth_blockNumber", []), 16)
hdr = call("eth_getBlockByNumber", [hex(head), False])
print("head", head, "ts", datetime.datetime.fromtimestamp(int(hdr["timestamp"], 16), datetime.UTC).isoformat())

# find block ~3600s back
lo, hi = head - 3000, head
target = int(hdr["timestamp"], 16) - 3600
while lo < hi:
    mid = (lo + hi) // 2
    t = int(call("eth_getBlockByNumber", [hex(mid), False])["timestamp"], 16)
    if t < target:
        lo = mid + 1
    else:
        hi = mid
b1h = lo
t1h = int(call("eth_getBlockByNumber", [hex(b1h), False])["timestamp"], 16)

for label, blk in (("1h ago", b1h), ("now", head)):
    d = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(blk)])[2:]
    v = int(d[0:64], 16) / 1e18
    u = int(d[64:128], 16) / 1e18
    print(f"{label:7s} blk {blk} VIRTUAL {v:,.2f} DEUS {u:,.2f} ratio {v/u:.9f}")

d = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(head)])[2:]
v = int(d[0:64], 16) / 1e18
u = int(d[64:128], 16) / 1e18
d1 = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(b1h)])[2:]
v1 = int(d1[0:64], 16) / 1e18
u1 = int(d1[64:128], 16) / 1e18
print(f"\nexact 1h window {b1h}..{head} ({head-b1h} blocks, {int(hdr['timestamp'],16)-t1h}s)")
print(f"DEUS/leg change {(v/u)/(v1/u1)*100-100:+.4f}%")

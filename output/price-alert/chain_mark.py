import json, urllib.request, sys

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"   # aerodrome classic DEUS/VIRTUAL
VIRT_POOL = "0x529d2863a1521d0b57db028168fdE2E97120017C"  # VIRTUAL/USDC v3

def rpc(method, params, _id=[0]):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                j = json.loads(r.read())
            if "error" in j:
                raise RuntimeError(f"{method} -> {j['error']}")
            return j["result"]
        except Exception as e:
            if attempt == 2:
                raise
    return None

def blk(num):
    return rpc("eth_getBlockByNumber", [hex(num), False])

head = int(rpc("eth_blockNumber", []), 16)
hb = blk(head)
HTS = int(hb["timestamp"], 16)

def find_block(target_ts):
    lo, hi = head - 200000, head
    # ensure lo is before target
    while int(blk(lo)["timestamp"], 16) > target_ts:
        lo -= 50000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if int(blk(mid)["timestamp"], 16) <= target_ts:
            lo = mid
        else:
            hi = mid - 1
    return lo

res = {}
for label, back in (("head", 0), ("h1", 3600), ("h24", 86400)):
    if back == 0:
        n = head
        ts = HTS
    else:
        n = find_block(HTS - back)
        ts = int(blk(n)["timestamp"], 16)
    raw = rpc("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(n)])
    d = raw[2:]
    r0 = int(d[0:64], 16)
    r1 = int(d[64:128], 16)
    bt = int(d[128:192], 16)
    # token0/token1 order unknown -> resolve via token0()
    t0 = rpc("eth_call", [{"to": POOL, "data": "0x0dfe1681"}, hex(n)])
    t1 = rpc("eth_call", [{"to": POOL, "data": "0xd21220a7"}, hex(n)])
    res[label] = {"block": n, "ts": ts, "r0": r0, "r1": r1, "blockTsLast": bt,
                  "t0": "0x" + t0[-40:], "t1": "0x" + t1[-40:], "tsdelta": HTS - ts}

vraw = rpc("eth_call", [{"to": VIRT_POOL, "data": "0x3850c7bd"}, hex(head)])[2:]
sqrtP = int(vraw[0:64], 16)
print(json.dumps({"head": head, "head_ts": HTS, "reserves": res,
                  "virt_sqrtPriceX96": str(sqrtP),
                  "virt_price_usdc_per_virtual": (sqrtP / 2**96) ** 2}, indent=1))

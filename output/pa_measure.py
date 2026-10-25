import json, time, urllib.request, math, sys
from decimal import Decimal

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"   # deepest DEUS/VIRTUAL (Solidly)
VPOOL = "0x529d2863"  # prefix; resolved below
VPOOL_FULL = "0x529d2863794c40b4d3a25b2d6e8d3b3c0e6a1f0d"  # placeholder, resolved by probe

def rpc(method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                j = json.loads(r.read())
            if "error" in j:
                raise RuntimeError(str(j["error"])[:200])
            return j["result"]
        except Exception as e:
            last = e
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("rpc fail %s: %s" % (method, last))

def call(to, data, blk="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk) if isinstance(blk, int) else blk])

def words(hexstr):
    h = hexstr[2:] if hexstr.startswith("0x") else hexstr
    return [h[i:i+64] for i in range(0, len(h), 64)]

def blk_ts(n):
    b = rpc("eth_getBlockByNumber", [hex(n), False])
    return int(b["timestamp"], 16)

def find_block_by_ts(target_ts, head):
    lo, hi = head - 200000, head
    # widening lower bound
    while blk_ts(lo) > target_ts:
        lo -= 200000
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if blk_ts(mid) <= target_ts:
            lo = mid
        else:
            hi = mid
    return lo

out = {}
head = int(rpc("eth_blockNumber", []), 16)
head_ts = blk_ts(head)
out["head"] = head
out["head_ts"] = head_ts

# --- deepest pool: token0/token1 + reserves at head, -1h, -24h
t0 = call(POOL, "0x0dfe1681")
t1 = call(POOL, "0xd21220a7")
out["token0"] = "0x" + words(t0)[0][-40:]
out["token1"] = "0x" + words(t1)[0][-40:]

def reserves(blk):
    r = words(call(POOL, "0x0902f1ac", blk))
    return int(r[0], 16), int(r[1], 16), int(r[2], 16)

rb = find_block_by_ts(head_ts - 3600, head)
rd = find_block_by_ts(head_ts - 86400, head)
assert blk_ts(rd) == head_ts - 86400 or abs(blk_ts(rd) - (head_ts-86400)) <= 2, "24h window off"
out["blk_1h"] = rb
out["blk_24h"] = rd
out["res_head"] = reserves(head)
out["res_1h"] = reserves(rb)
out["res_24h"] = reserves(rd)
out["ts_1h"] = blk_ts(rb)
out["ts_24h"] = blk_ts(rd)
out["dq_86400"] = head_ts - blk_ts(rd)
out["dq_3600"] = head_ts - blk_ts(rb)

print(json.dumps(out, indent=1))

import json, time, urllib.request
from decimal import Decimal, getcontext
getcontext().prec = 40

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VPOOL = "0x529d2863a1521d0b57db028168fdE2E97120017C"

def rpc(method, params, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.2
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                j = json.loads(r.read())
            if "error" in j:
                e = j["error"]; raise RuntimeError("%s %s" % (e.get("code"), e.get("message")))
            return j["result"]
        except Exception as ex:
            last = ex; time.sleep(delay); delay *= 2
    raise RuntimeError("rpc %s: %s" % (method, last))

def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [h[i:i+64] for i in range(0, len(h), 64)]

def call(to, data, blk):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk) if isinstance(blk, int) else blk])

def blk_ts(n):
    return int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)

def find_block(target_ts, head):
    lo, hi = head - 200000, head
    while blk_ts(lo) > target_ts:
        lo -= 200000
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if blk_ts(mid) <= target_ts:
            lo = mid
        else:
            hi = mid
    return lo

head = int(rpc("eth_blockNumber", []), 16)
head_ts = blk_ts(head)
b1h = find_block(head_ts - 3600, head)
b24h = find_block(head_ts - 86400, head)
assert head_ts - blk_ts(b1h) == 3600, "1h window not exact"
assert head_ts - blk_ts(b24h) == 86400, "24h window not exact"

def reserves(blk):
    w = words(call(POOL, "0x0902f1ac", blk))
    return int(w[0], 16), int(w[1], 16), int(w[2], 16)

def vusd_at(blk):
    sq = int(words(call(VPOOL, "0x3850c7bd", blk))[0], 16)
    # token0=VIRTUAL 18dp, token1=USDC 6dp -> price token1/token0 scaled
    p = (Decimal(sq) / (Decimal(2) ** 96)) ** 2
    return p * Decimal(10**18) / Decimal(10**6)

out = {"head": head, "head_ts": head_ts,
       "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(head_ts)),
       "b1h": b1h, "b24h": b24h}

R = {}
for lbl, b in [("head", head), ("1h", b1h), ("24h", b24h)]:
    v, d, ts_last = reserves(b)
    V = Decimal(v) / Decimal(10**18); D = Decimal(d) / Decimal(10**18)
    vp = vusd_at(b)
    mark = (V / D) * vp
    R[lbl] = {"blk": b, "virtual": float(V), "deus": float(D),
              "blockTimestampLast": ts_last, "virtual_usd": float(vp),
              "ratio": float(V / D), "mark_usd": float(mark)}
out["snapshots"] = R

mh = R["head"]["mark_usd"]; m1 = R["1h"]["mark_usd"]; m24 = R["24h"]["mark_usd"]
out["h1_pct"] = (mh / m1 - 1) * 100
out["h24_pct"] = (mh / m24 - 1) * 100
out["virt_leg_h1_pct"] = (R["head"]["virtual_usd"] / R["1h"]["virtual_usd"] - 1) * 100
out["virt_leg_h24_pct"] = (R["head"]["virtual_usd"] / R["24h"]["virtual_usd"] - 1) * 100
out["ratio_leg_h1_pct"] = (R["head"]["ratio"] / R["1h"]["ratio"] - 1) * 100
out["ratio_leg_h24_pct"] = (R["head"]["ratio"] / R["24h"]["ratio"] - 1) * 100
out["reserves_identical_1h"] = (R["head"]["virtual"] == R["1h"]["virtual"] and R["head"]["deus"] == R["1h"]["deus"])
out["silence_min"] = (head_ts - R["head"]["blockTimestampLast"]) / 60

for t in ["0.012", "0.025", "0.032", "0.041"]:
    out["dist_" + t] = (float(t) / mh - 1) * 100
out["dist_ath"] = (0.06876 / mh - 1) * 100

# level math
Vh = Decimal(repr(R["head"]["virtual"])); Dh = Decimal(repr(R["head"]["deus"]))
k = Vh * Dh
lv = {}
for t in ["0.012", "0.025", "0.032", "0.041"]:
    r_t = Decimal(t) / Decimal(repr(R["head"]["virtual_usd"]))
    Dt = (k / r_t).sqrt()
    dd = Dt - Dh
    lv[t] = {"deus_net": float(dd), "pct_of_pool": float(dd / Dh * 100),
             "usd_net": float(dd * Decimal(repr(mh))),
             "action": "SELL into pool" if dd > 0 else "BUY out of pool"}
out["level_math"] = lv

print(json.dumps(out, indent=1))

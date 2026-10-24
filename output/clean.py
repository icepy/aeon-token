import json, subprocess, time
from decimal import Decimal, getcontext
getcontext().prec = 60
RPC = "https://base.gateway.tenderly.co"
HEAD = 53043188
ONE96 = Decimal(2) ** 96
POOLS = ["0x7CB770D0513c30e0CB45E4899e4a2CbEEd6F9830",
         "0x529d2863a1521d0b57db028168fdE2E97120017C"]

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    for a in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * 2 ** a); continue
        if "error" in j:
            time.sleep(1.5 * 2 ** a); continue
        return j["result"]
    raise RuntimeError("fail")

def virtual_usd_avg(blk_hex):
    vals = []
    for p in POOLS:
        r = rpc("eth_call", [{"to": p, "data": "0x3850c7bd"}, blk_hex])
        sq = int(r[2:2 + 64], 16)
        vals.append(((Decimal(sq) / ONE96) ** 2) * Decimal(10) ** 12)
    return sum(vals) / len(vals), vals

def deep(blk_hex):
    r = rpc("eth_call", [{"to": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
                          "data": "0x0902f1ac"}, blk_hex])[2:]
    return (Decimal(int(r[0:64], 16)) / Decimal(10**18),
            Decimal(int(r[64:128], 16)) / Decimal(10**18))

def blk_at(secs):
    hts = int(rpc("eth_getBlockByNumber", [hex(HEAD), False])["timestamp"], 16)
    tgt = hts - secs
    lo, hi = HEAD - 70000, HEAD
    while lo < hi:
        mid = (lo + hi + 1) // 2
        b = rpc("eth_getBlockByNumber", [hex(mid), False])
        if int(b["timestamp"], 16) <= tgt: lo = mid
        else: hi = mid - 1
    b = rpc("eth_getBlockByNumber", [hex(lo), False])
    return lo, int(b["timestamp"], 16), hts

hts = int(rpc("eth_getBlockByNumber", [hex(HEAD), False])["timestamp"], 16)
b1, ts1, _ = blk_at(3600)
b24, ts24, _ = blk_at(86400)

res = {}
for label, blk in [("now", HEAD), ("1h", b1), ("24h", b24)]:
    vavg, vs = virtual_usd_avg(hex(blk))
    V, D = deep(hex(blk))
    ratio = V / D
    res[label] = {"vs": vs, "vavg": vavg, "V": V, "D": D, "ratio": ratio, "mark": ratio * vavg}

for label in ("now", "1h", "24h"):
    r = res[label]
    print(f"{label:4s} VIRTUAL pools {['%.7f'%v for v in r['vs']]} avg {r['vavg']:.7f}")
    print(f"     ratio {r['ratio']:.9f}  MARK ${r['mark']:.8f}")

n, o, d = res["now"], res["1h"], res["24h"]
print(f"\nh1  {((n['mark']/o['mark'])-1)*100:+.4f}%   (ratio {((n['ratio']/o['ratio'])-1)*100:+.4f}%, VIRTUAL/USD {((n['vavg']/o['vavg'])-1)*100:+.4f}%)")
print(f"h24 {((n['mark']/d['mark'])-1)*100:+.4f}%   (ratio {((n['ratio']/d['ratio'])-1)*100:+.4f}%, VIRTUAL/USD {((n['vavg']/d['vavg'])-1)*100:+.4f}%)")
print(f"windows: 1h blk {b1}->{HEAD} ({hts-ts1}s) | 24h blk {b24}->{HEAD} ({hts-ts24}s)")
print(f"DEUS net into pool: 1h {n['D']-o['D']:+.2f} | 24h {n['D']-d['D']:+.2f}")
json.dump({k: {kk: str(vv) for kk, vv in v.items() if kk != 'vs'} for k, v in res.items()},
          open("/home/runner/work/aeon-token/aeon-token/output/final.json", "w"), indent=2)

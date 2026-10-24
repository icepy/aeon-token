import json, subprocess, time
from decimal import Decimal, getcontext
getcontext().prec = 60

RPC = "https://base.gateway.tenderly.co"
HEAD = 53043188

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p}
                          for i, (m, p) in enumerate(calls)])
    last = ""
    for attempt in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        last = out
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * (2 ** attempt)); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(1.5 * (2 ** attempt)); continue
        return j
    raise RuntimeError("rpc failed: " + last[:200])

def word(res, idx):
    """result of call idx, raw hex word(s), no 0x"""
    r = res[idx].get("result")
    if not r:
        raise RuntimeError("empty result for call %d: %s" % (idx, res[idx]))
    return r[2:]

def sqrtp_from_slot0(h):
    # slot0() returns 7 ABI words; sqrtPriceX96 is word 0 (uint160, left-padded)
    return int(h[0:64], 16)

ONE = Decimal(1)
Q96 = Decimal(2) ** 96

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VIRT_USDC = ["0x7CB770D0513c30e0CB45E4899e4a2CbEEd6F9830",
             "0x529d2863a1521d0b57db028168fdE2E97120017C"]
USDC_DEUS = ["0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b",
             "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642",
             "0x75bc14950Ab093cBd1f80BbbDf458596939180A3"]

def virtual_usd_at(blk_hex):
    res = rpc([("eth_call", [{"to": a, "data": "0x3850c7bd"}, blk_hex]) for a in VIRT_USDC])
    out = []
    for i, a in enumerate(VIRT_USDC):
        sq = sqrtp_from_slot0(word(res, i))
        p = (Decimal(sq) / Q96) ** 2      # USDC_raw per VIRTUAL_raw
        usd = p * Decimal(10) ** 12       # adjust 18dp vs 6dp
        out.append(usd)
    return out

def deep_reserves(blk_hex):
    res = rpc([("eth_call", [{"to": DEEP, "data": "0x0902f1ac"}, blk_hex])])
    h = word(res, 0)
    V = Decimal(int(h[0:64], 16)) / Decimal(10**18)
    D = Decimal(int(h[64:128], 16)) / Decimal(10**18)
    return V, D

def usdc_venues_at(blk_hex):
    res = rpc([("eth_call", [{"to": a, "data": "0x3850c7bd"}, blk_hex]) for a in USDC_DEUS])
    out = []
    for i, a in enumerate(USDC_DEUS):
        sq = sqrtp_from_slot0(word(res, i))
        p = (Decimal(sq) / Q96) ** 2      # DEUS_raw per USDC_raw (token0=USDC 6, token1=DEUS 18)
        usd = Decimal(10) ** 12 / p       # USD per DEUS
        out.append(usd)
    return out

def block_at(seconds_back):
    hb = rpc([("eth_getBlockByNumber", [hex(HEAD), False])])[0]["result"]
    hts = int(hb["timestamp"], 16)
    target = hts - seconds_back
    lo, hi = HEAD - 70000, HEAD
    while lo < hi:
        mid = (lo + hi + 1) // 2
        b = rpc([("eth_getBlockByNumber", [hex(mid), False])])[0]["result"]
        if int(b["timestamp"], 16) <= target:
            lo = mid
        else:
            hi = mid - 1
    pb = rpc([("eth_getBlockByNumber", [hex(lo), False])])[0]["result"]
    return lo, int(pb["timestamp"], 16), hts

print("=== head block", HEAD, "===")
hb = rpc([("eth_getBlockByNumber", [hex(HEAD), False])])[0]["result"]
hts = int(hb["timestamp"], 16)
import datetime
print("head ts", hts, datetime.datetime.fromtimestamp(hts, datetime.UTC).isoformat())

VUSD_now = virtual_usd_at(hex(HEAD))
print("\nVIRTUAL/USD live pools:", ["%.7f" % v for v in VUSD_now])
vsorted = sorted(VUSD_now); vmed = vsorted[len(vsorted)//2]
print("VIRTUAL/USD median = %.7f  (spread %.3f%%)" % (vmed, (max(VUSD_now)/min(VUSD_now)-1)*100))

V, D = deep_reserves(hex(HEAD))
ratio = V / D
mark = ratio * vmed
print("\nDEEP reserves: VIRTUAL %.4f | DEUS %.4f" % (V, D))
print("ratio = %.9f  -> MARK $%.8f" % (ratio, mark))

uv = usdc_venues_at(hex(HEAD))
print("\nUSDC V3 venues:", ["%.8f" % u for u in uv])
usorted = sorted(uv); umed = usorted[len(usorted)//2]
print("USDC median $%.8f  premium %.3f%%" % (umed, (mark/umed-1)*100))

# h1
b1, ts1, _ = block_at(3600)
V1, D1 = deep_reserves(hex(b1))
r1 = V1 / D1
vu1 = virtual_usd_at(hex(b1))
vs1 = sorted(vu1); vm1 = vs1[len(vs1)//2]
mark1 = r1 * vm1
print("\n--- 1h window blk %d -> %d (delta %ds) ---" % (b1, HEAD, hts - ts1))
print("ratio %.9f -> %.9f = %+.4f%%" % (r1, ratio, (ratio/r1-1)*100))
print("VIRTUAL/USD %.7f -> %.7f = %+.4f%%" % (vm1, vmed, (vmed/vm1-1)*100))
print("MARK $%.8f -> $%.8f = %+.4f%%" % (mark1, mark, (mark/mark1-1)*100))
print("DEUS net into pool 1h = %.4f" % (D - D1))

# h24
b24, ts24, _ = block_at(86400)
V24, D24 = deep_reserves(hex(b24))
r24 = V24 / D24
vu24 = virtual_usd_at(hex(b24))
vs24 = sorted(vu24); vm24 = vs24[len(vs24)//2]
mark24 = r24 * vm24
print("\n--- 24h window blk %d -> %d (delta %ds) ---" % (b24, HEAD, hts - ts24))
print("ratio %.9f -> %.9f = %+.4f%%" % (r24, ratio, (ratio/r24-1)*100))
print("VIRTUAL/USD %.7f -> %.7f = %+.4f%%" % (vm24, vmed, (vmed/vm24-1)*100))
print("MARK $%.8f -> $%.8f = %+.4f%%" % (mark24, mark, (mark/mark24-1)*100))
print("DEUS net into pool 24h = %.2f" % (D - D24))

print("\n--- gates (from mark $%.8f) ---" % mark)
for t in ("0.012", "0.025", "0.032", "0.041"):
    print("  $%s  %+8.2f%%" % (t, (Decimal(t)/mark - 1) * 100))
print("  ATH $0.06876  %+.2f%%" % ((Decimal("0.06876")/mark - 1) * 100))

json.dump({"head": HEAD, "head_ts": hts, "mark": str(mark), "ratio": str(ratio),
           "virtual_usd": str(vmed), "usdc_venues": [str(x) for x in uv],
           "b1": b1, "ts1": ts1, "ratio1": str(r1), "mark1": str(mark1), "mark1_virtual": str(vm1),
           "b24": b24, "ts24": ts24, "ratio24": str(r24), "mark24": str(mark24), "mark24_virtual": str(vm24),
           "V": str(V), "D": str(D), "deus_net_1h": str(D - D1), "deus_net_24h": str(D - D24)},
          open("/home/runner/work/aeon-token/aeon-token/output/measure.json", "w"), indent=2)

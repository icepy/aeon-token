import json, subprocess, time
from decimal import Decimal, getcontext
getcontext().prec = 50
RPC = "https://base.gateway.tenderly.co"
HEAD = 53043188
BLK = hex(HEAD)

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p} for i, (m, p) in enumerate(calls)])
    for attempt in range(6):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(2 ** attempt); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(2 ** attempt); continue
        return j
    raise RuntimeError("rpc failed")

def block(ts_back):
    hb = rpc([("eth_getBlockByNumber", [BLK, False])])[0]["result"]
    hts = int(hb["timestamp"], 16)
    target = hts - ts_back
    lo, hi = HEAD - 60000, HEAD
    while lo < hi:
        mid = (lo + hi + 1) // 2
        b = rpc([("eth_getBlockByNumber", [hex(mid), False])])[0]["result"]
        if int(b["timestamp"], 16) <= target:
            lo = mid
        else:
            hi = mid - 1
    pb = rpc([("eth_getBlockByNumber", [hex(lo), False])])[0]["result"]
    return lo, int(pb["timestamp"], 16), hts

# --- USDC V3 venues (token0=USDC 6dp, token1=DEUS 18dp -> invert)
usdc_pools = {
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": True,
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": True,
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": True,
}
res = rpc([("eth_call", [{"to": a, "data": "0x3850c7bd"}, BLK]) for a in usdc_pools])
marks = []
for r in res:
    sq = r.get("result") or ""
    if len(sq) < 66:
        print("slot0 fail", r); continue
    sqrtP_raw = int(sq[2:66], 16)
    sqrtP = Decimal(sqrtP_raw) / (Decimal(2) ** 96)
    p_raw = sqrtP * sqrtP          # DEUS_raw per USDC_raw
    # USD per DEUS = (1/ (p_raw)) adjusted: p_raw = deus_raw/usdc_raw
    # human: deus/1e18 per usdc/1e6 -> usd_per_deus = (1e6/1e18)*(1/p_raw)... invert then scale
    usd_per_deus = (Decimal(10) ** 12) / p_raw
    print("USDC venue", r["id"], f"sqrtP={sqrtP_raw} mark=${usd_per_deus:.8f}")
    marks.append((r["id"], usd_per_deus))

# --- ratio + mark
res = rpc([("eth_call", [{"to": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa", "data": "0x0902f1ac"}, BLK]),
           ("eth_getBlockByNumber", [BLK, False])])
raw = res[0]["result"][2:]
V = Decimal(int(raw[0:64], 16)) / Decimal(10**18)
D = Decimal(int(raw[64:128], 16)) / Decimal(10**18)
ratio = V / D
VUSD = Decimal("0.62412")   # avg of 0.6235623 / 0.6246790
mark = ratio * VUSD
print(f"\nreserves V={V:.4f} D={D:.4f} ratio={ratio:.9f} VIRTUAL_USD={VUSD}")
print(f"MARK = ${mark:.8f}")

sorted_marks = sorted(m for _, m in marks)
med = sorted_marks[len(sorted_marks) // 2]
print(f"USDC median ${med:.8f}  premium {((mark/med)-1)*100:.3f}%")
print(f"DexScreener deepest print $0.01727")

# --- h24
b24, ts24, hts = block(86400)
r = rpc([("eth_call", [{"to": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa", "data": "0x0902f1ac"}, hex(b24)])])
raw2 = r[0]["result"][2:]
V24 = Decimal(int(raw2[0:64], 16)) / Decimal(10**18)
D24 = Decimal(int(raw2[64:128], 16)) / Decimal(10**18)
r24 = V24 / D24
print(f"\n24h block {b24} ts={ts24} delta={hts-ts24}s ratio={r24:.9f} -> ratio chg {((ratio/r24)-1)*100:.4f}%")
print(f"DEUS net into pool 24h = {D - D24:.2f}")

# --- 1h
b1, ts1, _ = block(3600)
r = rpc([("eth_call", [{"to": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa", "data": "0x0902f1ac"}, hex(b1)])])
raw3 = r[0]["result"][2:]
V1 = Decimal(int(raw3[0:64], 16)) / Decimal(10**18)
D1 = Decimal(int(raw3[64:128], 16)) / Decimal(10**18)
r1 = V1 / D1
print(f"1h block {b1} ts={ts1} delta={hts-ts1}s ratio={r1:.9f} -> ratio chg {((ratio/r1)-1)*100:.4f}%")
print(f"h1 window blocks {b1}..{HEAD}")

# gates
print("\n--- gates ---")
for t in (0.012, 0.025, 0.032, 0.041):
    print(f"  ${t}: {(Decimal(str(t))/mark - 1)*100:+.2f}%")
print(f"  ATH $0.06876: {(Decimal('0.06876')/mark - 1)*100:+.2f}%")
print(f"  h1: baseline source = on-chain ratio chg {((ratio/r1)-1)*100:+.4f}% (VIRTUAL leg not included)")

import json, subprocess, time
from decimal import Decimal, getcontext
getcontext().prec = 50
RPC = "https://base.gateway.tenderly.co"
BLK = "0x3295ff4"

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

pools = [
    ("0x7CB770D0513c30e0CB45E4899e4a2CbEEd6F9830", 6),   # VIRTUAL/USDC
    ("0x529d2863a1521d0b57db028168fdE2E97120017C", 6),   # VIRTUAL/USDC
    ("0x21594b992F68495dD28d605834b58889d0a727c7", 18),  # VIRTUAL/WETH (quote 18dp)
]
vals = []
for addr, qdec in pools:
    res = rpc([("eth_call", [{"to": addr, "data": "0x3850c7bd"}, BLK])])
    sq = res[0].get("result") or ""
    if len(sq) < 2 + 64:
        print(addr, "slot0 unreadable:", sq[:40]); time.sleep(1.5); continue
    sqrtP_raw = int(sq[2:2 + 64].lstrip("0") or "0", 16)
    sqrtP = Decimal(sqrtP_raw) / (Decimal(2) ** 96)
    price_raw = sqrtP * sqrtP                    # quote_raw per VIRTUAL_raw (token0=VIRTUAL 18dp)
    # human price = (quote_raw/10^qdec) / (virtual_raw/10^18) = price_raw * 10^(18-qdec)
    usd = price_raw * (Decimal(10) ** (18 - qdec))
    print(f"{addr} qdec={qdec} sqrtP={sqrtP_raw} VIRTUAL_USD={usd:.7f}")
    vals.append(usd)
    time.sleep(1.5)

if vals:
    vals_sorted = sorted(vals)
    med = vals_sorted[len(vals_sorted) // 2]
    print("median VIRTUAL/USD = %.7f" % med)

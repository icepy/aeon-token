import json, urllib.request, time, statistics
from decimal import Decimal, getcontext
getcontext().prec = 60

RPC = "https://base.gateway.tenderly.co"

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

def blk_at_ts(target):
    head = int(rpc("eth_blockNumber", []), 16)
    lo, hi = head - 40000, head
    while lo < hi:
        mid = (lo + hi) // 2
        if int(rpc("eth_getBlockByNumber", [hex(mid), False])["timestamp"], 16) < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

head = int(rpc("eth_blockNumber", []), 16)
head_ts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
blk1h = blk_at_ts(head_ts - 3600)
ts1h = int(rpc("eth_getBlockByNumber", [hex(blk1h), False])["timestamp"], 16)
iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
print(f"head {head} {iso(head_ts)}   |   1h ago {blk1h} {iso(ts1h)}  (delta {head_ts-ts1h}s)")

def call(to, data, blk):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk)])

def token_dec(tok):
    return int(call(tok, "0x313ce567", head), 16)

# ---------- V3 pools: sqrtPriceX96 ----------
def v3_mark(pool, blk, dec0, dec1, invert):
    sp = int(call(pool, "0x3850c7bd", blk)[2:][0:64], 16)
    p = (Decimal(sp) / Decimal(2**96)) ** 2          # raw1 per raw0
    usd_per_deus = p * Decimal(10) ** (dec0 - dec1)   # human1 per human0
    if invert:
        usd_per_deus = 1 / usd_per_deus
    return float(usd_per_deus)

V3_USDC = {
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": (6, 18),
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": (6, 18),
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": (6, 18),
}
print("\n--- DEUS/USDC V3 venues (token0=USDC 6dp, token1=DEUS 18dp -> invert) ---")
usdc_marks = []
for pool, (d0, d1) in V3_USDC.items():
    t0 = call(pool, "0x0dfe1681", head)
    t1 = call(pool, "0xd21220a7", head)
    now = v3_mark(pool, head, d0, d1, invert=True)
    hr = v3_mark(pool, blk1h, d0, d1, invert=True)
    chg = (now / hr - 1) * 100
    usdc_marks.append(now)
    print(f"  {pool[:10]} token0={t0[-40:][:8]} token1={t1[-40:][:8]} mark ${now:.8f}  1h {chg:+.3f}%")
print(f"  median USDC mark: ${statistics.median(usdc_marks):.8f}")

# ---------- VIRTUAL legs ----------
print("\n--- VIRTUAL venues (USD per VIRTUAL) ---")
VIRT = {
    "0x792f465e0434fB1028EA3BfeB05240CB839C4e04": "aero/Solidly",
    "0x21594b992F68495dD28d605834b58889d0a727c7": "aerodrome/Solidly",
    "0xE31c372a7Af875b3B5E0F3713B17ef51556da667": "uniswap/V3",
}
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
WETH = "0x4200000000000000000000000000000000000006"
vmarks = {}
for pool, kind in VIRT.items():
    try:
        t0 = call(pool, "0x0dfe1681", head); t1 = call(pool, "0xd21220a7", head)
        if "V3" in kind:
            sp = int(call(pool, "0x3850c7bd", head)[2:][0:64], 16)
            p = (Decimal(sp) / Decimal(2**96)) ** 2
            dec0 = token_dec("0x" + t0[-40:]); dec1 = token_dec("0x" + t1[-40:])
            # WETH is token0 or token1?
            virt_first = t0[-40:].lower() == VIRTUAL[2:].lower()
            # price in raw1 per raw0
            human = p * Decimal(10) ** (dec0 - dec1)   # token1 per token0
            eth_per_virt = human if virt_first else 1 / human
            vmarks[pool] = float(eth_per_virt)
            print(f"  {pool[:10]} V3  → {eth_per_virt:.8f} ETH/VIRTUAL")
        else:
            r = call(pool, "0x0902f1ac", head)[2:]
            r0 = int(r[0:64], 16); r1 = int(r[64:128], 16)
            virt_first = t0[-40:].lower() == VIRTUAL[2:].lower()
            ratio = (r1 / r0) if virt_first else (r0 / r1)   # WETH per VIRTUAL (both 18dp)
            vmarks[pool] = ratio
            print(f"  {pool[:10]} SOLIDLY → {ratio:.8f} ETH/VIRTUAL  (virt_first={virt_first})")
    except Exception as e:
        print(f"  {pool[:10]} ERROR {e}")

# WETH/USD
WETH_USDC_V3 = "0xd0b53D9277642d899DF5C87A3966A349A798F224"  # uniswap v3 WETH/USDC base
json.dump({"head": head, "head_ts": head_ts, "blk1h": blk1h, "ts1h": ts1h,
           "usdc_marks": usdc_marks, "virt_eth": vmarks},
          open("/home/runner/work/aeon-token/aeon-token/output/price-alert/venues.json", "w"), indent=1)

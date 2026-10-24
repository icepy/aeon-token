import json, urllib.request, time
from decimal import Decimal, getcontext
getcontext().prec = 60

RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa"
VIRT_ETH_SOLIDLY = "0x21594b992f68495dd28d605834b58889d0a727c7"
WETH_USDC_V3 = "0xd0b53D9277642d899DF5C87A3966A349A798F224"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"

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

def call(to, data, blk=None):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk) if blk else "latest"])

def blk_at(target_ts):
    head = int(rpc("eth_blockNumber", []), 16)
    lo, hi = head - 40000, head
    while lo < hi:
        m = (lo + hi) // 2
        if int(rpc("eth_getBlockByNumber", [hex(m), False])["timestamp"], 16) < target_ts:
            lo = m + 1
        else:
            hi = m
    return lo

head = int(rpc("eth_blockNumber", []), 16)
head_ts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
blk1h = blk_at(head_ts - 3600)

def v3_price(pool, blk, dec0, dec1, base_is_t0):
    sp = int(call(pool, "0x3850c7bd", blk)[2:][0:64], 16)
    p = (Decimal(sp) / Decimal(2**96)) ** 2
    human = p * Decimal(10) ** (dec0 - dec1)   # token1 per token0
    return human if base_is_t0 else 1 / human

# WETH/USDC: check orientation
t0 = call(WETH_USDC_V3, "0x0dfe1681", head)
t1 = call(WETH_USDC_V3, "0xd21220a7", head)
weth_is_t0 = "4200000000000000000000000000000000000006" in t0.lower()
dec0, dec1 = (18, 6) if weth_is_t0 else (6, 18)
eth_usd = v3_price(WETH_USDC_V3, head, dec0, dec1, weth_is_t0)
print(f"WETH/USDC pool token0={t0[-40:]} token1={t1[-40:]}  weth_is_t0={weth_is_t0}")
print(f"ETH/USD = ${float(eth_usd):,.2f}")

def virt_eth(blk):
    r = call(VIRT_ETH_SOLIDLY, "0x0902f1ac", blk)[2:]
    r0 = int(r[0:64], 16); r1 = int(r[64:128], 16)
    vt0 = call(VIRT_ETH_SOLIDLY, "0x0dfe1681", blk)
    virt_first = VIRTUAL[2:].lower() in vt0.lower()
    return Decimal(r1) / Decimal(r0) if virt_first else Decimal(r0) / Decimal(r1)

ve_now = virt_eth(head); ve_1h = virt_eth(blk1h)
v_usd_now = ve_now * eth_usd
print(f"VIRTUAL = {float(ve_now):.8f} ETH = ${float(v_usd_now):.6f}")

def reserves(pool, blk):
    r = call(pool, "0x0902f1ac", blk)[2:]
    return int(r[0:64], 16) / 1e18, int(r[64:128], 16) / 1e18

v_now, d_now = reserves(DEEP, head)
v_1h, d_1h = reserves(DEEP, blk1h)
mark_now = Decimal(v_now) / Decimal(d_now) * v_usd_now
mark_1h = Decimal(v_1h) / Decimal(d_1h) * (ve_1h * eth_usd)
print(f"\nDEEPEST POOL (VIRTUAL-quoted) mark: ${float(mark_1h):.8f} -> ${float(mark_now):.8f}  = {float((mark_now/mark_1h-1)*100):+.3f}% in 1h")
print(f"   ratio {v_1h/d_1h:.8f} -> {v_now/d_now:.8f}")

print("\n--- gate distances from deepest-pool mark ---")
m = float(mark_now)
for t in (0.012, 0.025, 0.032, 0.041):
    print(f"  {t}: {(t/m-1)*100:+.2f}%")
print(f"\nATH $0.06876 -> {(0.06876/m-1)*100:+.2f}%")

json.dump({"head": head, "head_ts": head_ts, "blk1h": blk1h,
           "eth_usd": float(eth_usd), "virtual_usd": float(v_usd_now),
           "mark_now": float(mark_now), "mark_1h": float(mark_1h),
           "ratio_now": v_now/d_now, "ratio_1h": v_1h/d_1h,
           "reserves_now": [v_now, d_now], "reserves_1h": [v_1h, d_1h]},
          open("/home/runner/work/aeon-token/aeon-token/output/price-alert/final.json", "w"), indent=1)

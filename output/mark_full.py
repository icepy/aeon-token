#!/usr/bin/env python3
"""Full DEUS mark: deepest-pool ratio x VIRTUAL/USD, plus USDC V3 cross-checks and on-chain h1."""
import json
import math
import urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    if "error" in d:
        raise RuntimeError(d["error"])
    return d["result"]

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

def addr(r):
    return "0x" + r[-40:].lower()

def dec(tok):
    return int(call(tok, "0x313ce567"), 16)

def slot0(pool, tag="latest"):
    r = call(pool, "0x3850c7bd", tag)
    return int(r[2:][0:64], 16)

def price_t1_per_t0_raw(sp, d0, d1):
    raw = (sp / (2 ** 96)) ** 2
    return raw * (10 ** d0) / (10 ** d1)

head = int(rpc("eth_blockNumber", []), 16)
blk = rpc("eth_getBlockByNumber", [hex(head), False])
head_ts = int(blk["timestamp"], 16)
print("head=%d ts=%d" % (head, head_ts))

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
WETH = "0x4200000000000000000000000000000000000006"
USDC = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"

# --- ETH and VIRTUAL USD, current
sp = slot0("0xd0b53D9277642d899DF5C87A3966A349A798F224")
eth_now = price_t1_per_t0_raw(sp, 18, 6)   # t0=WETH t1=USDC
sp = slot0("0x529d2863a1521d0b57db028168fdE2E97120017C")
virt_now = price_t1_per_t0_raw(sp, 18, 6)  # t0=VIRTUAL t1=USDC
sp = slot0("0x792f465e0434fB1028EA3BfeB05240CB839C4e04")
virt_via_eth_now = price_t1_per_t0_raw(sp, 18, 18) * eth_now
print("eth_usd=%.4f" % eth_now)
print("virtual_usd_direct=%.6f  virtual_usd_via_eth=%.6f" % (virt_now, virt_via_eth_now))

# --- deepest pool reserves now
def reserves(pool, tag="latest"):
    r = call(pool, "0x0902f1ac", tag)
    w = r[2:]
    return int(w[0:64], 16), int(w[64:128], 16)

r0, r1 = reserves(DEEP)
vres, dres = r0, r1
ratio_now = vres / dres
mark = ratio_now * virt_now
print("ratio_now=%.10f  mark_usd=%.8f" % (ratio_now, mark))
mark_via_eth = ratio_now * virt_via_eth_now
print("mark_if_virtual_via_eth=%.8f" % mark_via_eth)

# --- DEUS/USDC V3 pools: token0=USDC -> invert
usdc_pools = {
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": "aerodrome V3 DEUS/USDC",
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": "aero DEUS/USDC",
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": "aerodrome V3 DEUS/USDC",
}
marks = {}
for pool, label in usdc_pools.items():
    try:
        t0 = addr(call(pool, "0x0dfe1681"))
        t1 = addr(call(pool, "0xd21220a7"))
        sp = slot0(pool)
        if t0 == USDC and t1 == DEUS.lower():
            usd_per_deus = 1.0 / price_t1_per_t0_raw(sp, 6, 18)
        elif t0 == DEUS.lower() and t1 == USDC:
            usd_per_deus = price_t1_per_t0_raw(sp, 18, 6)
        else:
            print(json.dumps({"pool": pool, "skip": "unexpected tokens", "t0": t0, "t1": t1}))
            continue
        marks[pool] = usd_per_deus
        print(json.dumps({"pool": pool, "label": label, "mark_usd": round(usd_per_deus, 8)}))
    except Exception as e:
        print(json.dumps({"pool": pool, "label": label, "error": str(e)}))

if marks:
    vals = sorted(marks.values())
    med = vals[len(vals)//2] if len(vals) % 2 else (vals[len(vals)//2 - 1] + vals[len(vals)//2]) / 2
    print("usdc_median=%.8f  n=%d" % (med, len(vals)))
    print("deepest_vs_median_pct=%.3f" % ((mark / med - 1) * 100))

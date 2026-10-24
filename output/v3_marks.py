#!/usr/bin/env python3
"""Read V3-style sqrtPriceX96 marks and convert to USD with explicit orientation checks."""
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

def addr(call_ret):
    return "0x" + call_ret[-40:].lower()

def dec(tok):
    return int(call(tok, "0x313ce567"), 16)

def slot0(pool):
    r = call(pool, "0x3850c7bd")  # slot0()
    w = r[2:]
    return int(w[0:64], 16)

def probe(pool, label):
    try:
        t0 = addr(call(pool, "0x0dfe1681"))
        t1 = addr(call(pool, "0xd21220a7"))
        d0 = dec(t0)
        d1 = dec(t1)
        sp = slot0(pool)
        print(json.dumps({"label": label, "pool": pool, "t0": t0, "d0": d0,
                          "t1": t1, "d1": d1, "sqrtPriceX96": str(sp)}))
        return {"t0": t0, "t1": t1, "d0": d0, "d1": d1, "sp": sp, "pool": pool}
    except Exception as e:
        print(json.dumps({"label": label, "pool": pool, "error": str(e)}))
        return None

def price_1_in_0(p):
    """token1 raw units per token0 raw unit, human-adjusted: price of token0 in token1."""
    raw = (p["sp"] / (2 ** 96)) ** 2      # raw token1/token0
    return raw * (10 ** p["d0"]) / (10 ** p["d1"])

WETH = "0x4200000000000000000000000000000000000006"
USDC = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"

out = {}
out["virtual_usdc"] = probe("0x529d2863a1521d0b57db028168fdE2E97120017C", "VIRTUAL/USDC uni")
out["virtual_weth_slip"] = probe("0x792f465e0434fB1028EA3BfeB05240CB839C4e04", "VIRTUAL/WETH slip")
out["virtual_weth_uni"] = probe("0xE31c372a7Af875b3B5E0F3713B17ef51556da667", "VIRTUAL/WETH uni")
out["weth_usdc"] = probe("0xd0b53D9277642d899DF5C87A3966A349A798F224", "WETH/USDC 0.05%")
out["weth_usdc2"] = probe("0xcDAC0d6c6C59727a65F871236188350531885C43", "WETH/USDC 0.30%")

print("---DERIVED---")

def vp(p, quote_usd):
    """price of token0 in USD given price of token1 in USD."""
    if p is None:
        return None
    return price_1_in_0(p) * quote_usd

def vp_inv(p, quote_usd):
    if p is None:
        return None
    return (1.0 / price_1_in_0(p)) * quote_usd

# ETH/USD
eth = None
p = out["weth_usdc"]
if p:
    if p["t0"] == WETH:
        eth = price_1_in_0(p)   # USDC per WETH -> already USD (6dp USDC)
        print("eth_usd (weth_usdc, t0=WETH) = %.4f" % eth)
    else:
        eth = (1.0 / price_1_in_0(p))
        print("eth_usd (weth_usdc, t1=WETH) = %.4f" % eth)

# VIRTUAL/USD direct from USDC pool
p = out["virtual_usdc"]
if p:
    if p["t0"] == VIRTUAL:
        v_direct = price_1_in_0(p)
    else:
        v_direct = 1.0 / price_1_in_0(p)
    print("virtual_usd (direct USDC pool) = %.6f" % v_direct)

# VIRTUAL/USD via WETH legs
for k in ("virtual_weth_slip", "virtual_weth_uni"):
    p = out[k]
    if p and eth:
        if p["t0"] == VIRTUAL:
            v = price_1_in_0(p) * eth
        else:
            v = (1.0 / price_1_in_0(p)) * eth
        print("virtual_usd (%s) = %.6f" % (k, v))

# Final DEUS mark
ratio = 526295650273904121782893 / 18921310710200002071942720
print("ratio_virtual_per_deus=%.10f" % ratio)

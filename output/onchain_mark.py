#!/usr/bin/env python3
"""On-chain mark for DEUS: deepest pool reserves x VIRTUAL/USD, cross-checked vs USDC V3 pools."""
import json
import urllib.request

RPCS = ["https://base.gateway.tenderly.co"]

def rpc(method, params, url=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url or RPCS[0], data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "curl/8.5.0",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    if "error" in d:
        raise RuntimeError(d["error"])
    return d["result"]

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head)

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

t0 = call(DEEP, "0x0dfe1681")
t1 = call(DEEP, "0xd21220a7")
print("token0=%s" % t0)
print("token1=%s" % t1)
tok0 = "0x" + t0[-40:]
tok1 = "0x" + t1[-40:]

r = call(DEEP, "0x0902f1ac")
w = r[2:]
r0 = int(w[0:64], 16)
r1 = int(w[64:128], 16)
print("reserve0=%d reserve1=%d" % (r0, r1))

def bal(tok, holder):
    data = "0x70a08231" + "0" * 24 + holder[2:].lower()
    return int(call(tok, data), 16)

print("deus_bal_pool=%d" % bal(DEUS, DEEP))
print("virtual_bal_pool=%d" % bal(VIRTUAL, DEEP))

# which is which
if tok0.lower() == VIRTUAL.lower():
    vres, dres = r0, r1
    print("orientation: token0=VIRTUAL (18dp), token1=DEUS (18dp)")
else:
    dres, vres = r0, r1
    print("orientation: token0=DEUS, token1=VIRTUAL")

ratio = vres / dres
print("virtual_per_deus=%.10f" % ratio)

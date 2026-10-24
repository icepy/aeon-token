#!/usr/bin/env python3
"""Cross-check: USDC-quoted V3 DEUS pools (inverted mark) + VIRTUAL/USD from two live venues."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last=None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode())
            if "error" in d: raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last=e; time.sleep(1.5*(2**i))
    raise last

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to":to,"data":data}, tag])

def slot0(pool, tag="latest"):
    r = call(pool, "0x3850c7bd", tag)
    return int(r[2:][0:64], 16) if r and len(r) > 2 else None

def mark_t1_per_t0(sp, d0, d1):
    return ((sp/2**96)**2) * (10**d0)/(10**d1)

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head)

# DEUS/USDC V3 pools: token0=USDC(6), token1=DEUS(18) -> price t1/t0 = DEUS per USDC; invert for USD/DEUS
for name, addr in [("0x58dBa34e","0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b"),
                   ("0x1B2f3f5C","0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642"),
                   ("0x75bc1495","0x75bc14950Ab093cBd1f80BbbDf458596939180A3")]:
    try:
        t0 = call(addr, "0x0dfe1681"); t1 = call(addr, "0xd21220a7")
        d0 = call(addr, "0x313ce567"); d1 = call(addr, "0x313ce567")
        sp = slot0(addr)
        # decimals: token0=USDC -> 6, token1=DEUS -> 18 (confirmed prior runs)
        p = mark_t1_per_t0(sp, 6, 18)   # DEUS per USDC
        print("%s t0=%s t1=%s sqrt=%d  DEUS_per_USDC=%.6f  USD_per_DEUS=%.8f" % (
            name, t0[-40:], t1[-40:], sp, p, 1.0/p if p else 0))
    except Exception as e:
        print("%s ERROR %s" % (name, e))

# VIRTUAL/USD from two venues
VIRT_USDC = "0x529d2863a1521d0b57db028168fdE2E97120017C"
VIRT_WETH = "0x792f465e0434fB1028EA3BfeB05240CB839C4e04"
WETH_USDC = "0xd0b53D9277642d899DF5C87A3966A349A798F224"

try:
    sp = slot0(VIRT_USDC)
    print("VIRTUAL/USDC(0x529d) USD/DEUS-> USD per VIRTUAL = %.6f" % mark_t1_per_t0(sp, 18, 6))
except Exception as e:
    print("VIRT/USDC ERR", e)

try:
    r = call(VIRT_WETH, "0x0902f1ac")
    w = r[2:]
    r0 = int(w[0:64],16); r1 = int(w[64:128],16)
    # token0/token1 order check
    t0 = call(VIRT_WETH, "0x0dfe1681"); t1 = call(VIRT_WETH, "0xd21220a7")
    print("VIRT/WETH t0=%s t1=%s r0=%.6f r1=%.6f" % (t0[-40:], t1[-40:], r0/1e18, r1/1e18))
    ethusd = mark_t1_per_t0(slot0(WETH_USDC), 18, 6)
    print("ETH/USD(WETH/USDC 0xd0b5) = %.4f" % ethusd)
    # 0x792f: if t0=VIRTUAL(18), t1=WETH(18) -> WETH per VIRTUAL
    weth_per_virtual = (r1/1e18)/(r0/1e18)
    print("WETH_per_VIRTUAL=%.10f  => USD/VIRTUAL=%.6f" % (weth_per_virtual, weth_per_virtual*ethusd))
except Exception as e:
    print("VIRT/WETH ERR", e)

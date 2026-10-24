#!/usr/bin/env python3
"""Corrected V3 marks: call decimals() on the TOKEN, not the pool."""
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

def calli(to, data, tag="latest"):
    r = rpc("eth_call", [{"to":to,"data":data}, tag])
    return int(r[2:][0:64], 16) if r and len(r) >= 66 else None

DEC = {}
def dec(tok):
    if tok not in DEC:
        DEC[tok] = calli(tok, "0x313ce567")
    return DEC[tok]

def v3_mark(pool, tag="latest"):
    t0r = rpc("eth_call", [{"to":pool,"data":"0x0dfe1681"}, tag])
    t1r = rpc("eth_call", [{"to":pool,"data":"0xd21220a7"}, tag])
    t0 = "0x"+t0r[-40:]; t1 = "0x"+t1r[-40:]
    sp = calli(pool, "0x3850c7bd", tag)
    d0, d1 = dec(t0), dec(t1)
    # price of token1 per token0 in raw units -> human
    p_t1_per_t0 = ((sp/2**96)**2) * (10**d0)/(10**d1)
    return t0, t1, d0, d1, sp, p_t1_per_t0

head = int(rpc("eth_blockNumber", []), 16)
print("head=%d" % head)

USDC = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
VIRT = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
WETH = "0x4200000000000000000000000000000000000006"

print("\n-- DEUS/USDC V3 pools (token0=USDC 6dp, token1=DEUS 18dp) --")
marks = []
for name, addr in [("0x58dBa34e","0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b"),
                   ("0x1B2f3f5C","0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642"),
                   ("0x75bc1495","0x75bc14950Ab093cBd1f80BbbDf458596939180A3")]:
    t0,t1,d0,d1,sp,p = v3_mark(addr)
    # p = DEUS per USDC -> USD per DEUS = 1/p
    usd = 1.0/p
    marks.append((name, usd))
    print("  %s t0=%s(%d) t1=%s(%d) DEUS/USDC=%.4f  USD/DEUS=%.8f" % (name, t0[-8:], d0, t1[-8:], d1, p, usd))

if marks:
    vals = sorted(m[1] for m in marks)
    med = vals[len(vals)//2] if len(vals)%2 else (vals[len(vals)//2-1]+vals[len(vals)//2])/2
    print("  median USD/DEUS (USDC venues) = %.8f" % med)

print("\n-- VIRTUAL/USD --")
t0,t1,d0,d1,sp,p = v3_mark("0x529d2863a1521d0b57db028168fdE2E97120017C")
print("  VIRT/USDC t0=%s(%d) t1=%s(%d) USD per VIRTUAL=%.6f" % (t0[-8:],d0,t1[-8:],d1,p))
virt_usd = p

t0,t1,d0,d1,sp,pw = v3_mark("0x792f465e0434fB1028EA3BfeB05240CB839C4e04")
print("  VIRT/WETH t0=%s(%d) t1=%s(%d) WETH per VIRTUAL=%.10f" % (t0[-8:],d0,t1[-8:],d1,pw))
t0e,t1e,d0e,d1e,spe,pe = v3_mark("0xd0b53D9277642d899DF5C87A3966A349A798F224")
# WETH/USDC: token0=WETH? check
print("  WETH/USDC t0=%s(%d) t1=%s(%d) val=%.4f" % (t0e[-8:],d0e,t1e[-8:],d1e,pe))
eth_usd = pe if t0e.lower()==WETH else 1.0/pe
print("  ETH/USD=%.4f" % eth_usd)
print("  VIRTUAL via WETH leg = %.6f" % (pw*eth_usd))

print("\n-- deepest pool (Solidly VIRTUAL/DEUS) --")
r = rpc("eth_call", [{"to":"0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa","data":"0x0902f1ac"}, "latest"])
w = r[2:]
v = int(w[0:64],16)/1e18; dd = int(w[64:128],16)/1e18
ratio = v/dd
print("  reserves VIRTUAL=%.4f DEUS=%.4f ratio=%.10f VIRTUAL per DEUS" % (v, dd, ratio))
print("  mark = ratio x VIRTUAL_price:")
for label, vp in [("VIRT/USDC", virt_usd), ("VIRT/WETH leg", pw*eth_usd)]:
    print("    %-14s $%.8f" % (label, ratio*vp))

#!/usr/bin/env python3
"""Isolate which view selector reverts per pool."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=3):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last=None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            if "error" in d: raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last=e; time.sleep(1.0*(2**i))
    raise last

SEL = {"token0":"0x0dfe1681","token1":"0xd21220a7","decimals":"0x313ce567",
       "slot0":"0x3850c7bd","getReserves":"0x0902f1ac","fee":"0xddca3f43",
       "liquidity":"0x1a686502","stable":"0x22be3de1","globalState":"0xe76c01e4"}

POOLS = {
 "0x58dBa34e":"0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b",
 "0x1B2f3f5C":"0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642",
 "0x75bc1495":"0x75bc14950Ab093cBd1f80BbbDf458596939180A3",
 "VIRT/WETH":"0x792f465e0434fB1028EA3BfeB05240CB839C4e04",
 "DEEP":"0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
 "VIRT/USDC":"0x529d2863a1521d0b57db028168fdE2E97120017C",
}

for name, addr in POOLS.items():
    print("== %s %s" % (name, addr))
    for sname, sel in SEL.items():
        try:
            r = rpc("eth_call", [{"to": addr, "data": sel}, "latest"])
            print("   %-12s OK len=%d %s" % (sname, len(r), r[:130]))
        except Exception as e:
            print("   %-12s REVERT/ERR %s" % (sname, str(e)[:90]))

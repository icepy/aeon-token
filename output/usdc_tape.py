import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
V3_TOPIC = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
POOLS = {
    "0x58dBa34e": "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b",
    "0x1B2f3f5C": "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642",
    "0x75bc1495": "0x75bc14950Ab093cBd1f80BbbDf458596939180A3",
}
START, END = 53037783, 53039582


def rpc(payload, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
            )
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


for name, addr in POOLS.items():
    logs = []
    lo = START
    ok = True
    while lo <= END:
        hi = min(lo + 999, END)
        r = rpc(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_getLogs",
                "params": [
                    {
                        "address": addr,
                        "topics": [V3_TOPIC],
                        "fromBlock": hex(lo),
                        "toBlock": hex(hi),
                    }
                ],
            }
        )
        if r is None:
            ok = False
            break
        if "error" in r:
            print(name, "ERR", r["error"])
            ok = False
            break
        logs.extend(r["result"])
        lo = hi + 1
    if not ok:
        continue
    # V3 Swap: amount0, amount1, sqrtPriceX96, liquidity, tick
    net_deus = 0.0
    vol = 0.0
    for L in logs:
        d = L["data"][2:]
        a0 = int(d[0:64], 16)
        a1 = int(d[64:128], 16)
        if a0 >= 2**255:
            a0 -= 2**256
        if a1 >= 2**255:
            a1 -= 2**256
        # token0=USDC(6dp), token1=DEUS(18dp)
        net_deus += a1 / 1e18
        vol += abs(a1) / 1e18
    print(name, "swaps", len(logs), "net_deus(+ = into pool)", round(net_deus, 2), "vol", round(vol, 2))
    time.sleep(1)

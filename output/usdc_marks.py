import json, urllib.request

URL = "https://base.gateway.tenderly.co"
USDC_POOLS = {
    "0x58dBa34e": "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b",
    "0x75bc1495": "0x75bc14950Ab093cBd1f80BbbDf458596939180A3",
    "0x1B2f3f5C": "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642",
}


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def mark(pool, block):
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": pool, "data": "0x3850c7bd"}, hex(block)],
        }
    )
    if "error" in r:
        return None
    sq = int(r["result"][2:66], 16)
    ratio = (sq / 2**96) ** 2 * 10 ** (6 - 18)
    return 1 / ratio


for blk in (53037782, 53039582):
    vals = []
    for k, p in USDC_POOLS.items():
        m = mark(p, blk)
        vals.append(m)
        print(blk, k, "n/a" if m is None else round(m, 8))
    ok = [v for v in vals if v]
    vals_sorted = sorted(ok)
    med = vals_sorted[len(vals_sorted) // 2]
    print(blk, "USDC median", round(med, 8))
    print()

deep_1h = 0.017192991120988578
deep_now = 0.01735651487005396
print("deepest 1h vs now pct", (deep_now / deep_1h - 1) * 100)

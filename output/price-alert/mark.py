import json, urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
VUSDC_POOL = "0x529d2863"  # truncated guard; real address set below


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def call(to, data, blk="latest"):
    r = rpc("eth_call", [{"to": to, "data": data}, blk])
    return r.get("result"), (r.get("error") or {}).get("message")


def dec(hexstr):
    return int(hexstr, 16) if hexstr and hexstr != "0x" else 0


def wallet(addr, calldata):
    out, err = call(addr, calldata)
    if err or not out:
        return None
    return dec(out)


def main():
    b = int(rpc("eth_blockNumber", [])["result"], 16)
    now_ts = int(rpc("eth_getBlockByNumber", [hex(b), False])["result"]["timestamp"], 16)

    # ---- reserves now + 1h ago ----
    def reserves(blk):
        out, _ = call(POOL, "0x0902f1ac", blk)
        raw = out[2:]
        return dec("0x" + raw[0:64]), dec("0x" + raw[64:128])

    r0, r1 = reserves(hex(b))
    # find block ~3600s back by walking
    lo, hi = b - 3000, b
    target = now_ts - 3600
    blk_1h = None
    while lo <= hi:
        mid = (lo + hi) // 2
        ts = int(rpc("eth_getBlockByNumber", [hex(mid), False])["result"]["timestamp"], 16)
        if ts <= target:
            blk_1h = mid
            lo = mid + 1
        else:
            hi = mid - 1
    p0, p1 = reserves(hex(blk_1h))
    ts_1h = int(rpc("eth_getBlockByNumber", [hex(blk_1h), False])["result"]["timestamp"], 16)

    # VIRTUAL is token0 (18 dec), DEUS token1 (18 dec)
    ratio_now = r0 / r1
    ratio_1h = p0 / p1
    print("block_now", b, "ts", now_ts)
    print("block_1h", blk_1h, "ts", ts_1h, "delta_s", now_ts - ts_1h)
    print("VIRTUAL_reserve_now", r0 / 1e18, "DEUS_reserve_now", r1 / 1e18)
    print("VIRTUAL_reserve_1h", p0 / 1e18, "DEUS_reserve_1h", p1 / 1e18)
    print("ratio_now %.8f ratio_1h %.8f  chg %% %.4f" % (ratio_now, ratio_1h, (ratio_now / ratio_1h - 1) * 100))

    # ---- VIRTUAL price via its deepest USDC pool ----
    ds = json.load(open("/tmp/ds.json"))
    pairs = [x for x in ds.get("pairs", []) if x.get("chainId") == "base"]
    print("deepest_pair_priceUsd", pairs[0].get("priceUsd"), "priceNative", pairs[0].get("priceNative"))

    # USDC-quoted DEUS venues
    usdc = [x for x in pairs if x["quoteToken"]["symbol"] == "USDC"]
    prices = sorted(float(x["priceUsd"]) for x in usdc if x.get("priceUsd"))
    med = prices[len(prices) // 2] if prices else None
    print("usdc_venue_prices", prices, "median", med)

    print("implied_from_ratio_at_ds_native", pairs[0].get("priceUsd"))


main()

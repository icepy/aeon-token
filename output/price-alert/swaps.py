import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def get_logs(lo, hi, **extra):
    params = {"address": POOL, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [SWAP]}
    params.update(extra)
    out = rpc("eth_getLogs", [params])
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


def s(h):
    return int(h, 16) - (1 << 256) if int(h, 16) > (1 << 255) else int(h, 16)


def main():
    b = int(rpc("eth_blockNumber", [])["result"], 16)
    now_ts = int(rpc("eth_getBlockByNumber", [hex(b), False])["result"]["timestamp"], 16)
    # binary search for block 1h ago
    lo, hi = b - 3000, b
    target = now_ts - 3600
    b1 = None
    while lo <= hi:
        mid = (lo + hi) // 2
        ts = int(rpc("eth_getBlockByNumber", [hex(mid), False])["result"]["timestamp"], 16)
        if ts <= target:
            b1 = mid
            lo = mid + 1
        else:
            hi = mid - 1
    print("window", b1, "->", b, "blocks", b - b1)

    logs = []
    start = b1
    while start <= b:
        end = min(start + 999, b)
        logs.extend(get_logs(start, end))
        start = end + 1
    print("swap_events", len(logs))

    rows = []
    for lg in logs:
        d = lg["data"][2:]
        words = [d[i:i + 64] for i in range(0, len(d), 64)]
        # Solidly Swap: amount0In, amount1Out, amount0Out, amount1In, to
        a0in = int(words[0], 16)
        a1out = int(words[1], 16)
        a0out = int(words[2], 16)
        a1in = int(words[3], 16)
        # token0 = VIRTUAL (18), token1 = DEUS (18)
        deus_in = a1in / 1e18
        deus_out = a1out / 1e18
        ts = int(rpc("eth_getBlockByNumber", [lg["blockNumber"], False])["result"]["timestamp"], 16)
        rows.append({
            "tx": lg["transactionHash"],
            "blk": int(lg["blockNumber"], 16),
            "ts": ts,
            "deus_in": deus_in,
            "deus_out": deus_out,
            "sender": "0x" + lg["topics"][1][-40:],
            "to": "0x" + lg["topics"][2][-40:] if len(lg["topics"]) > 2 else None,
        })

    buys = [r for r in rows if r["deus_out"] > 0]   # DEUS leaving pool = buy
    sells = [r for r in rows if r["deus_in"] > 0]
    print("buys", len(buys), "sum_deus_out %.3f" % sum(r["deus_out"] for r in buys))
    print("sells", len(sells), "sum_deus_in %.3f" % sum(r["deus_in"] for r in sells))
    print("net_into_pool %.3f" % (sum(r["deus_in"] for r in sells) - sum(r["deus_out"] for r in buys)))

    rows.sort(key=lambda r: -(r["deus_in"] + r["deus_out"]))
    print("\ntop 5 by size:")
    for r in rows[:5]:
        import datetime
        t = datetime.datetime.fromtimestamp(r["ts"], datetime.timezone.utc).strftime("%H:%M:%SZ")
        print(" ", t, "blk", r["blk"], "in %.3f out %.3f" % (r["deus_in"], r["deus_out"]), r["sender"], r["tx"][:18])

    gaps = []
    prev = None
    for r in sorted(rows, key=lambda x: x["ts"]):
        if prev is not None:
            gaps.append(r["ts"] - prev)
        prev = r["ts"]
    if gaps:
        print("\nmax_gap_s", max(gaps), "median_gap_s", sorted(gaps)[len(gaps) // 2])


main()

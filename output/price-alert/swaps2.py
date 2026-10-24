import json, urllib.request, datetime
from collections import Counter

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SOLIDLY_SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def get_logs(lo, hi):
    out = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(lo), "toBlock": hex(hi),
                               "topics": [SOLIDLY_SWAP]}])
    if "error" in out:
        raise RuntimeError(json.dumps(out["error"])[:300])
    return out["result"]


def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%H:%M:%SZ")


def main():
    b = int(rpc("eth_blockNumber", [])["result"], 16)
    now_ts = int(rpc("eth_getBlockByNumber", [hex(b), False])["result"]["timestamp"], 16)
    lo, hi = b - 3000, b
    target = now_ts - 3600
    b1 = None
    while lo <= hi:
        mid = (lo + hi) // 2
        ts = int(rpc("eth_getBlockByNumber", [hex(mid), False])["result"]["timestamp"], 16)
        if ts <= target:
            b1, lo = mid, mid + 1
        else:
            hi = mid - 1

    logs, start = [], b1
    while start <= b:
        end = min(start + 999, b)
        logs.extend(get_logs(start, end))
        start = end + 1

    ts_cache = {}
    rows = []
    for lg in logs:
        d = lg["data"][2:]
        w = [d[i:i + 64] for i in range(0, len(d), 64)]
        if len(w) < 4:
            continue
        a0in, a1in, a0out, a1out = (int(x, 16) for x in w[:4])
        blk = int(lg["blockNumber"], 16)
        if blk not in ts_cache:
            ts_cache[blk] = int(rpc("eth_getBlockByNumber", [hex(blk), False])["result"]["timestamp"], 16)
        rows.append({
            "ts": ts_cache[blk], "blk": blk, "tx": lg["transactionHash"],
            "sender": "0x" + lg["topics"][1][-40:],
            "deus_in": a1in / 1e18, "deus_out": a1out / 1e18,
            "virt_in": a0in / 1e18, "virt_out": a0out / 1e18,
        })

    print("window", b1, "->", b, " swaps", len(rows))
    buys = [r for r in rows if r["deus_out"] > 0]
    sells = [r for r in rows if r["deus_in"] > 0]
    print("buys %d  sum_deus_out %.3f" % (len(buys), sum(r["deus_out"] for r in buys)))
    print("sells %d  sum_deus_in %.3f" % (len(sells), sum(r["deus_in"] for r in sells)))
    print("net_deus_into_pool %.3f" % (sum(r["deus_in"] for r in sells) - sum(r["deus_out"] for r in buys)))

    print("\nlargest 6:")
    for r in sorted(rows, key=lambda x: -(x["deus_in"] + x["deus_out"]))[:6]:
        print("  %s blk %d  DEUS in %.3f / out %.3f  %s" % (utc(r["ts"]), r["blk"], r["deus_in"], r["deus_out"], r["sender"]))

    rs = sorted(rows, key=lambda x: x["ts"])
    if len(rs) > 1:
        gaps = [rs[i + 1]["ts"] - rs[i]["ts"] for i in range(len(rs) - 1)]
        print("\nfirst %s  last %s" % (utc(rs[0]["ts"]), utc(rs[-1]["ts"])))
        print("max_gap_s", max(gaps), "median_gap_s", sorted(gaps)[len(gaps) // 2])

    senders = Counter(r["sender"] for r in rows)
    print("\nunique_senders", len(senders))
    for s_, n in senders.most_common(5):
        print(" ", s_, n)


main()

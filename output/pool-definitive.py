#!/usr/bin/env python3
"""Definitive deepest-pool read: strict (block, logIndex) ordering, exact reserve path."""
import json
import sys
import time
import urllib.request
from decimal import Decimal, getcontext

getcontext().prec = 60
RPCS = ["https://base.gateway.tenderly.co", "https://base-rpc.publicnode.com"]
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
VIRTUAL_USD = Decimal("0.6312889301405042")  # on-chain VIRTUAL/USDC uni pool 0x529d2863, sqrtPriceX96


def rpc(method, params):
    last = None
    for _ in range(3):
        for url in RPCS:
            try:
                body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
                req = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    j = json.loads(r.read())
                if "error" in j:
                    last = j["error"]
                    continue
                return j["result"]
            except Exception as e:  # noqa: BLE001
                last = e
        time.sleep(1)
    raise RuntimeError(f"{method} {last}")


_TS = {}


def bts(n):
    if n not in _TS:
        _TS[n] = int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)
    return _TS[n]


def main():
    head = int(rpc("eth_blockNumber", []), 16)
    head_ts = bts(head)
    print(f"head={head} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(head_ts))}")

    raw = []
    s = head - 43200
    while s <= head:
        e = min(s + 899, head)
        raw.extend(rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(s), "toBlock": hex(e)}]))
        s = e + 1

    ev = []
    for lg in raw:
        t0 = lg["topics"][0]
        d = lg["data"][2:]
        w = [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]
        ev.append({"li": lg["logIndex"], "bn": int(lg["blockNumber"], 16), "t0": t0, "w": w,
                   "tx": lg["transactionHash"]})
    ev.sort(key=lambda r: (r["bn"], r["li"]))
    print(f"events 24h: {len(ev)}")

    # reserve0 = VIRTUAL (18dp), reserve1 = DEUS (18dp)
    path = []
    for e in ev:
        if e["t0"] == SYNC and len(e["w"]) >= 2:
            v = Decimal(e["w"][0]) / Decimal(10 ** 18)
            d = Decimal(e["w"][1]) / Decimal(10 ** 18)
            path.append({"bn": e["bn"], "ts": bts(e["bn"]), "v": v, "d": d, "ratio": v / d})
    path.sort(key=lambda r: r["bn"])
    print(f"syncs: {len(path)}")
    print(f"  newest reserves: VIRTUAL {path[-1]['v']:,.2f} / DEUS {path[-1]['d']:,.2f}")
    print(f"  ratio VIRTUAL/DEUS = {path[-1]['ratio']:.8f} -> USD ${path[-1]['ratio'] * VIRTUAL_USD:.8f}/DEUS")

    # strict per-event DEUS delta from Swap, sum by window using ts
    def win(label, back):
        cut = head_ts - back
        sw = [e for e in ev if e["t0"] == SWAP and bts(e["bn"]) >= cut]
        sy = [p for p in path if p["ts"] >= cut]
        vol = Decimal(0)
        net = Decimal(0)
        for e in sw:
            if len(e["w"]) < 4:
                continue
            a1in = Decimal(e["w"][1]) / Decimal(10 ** 18)
            a1out = Decimal(e["w"][3]) / Decimal(10 ** 18)
            net += a1in - a1out
            vol += abs(a1in - a1out)
        if not sy:
            print(f"\n{label}: 0 syncs -> NOT MEASURED")
            return
        m0, m1 = sy[0]["ratio"], sy[-1]["ratio"]
        print(f"\n{label}: {len(sw)} swaps | DEUS vol {vol:,.1f} | net DEUS {'+' if net >= 0 else ''}{net:,.1f} (into pool) "
              f"| VIRTUAL/DEUS {m0:.8f} -> {m1:.8f} = {((m1 / m0) - 1) * 100:+.3f}%")
        print(f"   USD: ${m0 * VIRTUAL_USD:.8f} -> ${m1 * VIRTUAL_USD:.8f} "
              f"({((m1 / m0) - 1) * 100:+.3f}%)")
        print(f"   window {time.strftime('%m-%dT%H:%M:%SZ', time.gmtime(sy[0]['ts']))} -> {time.strftime('%m-%dT%H:%M:%SZ', time.gmtime(sy[-1]['ts']))}")

    for label, back in (("1h", 3600), ("6h", 21600), ("24h", 86400)):
        win(label, back)

    # decode the 50k tx specifically
    tx = "0x72935a6a89f30f0b158c8ad9552f28b0cfdb94e5bead7718bff24419c695b918"
    print(f"\n-- tx {tx} --")
    rc = rpc("eth_getTransactionReceipt", [tx])
    for lg in rc["logs"]:
        if lg["address"].lower() == POOL.lower():
            d = lg["data"][2:]
            w = [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]
            print(f"  {lg['topics'][0]}")
            if lg["topics"][0] == SWAP:
                print(f"    a0in={w[0]/1e18:,.4f} a1in={w[1]/1e18:,.4f} a0out={w[2]/1e18:,.4f} a1out={w[3]/1e18:,.4f}")
            elif lg["topics"][0] == SYNC:
                print(f"    r0(VIRTUAL)={w[0]/1e18:,.4f} r1(DEUS)={w[1]/1e18:,.4f}")


if __name__ == "__main__":
    main()

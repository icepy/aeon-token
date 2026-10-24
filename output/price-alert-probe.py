#!/usr/bin/env python3
"""price-alert probe v2: measure DEUS mark + 1h/24h change from on-chain V3 Swap logs.

Pools are USDC(token0, 6dp) / DEUS(token1, 18dp) Uniswap-V3 forks on Base.
price = token1 per token0 from sqrtPriceX96, adjusted by decimals, then inverted
to get USD per DEUS (token0 is USDC, ~$1).
"""
import json
import sys
import time
import urllib.request
from decimal import Decimal, getcontext

getcontext().prec = 60

RPCS = [
    "https://base.gateway.tenderly.co",
    "https://base-rpc.publicnode.com",
    "https://mainnet.base.org",
]

V3_SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"

POOLS = {
    # pool -> (token0_decimals, token1_decimals)
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": (6, 18),
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": (6, 18),
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": (6, 18),
}

WINDOWS = {"1h": 3600, "6h": 6 * 3600, "24h": 86400}


def rpc(method, params):
    last = None
    for attempt in range(4):
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
        time.sleep(1 + attempt)
    raise RuntimeError(f"{method} failed: {last}")


_TS = {}


def block_ts(n):
    if n not in _TS:
        b = rpc("eth_getBlockByNumber", [hex(n), False])
        _TS[n] = int(b["timestamp"], 16)
    return _TS[n]


def get_logs(addr, frm, to, topics=None):
    out, start = [], frm
    while start <= to:
        end = min(start + 899, to)
        p = {"address": addr, "fromBlock": hex(start), "toBlock": hex(end)}
        if topics:
            p["topics"] = topics
        try:
            out.extend(rpc("eth_getLogs", [p]))
        except RuntimeError as e:  # noqa: BLE001
            print(f"    warn: chunk {start}-{end} failed ({e})", file=sys.stderr)
        start = end + 1
    return out


def usd_per_deus(sqrt_x96, d0, d1):
    """token0=USDC($1), token1=DEUS. price token1/token0 raw -> human -> invert."""
    sp = Decimal(int(sqrt_x96)) / (Decimal(2) ** 96)
    raw = sp * sp  # token1 per token0, raw units
    human = raw * (Decimal(10) ** d0) / (Decimal(10) ** d1)  # DEUS per USDC
    if human == 0:
        return None
    return Decimal(1) / human  # USD per DEUS


def main():
    head = int(rpc("eth_blockNumber", []), 16)
    head_ts = block_ts(head)
    print(f"HEAD block={head} ts={head_ts} ({time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(head_ts))})")

    all_marks = {}
    summary = {}

    for addr, (d0, d1) in POOLS.items():
        print(f"\n=== {addr} ===")
        # Tell: never trust a filter until the family is confirmed by histogram.
        hist = {}
        for lg in get_logs(addr, max(0, head - 899), head):
            hist[lg["topics"][0]] = hist.get(lg["topics"][0], 0) + 1
        print(f"  topic0 histogram (last 900 blocks): {hist}")

        logs = get_logs(addr, max(0, head - 86400 // 2), head, [V3_SWAP])
        print(f"  24h V3 Swap logs: {len(logs)}")

        rows = []
        for lg in logs:
            data = lg["data"][2:]
            w = [data[i:i + 64] for i in range(0, len(data), 64)]
            if len(w) < 5:
                continue
            a0 = int(w[0], 16)
            if a0 >= 2 ** 255:
                a0 -= 2 ** 256
            a1 = int(w[1], 16)
            if a1 >= 2 ** 255:
                a1 -= 2 ** 256
            sqrtp = int(w[2], 16)
            bn = int(lg["blockNumber"], 16)
            rows.append({"block": bn, "ts": block_ts(bn), "a0": a0, "a1": a1, "sqrtp": sqrtp,
                         "tx": lg["transactionHash"]})
        rows.sort(key=lambda r: (r["block"], r["ts"]))

        if not rows:
            print("  no swaps -> pool NOT MEASURED")
            continue

        m_now = usd_per_deus(rows[-1]["sqrtp"], d0, d1)
        print(f"  latest on-chain mark: ${m_now:.8f}  (last swap {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(rows[-1]['ts']))})")
        all_marks[addr] = float(m_now)

        for label, back in WINDOWS.items():
            cut = head_ts - back
            inside = [r for r in rows if r["ts"] >= cut]
            if not inside:
                print(f"  {label}: 0 swaps -> NOT MEASURED (do not read as flat)")
                summary.setdefault(label, {})[addr] = None
                continue
            m0 = usd_per_deus(inside[0]["sqrtp"], d0, d1)
            m1 = usd_per_deus(inside[-1]["sqrtp"], d0, d1)
            chg = (m1 / m0 - 1) * 100
            # DEUS volume = |a1| (token1)
            vol = sum(abs(r["a1"]) for r in inside) / Decimal(10 ** d1)
            print(f"  {label}: {len(inside)} swaps | ${m0:.8f} -> ${m1:.8f} = {chg:+.3f}% | DEUS vol {vol:,.1f}")
            summary.setdefault(label, {})[addr] = {
                "swaps": len(inside), "chg_pct": float(chg), "vol_deus": float(vol),
                "start": float(m0), "end": float(m1),
            }

    print("\n=== AGGREGATE ===")
    for label in WINDOWS:
        vals = summary.get(label, {})
        chgs = [v["chg_pct"] for v in vals.values() if v]
        total_vol = sum(v["vol_deus"] for v in vals.values() if v)
        if chgs:
            avg = sum(chgs) / len(chgs)
            print(f"  {label}: pools measured={len(chgs)}/3 | mean chg {avg:+.3f}% | total DEUS vol {total_vol:,.1f}")
        else:
            print(f"  {label}: NO POOL MEASURED")
    if all_marks:
        ms = sorted(all_marks.values())
        med = ms[len(ms) // 2] if len(ms) % 2 else (ms[len(ms) // 2 - 1] + ms[len(ms) // 2]) / 2
        print(f"  median live mark: ${med:.8f}")
    print("\n" + json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())

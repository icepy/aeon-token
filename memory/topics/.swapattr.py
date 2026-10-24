import json, urllib.request, collections

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
FB, TB = "0x3292cf0", "0x32930d8"


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


logs = call("eth_getLogs", [{"address": POOL, "fromBlock": FB, "toBlock": TB, "topics": [SWAP]}])["result"]
print("swaps", len(logs))

by_tx = collections.defaultdict(list)
for lg in logs:
    by_tx[lg["transactionHash"]].append(lg)
print("unique txs", len(by_tx))

rows = []
for tx, lgs in by_tx.items():
    info = call("eth_getTransactionByHash", [tx])["result"]
    frm, to = info["from"], info["to"]
    deus_bought = 0.0
    deus_sold = 0.0
    virt = 0.0
    for lg in lgs:
        d = lg["data"][2:]
        a0i, a1i, a0o, a1o = (int(d[i:i + 64], 16) / 1e18 for i in (0, 64, 128, 192))
        deus_bought += a1o
        deus_sold += a1i
        virt += a0i if a0i else a0o
    rows.append((deus_bought, deus_sold, virt, frm, to, tx))

rows.sort(key=lambda r: -(r[0] + r[1]))
print("\n-- per-tx --")
for b, s, v, frm, to, tx in rows:
    print(f"{'BUY ' if b else 'SELL'} deus={b or s:10.2f} virt={v:9.2f} from={frm} to={to} {tx[:12]}")

print("\n-- tx.from histogram --")
for k, v in collections.Counter(r[3] for r in rows).most_common():
    print(f"  {k} {v}")

print("\n-- deus moved by tx.from --")
agg = collections.defaultdict(lambda: [0.0, 0.0])
for b, s, v, frm, to, tx in rows:
    agg[frm][0] += b
    agg[frm][1] += s
for k, (b, s) in sorted(agg.items(), key=lambda kv: -(kv[1][0] + kv[1][1])):
    print(f"  {k} buys_deus={b:10.2f} sells_deus={s:10.2f} net={b - s:+10.2f}")

net_deus = sum(r[0] for r in rows) - sum(r[1] for r in rows)
print(f"\npool net DEUS out (bought by takers) = {net_deus:+.2f}")
print("buys", sum(1 for r in rows if r[0]), "sells", sum(1 for r in rows if r[1]))

codes = {}
for frm in set(r[3] for r in rows) | set(r[4] for r in rows):
    if frm is None:
        continue
    c = call("eth_getCode", [frm, "latest"])["result"]
    codes[frm] = (len(c) - 2) // 2
print("\n-- code size (bytes) --")
for k, v in codes.items():
    kind = "EOA" if v == 0 else ("EIP-7702" if v == 23 else f"contract")
    print(f"  {k} {v}B {kind}")

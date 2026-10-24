import json, urllib.request, datetime, collections

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


def ts(b):
    return datetime.datetime.fromtimestamp(
        int(call("eth_getBlockByNumber", [hex(b), False])["timestamp"], 16), datetime.UTC
    ).strftime("%H:%M:%SZ")


def reserves(block):
    d = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(block)])[2:]
    return int(d[0:64], 16) / 1e18, int(d[64:128], 16) / 1e18


head = int(call("eth_blockNumber", []), 16)
start = head - 1800
print("head", head, ts(head), "| window start", start, ts(start))

v0, d0 = reserves(start)
v1, d1 = reserves(head)

logs = []
b = start
while b < head:
    e = min(b + 999, head)
    chunk = call("eth_getLogs", [{"address": POOL, "fromBlock": hex(b), "toBlock": hex(e), "topics": [SWAP]}])
    logs.extend(chunk)
    b = e + 1

buy_ct = sell_ct = 0
buys = sells = 0.0
v_in = v_out = 0.0
feeds = []
for lg in logs:
    d = lg["data"][2:]
    a0i, a1i, a0o, a1o = (int(d[i:i + 64], 16) / 1e18 for i in (0, 64, 128, 192))
    v_in += a0i
    v_out += a0o
    if a1o:
        buy_ct += 1
        buys += a1o
    if a1i:
        sell_ct += 1
        sells += a1i
    feeds.append((a1o, a1i, a0i, a0o, lg["transactionHash"], lg["blockNumber"]))

net_deus = buys - sells
print(f"\nswaps n={len(logs)}  buys={buy_ct} ({buys:,.2f} DEUS)  sells={sell_ct} ({sells:,.2f} DEUS)")
print(f"net DEUS {'OUT of' if net_deus>0 else 'INTO'} pool {abs(net_deus):,.2f}")
print(f"\nreserves start VIRTUAL {v0:,.2f} DEUS {d0:,.2f}")
print(f"reserves head  VIRTUAL {v1:,.2f} DEUS {d1:,.2f}")
print(f"delta VIRTUAL {v1-v0:+,.2f} DEUS {d1-d0:+,.2f}")
print(f"event-implied dDEUS {-(net_deus):+,.2f}")
print(f"reconcile DEUS {(d1-d0)-(-net_deus):+.4f}   VIRTUAL fee residual {(v1-v0)-(v_in-v_out):+.4f} (={(v1-v0)/(v_in-v_out) if v_in-v_out else 0:.4f} of input)")

print(f"\nratio {v0/d0:.6f} -> {v1/d1:.6f} = {(v1/d1)/(v0/d0)*100-100:+.4f}%")

print("\n-- sells --")
for a1o, a1i, a0i, a0o, tx, blk in feeds:
    if a1i:
        print(f"  SELL {a1i:10.2f} DEUS for {a0o:9.2f} VIRTUAL blk {int(blk,16)} {tx}")

print("\n-- largest buys --")
for r in sorted(feeds, key=lambda x: -x[0])[:5]:
    print(f"  BUY {r[0]:10.2f} DEUS with {r[2]:9.2f} VIRTUAL blk {int(r[5],16)} {r[4]}")

import json, urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def reserves(block):
    res = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(block)])["result"]
    d = res[2:]
    return int(d[0:64], 16) / 1e18, int(d[64:128], 16) / 1e18, int(d[128:192], 16)


FB, TB = 0x3292cf0, 0x32930d8
v0, d0, t0 = reserves(FB - 1)
v1, d1, t1 = reserves(TB)

logs = call("eth_getLogs", [{"address": POOL, "fromBlock": hex(FB), "toBlock": hex(TB), "topics": [SWAP]}])["result"]

sum0in = sum1in = sum0out = sum1out = 0.0
for lg in logs:
    d = lg["data"][2:]
    a0i, a1i, a0o, a1o = (int(d[i:i + 64], 16) / 1e18 for i in (0, 64, 128, 192))
    sum0in += a0i
    sum1in += a1i
    sum0out += a0o
    sum1out += a1o

print(f"window blocks {FB}..{TB} ({TB-FB+1} blocks)")
print(f"reserves @{(FB-1)}: VIRTUAL {v0:,.2f}  DEUS {d0:,.2f}  ts {t0}")
print(f"reserves @{TB}: VIRTUAL {v1:,.2f}  DEUS {d1:,.2f}  ts {t1}")
print(f"delta: VIRTUAL {v1-v0:+,.2f}  DEUS {d1-d0:+,.2f}")
print(f"swaps: n={len(logs)}")
print(f"  sum amount0In (VIRTUAL in)  {sum0in:,.2f}")
print(f"  sum amount1In (DEUS in)     {sum1in:,.2f}")
print(f"  sum amount0Out (VIRTUAL out) {sum0out:,.2f}")
print(f"  sum amount1Out (DEUS out)    {sum1out:,.2f}")
print(f"  expected dVIRTUAL {sum0in-sum0out:+,.2f}  expected dDEUS {sum1in-sum1out:+,.2f}")
print(f"  reconcile dVIRTUAL {v1-v0-(sum0in-sum0out):+.4f}  dDEUS {d1-d0-(sum1in-sum1out):+.4f}")
print(f"ratio start {v0/d0:.6f}  end {v1/d1:.6f}  pct {(v1/d1)/(v0/d0)*100-100:+.4f}%")

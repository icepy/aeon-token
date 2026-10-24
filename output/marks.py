import json, urllib.request

URL = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
H1 = 53037782
H24 = 52996382
HEAD = 53039582


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def reserves(block):
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": POOL, "data": "0x0902f1ac"}, hex(block)],
        }
    )
    if "error" in r:
        print("ERROR", r["error"])
        return None
    d = r["result"][2:]
    r0 = int(d[0:64], 16)
    r1 = int(d[64:128], 16)
    return r0 / 1e18, r1 / 1e18


def vslot0(block):
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [
                {"to": "0x529d2863a1521d0b57db028168fdE2E97120017C", "data": "0x3850c7bd"},
                hex(block),
            ],
        }
    )
    if "error" in r:
        print("ERROR slot0", r["error"])
        return None
    sq = int(r["result"][2:66], 16)
    return (sq / 2**96) ** 2 * 10 ** (18 - 6)


def mark(block):
    res = reserves(block)
    vp = vslot0(block)
    if res is None or vp is None:
        return None
    v, d = res
    return {"blk": block, "virtual": v, "deus": d, "ratio": v / d, "vusd": vp, "mark": v / d * vp}


for b in (H24, H1, HEAD):
    print(mark(b))

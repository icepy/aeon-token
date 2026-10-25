import json, time, urllib.request, math

RPC = "https://base.gateway.tenderly.co"
VPOOL = "0x529d2863a1521d0b57db028168fdE2E97120017C"   # VIRTUAL/USDC V3

def rpc(method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                j = json.loads(r.read())
            if "error" in j:
                raise RuntimeError(str(j["error"])[:200])
            return j["result"]
        except Exception as e:
            last = e; time.sleep(delay); delay *= 2
    raise RuntimeError("rpc fail %s: %s" % (method, last))

def call(to, data, blk="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk) if isinstance(blk, int) else blk])

def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [h[i:i+64] for i in range(0, len(h), 64)]

def slot0(blk):
    w = words(call(VPOOL, "0x3850c7bd", blk))   # slot0()
    return int(w[0], 16)

def dec(addr):
    return int(words(call(addr, "0x313ce567"))[0], 16)

out = {}
head = int(rpc("eth_blockNumber", []), 16)
b1h, b24h = 53057586, 53016186

t0 = "0x" + words(call(VPOOL, "0x0dfe1681"))[0][-40:]
t1 = "0x" + words(call(VPOOL, "0xd21220a7"))[0][-40:]
d0 = dec(t0); d1 = dec(t1)
out["token0"] = t0; out["token1"] = t1
out["dec0"] = d0; out["dec1"] = d1

def price_usd_per_virtual(sq, blk_label):
    # price of token1 in token0 terms = (sq/2^96)^2 * 10^dec0 / 10^dec1
    p = (sq / (1 << 96)) ** 2
    raw = p * (10 ** d0) / (10 ** d1)
    # raw = token1 per token0 units adjusted; identify which is VIRTUAL
    return raw

rows = {}
for label, blk in [("head", head), ("1h", b1h), ("24h", b24h)]:
    sq = slot0(blk)
    rows[label] = {"block": blk, "sqrtPriceX96": str(sq)}
out["slot0"] = rows

# resolve orientation using known: VIRTUAL ~ $0.62, USDC = $1
sq = slot0(head)
p = (sq / (1 << 96)) ** 2 * (10 ** d0) / (10 ** d1)
out["raw_price_token1_per_token0"] = p
out["inverse"] = 1 / p if p else None
print(json.dumps(out, indent=1))

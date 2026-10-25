import json, time, urllib.request
from decimal import Decimal, getcontext
getcontext().prec = 40

RPC = "https://base.gateway.tenderly.co"
V3SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
POOL = "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b"

def rpc(method, params, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.2
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                j = json.loads(r.read())
            if "error" in j:
                e = j["error"]; raise RuntimeError("%s %s" % (e.get("code"), e.get("message")))
            return j["result"]
        except Exception as ex:
            last = ex; time.sleep(delay); delay *= 2
    raise RuntimeError("rpc %s: %s" % (method, last))

def call(to, data, blk="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, blk if isinstance(blk, str) else hex(blk)])

def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [h[i:i+64] for i in range(0, len(h), 64)]

def s128(x):
    v = int(x, 16)
    return v - (1 << 256) if v >= (1 << 255) else v

lo, hi = 53057586, 53059548
logs, fails = [], []
_s = lo
while _s <= hi:
    _e = min(_s + 999, hi)
    ok = False
    for _a in range(3):
        try:
            logs.extend(rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(_s), "toBlock": hex(_e), "topics": [V3SWAP]}]))
            ok = True; break
        except Exception:
            time.sleep(1 + _a)
    if not ok:
        fails.append("%d-%d" % (_s, _e))
    _s = _e + 1
print("failed_chunks:", fails)
rows = []
for l in logs:
    d = l["data"][2:]
    w = [d[i:i+64] for i in range(0, len(d), 64)]
    a0, a1 = s128(w[0]), s128(w[1])
    blk = int(l["blockNumber"], 16)
    ts = int(rpc("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16)
    # token0=USDC 6dp, token1=DEUS 18dp
    usdc = Decimal(a0) / Decimal(10**6)
    deus = Decimal(a1) / Decimal(10**18)
    rows.append({
        "ts": ts, "blk": blk, "tx": l["transactionHash"][:18],
        "usdc_delta": float(usdc), "deus_delta": float(deus),
        "side": "BUY DEUS" if deus > 0 else "SELL DEUS",
        "implied_usd": float(-usdc / deus) if deus else None,
    })
print(json.dumps(rows, indent=1))
t0 = "0x" + words(call(POOL, "0x0dfe1681"))[0][-40:]
t1 = "0x" + words(call(POOL, "0xd21220a7"))[0][-40:]
print("token0", t0, "token1", t1)

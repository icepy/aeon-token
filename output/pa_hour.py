import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
V3SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
VENUES = {
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": 6,
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": 6,
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": 6,
}
DEEPEST = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SOLIDLY = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

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

def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [h[i:i+64] for i in range(0, len(h), 64)]

def call(to, data, blk="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, blk if isinstance(blk, str) else hex(blk)])

def supply(token, blk="latest"):
    return int(words(call(token, "0x18160ddd", blk))[0], 16) / 1e18

def bal(token, holder, blk="latest"):
    return int(words(call(token, "0x70a08231" + "0"*24 + holder[2:].lower(), blk))[0], 16) / 1e18

def scan(addr, topic, lo, hi):
    out, fails = [], []
    s = lo
    while s <= hi:
        e = min(s + 999, hi)
        ok = False
        for a in range(3):
            try:
                out.extend(rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(s), "toBlock": hex(e), "topics": [topic]}]))
                ok = True; break
            except Exception:
                time.sleep(1 + a)
        if not ok:
            fails.append("%d-%d" % (s, e))
        s = e + 1
    return out, fails

head = int(rpc("eth_blockNumber", []), 16)
b1h, b24h = 53057586, 53016186
res = {"head": head}

res["supply_now"] = supply(DEUS)
res["supply_1h"] = supply(DEUS, b1h)
res["supply_24h"] = supply(DEUS, b24h)
res["supply_1h_delta"] = res["supply_now"] - res["supply_1h"]
res["supply_24h_delta"] = res["supply_now"] - res["supply_24h"]

res["claim_now"] = bal(DEUS, CLAIM)
res["claim_1h"] = bal(DEUS, CLAIM, b1h)
res["claim_1h_delta"] = res["claim_now"] - res["claim_1h"]

v = {}
for addr in VENUES:
    logs, fails = scan(addr, V3SWAP, b1h, head)
    v[addr] = {"swaps": len(logs), "failed_chunks": fails}
res["usdc_venues_1h"] = v

d, dfails = scan(DEEPEST, SOLIDLY, b1h, head)
res["deepest_swaps_1h"] = len(d)
res["deepest_scan_failures"] = dfails

print(json.dumps(res, indent=1))

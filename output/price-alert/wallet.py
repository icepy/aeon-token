import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
W = "0x1184de98c71b565a7bc8313d89d74322c3df7f3b"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SOLIDLY_SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
SOLIDLY_SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"


def rpc(m, p):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%H:%M:%SZ")


b = int(rpc("eth_blockNumber", [])["result"], 16)


def bal(addr, blk):
    d = "0x70a08231" + addr[2:].rjust(64, "0")
    r = rpc("eth_call", [{"to": DEUS, "data": d}, hex(blk)])
    return int(r["result"], 16) / 1e18 if r.get("result") and r["result"] != "0x" else None


print("== 0x1184de98 DEUS balance trail ==")
for back, label in [(0, "now"), (600, "-20m"), (1800, "-1h"), (5400, "-3h"), (21600, "-12h"), (64800, "-36h")]:
    blk = b - back
    ts = int(rpc("eth_getBlockByNumber", [hex(blk), False])["result"]["timestamp"], 16)
    print("  %-6s blk %d %s  %.6f" % (label, blk, utc(ts), bal(W, blk) or 0))

print("\n== DEUS Transfer events touching 0x1184de98 (last 3 days) ==")
lo = b - 129600
logs = []
s = lo
while s <= b:
    e = min(s + 999, b)
    r = rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(s), "toBlock": hex(e),
                             "topics": [TRANSFER]}])
    if "error" in r:
        print("err", r["error"])
        break
    logs.extend(r["result"])
    s = e + 1
pad = W[2:].rjust(64, "0")
touch = [l for l in logs if l["topics"][1][-64:] == pad or (len(l["topics"]) > 2 and l["topics"][2][-64:] == pad)]
print("transfer_logs_total", len(logs), "touching_wallet", len(touch))
for l in sorted(touch, key=lambda x: int(x["blockNumber"], 16))[-12:]:
    frm = "0x" + l["topics"][1][-40:]
    to = "0x" + l["topics"][2][-40:]
    amt = int(l["data"][2:66], 16) / 1e18 if len(l["data"]) >= 66 else 0
    ts = int(rpc("eth_getBlockByNumber", [l["blockNumber"], False])["result"]["timestamp"], 16)
    dirn = "IN " if to == W else "OUT"
    print("  %s blk %s %s %.3f  frm %s to %s" % (
        utc(ts), l["blockNumber"], dirn, amt, frm[:12], to[:12]))

print("\n== Sync reconciliation over the last hour ==")
r = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(b - 1800), "toBlock": hex(b),
                         "topics": [SOLIDLY_SYNC]}])
print("sync", len(r.get("result", [])), r.get("error"))

import json, urllib.request, time, datetime
from collections import defaultdict

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"


def rpc(m, p, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    for i in range(tries):
        req = urllib.request.Request(RPC, data=body, headers={
            "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
        try:
            return json.load(urllib.request.urlopen(req, timeout=45))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (i + 1))
                continue
            raise
    return {"error": "429"}


def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%H:%M:%SZ")


b = int(rpc("eth_blockNumber", [])["result"], 16)
logs, s = [], b - 1800
while s <= b:
    e = min(s + 900, b)
    r = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(s), "toBlock": hex(e), "topics": [SWAP]}])
    logs.extend(r.get("result", []))
    s = e + 1
    time.sleep(1.2)

cache = {}
by_eoa = defaultdict(lambda: {"buys": 0.0, "sells": 0.0, "n": 0})
print("%-9s %-42s %10s %10s  %s" % ("time", "tx_from (EOA)", "DEUS_out", "DEUS_in", "router"))
for lg in sorted(logs, key=lambda l: int(l["blockNumber"], 16)):
    d = lg["data"][2:]
    w = [d[i:i + 64] for i in range(0, len(d), 64)]
    a1in, a1out = int(w[1], 16) / 1e18, int(w[3], 16) / 1e18
    txh = lg["transactionHash"]
    if txh not in cache:
        tx = rpc("eth_getTransactionByHash", [txh])["result"]
        blk = lg["blockNumber"]
        ts = int(rpc("eth_getBlockByNumber", [blk, False])["result"]["timestamp"], 16)
        cache[txh] = (tx["from"], tx["to"], ts)
        time.sleep(0.8)
    frm, to, ts = cache[txh]
    print("%-9s %-42s %10.2f %10.2f  %s" % (utc(ts), frm, a1out, a1in, (to or "")[:12]))
    by_eoa[frm]["buys"] += a1out
    by_eoa[frm]["sells"] += a1in
    by_eoa[frm]["n"] += 1

print("\n== per EOA ==")
for e, v in sorted(by_eoa.items(), key=lambda kv: -(kv[1]["buys"] + kv[1]["sells"])):
    net = v["buys"] - v["sells"]
    print("%s  n=%d  bought %.2f  sold %.2f  net %+.2f" % (e, v["n"], v["buys"], v["sells"], net))

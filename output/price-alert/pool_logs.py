import json, urllib.request, datetime, time

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
_id = [1700]

def rpc(method, params):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params}).encode()
    for attempt in range(6):
        req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                j = json.loads(r.read())
            if "error" in j:
                raise RuntimeError(j["error"])
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 5:
                time.sleep(2 + 3 * attempt)
                continue
            raise

def ts(n):
    return int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)

# widen: last 4h of any pool log
head = int(rpc("eth_blockNumber", []), 16)
start = head - 7200
allogs = []
b = start
while b <= head:
    e = min(b + 999, head)
    allogs.extend(rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(b), "toBlock": hex(e)}]))
    b = e + 1

names = {
 "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822": "Swap",
 "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f": "Mint",
 "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496": "Burn",
 "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1": "Sync",
}
rows = []
for lg in allogs:
    rows.append({"blk": int(lg["blockNumber"], 16),
                 "iso": datetime.datetime.fromtimestamp(ts(int(lg["blockNumber"], 16)), datetime.UTC).strftime("%H:%M:%SZ"),
                 "ev": names.get(lg["topics"][0], lg["topics"][0][:10]), "tx": lg["transactionHash"], "logidx": lg["logIndex"]})
rows.sort(key=lambda r: (r["blk"], int(r["logidx"], 16)))
print(json.dumps({"range": [start, head], "n": len(rows), "events": rows[-20:],
                  "counts": {k: sum(1 for r in rows if r["ev"] == k) for k in names.values()}}, indent=1))

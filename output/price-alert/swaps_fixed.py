import json, urllib.request, datetime, time

RPC = "https://base.gateway.tenderly.co"
POOLS = {
 "deep_0x3E97c5EC": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
 "usdc_0x58dBa34e": "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b",
 "usdc_0x1B2f3f5C": "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642",
 "usdc_0x75bc1495": "0x75bc14950Ab093cBd1f80BbbDf458596939180A3",
}
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
BAD  = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75c"
_id = [4000]

def rpc(method, params):
    _id[0] += 1
    body = json.dumps({"jsonrpc":"2.0","id":_id[0],"method":method,"params":params}).encode()
    for a in range(6):
        req = urllib.request.Request(RPC, data=body, headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                j = json.loads(r.read())
            if "error" in j: raise RuntimeError(j["error"])
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a < 5:
                time.sleep(2+3*a); continue
            raise

head = int(rpc("eth_blockNumber", []), 16)
HTS = int(rpc("eth_getBlockByNumber",[hex(head),False])["timestamp"],16)
start = head - 2600   # ~87 min

tsc = {}
def bts(n):
    if n not in tsc:
        tsc[n] = int(rpc("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)
    return tsc[n]

out = {"head": head, "head_iso": datetime.datetime.fromtimestamp(HTS, datetime.UTC).strftime("%FT%TZ"), "pools": {}}
for name, addr in POOLS.items():
    logs = []
    b = start
    while b <= head:
        e = min(b+999, head)
        logs.extend(rpc("eth_getLogs",[{"address":addr,"fromBlock":hex(b),"toBlock":hex(e),"topics":[SWAP]}]))
        b = e+1
    rows = []
    for lg in logs:
        d = lg["data"][2:]
        a0in  = int(d[0:64],16);   a1in  = int(d[64:128],16)
        a0out = int(d[128:192],16); a1out = int(d[192:256],16)
        rows.append({"blk": int(lg["blockNumber"],16),
                     "iso": datetime.datetime.fromtimestamp(bts(int(lg["blockNumber"],16)), datetime.UTC).strftime("%H:%M:%SZ"),
                     "a0in": a0in, "a1in": a1in, "a0out": a0out, "a1out": a1out,
                     "sender": lg["topics"][1][-40:], "to": lg["topics"][2][-40:],
                     "tx": lg["transactionHash"]})
    out["pools"][name] = {"n": len(rows), "rows": rows, "watch_min": round((HTS-bts(int(rpc("eth_blockNumber",[]),16)) )/60,1)}

# discrimination control on deep pool over a range we know has ≥1 log
daddr = POOLS["deep_0x3E97c5EC"]
r_true  = rpc("eth_getLogs",[{"address":daddr,"fromBlock":hex(head-999),"toBlock":hex(head),"topics":[SWAP]}])
r_false = rpc("eth_getLogs",[{"address":daddr,"fromBlock":hex(head-999),"toBlock":hex(head),"topics":[BAD]}])
out["control"] = {"true_topic_hits": len(r_true), "corrupt_topic_hits": len(r_false)}

print(json.dumps(out, indent=1))

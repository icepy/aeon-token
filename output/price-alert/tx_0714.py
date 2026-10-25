import json, urllib.request, datetime, time

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
TX = "0x7811d76d247cf8392c9fa1ba968b90a97aecca4edf6e30ac51754a7c6e43fec7"
_id = [3000]

def rpc(method, params):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params}).encode()
    for a in range(6):
        req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                j = json.loads(r.read())
            if "error" in j:
                raise RuntimeError(j["error"])
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a < 5:
                time.sleep(2+3*a); continue
            raise

rc = rpc("eth_getTransactionReceipt", [TX])
out = []
for lg in rc["logs"]:
    if lg["address"].lower() == POOL.lower():
        out.append({"topic0": lg["topics"][0], "topics_n": len(lg["topics"]),
                    "topics": lg["topics"], "data": lg["data"]})

tx = rpc("eth_getTransactionByHash", [TX])
blk = int(rc["blockNumber"], 16)
bt = rpc("eth_getBlockByNumber", [hex(blk), False])
print(json.dumps({
  "block": blk, "iso": datetime.datetime.fromtimestamp(int(bt["timestamp"],16), datetime.UTC).strftime("%FT%TZ"),
  "from": tx["from"], "to": tx["to"], "status": rc["status"],
  "pool_logs": out,
  "log_count_total": len(rc["logs"]),
}, indent=1))

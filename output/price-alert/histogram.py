import json, urllib.request
from collections import Counter

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def logs(lo, hi, addr):
    out = rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(lo), "toBlock": hex(hi)}])
    if "error" in out:
        raise RuntimeError(json.dumps(out["error"])[:300])
    return out["result"]


b = int(rpc("eth_blockNumber", [])["result"], 16)
all_logs = []
start = b - 1800
while start <= b:
    end = min(start + 999, b)
    all_logs.extend(logs(start, end, POOL))
    start = end + 1
print("total_logs_by_address", len(all_logs))
c = Counter(l["topics"][0] if l["topics"] else "0x" for l in all_logs)
for t, n in c.most_common(10):
    print(" ", t, n)

# blocks spanned by those logs
if all_logs:
    bl = sorted(int(l["blockNumber"], 16) for l in all_logs)
    print("first_blk", bl[0], "last_blk", bl[-1])

# also check eth_getCode to confirm it is a contract and not proxy w/ different address
r = rpc("eth_getCode", [POOL, hex(b)])
code = r.get("result", "")
print("code_len", len(code))

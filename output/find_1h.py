import json, subprocess, datetime

RPC = "https://base.gateway.tenderly.co"

def call_one(method, params, idx=1):
    payload = json.dumps({"jsonrpc": "2.0", "id": idx, "method": method, "params": params})
    out = subprocess.run(["curl", "-s", "--max-time", "20", "-X", "POST", RPC,
                          "-H", "Content-Type: application/json", "-d", payload],
                         capture_output=True, text=True).stdout
    j = json.loads(out)
    if "error" in j:
        raise RuntimeError(j["error"])
    return j["result"]

head = 53043188
hb = call_one("eth_getBlockByNumber", [hex(head), False])
hts = int(hb["timestamp"], 16)
target = hts - 3600
print("head", head, hts, "target", target)

# binary search for the highest block with timestamp <= target
lo, hi = head - 2400, head
while lo < hi:
    mid = (lo + hi + 1) // 2
    b = call_one("eth_getBlockByNumber", [hex(mid), False])
    if int(b["timestamp"], 16) <= target:
        lo = mid
    else:
        hi = mid - 1
prev = lo
pb = call_one("eth_getBlockByNumber", [hex(prev), False])
pts = int(pb["timestamp"], 16)
print("prev block", prev, pts, "delta_s", hts - pts)
print("prev_hex", hex(prev))

res = call_one("eth_call", [{"to": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
                             "data": "0x0902f1ac"}, hex(prev)])
print("reserves_prev", res)

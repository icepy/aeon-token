import json, urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def bts(n):
    r = rpc("eth_getBlockByNumber", [hex(n), False])["result"]
    return int(r["timestamp"], 16), r["number"]

head = int(rpc("eth_blockNumber", [])["result"], 16)
head_ts, _ = bts(head)
target = head_ts - 3600
print("head", head, "head_ts", head_ts, "target_ts", target)

lo, hi = head - 40000, head
while lo < hi:
    mid = (lo + hi) // 2
    ts, _ = bts(mid)
    if ts < target:
        lo = mid + 1
    else:
        hi = mid
blk1h = lo
ts1h, _ = bts(blk1h)
print("block 1h ago", blk1h, "ts", ts1h, "delta_s", head_ts - ts1h, "blocks", head - blk1h,
      "avg_s_per_block", round((head_ts - ts1h) / (head - blk1h), 3))

def res(block):
    out = rpc("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(block)])["result"][2:]
    return int(out[0:64], 16) / 1e18, int(out[64:128], 16) / 1e18, int(out[128:192], 16)

v_now, d_now, ts_now = res(head)
v_1h, d_1h, _ = res(blk1h)
r_now = v_now / d_now
r_1h = v_1h / d_1h
print(f"VIRTUAL {v_1h:.6f} -> {v_now:.6f}   DEUS {d_1h:.6f} -> {d_now:.6f}")
print(f"ratio VIRTUAL/DEUS {r_1h:.8f} -> {r_now:.8f}  = {(r_now/r_1h-1)*100:+.4f}% across the hour")
print(f"reserve ts match: {ts_now == head_ts}")
json.dump({"head": head, "head_ts": head_ts, "blk_1h": blk1h, "ts_1h": ts1h,
           "v_now": v_now, "d_now": d_now, "v_1h": v_1h, "d_1h": d_1h,
           "ratio_now": r_now, "ratio_1h": r_1h},
          open("/home/runner/work/aeon-token/aeon-token/output/price-alert/reserves.json", "w"), indent=1)

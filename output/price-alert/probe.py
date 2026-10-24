import json, urllib.request, sys

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def call(to, data, block):
    return rpc("eth_call", [{"to": to, "data": data}, block])["result"]

head = int(rpc("eth_blockNumber", [])["result"], 16)
print("head", head)

POOL_PY = POOL
for offset in (0, 1800):
    blk = hex(head - offset)
    res = call(POOL, "0x0902f1ac", blk)  # getReserves()
    raw = res[2:]
    r0 = int(raw[0:64], 16)
    r1 = int(raw[64:128], 16)
    ts = int(raw[128:192], 16)
    print(f"block {int(blk,16)} ts {ts} reserve0 {r0/1e18:.6f} reserve1 {r1/1e18:.6f} ratio {(r0/1e18)/(r1/1e18):.8f}")

# token0 / token1 orientation
print("token0", call(POOL, "0x0dfe1681", hex(head)))
print("token1", call(POOL, "0xd21220a7", hex(head)))

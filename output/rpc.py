import json, sys, urllib.request

RPC = "https://base.gateway.tenderly.co"

def call(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.loads(r.read())
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "head":
        print(int(call("eth_blockNumber", []), 16))
    elif cmd == "headts":
        blk = int(call("eth_blockNumber", []), 16)
        b = call("eth_getBlockByNumber", [hex(blk), False])
        print(blk, int(b["timestamp"], 16))
    elif cmd == "reserves":
        pool = sys.argv[2]
        blk = sys.argv[3] if len(sys.argv) > 3 else "latest"
        blk = hex(int(blk)) if blk != "latest" else blk
        r = call("eth_call", [{"to": pool, "data": "0x0902f1ac"}, blk])
        w = r[2:]
        print(json.dumps({
            "reserve0": int(w[0:64], 16),
            "reserve1": int(w[64:128], 16),
            "blockTimestampLast": int(w[128:192], 16),
            "raw": r,
        }))
    elif cmd == "call":
        to = sys.argv[2]
        data = sys.argv[3]
        blk = sys.argv[4] if len(sys.argv) > 4 else "latest"
        blk = hex(int(blk)) if blk != "latest" else blk
        print(call("eth_call", [{"to": to, "data": data}, blk]))
    elif cmd == "blockts":
        b = call("eth_getBlockByNumber", [hex(int(sys.argv[2])), False])
        print(int(b["timestamp"], 16))

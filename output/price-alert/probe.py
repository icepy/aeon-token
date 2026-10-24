import json, urllib.request, sys

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def call(data, blk):
    r = rpc("eth_call", [{"to": POOL, "data": data}, blk])
    return r.get("result"), (r.get("error") or {}).get("message")


def main():
    b = int(rpc("eth_blockNumber", [])["result"], 16)
    print("latest_block", b)

    for sel, name in [("0x0dfe1681", "token0"), ("0xd21220a7", "token1"),
                      ("0x0902f1ac", "getReserves")]:
        res, err = call(sel, hex(b))
        print(name, res, err or "")

    # reserves one hour back (~1800 blocks at 2s)
    for back in (1500, 1800, 2100):
        res, err = call("0x0902f1ac", hex(b - back))
        print("reserves_minus_%d_blocks" % back, res, err or "")

    # block timestamp to confirm block time
    blk = rpc("eth_getBlockByNumber", [hex(b), False])["result"]
    print("block_timestamp", int(blk["timestamp"], 16))


main()

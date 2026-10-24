import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SENDERS = [
    "0xcf77a3ba9a5ca399b7c97c74d54e5b1beb874e43",
    "0xae629bf1cf17cbdd1b8e9a462519f678d8b40b3f",
    "0x8f10b468b06c6fd214b65f87778827f7d113f996",
    "0xafe3bec07253acef080cf7e01aa13a15f38004b0",
    "0x59c7c832e96d2568bea6db468c1aadcbbda08a52",
]


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


for a in SENDERS:
    code = rpc("eth_getCode", [a, "latest"]).get("result", "")
    nonce = int(rpc("eth_getTransactionCount", [a, "latest"]).get("result", "0x0"), 16)
    kind = "EOA" if code in ("0x", "") else ("EIP-7702" if code.startswith("0xef0100") else "CONTRACT")
    print("%s  %-9s codelen=%d nonce=%d" % (a, kind, len(code), nonce))

# Sync events to reconcile reserves across the hour
SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
b = int(rpc("eth_blockNumber", [])["result"], 16)
out = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(b - 1800), "toBlock": hex(b),
                           "topics": [SYNC]}])["result"]
print("\nsync_events", len(out))
last = out[-1]
d = last["data"][2:]
r0 = int(d[0:64], 16) / 1e18
r1 = int(d[64:128], 16) / 1e18
print("last_sync blk", int(last["blockNumber"], 16), "VIRTUAL %.4f DEUS %.4f ratio %.8f" % (r0, r1, r0 / r1))
for lg in out[-3:]:
    ts = int(rpc("eth_getBlockByNumber", [lg["blockNumber"], False])["result"]["timestamp"], 16)
    d = lg["data"][2:]
    a = int(d[0:64], 16) / 1e18
    bb = int(d[64:128], 16) / 1e18
    print(" ", datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%H:%M:%SZ"),
          "blk", int(lg["blockNumber"], 16), "VIRTUAL %.4f DEUS %.4f ratio %.8f" % (a, bb, a / bb))

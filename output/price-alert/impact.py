import json, urllib.request, time, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
DUMP_BLK = 53023409


def rpc(m, p, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    for i in range(tries):
        req = urllib.request.Request(RPC, data=body, headers={
            "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
        try:
            return json.load(urllib.request.urlopen(req, timeout=45))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (i + 1))
                continue
            raise
    return {}


def ratio(blk):
    r = rpc("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(blk)])
    d = r.get("result", "0x")[2:]
    if len(d) < 128:
        return None
    return int(d[0:64], 16) / int(d[64:128], 16)


for delta in (-3, -1, 0, 1, 2, 4, 10, 20):
    blk = DUMP_BLK + delta
    v = ratio(blk)
    ts = int(rpc("eth_getBlockByNumber", [hex(blk), False])["result"]["timestamp"], 16)
    print("blk %d %s ratio %.8f" % (blk, datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%H:%M:%SZ"), v))
    time.sleep(1)

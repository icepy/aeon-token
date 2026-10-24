import json, urllib.request, time, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SYNC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"


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
    raise RuntimeError("rate limited")


def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%H:%M:%SZ")


b = int(rpc("eth_blockNumber", [])["result"], 16)
lo = b - 1800
logs, s = [], lo
while s <= b:
    e = min(s + 900, b)
    r = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(s), "toBlock": hex(e), "topics": [SYNC]}])
    if "error" in r:
        print("err", r["error"])
        break
    logs.extend(r["result"])
    s = e + 1
    time.sleep(1.5)

logs.sort(key=lambda l: int(l["blockNumber"], 16))
print("sync_events", len(logs))
for tag, lg in [("first", logs[0]), ("last", logs[-1])]:
    d = lg["data"][2:]
    r0 = int(d[0:64], 16) / 1e18
    r1 = int(d[64:128], 16) / 1e18
    ts = int(rpc("eth_getBlockByNumber", [lg["blockNumber"], False])["result"]["timestamp"], 16)
    print("%s blk %d %s VIRTUAL %.4f DEUS %.4f ratio %.8f" % (
        tag, int(lg["blockNumber"], 16), utc(ts), r0, r1, r0 / r1))
    time.sleep(1)

d0 = logs[0]["data"][2:]
d1 = logs[-1]["data"][2:]
d_deus = (int(d1[64:128], 16) - int(d0[64:128], 16)) / 1e18
d_virt = (int(d1[0:64], 16) - int(d0[0:64], 16)) / 1e18
print("reserve_delta over window: VIRTUAL %+.4f  DEUS %+.4f" % (d_virt, d_deus))

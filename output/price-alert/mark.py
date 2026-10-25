import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VIRT_POOL = "0x529d2863a1521d0b57db028168fdE2E97120017C"
_id = [100]

def rpc(method, params):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read())
    if "error" in j:
        raise RuntimeError(j["error"])
    return j["result"]

head = int(rpc("eth_blockNumber", []), 16)
hb = rpc("eth_getBlockByNumber", [hex(head), False])
HTS = int(hb["timestamp"], 16)

blocks = {"head": head, "h1": 53061181, "h24": 53019781}

def slot0_ts(n):
    return int(rpc("eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)

out = {}
for label, n in blocks.items():
    raw = rpc("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(n)])[2:]
    r0 = int(raw[0:64], 16) / 1e18   # VIRTUAL
    r1 = int(raw[64:128], 16) / 1e18 # DEUS
    btl = int(raw[128:192], 16)
    v = rpc("eth_call", [{"to": VIRT_POOL, "data": "0x3850c7bd"}, hex(n)])[2:]
    sp = int(v[0:64], 16)
    virt = (sp / 2**96) ** 2 * 1e12   # 18 dec VIRTUAL vs 6 dec USDC
    ratio = r0 / r1
    out[label] = {"block": n, "ts": slot0_ts(n), "virtual": r0, "deus": r1,
                  "block_ts_last": btl, "virt_usd": virt, "ratio": ratio,
                  "mark": ratio * virt}

h, o1, d1 = out["head"], out["h1"], out["h24"]
chg1 = (h["mark"] / o1["mark"] - 1) * 100
chg24 = (h["mark"] / d1["mark"] - 1) * 100
rchg1 = (h["ratio"] / o1["ratio"] - 1) * 100
rchg24 = (h["ratio"] / d1["ratio"] - 1) * 100
vchg1 = (h["virt_usd"] / o1["virt_usd"] - 1) * 100
vchg24 = (h["virt_usd"] / d1["virt_usd"] - 1) * 100

res = {"head_block": head, "head_ts": HTS, "head_iso": datetime.datetime.utcfromtimestamp(HTS).isoformat() + "Z",
       "mark": h["mark"], "ratio": h["ratio"], "virt_usd": h["virt_usd"],
       "h1_pct": chg1, "h24_pct": chg24,
       "legs_1h": {"ratio": rchg1, "virtual": vchg1},
       "legs_24h": {"ratio": rchg24, "virtual": vchg24},
       "silence_min": (HTS - h["block_ts_last"]) / 60,
       "last_trade_iso": datetime.datetime.utcfromtimestamp(h["block_ts_last"]).isoformat() + "Z",
       "reserves": {k: {"virtual": v["virtual"], "deus": v["deus"], "ts_delta": HTS - v["ts"]} for k, v in out.items()},
       "ts_assert": {"h1": HTS - o1["ts"], "h24": HTS - d1["ts"]}}
print(json.dumps(res, indent=1))

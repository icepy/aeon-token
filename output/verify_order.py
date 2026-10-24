import json, urllib.request

URL = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def reserves(block):
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": POOL, "data": "0x0902f1ac"}, hex(block)],
        }
    )
    if "error" in r:
        raise SystemExit("ERR " + str(r["error"]))
    d = r["result"][2:]
    return int(d[0:64], 16) / 1e18, int(d[64:128], 16) / 1e18


# swap at block 53038045 declared words: [0.0, 5500.0, 152.04820900488835, 0.0]
before = reserves(53038044)
after = reserves(53038046)
print("before VIRTUAL/DEUS", before)
print("after  VIRTUAL/DEUS", after)
print("dV =", after[0] - before[0])
print("dD =", after[1] - before[1])
print()
print("If ordering is (In,In,Out,Out): VIRTUAL in 0, DEUS in 5500, VIRTUAL out 152 -> expect dD +5500, dV -152")
print("If ordering is (Out,Out,In,In): VIRTUAL out 0, DEUS out 5500, VIRTUAL in 152 -> expect dD -5500, dV +152")

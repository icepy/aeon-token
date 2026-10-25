import json, sys, time
sys.path.insert(0, "output")
from rpc import call

SOLIDLY = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"

POOLS = {
    "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa": ("deepest", SOLIDLY),
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": ("usdc58", V3),
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": ("usdc1B", V3),
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": ("usdc75", V3),
}

def getlogs(addr, topic0, lo, hi, attempts=4):
    for i in range(attempts):
        try:
            return call("eth_getLogs", [{"address": addr, "topics": [topic0],
                                          "fromBlock": hex(lo), "toBlock": hex(hi)}])
        except Exception as e:
            time.sleep(1 + 2 ** i)
    return None

lo, hi = int(sys.argv[1]), int(sys.argv[2])
out = {}
for addr, (name, topic) in POOLS.items():
    logs, chunk_ok = [], True
    for a in range(lo, hi + 1, 999):
        b = min(a + 998, hi)
        r = getlogs(addr, topic, a, b)
        if r is None:
            chunk_ok = False
            chunk_ok = False
        else:
            logs.extend(r)
    out[name] = {"count": len(logs), "complete": chunk_ok,
                 "blocks": [int(l["blockNumber"], 16) for l in logs]}
print(json.dumps(out, indent=1))

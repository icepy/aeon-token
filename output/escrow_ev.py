import json, sys, time
sys.path.insert(0, "output")
from rpc import call

ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
STAKE = "0x7162984403f6c73c8639375d45a9187dfd04602231bd8e587c415718b5f7e5f9"

def getlogs(addr, topic0, lo, hi):
    for i in range(4):
        try:
            return call("eth_getLogs", [{"address": addr, "topics": [topic0],
                                          "fromBlock": hex(lo), "toBlock": hex(hi)}])
        except Exception:
            time.sleep(1 + 2 ** i)
    return None

lo, hi = int(sys.argv[1]), int(sys.argv[2])
res = {}
for name, topic in (("burns", BURN), ("stakes", STAKE)):
    logs, ok = [], True
    for a in range(lo, hi + 1, 999):
        b = min(a + 998, hi)
        r = getlogs(ESCROW, topic, a, b)
        if r is None:
            ok = False
        else:
            logs.extend(r)
    res[name] = {"count": len(logs), "complete": ok,
                 "events": [{"blk": int(l["blockNumber"], 16),
                             "tx": l["transactionHash"]} for l in logs]}
print(json.dumps(res, indent=1))

import json, sys, time
sys.path.insert(0, "output")
from rpc import call

USDC58 = "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b"
V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
SINK9232 = "0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f"

def getlogs(addr, topics, lo, hi):
    for i in range(4):
        try:
            return call("eth_getLogs", [{"address": addr, "topics": topics,
                                          "fromBlock": hex(lo), "toBlock": hex(hi)}])
        except Exception:
            time.sleep(1 + 2 ** i)
    return None

# token0/token1 of usdc58
t0 = call("eth_call", [{"to": USDC58, "data": "0x0dfe1681"}, "latest"])
t1 = call("eth_call", [{"to": USDC58, "data": "0xd21220a7"}, "latest"])
print("token0", t0, "token1", t1)

logs = getlogs(USDC58, [V3], 53059413, 53061213) or []
rows = []
for l in logs:
    d = l["data"][2:]
    a0 = int(d[0:64], 16); a1 = int(d[64:128], 16)
    # signed
    if a0 >= 2**255: a0 -= 2**256
    if a1 >= 2**255: a1 -= 2**256
    rows.append({"blk": int(l["blockNumber"], 16), "tx": l["transactionHash"],
                 "amount0": a0, "amount1": a1})
print("swaps", json.dumps(rows, indent=1))

# escrow at 24h block
def bal(token, who, blk):
    r = call("eth_call", [{"to": token,
                           "data": "0x70a08231" + "0" * 24 + who[2:].lower()}, hex(blk)])
    return int(r, 16) / 1e18

print(json.dumps({
    "escrow_24h_ago": bal(DEUS, ESCROW, 53018013),
    "escrow_now": bal(DEUS, ESCROW, 53061213),
    "sink9232_deus_now": bal(DEUS, SINK9232, 53061213),
}, indent=1))

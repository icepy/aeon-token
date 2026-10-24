import json, subprocess, time
RPC = "https://base.gateway.tenderly.co"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
CLAIM = "0x5cbF5DFAa5336ce0456e24217e7911365100879a"
HOLDER = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"
BURN_TOPIC = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
HEAD = 53043188

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p}
                          for i, (m, p) in enumerate(calls)])
    last = ""
    for a in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        last = out
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * 2 ** a); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(1.5 * 2 ** a); continue
        return j
    raise RuntimeError(last[:300])

def bal(token, who, blk=hex(HEAD)):
    data = "0x70a08231" + "0" * 24 + who[2:].lower()
    return int(rpc([("eth_call", [{"to": token, "data": data}, blk])])[0]["result"], 16)

def total_supply(token, blk=hex(HEAD)):
    return int(rpc([("eth_call", [{"to": token, "data": "0x18160ddd"}, blk])])[0]["result"], 16)

print("DEUS total supply   :", total_supply(DEUS) / 1e18)
print("escrow DEUS         :", bal(DEUS, ESCROW) / 1e18)
print("CLAIM main vault    :", bal(DEUS, CLAIM) / 1e18)
print("xDEUS totalSupply   :", total_supply(XDEUS))
print("0xbb0f7533 DEUS     :", bal(DEUS, HOLDER) / 1e18)
# xDEUS balance (ERC721 -> balanceOf is same selector)
print("0xbb0f7533 xDEUS NFTs:", bal(XDEUS, HOLDER))

# escrow burns in last hour
logs = []
start = 53041388
while start <= HEAD:
    end = min(start + 999, HEAD)
    j = rpc([("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(start), "toBlock": hex(end),
                               "topics": [BURN_TOPIC]}])])[0]
    logs += j.get("result", [])
    start = end + 1
    time.sleep(0.5)
print("\nescrow Burn events last 1h:", len(logs))
for l in logs:
    d = l["data"][2:]
    amt = int(d[0:64], 16) / 1e18
    print("   tokenId", int(l["topics"][2], 16), "amount", amt, "owner", "0x" + l["topics"][1][-40:])

# 24h escrow delta
def block_at(secs):
    hts = int(rpc([("eth_getBlockByNumber", [hex(HEAD), False])])[0]["result"]["timestamp"], 16)
    tgt = hts - secs
    lo, hi = HEAD - 70000, HEAD
    while lo < hi:
        mid = (lo + hi + 1) // 2
        b = rpc([("eth_getBlockByNumber", [hex(mid), False])])[0]["result"]
        if int(b["timestamp"], 16) <= tgt: lo = mid
        else: hi = mid - 1
    return lo

b24 = block_at(86400)
e24 = bal(DEUS, ESCROW, hex(b24)) / 1e18
enow = bal(DEUS, ESCROW) / 1e18
print("\nescrow 24h: %.2f -> %.2f  delta %.2f (%.3f%%)  [blk %d]" %
      (e24, enow, enow - e24, (enow/e24 - 1) * 100, b24))
print("5%%/day line: %.2f  ratio %.3f" % (e24 * 0.05, abs(enow - e24) / (e24 * 0.05)))

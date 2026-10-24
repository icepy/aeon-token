import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ACTORS = [
    "0x111116058b9828cdcdd810c502b925c14f34ca11",
    "0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f",
    "0x205db642e4a907d65340f3f44ed47c8421988850",
]


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


head = int(call("eth_blockNumber", []), 16)

for a in ACTORS:
    code = call("eth_getCode", [a, "latest"])
    n = (len(code) - 2) // 2
    kind = "EOA" if n == 0 else ("EIP-7702" if n == 23 else f"contract({n}B prefix {code[2:10]})")
    eth = int(call("eth_getBalance", [a, "latest"]), 16) / 1e18
    nonce = int(call("eth_getTransactionCount", [a, "latest"]), 16)
    bal = int(call("eth_call", [{"to": DEUS, "data": "0x70a08231" + a[2:].lower().rjust(64, "0")}, "latest"]), 16) / 1e18
    print(f"{a}\n  {kind} nonce={nonce} ETH={eth:.6f} DEUS={bal:,.6f}")

print("\n-- DEUS flows touching 0x92325e5a (last 60,000 blocks) --")
b = head - 60000
inb, outb = [], []
while b < head:
    e = min(b + 999, head)
    for direction, topic in (("in", None), ("out", "0x" + ACTORS[1][2:].lower().rjust(64, "0"))):
        try:
            topics = [TRANSFER, topic, "0x" + ACTORS[1][2:].lower().rjust(64, "0")] if direction == "in" \
                else [TRANSFER, "0x" + ACTORS[1][2:].lower().rjust(64, "0")]
            logs = call("eth_getLogs", [{"address": DEUS, "fromBlock": hex(b), "toBlock": hex(e), "topics": topics}])
        except Exception as ex:
            print(" err", b, ex)
            logs = []
        for lg in logs:
            frm = "0x" + lg["topics"][1][-40:]
            to = "0x" + lg["topics"][2][-40:]
            val = int(lg["data"], 16) / 1e18
            (inb if direction == "in" else outb).append((int(lg["blockNumber"], 16), frm, to, val, lg["transactionHash"]))
    b = e + 1

print(f"inbound n={len(inb)} total={sum(x[3] for x in inb):,.2f}")
for x in inb[-12:]:
    print(f"  blk {x[0]} from {x[1]} {x[3]:,.4f}")
print(f"outbound n={len(outb)} total={sum(x[3] for x in outb):,.2f}")
for x in outb[-12:]:
    print(f"  blk {x[0]} -> {x[2]} {x[3]:,.4f} {x[4][:12]}")

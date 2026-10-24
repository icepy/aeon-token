import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
TX = "0x428bbb417b6378e5f571c4e31763f3a2b3b2369f946c4c330d9743d9d2d53e94"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


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


tx = call("eth_getTransactionByHash", [TX])
rc = call("eth_getTransactionReceipt", [TX])
blk = int(tx["blockNumber"], 16)
print("tx.from", tx["from"])
print("tx.to  ", tx["to"])
print("block", blk, datetime.datetime.fromtimestamp(int(rc["blockNumber"] and call("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16), datetime.UTC).isoformat())

seller = tx["from"]
code = call("eth_getCode", [seller, "latest"])
n = (len(code) - 2) // 2
print("seller code bytes", n, "->", "EOA" if n == 0 else ("EIP-7702" if n == 23 else "contract"))
print("seller nonce", int(call("eth_getTransactionCount", [seller, "latest"]), 16))
print("seller ETH", int(call("eth_getBalance", [seller, "latest"]), 16) / 1e18)

bal = int(call("eth_call", [{"to": DEUS, "data": "0x70a08231" + seller[2:].lower().rjust(64, "0")}, "latest"]), 16) / 1e18
print("seller DEUS balance now", f"{bal:,.6f}")

# DEUS transfers in the tx
print("\n-- DEUS transfers in this tx --")
for lg in rc["logs"]:
    if lg["address"].lower() != DEUS.lower():
        continue
    if lg["topics"][0].lower() != TRANSFER:
        continue
    frm = "0x" + lg["topics"][1][-40:]
    to = "0x" + lg["topics"][2][-40:]
    val = int(lg["data"], 16) / 1e18
    print(f"  {frm} -> {to}  {val:,.6f} DEUS")

# where did its DEUS come from? scan last 40k blocks in 1000 chunks for Transfer to seller
print("\n-- inbound DEUS transfers to seller (last 40,000 blocks) --")
head = blk
hits = []
b = head - 40000
while b < head:
    e = min(b + 999, head)
    try:
        logs = call("eth_getLogs", [{
            "address": DEUS, "fromBlock": hex(b), "toBlock": hex(e),
            "topics": [TRANSFER, None, "0x" + seller[2:].lower().rjust(64, "0")],
        }])
    except Exception as ex:
        print("  err", b, ex)
        b = e + 1
        continue
    for lg in logs:
        hits.append(lg)
    b = e + 1

for lg in hits[-15:]:
    frm = "0x" + lg["topics"][1][-40:]
    val = int(lg["data"], 16) / 1e18
    bb = int(lg["blockNumber"], 16)
    print(f"  blk {bb} from {frm} {val:,.6f}  {'<== CLAIM VAULT' if frm.lower()==CLAIM.lower() else ''}")
print("total inbound count", len(hits))

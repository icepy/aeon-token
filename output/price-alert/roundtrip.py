import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
W = "0x1184de98c71b565a7bc8313d89d74322c3df7f3b"
CP = "0x0a2854fbbd"  # prefix; full addr resolved below
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def rpc(m, p):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


b = int(rpc("eth_blockNumber", [])["result"], 16)
pad = W[2:].rjust(64, "0")

# find the two transfers, get full counterparty
logs = []
s = b - 129600
while s <= b:
    e = min(s + 999, b)
    r = rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(s), "toBlock": hex(e),
                             "topics": [TRANSFER]}])
    logs.extend(r.get("result", []))
    s = e + 1

touch = [l for l in logs if l["topics"][1][-64:] == pad or (len(l["topics"]) > 2 and l["topics"][2][-64:] == pad)]
cp = None
for l in touch:
    frm = "0x" + l["topics"][1][-40:]
    to = "0x" + l["topics"][2][-40:]
    if frm != W:
        cp = frm
print("counterparty", cp)
code = rpc("eth_getCode", [cp, "latest"]).get("result", "")
print("counterparty code_len", len(code), "kind", "EOA" if code in ("0x", "") else "CONTRACT")

for l in sorted(touch, key=lambda x: int(x["blockNumber"], 16)):
    txh = l["transactionHash"]
    tx = rpc("eth_getTransactionByHash", [txh])["result"]
    rc = rpc("eth_getTransactionReceipt", [txh])["result"]
    ts = int(rpc("eth_getBlockByNumber", [l["blockNumber"], False])["result"]["timestamp"], 16)
    amt = int(l["data"][2:66], 16) / 1e18
    print("\n%s blk %s amt %.6f" % (utc(ts), int(l["blockNumber"], 16), amt))
    print("  tx", txh)
    print("  from", tx["from"], "-> to", tx["to"], "selector", tx["input"][:10])
    print("  status", rc["status"], "logs", len(rc["logs"]))
    # list ERC20 transfers in this tx
    for lg in rc["logs"]:
        if lg["topics"] and lg["topics"][0] == TRANSFER:
            sym = lg["address"]
            a = int(lg["data"][2:66], 16) / 1e18 if len(lg["data"]) >= 66 else 0
            print("     %s  %s -> %s  %.6f" % (sym[:12], ("0x" + lg["topics"][1][-40:])[:12],
                                               ("0x" + lg["topics"][2][-40:])[:12], a))

print("\n== wallet kind ==")
c = rpc("eth_getCode", [W, "latest"]).get("result", "")
print("0x1184de98 code_len", len(c), "kind", "EOA" if c in ("0x", "") else ("EIP-7702" if c.startswith("0xef0100") else "CONTRACT"))
print("nonce", int(rpc("eth_getTransactionCount", [W, "latest"]).get("result", "0x0"), 16))

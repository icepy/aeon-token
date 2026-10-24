import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
TOK = "0x6bd83abc39"  # resolve below


def rpc(m, p):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    return json.load(urllib.request.urlopen(req, timeout=45))


# recover full address of 0x6bd83abc39... from the receipt
TXH = "0xf1e8fefec12702cb55523ffc2c04930972523e429ac9342d37d51cc05c29541f"
rc = rpc("eth_getTransactionReceipt", [TXH])["result"]
addrs = sorted({l["address"] for l in rc["logs"]})
print("log-emitting contracts:")
for a in addrs:
    print(" ", a)


def name(addr):
    out = {}
    for sel, key in [("0x06fdde03", "name"), ("0x95d89b41", "symbol"), ("0x313ce567", "decimals")]:
        r = rpc("eth_call", [{"to": addr, "data": sel}, "latest"]).get("result", "0x")
        if r and r != "0x":
            if key == "decimals":
                out[key] = int(r, 16)
            else:
                raw = bytes.fromhex(r[2:])
                if len(raw) >= 64:
                    ln = int.from_bytes(raw[32:64], "big")
                    out[key] = raw[64:64 + ln].decode("utf-8", "replace")
    return out


for a in addrs:
    print(a, name(a))

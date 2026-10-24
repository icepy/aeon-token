import json, urllib.request

URL = "https://base.gateway.tenderly.co"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
H24, HEAD = 52996382, 53039582


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def call(to, data, block="latest"):
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": to, "data": data}, block if block == "latest" else hex(block)],
        }
    )
    if "error" in r:
        return None, r["error"]
    return r["result"], None


def bal(token, holder, block="latest", dec=18):
    data = "0x70a08231" + "0" * 24 + holder[2:].lower()
    v, e = call(token, data, block)
    if e:
        return None
    return int(v, 16) / 10**dec


def supply(token, block="latest"):
    v, e = call(token, "0x18160ddd", block)
    if e:
        return None
    return int(v, 16)


print("escrow DEUS now", bal(ESCROW, ESCROW))
print("escrow DEUS H24", bal(ESCROW, ESCROW, H24))
print("xDEUS supply now", supply(XDEUS))
print("xDEUS supply H24", supply(XDEUS, H24))
print("DEUS total supply now", supply(DEUS) / 1e18)
print("DEUS total supply H24", supply(DEUS, H24) / 1e18)
print("CLAIM vault DEUS now", bal(DEUS, CLAIM))

W = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"
print()
print("pending trigger 0xbb0f7533:")
print("  xDEUS balance", bal(XDEUS, W, "latest", 0))
v, e = call(XDEUS, "0x2f745c59" + "0" * 24 + W[2:] + "0" * 64)
print("  tokenOfOwnerByIndex(0)", None if e else int(v, 16))
print("  DEUS balance", bal(DEUS, W))

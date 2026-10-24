import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
W = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"
H24 = 52996382


def rpc(payload, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
            )
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print("retry", i, repr(e)[:60])
            time.sleep(1.5 * (i + 1))
    return None


def bal(token, holder, block="latest"):
    data = "0x70a08231" + "0" * 24 + holder[2:].lower()
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": token, "data": data}, block if block == "latest" else hex(block)],
        }
    )
    if not r or "error" in r:
        return None, (r or {}).get("error")
    return int(r["result"], 16) / 1e18, None


for blk in ("latest", H24):
    b, e = bal(DEUS, ESCROW, blk)
    print("escrow", blk, b, e)
    time.sleep(2)

b, e = bal(DEUS, W)
print("0xbb0f7533 DEUS", b, e)

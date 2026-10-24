import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
H24 = 52996382


def rpc(payload, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
            )
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def bal(holder, block="latest"):
    data = "0x70a08231" + "0" * 24 + holder[2:].lower()
    r = rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": DEUS, "data": data}, block if block == "latest" else hex(block)],
        }
    )
    if not r or "error" in r:
        return None
    return int(r["result"], 16) / 1e18


now = bal(CLAIM)
old = bal(CLAIM, H24)
print("CLAIM now", now)
print("CLAIM 24h ago", old)
print("CLAIM 24h net out", None if (now is None or old is None) else old - now)

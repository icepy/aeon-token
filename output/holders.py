import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
WATCH = {
    "0x9d1c316f (new buyer 18:01Z)": "0x9d1c316f1f307894c80e7d2963454e6342c8e0a9",
    "0x7f6aba75 (335k whale)": "0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3",
    "0xeb7c90d3 (sold 5500)": "0xeb7c90d3d8eb5cce9c3da4725ba9d5177cf8cc50",
    "0x659c92a1 (sold 6414)": "0x659c92a1c1050684ab6dac7755dc4f35912bd5de",
}


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


for name, a in WATCH.items():
    now = bal(a)
    h1 = bal(a, 53037782)
    print(f"{name}: now={now}  at_1h_ago={h1}")
    time.sleep(1)

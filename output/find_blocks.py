import json, urllib.request

URL = "https://base.gateway.tenderly.co"


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def ts(b):
    r = rpc({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(b), False]})
    return int(r["result"]["timestamp"], 16)


head = 53039582
headts = ts(head)
print("head", head, headts)
for delta in (3600, 86400):
    target = headts - delta
    lo, hi = head - delta // 2 - 4000, head
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ts(mid) <= target:
            lo = mid
        else:
            hi = mid - 1
    print(delta, "->", lo, ts(lo), "exact_delta", headts - ts(lo))

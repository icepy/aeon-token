import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"


def rpc(m, p, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(req, timeout=45))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 * (i + 1))
                continue
            raise
    raise RuntimeError("rate limited")


def meta(addr):
    out = {}
    for sel, key in [("0x95d89b41", "symbol"), ("0x313ce567", "decimals")]:
        r = rpc("eth_call", [{"to": addr, "data": sel}, "latest"]).get("result", "0x")
        if r and r != "0x":
            if key == "decimals":
                out[key] = int(r, 16)
            else:
                raw = bytes.fromhex(r[2:])
                ln = int.from_bytes(raw[32:64], "big")
                out[key] = raw[64:64 + ln].decode("utf-8", "replace")
        time.sleep(2)
    return out


for a in ["0x6bd83abc39391af1e24826e90237c4bd3468b5d2",
          "0x0a2854fbbd9b3ef66f17d47284e7f899b9509330"]:
    print(a, meta(a))

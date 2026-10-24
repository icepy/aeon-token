import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa"

REAL = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
TYPO = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abdf50e9722b7ff3d2de2b0d2f2c"
BOGUS = "0x" + "01" * 32

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    for a, b in enumerate([1, 2, 4, 8]):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if a == 3: raise
            time.sleep(b)

head = int(rpc("eth_blockNumber", []), 16)
# window proven to contain 2 real Sync events
lo, hi = 53024572, 53025572
print(f"window {lo}-{hi}")

base = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi)}])
print(f"address-only total logs: {len(base)}")

for name, h in (("REAL", REAL), ("TYPO", TYPO), ("BOGUS 0x01*32", BOGUS)):
    got = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [h]}])
    print(f"\n{name} filter -> {len(got)} logs")
    for lg in got:
        actual = lg["topics"][0]
        print(f"   actual topic0 = {actual}")
        print(f"   MATCHES FILTER? {actual.lower() == h.lower()}")

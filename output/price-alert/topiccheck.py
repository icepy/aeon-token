import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

SYNC_TRUE = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
SYNC_TYPO = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abdf50e9722b7ff3d2de2b0d2f2c"
BOGUS     = "0x" + "01" * 32

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    for attempt, back in enumerate([1, 2, 4, 8]):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if attempt == 3:
                raise
            time.sleep(back)

head = int(rpc("eth_blockNumber", []), 16)
lo, hi = head - 999, head
print(f"window {lo} -> {hi} (head {head})\n")

print("--- address-only, all logs, verbatim ---")
all_logs = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi)}])
print(f"count = {len(all_logs)}")

# widen: walk back further in 1000-blk windows to find the last event
print("\n--- walking back to locate last pool event ---")
for w in range(8):
    h2 = head - w * 1000
    l2 = h2 - 999
    logs = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(l2), "toBlock": hex(h2)}])
    tag = f"blk {l2}-{h2}"
    if logs:
        print(f"  {tag}: {len(logs)} logs")
        for lg in logs:
            bn = int(lg["blockNumber"], 16)
            ts = int(rpc("eth_getBlockByNumber", [hex(bn), False])["timestamp"], 16)
            print(f"      blk {bn} {time.strftime('%H:%M:%SZ', time.gmtime(ts))} topic0 {lg['topics'][0][:18]}…")
    else:
        print(f"  {tag}: 0")

print("\n--- filter discrimination (same 1000-blk window) ---")
for name, h in (("SYNC_TRUE", SYNC_TRUE), ("SYNC_TYPO", SYNC_TYPO), ("BOGUS_01*32", BOGUS)):
    got = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [h]}])
    print(f"  {name:12s} -> {len(got)} logs", [lg["topics"][0][:18] + "…" for lg in got])

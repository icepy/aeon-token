import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

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
# window that we know contains logs
lo, hi = head - 1600, head - 600
logs = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi)}])
print(f"logs in {lo}-{hi}: {len(logs)}")
seen = {}
for lg in logs:
    for t in lg["topics"]:
        seen[t] = seen.get(t, 0) + 1
for t, n in sorted(seen.items(), key=lambda x: -x[1]):
    print(f"  {t}  x{n}")

real_sync = [t for t in seen if t.startswith("0xcf2aa50876cdfbb541206f89")]
print("\nreal Sync topic0s found:", real_sync)

# decode Sync with the real topic
if real_sync:
    SYNC = real_sync[0]
    got = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": [SYNC]}])
    print(f"Sync count with real hash: {len(got)}")
    # negative control: same window, bogus topic
    bog = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi), "topics": ["0x" + "01"*32]}])
    print(f"negative control (0x01*32) in SAME window: {len(bog)}  <-- must be 0")
    json.dump({"sync_topic0": SYNC}, open("/home/runner/work/aeon-token/aeon-token/output/price-alert/topic0.json", "w"), indent=1)

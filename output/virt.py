import json, subprocess, time
RPC = "https://base.gateway.tenderly.co"
BLK = "0x3295ff4"
pools = {
    "0x7CB770D0513c30e0CB45E4899e4a2CbEEd6F9830": "VIRTUAL/USDC pancake",
    "0x529d2863a1521d0b57db028168fdE2E97120017C": "VIRTUAL/USDC uni",
    "0x21594b992F68495dD28d605834b58889d0a727c7": "VIRTUAL/WETH",
}

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p} for i, (m, p) in enumerate(calls)])
    for attempt in range(5):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(2 ** attempt); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(2 ** attempt); continue
        return j
    raise RuntimeError("failed: " + out[:300])

for addr, name in pools.items():
    res = rpc([
        ("eth_call", [{"to": addr, "data": "0x3850c7bd"}, BLK]),
        ("eth_call", [{"to": addr, "data": "0x0dfe1681"}, BLK]),
        ("eth_call", [{"to": addr, "data": "0xd21220a7"}, BLK]),
    ])
    d = {r["id"]: r.get("result") for r in res}
    print("==", name, addr)
    print("  slot0 :", (d.get(0) or "")[:80])
    print("  token0:", d.get(1))
    print("  token1:", d.get(2))
    time.sleep(1.5)

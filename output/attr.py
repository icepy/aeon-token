import json, subprocess, time
RPC = "https://base.gateway.tenderly.co"
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
TXS = ["0xc850ee0dfb125c2e1a6fed77c8746d6b670f9c122e1cfd5f445a38172f52b6b5",
       "0x861538dff0899584ab9158828daed562e88ce345423ad109a1e9247ff181e89c"]

def rpc(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": m, "params": p}
                          for i, (m, p) in enumerate(calls)])
    for a in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * 2 ** a); continue
        if isinstance(j, dict) and "error" in j:
            time.sleep(1.5 * 2 ** a); continue
        return j
    raise RuntimeError("fail")

for tx in TXS:
    print("=" * 70)
    print("TX", tx)
    j = rpc([("eth_getTransactionByHash", [tx]), ("eth_getTransactionReceipt", [tx])])
    t = j[0]["result"]; r = j[1]["result"]
    print("  from:", t["from"], " to:", t["to"], " block:", int(r["blockNumber"], 16))
    from collections import Counter
    # DEUS transfer legs involving the pool
    logs = r["logs"]
    print("  logs:", len(logs))
    for l in logs:
        if len(l["topics"]) == 3:  # ERC20 Transfer
            amt = int(l["data"][2:66], 16) / 1e18
            frm = "0x" + l["topics"][1][-40:]
            to = "0x" + l["topics"][2][-40:]
            tag = ""
            if amt > 1:
                if frm.lower() == DEEP.lower(): tag = "[OUT of pool]"
                elif to.lower() == DEEP.lower(): tag = "[INTO pool]"
                print(f"    {frm} -> {to}  {amt:,.4f}  {tag}")
    time.sleep(1)

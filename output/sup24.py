import json, subprocess, time
RPC = "https://base.gateway.tenderly.co"
HEAD, B24 = 53043188, 52999988
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
CLAIM = "0x5cbF5DFAa5336ce0456e24217e7911365100879a"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    last = ""
    for a in range(7):
        out = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST", RPC,
                              "-H", "Content-Type: application/json", "-d", payload],
                             capture_output=True, text=True).stdout
        last = out
        try:
            j = json.loads(out)
        except Exception:
            time.sleep(1.5 * 2 ** a); continue
        if "error" in j:
            time.sleep(1.5 * 2 ** a); continue
        return j["result"]
    raise RuntimeError(last[:200])

def bal(tok, who, blk):
    d = "0x70a08231" + "0" * 24 + who[2:].lower()
    return int(rpc("eth_call", [{"to": tok, "data": d}, hex(blk)]), 16)

def ts(blk):
    return int(rpc("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16)

print("B24 ts", ts(B24), "delta", ts(HEAD) - ts(B24))
sup_now = int(rpc("eth_call", [{"to": DEUS, "data": "0x18160ddd"}, hex(HEAD)]), 16) / 1e18
sup_24 = int(rpc("eth_call", [{"to": DEUS, "data": "0x18160ddd"}, hex(B24)]), 16) / 1e18
print("supply %.2f -> %.2f  delta %+.2f" % (sup_24, sup_now, sup_now - sup_24))

c_now = bal(DEUS, CLAIM, HEAD) / 1e18
c_24 = bal(DEUS, CLAIM, B24) / 1e18
print("CLAIM  %.2f -> %.2f  net out %+.2f  (%.3f%% of supply)" %
      (c_24, c_now, c_24 - c_now, c_now / sup_now * 100))

x_now = int(rpc("eth_call", [{"to": XDEUS, "data": "0x18160ddd"}, hex(HEAD)]), 16)
x_24 = int(rpc("eth_call", [{"to": XDEUS, "data": "0x18160ddd"}, hex(B24)]), 16)
print("xDEUS  %d -> %d  delta %+d" % (x_24, x_now, x_now - x_24))

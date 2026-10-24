#!/usr/bin/env python3
"""On-chain probe for the price-alert run. Keyless, Tenderly public gateway."""
import json, time, urllib.request, sys

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"   # deepest DEUS pool (VIRTUAL token0 / DEUS token1)
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
XDEUS = "0xe6d5f7434c000000000000000000000000000000"  # placeholder, replaced below if needed
VIRTUAL_USDC = "0x529d28634d5d1d6d4f6c9d1e0f9b4a0b0b1e6d1c"  # placeholder, resolved from state instead
SWAP_SOLIDLY = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                last = d["error"]
                msg = json.dumps(d["error"])
                if "-32005" in msg or "rate" in msg.lower() or "too large" in msg.lower():
                    time.sleep(delay); delay *= 2; continue
                raise RuntimeError(msg)
            return d.get("result")
        except Exception as e:
            last = e
            time.sleep(delay); delay *= 2
    raise RuntimeError(f"rpc failed {method}: {last}")

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

def hexint(x):
    return int(x, 16) if x and x != "0x" else 0

def word(h, i):
    s = h[2:] if h.startswith("0x") else h
    return "0x" + s[i*64:(i+1)*64]

def pad(addr):
    return "0x" + addr[2:].rjust(64, "0")

out = {}
head = hexint(rpc("eth_blockNumber", []))
hb = rpc("eth_getBlockByNumber", [hex(head), False])
head_ts = hexint(hb["timestamp"])
out["head_block"] = head
out["head_ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(head_ts))

def reserves(tag="latest"):
    r = call(POOL, "0x0902f1ac", tag)  # getReserves()
    if not r or r == "0x":
        return None
    r0, r1, ts = hexint(word(r,0)), hexint(word(r,1)), hexint(word(r,2))
    return {"reserve0_virtual": r0/1e18, "reserve1_deus": r1/1e18, "ratio_virtual_per_deus": (r0/1e18)/(r1/1e18), "block_ts_last": ts}

# token0 / token1 sanity
try:
    t0 = call(POOL, "0x0dfe1681"); t1 = call(POOL, "0xd21220a7")
    out["token0"] = "0x" + word(t0,0)[-40:]
    out["token1"] = "0x" + word(t1,0)[-40:]
except Exception as e:
    out["token_err"] = str(e)

out["reserves_now"] = reserves()

# reserves exactly 3600s ago -> find block by timestamp
lo, hi = head - 4000, head
target = head_ts - 3600
while lo < hi:
    mid = (lo + hi) // 2
    b = rpc("eth_getBlockByNumber", [hex(mid), False])
    if hexint(b["timestamp"]) < target:
        lo = mid + 1
    else:
        hi = mid
blk_1h = lo
b1 = rpc("eth_getBlockByNumber", [hex(blk_1h), False])
out["blk_1h"] = blk_1h
out["blk_1h_ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hexint(b1["timestamp"])))
out["blk_1h_delta"] = head_ts - hexint(b1["timestamp"])
out["reserves_1h"] = reserves(hex(blk_1h))

# 24h ago reserves
lo, hi = head - 90000, head
target24 = head_ts - 86400
while lo < hi:
    mid = (lo + hi) // 2
    b = rpc("eth_getBlockByNumber", [hex(mid), False])
    if hexint(b["timestamp"]) < target24:
        lo = mid + 1
    else:
        hi = mid
blk_24h = lo
b24 = rpc("eth_getBlockByNumber", [hex(blk_24h), False])
out["blk_24h"] = blk_24h
out["blk_24h_delta"] = head_ts - hexint(b24["timestamp"])
out["reserves_24h"] = reserves(hex(blk_24h))

# Swap scan on deepest pool: 1h window, 1000-block chunks
def scan_swaps(from_blk, to_blk):
    logs = []
    s = from_blk
    while s <= to_blk:
        e = min(s + 999, to_blk)
        try:
            res = rpc("eth_getLogs", [{"address": POOL, "topics": [SWAP_SOLIDLY], "fromBlock": hex(s), "toBlock": hex(e)}])
            logs.extend(res or [])
        except Exception as ex:
            out.setdefault("scan_errors", []).append(f"{s}-{e}: {ex}")
        s = e + 1
    return logs

logs_1h = scan_swaps(blk_1h, head)
out["swaps_1h"] = len(logs_1h)
last = logs_1h[-1] if logs_1h else None
out["last_swap_1h"] = {"block": hexint(last["blockNumber"]), "tx": last["transactionHash"]} if last else None

# find last swap before the 1h window (scan backwards in 1000s up to 6h)
back = []
s = blk_1h - 1
limit = blk_1h - 12000
while s > limit and not back:
    e = max(s - 999, limit)
    try:
        res = rpc("eth_getLogs", [{"address": POOL, "topics": [SWAP_SOLIDLY], "fromBlock": hex(e), "toBlock": hex(s)}])
        if res:
            back = res
            break
    except Exception as ex:
        out.setdefault("scan_errors", []).append(f"back {e}-{s}: {ex}")
    s = e - 1
if back:
    lb = hexint(back[-1]["blockNumber"])
    bb = rpc("eth_getBlockByNumber", [hex(lb), False])
    out["last_swap_before_1h"] = {
        "block": lb, "tx": back[-1]["transactionHash"],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hexint(bb["timestamp"]))),
        "minutes_before_run": round((head_ts - hexint(bb["timestamp"]))/60, 1),
    }
else:
    out["last_swap_before_1h"] = None

# control: known-active window from prior runs (53027400..53028000 had 2 swaps)
try:
    ctl = rpc("eth_getLogs", [{"address": POOL, "topics": [SWAP_SOLIDLY], "fromBlock": hex(53027400), "toBlock": hex(53028000)}])
    out["control_known_window"] = len(ctl or [])
    bad = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75c"
    ctl2 = rpc("eth_getLogs", [{"address": POOL, "topics": [bad], "fromBlock": hex(53027400), "toBlock": hex(53028000)}])
    out["control_altered_topic"] = len(ctl2 or [])
except Exception as ex:
    out["control_err"] = str(ex)

# balances: DEUS balanceOf for key wallets + escrow
WALLETS = {
    "escrow": "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373",
    "claim_main": "0x5cbf5dfaa5336ce0456e24217e7911365100879a",
    "claim_dist_0x20d2": "0x20d29c8ec7489c600da7e595ce4ae1da11d76fc5",
    "0xbb0f7533": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
    "0xf0a04b07": "0xf0a04b079dcf7b9d92682123ba2e2180109cb650",
    "0x7f6aba75": "0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3",
    "0x6a45ca8b": "0x6a45ca8bb30f396f40721e105e0aa6cabf326657",
    "0xcae798c0": "0xcae798c0c6958df8299df4f13726da433b8ba7ba",
}
bal = {}
for k, a in WALLETS.items():
    try:
        r = call(DEUS, "0x70a08231" + pad(a)[2:])
        bal[k] = hexint(r)/1e18
    except Exception as ex:
        bal[k] = f"ERR {ex}"
out["deus_balances"] = bal

# escrow balance at 24h ago
try:
    r = call(DEUS, "0x70a08231" + pad(WALLETS["escrow"])[2:], hex(blk_24h))
    out["escrow_24h_ago"] = hexint(r)/1e18
except Exception as ex:
    out["escrow_24h_ago"] = f"ERR {ex}"

# xDEUS allowance for 0xbb0f7533 (does it still hold NFT 1396?)
XDEUS_ADDR = "0xe6d5f7434c000000000000000000000000000000"
out["note_xdeus_addr_placeholder"] = True

print(json.dumps(out, indent=2))

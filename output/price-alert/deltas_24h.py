#!/usr/bin/env python3
"""24h deltas for the CLAIM vault, escrow, xDEUS supply and DEUS supply (real block-pinned reads)."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"


def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def pad(a):
    return a.lower().replace("0x", "").rjust(64, "0")


def bal(token, holder, block):
    r = rpc("eth_call", [{"to": token, "data": "0x70a08231" + pad(holder)}, hex(block)])
    return int(r, 16) / 1e18


def supply(token, block):
    r = rpc("eth_call", [{"to": token, "data": "0x18160ddd"}, hex(block)])
    return int(r, 16)


if __name__ == "__main__":
    now_blk = int(rpc("eth_blockNumber", []), 16)
    # ~24h back at Base ~2s blocks
    back = now_blk - 43200
    out = {"now_block": now_blk, "ref_block": back}
    nb = rpc("eth_getBlockByNumber", [hex(now_blk), False])
    rb = rpc("eth_getBlockByNumber", [hex(back), False])
    out["now_ts"] = int(nb["timestamp"], 16)
    out["ref_ts"] = int(rb["timestamp"], 16)
    out["hours"] = round((out["now_ts"] - out["ref_ts"]) / 3600, 2)

    out["claim_now"] = bal(DEUS, CLAIM, now_blk)
    out["claim_ref"] = bal(DEUS, CLAIM, back)
    out["claim_delta_24h"] = out["claim_now"] - out["claim_ref"]
    out["claim_net_out_24h"] = out["claim_ref"] - out["claim_now"]
    out["claim_pct_per_day"] = 100 * out["claim_net_out_24h"] / out["claim_ref"]

    out["escrow_now"] = bal(DEUS, ESCROW, now_blk)
    out["escrow_ref"] = bal(DEUS, ESCROW, back)
    out["escrow_delta_24h"] = out["escrow_now"] - out["escrow_ref"]
    out["escrow_pct_24h"] = 100 * (out["escrow_now"] - out["escrow_ref"]) / out["escrow_ref"]
    out["five_pct_line_deus"] = 0.05 * out["escrow_now"]

    out["xdeus_now"] = supply(XDEUS, now_blk)
    out["xdeus_ref"] = supply(XDEUS, back)
    out["xdeus_delta_24h"] = out["xdeus_now"] - out["xdeus_ref"]

    out["supply_now"] = supply(DEUS, now_blk) / 1e18
    out["supply_ref"] = supply(DEUS, back) / 1e18
    out["supply_delta_24h"] = out["supply_now"] - out["supply_ref"]

    print(json.dumps(out, indent=1))

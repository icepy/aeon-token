#!/usr/bin/env python3
"""Forward signals for the DEUS operator: escrow burn trigger, buyer holdings, claim drip."""
import json
import sys
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
BURN_TOPIC0 = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
BUYER1 = "0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3"
BUYER2 = "0x6a45ca8bb30f396f40721e105e0aa6cabf326657"
UNSTAKER = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"


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


def bal(token, holder):
    r = rpc("eth_call", [{"to": token, "data": "0x70a08231" + pad(holder)}, "latest"])
    return int(r, 16) if r and r != "0x" else 0


def walk(pool, lo, hi, topics):
    out, start = [], lo
    while start <= hi:
        end = min(start + 999, hi)
        out.extend(rpc("eth_getLogs", [{"address": pool, "fromBlock": hex(start),
                                        "toBlock": hex(end), "topics": topics}]))
        start = end + 1
        time.sleep(0.35)
    return out


if __name__ == "__main__":
    bn = int(rpc("eth_blockNumber", []), 16)
    res = {"block": bn}

    # escrow burn scan: last ~4000 blocks (~2.2h)
    burns = walk(ESCROW, bn - 4000, bn, [BURN_TOPIC0])
    res["escrow_burns_last_4000"] = len(burns)
    res["escrow_burn_details"] = [
        {"block": int(b["blockNumber"], 16), "tx": b["transactionHash"],
         "topics": b["topics"], "data": b["data"]} for b in burns
    ]
    # control: known burn window around block 53002812
    ctl = walk(ESCROW, 53002812 - 50, 53002812 + 50, [BURN_TOPIC0])
    res["control_burn_window_53002812"] = len(ctl)

    res["escrow_deus_balance"] = bal(DEUS, ESCROW) / 1e18
    res["xdeus_total_supply"] = int(rpc("eth_call", [{"to": XDEUS, "data": "0x18160ddd"}, "latest"]), 16)
    res["claim_deus_balance"] = bal(DEUS, CLAIM) / 1e18
    res["deus_total_supply"] = int(rpc("eth_call", [{"to": DEUS, "data": "0x18160ddd"}, "latest"]), 16) / 1e18

    res["buyer1_deus"] = bal(DEUS, BUYER1) / 1e18
    res["buyer2_deus"] = bal(DEUS, BUYER2) / 1e18
    res["unstaker_deus"] = bal(DEUS, UNSTAKER) / 1e18
    # which xDEUS NFT does the record unsaker still hold?
    try:
        r = rpc("eth_call", [{"to": XDEUS, "data": "0x2f745c59" + pad(UNSTAKER) + hex(0)[2:].rjust(64, "0")}, "latest"])
        res["unstaker_xdeus_nft_0"] = int(r, 16) if r and r != "0x" else None
    except Exception as e:  # noqa: BLE001
        res["unstaker_xdeus_nft_0"] = f"error: {e}"

    print(json.dumps(res, indent=1))

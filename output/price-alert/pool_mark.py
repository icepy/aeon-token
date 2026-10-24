#!/usr/bin/env python3
"""Read canonical DEUS mark from the deepest pool's own reserves + live VIRTUAL leg."""
import json
import sys
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
DEEP_POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"  # aerodrome slipstream DEUS/VIRTUAL
VIRTUAL = "0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b"      # VIRTUAL token on Base
BALANCEOF = "0x70a08231"
DECIMALS = "0x313ce567"


def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(f"rpc error: {out['error']}")
            return out["result"]
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def pad(addr):
    return "0x" + addr.lower().replace("0x", "").rjust(64, "0")


def bal(token, holder, block="latest"):
    r = rpc("eth_call", [{"to": token, "data": BALANCEOF + pad(holder)[2:]}, block])
    return int(r, 16) if r and r != "0x" else 0


def dec(token):
    r = rpc("eth_call", [{"to": token, "data": DECIMALS}, "latest"])
    return int(r, 16) if r and r != "0x" else 18


if __name__ == "__main__":
    blk = rpc("eth_blockNumber", [])
    bn = int(blk, 16)
    d_dec = dec(DEUS)
    v_dec = dec(VIRTUAL)
    deus_in_pool = bal(DEUS, DEEP_POOL) / 10**d_dec
    virt_in_pool = bal(VIRTUAL, DEEP_POOL) / 10**v_dec
    virt_total = rpc("eth_call", [{"to": VIRTUAL, "data": "0x18160ddd"}, "latest"])
    print(json.dumps({
        "block": bn,
        "deus_decimals": d_dec,
        "virtual_decimals": v_dec,
        "pool_deus": deus_in_pool,
        "pool_virtual": virt_in_pool,
        "mark_virtual_per_deus": virt_in_pool / deus_in_pool if deus_in_pool else None,
        "virtual_total_supply_raw": virt_total,
    }, indent=1))

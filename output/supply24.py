#!/usr/bin/env python3
"""Block-pinned 24h: DEUS total supply, escrow, CLAIM vault, xDEUS supply."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last = e
            time.sleep(0.8 * (2 ** i))
    raise last

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

def ts_of(b):
    return int(rpc("eth_getBlockByNumber", [hex(b), False])["timestamp"], 16)

head = int(rpc("eth_blockNumber", []), 16)
hts = ts_of(head)

def find(target, lo, hi):
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if ts_of(mid) <= target:
            lo = mid
        else:
            hi = mid
    return lo

b24 = find(hts - 86400, head - 90000, head)
print("head=%d  b24=%d  dt=%d" % (head, b24, hts - ts_of(b24)), flush=True)

DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"

def ts_(to, sel, tag):
    return int(call(to, sel, tag), 16)

sup_now = ts_(DEUS, "0x18160ddd", "latest") / 1e18
sup_24 = ts_(DEUS, "0x18160ddd", hex(b24)) / 1e18
print("supply now=%.4f 24h_ago=%.4f delta=%.2f" % (sup_now, sup_24, sup_now - sup_24), flush=True)

pad = "0" * 24
def bal(tok, holder, tag):
    return int(call(tok, "0x70a08231" + pad + holder[2:].lower(), tag), 16) / 1e18

e_now = bal(DEUS, ESCROW, "latest")
e_24 = bal(DEUS, ESCROW, hex(b24))
print("escrow now=%.4f 24h_ago=%.4f delta=%.2f pct=%.3f" % (
    e_now, e_24, e_now - e_24, (e_now / e_24 - 1) * 100), flush=True)
print("escrow_5pct_line=%.2f ratio=%.3f" % (e_24 * 0.05, (e_24 - e_now) / (e_24 * 0.05)), flush=True)

c_now = bal(DEUS, CLAIM, "latest")
c_24 = bal(DEUS, CLAIM, hex(b24))
print("claim now=%.4f 24h_ago=%.4f net_out=%.2f" % (c_now, c_24, c_24 - c_now), flush=True)
print("claim_pct_supply=%.2f" % (c_now / sup_now * 100), flush=True)

x_now = ts_(XDEUS, "0x18160ddd", "latest")
x_24 = ts_(XDEUS, "0x18160ddd", hex(b24))
print("xdeus now=%d 24h_ago=%d delta=%d" % (x_now, x_24, x_now - x_24), flush=True)
print("deus_price_assumed=0.01750110  claim_usd_per_day=%.0f" % ((c_24 - c_now) * 0.0175011), flush=True)

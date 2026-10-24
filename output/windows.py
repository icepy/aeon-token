#!/usr/bin/env python3
"""Block-pinned 1h / 24h marks for the deepest DEUS pool + a Swap-log activity scan."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=3):
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
            time.sleep(1.5 * (2 ** i))
    raise last

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

def block(hexnum):
    return rpc("eth_getBlockByNumber", [hexnum, False])

def ts_of(b):
    return int(b["timestamp"], 16)

head = int(rpc("eth_blockNumber", []), 16)
head_ts = ts_of(block(hex(head)))
print("head=%d head_ts=%d" % (head, head_ts))

def find_block_at(target_ts, lo, hi):
    """binary search for the greatest block with ts <= target_ts."""
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if ts_of(block(hex(mid))) <= target_ts:
            lo = mid
        else:
            hi = mid
    return lo

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VIRTUAL = "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
WETH = "0x4200000000000000000000000000000000000006"

def reserves(pool, tag):
    r = call(pool, "0x0902f1ac", tag)
    w = r[2:]
    return int(w[0:64], 16), int(w[64:128], 16)

def slot0(pool, tag):
    r = call(pool, "0x3850c7bd", tag)
    return int(r[2:][0:64], 16)

def p_t1_per_t0(sp, d0, d1):
    return ((sp / 2**96) ** 2) * (10 ** d0) / (10 ** d1)

# reference blocks
b1h = find_block_at(head_ts - 3600, head - 4000, head)
b24h = find_block_at(head_ts - 86400, head - 90000, head)
print("1h_block=%d ts=%d delta=%d" % (b1h, ts_of(block(hex(b1h))), head_ts - ts_of(block(hex(b1h)))))
print("24h_block=%d ts=%d delta=%d" % (b24h, ts_of(block(hex(b24h))), head_ts - ts_of(block(hex(b24h)))))

# VIRTUAL/USD and ETH/USD at the three timestamps
ETH_POOL = "0xd0b53D9277642d899DF5C87A3966A349A798F224"
VIRT_POOL = "0x529d2863a1521d0b57db028168fdE2E97120017C"

def refs(tag):
    eth = p_t1_per_t0(slot0(ETH_POOL, tag), 18, 6)
    vir = p_t1_per_t0(slot0(VIRT_POOL, tag), 18, 6)
    return eth, vir

eth_h, vir_h = refs(hex(b1h))
eth_24, vir_24 = refs(hex(b24h))
eth_n, vir_n = refs("latest")
print("eth: 24h=%.4f 1h=%.4f now=%.4f" % (eth_24, eth_h, eth_n))
print("virtual: 24h=%.6f 1h=%.6f now=%.6f" % (vir_24, vir_h, vir_n))

v1, d1 = reserves(DEEP, hex(b1h))
v24, d24 = reserves(DEEP, hex(b24h))
v0, d0 = reserves(DEEP, "latest")

r1h, r24, rn = v1 / d1, v24 / d24, v0 / d0
m1h, m24, mn = r1h * vir_h, r24 * vir_24, rn * vir_n

print("ratio: 24h=%.10f 1h=%.10f now=%.10f" % (r24, r1h, rn))
print("mark : 24h=%.8f 1h=%.8f now=%.8f" % (m24, m1h, mn))
print("h1_pct=%.3f" % ((mn / m1h - 1) * 100))
print("h24_pct=%.3f" % ((mn / m24 - 1) * 100))
print("reserve_deus: 24h=%d 1h=%d now=%d" % (d24, d1, d0))
print("reserve_virtual: 24h=%d 1h=%d now=%d" % (v24, v1, v0))

# Swap activity in the last hour (Solidly family: full 64-hex topic0)
SWAP_SOLIDLY = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
logs = []
lo = b1h
while lo < head:
    hi = min(lo + 999, head)
    got = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(lo), "toBlock": hex(hi),
                               "topics": [SWAP_SOLIDLY]}])
    logs.extend(got)
    lo = hi + 1
print("swaps_1h=%d" % len(logs))

# decode Solidly Swap: data = amount0In, amount1In, amount0Out, amount1Out
# topics[1]=sender topics[2]=to
buys = 0
sells = 0
deus_bought = 0
deus_sold = 0
last_ts = None
for lg in logs:
    w = lg["data"][2:]
    a0i = int(w[0:64], 16)
    a1i = int(w[64:128], 16)
    a0o = int(w[128:192], 16)
    a1o = int(w[192:256], 16)
    # token0=VIRTUAL, token1=DEUS
    # DEUS out of pool = a1o (buyer received DEUS); DEUS into pool = a1i (seller sent DEUS)
    if a1o > 0:
        buys += 1
        deus_bought += a1o / 1e18
    if a1i > 0:
        sells += 1
        deus_sold += a1i / 1e18
    last_ts = int(lg["blockNumber"], 16)
print("buy_tx=%d sell_tx=%d deus_bought=%.2f deus_sold=%.2f" % (buys, sells, deus_bought, deus_sold))
print("net_deus_out_of_pool=%.2f" % (deus_bought - deus_sold))

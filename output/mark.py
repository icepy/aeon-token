import json, sys
from decimal import Decimal, getcontext
sys.path.insert(0, "output")
from rpc import call

getcontext().prec = 40
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
VUSDC = "0x529d2863a1521d0b57db028168fdE2E97120017C"

def reserves(blk):
    r = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(blk)])[2:]
    return (int(r[0:64], 16), int(r[64:128], 16), int(r[128:192], 16))

def virtual_usd(blk):
    w = call("eth_call", [{"to": VUSDC, "data": "0x3850c7bd"}, hex(blk)])[2:]
    sq = int(w[0:64], 16)
    return Decimal(sq) ** 2 / Decimal(2) ** 192 * Decimal(10) ** 12

def mark(blk):
    r0, r1, ts_last = reserves(blk)
    v = Decimal(r0) / Decimal(10) ** 18
    d = Decimal(r1) / Decimal(10) ** 18
    p = virtual_usd(blk)
    return {"blk": blk, "virtual": float(v), "deus": float(d),
            "ratio": float(v / d), "virtual_usd": float(p),
            "mark_usd": float(v / d * p), "pool_ts_last": ts_last}

for lbl, blk in (("head", 53061213), ("h1", 53059413), ("h24", 53018013)):
    print(lbl, json.dumps(mark(blk)))

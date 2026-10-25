import json, sys
sys.path.insert(0, "output")
from rpc import call

def ts(blk):
    b = call("eth_getBlockByNumber", [hex(blk), False])
    return int(b["timestamp"], 16)

def find(target, lo=0, hi=None):
    """largest block with ts <= target"""
    if hi is None:
        hi = int(call("eth_blockNumber", []), 16)
    if lo == 0:
        lo = hi - 200000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ts(mid) <= target:
            lo = mid
        else:
            hi = mid - 1
    return lo

head = int(call("eth_blockNumber", []), 16)
head_ts = ts(head)
print("head", head, head_ts)
for name, delta in (("h1", 3600), ("h24", 86400)):
    blk = find(head_ts - delta, lo=head - 300000, hi=head)
    print(name, blk, ts(blk), "gap", head_ts - ts(blk))

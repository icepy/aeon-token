import json, urllib.request
from decimal import Decimal, getcontext
getcontext().prec = 50

RPC = "https://base.gateway.tenderly.co"
USDC_POOL = "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b"   # V3, token0=USDC(6) token1=DEUS(18)
DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.loads(r.read())
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]

head = int(rpc("eth_blockNumber", []), 16)
blk1h = 0x3291619 + (head - 53026081)   # ~1h back at 2s blocks
blk1h = head - 1800

def slot0(pool, blk):
    return int(rpc("eth_call", [{"to": pool, "data": "0x3850c7bd"}, hex(blk)])[2:][0:64], 16)

def v3_mark_usd(pool, blk):
    sp = slot0(pool, blk)
    p = (Decimal(sp) / Decimal(2**96)) ** 2      # token1_raw / token0_raw
    return float(Decimal(1e12) / p)              # USD per DEUS (token0=USDC6, token1=DEUS18)

m_now = v3_mark_usd(USDC_POOL, head)
m_1h = v3_mark_usd(USDC_POOL, blk1h)
print(f"USDC/V3 pool mark  {m_1h:.8f} -> {m_now:.8f}  = {(m_now/m_1h-1)*100:+.3f}% in 1h (head {head}, 1h {blk1h})")

# deepest-pool VIRTUAL leg -> USD
res = rpc("eth_call", [{"to": DEEP, "data": "0x0902f1ac"}, hex(head)])[2:]
v = int(res[0:64], 16) / 1e18
d = int(res[64:128], 16) / 1e18
ratio = v / d
for label, vp in (("deepest VIRTUAL/WETH $0.6270", 0.6270), ("aerodrome VIRTUAL/WETH $0.6324", 0.6324)):
    print(f"deepest-pool mark using {label}: ${ratio*vp:.8f}")

# swap activity on deepest pool, last ~1h (Solidly Swap topic0, full hash)
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
try:
    logs = rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(blk1h), "toBlock": hex(head), "topics": [SWAP]}])
    print(f"deepest pool swaps in last ~1h: {len(logs)}")
except Exception as e:
    print("getLogs err", e)

json.dump({"head": head, "blk1h": blk1h, "usdc_mark_now": m_now, "usdc_mark_1h": m_1h,
           "ratio": ratio}, open("/home/runner/work/aeon-token/aeon-token/output/price-alert/verify.json", "w"), indent=1)

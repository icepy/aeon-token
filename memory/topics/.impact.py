import json, urllib.request, math, datetime

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SELL_BLK = 53033946


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


def res(blk):
    d = call("eth_call", [{"to": POOL, "data": "0x0902f1ac"}, hex(blk)])[2:]
    return int(d[0:64], 16) / 1e18, int(d[64:128], 16) / 1e18


v_pre, d_pre = res(SELL_BLK - 1)
v_post, d_post = res(SELL_BLK)
print(f"single-tx impact (blk {SELL_BLK})")
print(f"  pre  V {v_pre:,.2f} D {d_pre:,.2f} ratio {v_pre/d_pre:.9f}")
print(f"  post V {v_post:,.2f} D {d_post:,.2f} ratio {v_post/d_post:.9f}")
print(f"  ratio change {(v_post/d_post)/(v_pre/d_pre)*100-100:+.4f}%")
print(f"  DEUS absorbed {d_post-d_pre:,.2f}")

v, d = res(int(call("eth_blockNumber", []), 16))
virt_usd = 0.6128  # live median, 5 venues
mark = (v / d) * virt_usd
print(f"\nhead reserves V {v:,.2f} D {d:,.2f} ratio {v/d:.9f}")
print(f"mark = ratio x $0.6128 = ${mark:.6f}")

print("\n-- constant-product target levels (x*y=k, ignoring fees) --")
for tgt in (0.012, 0.025, 0.032, 0.041):
    f = tgt / mark
    if f < 1:
        need = d * (1 / math.sqrt(f) - 1)
        print(f"  ${tgt:<6} needs net SELL  {need:>12,.0f} DEUS  (${need*mark:>10,.0f})  = {need/102000:.2f}x the 101,983 dump")
    else:
        need = d - d / math.sqrt(f)
        print(f"  ${tgt:<6} needs net BUY   {need:>12,.0f} DEUS  (${need*mark:>10,.0f})  pool D would fall to {d-need:,.0f}")
print(f"\n  gate distances from mark ${mark:.6f}:")
for tgt in (0.012, 0.025, 0.032, 0.041):
    print(f"    ${tgt:<6} {tgt/mark*100-100:+.2f}%")

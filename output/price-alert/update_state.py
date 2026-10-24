import json, os, shutil, datetime

P = "/home/runner/work/aeon-token/aeon-token/memory/topics/price-alert-state.json"
NOW = "2026-10-24T10:02:19Z"

with open(P) as f:
    st = json.load(f)

shutil.copyfile(P, P + ".bak")

prior_ath = st["ath"]["price_usd"]
cur = 0.01773
h1 = -0.76
h24 = 0.60

# ATH gate: must be strict higher
new_ath = cur > prior_ath
if new_ath:
    st["ath"] = {"price_usd": cur, "observed_at": NOW, "announced_at": NOW}

# target evaluation
targets_out = {}
for k, v in st["targets"].items():
    t = float(k)
    side = v.get("side")
    crossed = False
    if v.get("hit_at") is None:
        if side == "above" and cur >= t:
            crossed = True
        if side == "below" and cur <= t:
            crossed = True
    if crossed:
        v["hit_at"] = NOW
        v["announced_at"] = NOW
    targets_out[k] = v

st["targets"] = targets_out
st["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
st["chain"] = "base"
st["last_run_at"] = NOW
st["last_price"] = {
    "price_usd": cur,
    "h1_pct": h1,
    "h24_pct": h24,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL — deepest, liq $667,670",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 667669.97,
    "volume_24h_usd": 30043.48,
    "volume_1h_usd": 936.65,
    "txns_1h": "15 buys / 0 sells on deepest pool (DexScreener h1)",
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "h1_source": "measured — pool reserve ratio + VIRTUAL/USD leg, cross-checked vs DexScreener h1=-0.76%",
    "h1_note": (
        "h1 IS MEASURED this run (not null). Deepest pool reserves at blk 53,021,596 "
        "(09:02:19Z) VIRTUAL 527,596.678 / DEUS 18,874,651.672 -> ratio 0.02795266; "
        "at blk 53,023,396 (10:02:19Z) VIRTUAL 529,062.421 / DEUS 18,822,360.326 -> "
        "0.02810819 VIRTUAL/DEUS = +0.556% in DEUS/VIRTUAL terms. The VIRTUAL leg fell "
        "~1.3% over the same hour, so the USD mark nets to -0.76% — identical to "
        "DexScreener's deepest-pair h1. Both far from the 20% gate. Three live USDC "
        "venues printed h1 -1.05% / -1.50% / -2.12% (median venue -1.50%). "
        "No venue anywhere near +/-20%."
    ),
    "mark_source": "deepest-pool reserves converted via on-chain VIRTUAL/USD + live USDC venues",
    "mark_note": (
        "Deepest pool 0x3E97c5EC: token0 = VIRTUAL (0x0b3e3284), token1 = DEUS "
        "(0x940a319b) — orientation confirmed by eth_call this run, so USD mark = "
        "ratio x VIRTUAL price, never the ratio read as dollars. Ratio 0.02810819 x "
        "VIRTUAL $0.6309 (deepest VIRTUAL/WETH, liq $3.29M) = $0.017733. Cross-check: "
        "USDC venues 0x58dBa34e $0.01770 / 0x1B2f3f5C $0.01762 / 0x75bc1495 $0.01762 "
        "-> median $0.01762. Deepest-pool mark sits +0.6% above the USDC median, same "
        "order as prior runs. Dust uniswap pool at $0.01851 (liq $1.30) excluded."
    ),
    "gate_distances_pct": {
        "0.012": -32.32,
        "0.025": 41.01,
        "0.032": 80.49,
        "0.041": 131.27,
    },
}

tmp = P + ".tmp"
with open(tmp, "w") as f:
    json.dump(st, f, indent=2, ensure_ascii=False)
json.load(open(tmp))  # validate
os.replace(tmp, P)
print("state ok, ath", st["ath"]["price_usd"], "new_ath", new_ath)
print("targets", {k: v["hit_at"] for k, v in st["targets"].items()})

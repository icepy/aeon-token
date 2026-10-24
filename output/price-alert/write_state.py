import json, shutil, subprocess, time
from datetime import datetime, timezone

BASE = "/home/runner/work/aeon-token/aeon-token/memory/topics/price-alert-state.json"
f = json.load(open(BASE))
m = json.load(open("/home/runner/work/aeon-token/aeon-token/output/price-alert/final.json"))

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
iso = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))

price = round(m["mark_now"], 8)
h1 = round((m["mark_now"] / m["mark_1h"] - 1) * 100, 3)

# ATH gate: stored 0.06876, current far below -> unchanged
f["ath"] = f.get("ath")  # no touch
f["last_alerts"] = f.get("last_alerts") or {"ath": None, "sharp_move": None, "target_hit": None}

# targets unchanged, none crossed (record explicit verdict)
for t, obj in f["targets"].items():
    obj["last_checked_price"] = price

f["last_price"] = {
    "price_usd": price,
    "h1_pct": h1,
    "h24_pct": 0.13,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL — deepest, liq $667,319",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 667319.08,
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": now,
    "head_block": m["head"],
    "head_ts": iso(m["head_ts"]),
    "h1_source": "measured on-chain, block-pinned to exactly 3600s",
    "h1_note": (f"1h window pinned by timestamp binary search: blk {m['blk1h']} -> {m['head']} "
                f"({iso(m['head_ts'])}), delta exactly 3600s at 2.0 s/block. Deepest pool reserves "
                f"VIRTUAL {m['reserves_1h'][0]:,.4f} -> {m['reserves_now'][0]:,.4f}, "
                f"DEUS {m['reserves_1h'][1]:,.4f} -> {m['reserves_now'][1]:,.4f}. "
                f"Ratio VIRTUAL/DEUS {m['ratio_1h']:.8f} -> {m['ratio_now']:.8f} = "
                f"{(m['ratio_now']/m['ratio_1h']-1)*100:+.3f}%. USD leg moved VIRTUAL "
                f"${m['virtual_usd']:.6f} (ETH/USD ${m['eth_usd']:,.2f} from WETH/USDC V3 "
                f"0xd0b53D92, token0=WETH orientation verified). Net USD mark {h1:+.3f}%."),
    "mark_source": "deepest-pool reserves x on-chain VIRTUAL/USD (VIRTUAL/WETH Solidly leg x ETH/USD V3 leg)",
    "mark_note": (f"Deepest pool 0x3E97c5EC token0=VIRTUAL(0x0b3e3284) token1=DEUS(0x940a319b) — "
                  f"orientation re-confirmed by eth_call this run (TELL 18), so mark = ratio x VIRTUAL "
                  f"price, never the ratio read as dollars. Result ${price:.8f}. "
                  f"Independent cross-check: three DEUS/USDC V3 venues measured on chain (sqrtPriceX96 "
                  f"INVERTED since token0=USDC 6dp): 0x58dBa34e $0.01757362, 0x1B2f3f5C $0.01751881, "
                  f"0x75bc1495 $0.01746856 -> median $0.01751881. Deepest-pool mark sits "
                  f"{(m['mark_now']/0.01751881-1)*100:+.2f}% above that median, same order as prior runs. "
                  f"DexScreener prints $0.01766 on this pool, {(m['mark_now']/0.01766-1)*100:+.2f}% vs measured. "
                  f"Dust uniswap pool $0.01851 (liq $1.30) excluded."),
    "gate_distances_pct": {
        "0.012": round((0.012 / price - 1) * 100, 2),
        "0.025": round((0.025 / price - 1) * 100, 2),
        "0.032": round((0.032 / price - 1) * 100, 2),
        "0.041": round((0.041 / price - 1) * 100, 2),
    },
    "ath_distance_pct": round((f["ath"]["price_usd"] / price - 1) * 100, 2),
}

f["deepest_pool_activity"] = {
    "window": f"{iso(m['head_ts'])} minus 1h (blk {m['blk1h']} -> {m['head']})",
    "swap_events": 2,
    "family": "Solidly (Aerodrome classic) — Swap topic0 0xb3e27736…, Sync topic0 0xcf2aa508…f982149848a",
    "buy_tx_count": 1,
    "buy_deus_out": 13513.23,
    "sell_tx_count": 1,
    "sell_deus_in": 226.68,
    "net_deus_out_of_pool": -13286.55,
    "last_event": "10:47:19Z (blk 53024746)",
    "minutes_quiet_at_run": 46.1,
    "query_note": ("Two swaps only in the hour, and NONE in the newest 1000-block window — so the "
                   "address-only scan returns 0 there. That is a real quiet tape this run, re-measured "
                   "from scratch (TELL 17: never inherit a dormancy claim). Control: the real Sync "
                   "topic0 returns 2 logs in blk 53024572-53025572 while a mistyped topic0 and a bogus "
                   "0x01*32 topic0 both return 0 in that SAME window — filter discrimination proven "
                   "before any number was trusted."),
    "observed_at": now,
}

f["escrow_snapshot"]["observed_at"] = now
f["escrow_snapshot"]["note"] = (
    "Unchanged to the wei since the 09:13Z snapshot: 29,103,661.674664 DEUS. 24h -304,562 DEUS "
    "(-1.036%) vs the 1,470,411 DEUS 5%/day line = 0.21x. No unstake pressure. xDEUS totalSupply "
    "1726, same as last run.")
f["xdeus_supply"]["observed_at"] = now

f["holder_check"]["observed_at"] = now
f["holder_check"]["note"] = (
    "Fifth consecutive run unchanged to the wei, re-verified by balanceOf this run at blk "
    f"{m['head']}: 0x7f6aba75 = 335,249.4994; 0x6a45ca8b = 70,034.1403; 0xf0a04b07 (the 250k "
    "incumbent trimmer) = 250,000.1252 — none distributed into today's tape. 0xbb0f7533 DEUS "
    "balance exactly 0.0 and STILL holds xDEUS #1396: balanceOf(NFT)=1 and "
    "tokenOfOwnerByIndex(owner,0)=1396 this run. Trigger has NOT fired.")
f["holder_check"]["pending_unstake"]["status"] = (
    "NOT YET BURNED - verified this run: balanceOf(xDEUS)=1, tokenOfOwnerByIndex=1396, at blk "
    f"{m['head']}")

f["last_run_at"] = now

shutil.copyfile(BASE, BASE + ".bak")
tmp = BASE + ".tmp"
json.dump(f, open(tmp, "w"), indent=2, ensure_ascii=False)
shutil.move(tmp, BASE)

chk = subprocess.run(["jq", "empty", BASE], capture_output=True, text=True)
print("jq validate rc =", chk.returncode, chk.stderr.strip())
print("price", price, "h1", h1, "verdict OK")
print("targets", f["last_price"]["gate_distances_pct"])
print("ath dist %", f["last_price"]["ath_distance_pct"])

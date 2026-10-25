import json
from decimal import Decimal, getcontext

getcontext().prec = 40
p = "memory/topics/price-alert-state.json"
d = json.load(open(p))

NOW = "2026-10-25T07:01:57Z"
MARK = 0.017085918697330078
H1 = -0.5227
H24 = -4.6285
RATIO = 0.027669824923521186
VUSD = 0.6174928372172647

d["last_run_at"] = NOW
d["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
d["chain"] = "base"

# ATH unchanged (mark far below 0.06876)
d["ath"]["last_verdict"] = "UNCHANGED"

# targets: no cross, refresh distance bookkeeping
dist = {"0.012": -29.77, "0.025": 46.32, "0.032": 87.29, "0.041": 139.96}
for k, t in d["targets"].items():
    t["last_checked_price"] = MARK
    t["last_checked_at"] = NOW
    t["distance_pct"] = dist[k]

d["last_price"] = {
    "price_usd": MARK,
    "h1_pct": H1,
    "h24_pct": H24,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL - deepest, liq $656,534",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": 53061213,
    "head_ts": "2026-10-25T07:01:57Z",
    "h1_source": "MEASURED ON-CHAIN. DexScreener returned h1=null on the deepest pair for the FOURTH consecutive run (null on 4 of 5 Base pairs again). Deep pool blockTimestampLast STILL 1792900663 = 03:57:43Z; reserves at blk 53059413 and blk 53061213 BYTE-IDENTICAL (VIRTUAL 524920.7065395488 / DEUS 18970871.987459935). So the whole h1 came from the QUOTE LEG: VIRTUAL/USD 0.6207373 -> 0.6174928 = -0.523%. Same tell as the prior three runs.",
    "mark_source": "Deepest-pool reserves at blk 53061213: VIRTUAL 524920.706539548794602224 / DEUS 18970871.987459934948375054 (token0=VIRTUAL 0x0b3e3284 18dp, token1=DEUS 0x940A319B 18dp). ratio 0.027669824923521186 x VIRTUAL/USD 0.6174928372 = $0.01708592. VIRTUAL/USD from VIRTUAL/USDC V3 pool 0x529d2863a1521d0b57db028168fdE2E97120017C slot0 word0 (sqrtPriceX96 62378429290283301000448 at head), correctly inverted for token0=VIRTUAL/18dp vs token1=USDC/6dp. DexScreener prints $0.01730 on the same pair = +1.25% spread, still API ABOVE on-chain - second run in a row in that direction.",
    "h24_note": "h24 -4.6285% over the EXACT 86400s window (blk 53018013 ts 1792825373 -> head blk 53061213 ts 1792911773; asserted ts(head)-ts(pin) == 86400). Legs: VIRTUAL/DEUS ratio 0.0280085435 -> 0.0276698249 = -1.209%; VIRTUAL/USD 0.6396303 -> 0.6174928 = -3.461%; the two COMPOUND to -4.628%. Do NOT add the legs.",
    "gate_distances_pct": dist,
    "ath_distance_pct": 302.44,
    "api_vs_chain_spread_pct": 1.253,
}

d["gate_results"] = {
    "observed_at": NOW,
    "ath": {"verdict": "UNCHANGED", "prior": 0.06876, "current": MARK, "distance_pct": 302.44},
    "sharp_move": {"verdict": "QUIET", "h1_pct": H1, "threshold_pct": 20,
                   "note": "链上实测。DexScreener 深池 h1 第四次为 null。1h -0.5227% 100% 来自 VIRTUAL 引腿（0.6207373 -> 0.6174928），深池储备逐 wei 未动。距 20% 门槛 38x。"},
    "targets": {"0.012": "NO_CROSS", "0.025": "NO_CROSS", "0.032": "NO_CROSS", "0.041": "NO_CROSS"},
    "run_verdict": "OK",
    "notifications_sent": 0,
}

d["level_math"] = {
    "method": "constant-product x*y=k on deepest-pool reserves at head blk 53061213, zero fees, no other flow. D_new = sqrt(k / r_t), r_t = target_usd / virtual_usd.",
    "observed_at": NOW,
    "reserves": {"virtual": 524920.7065395488, "deus": 18970871.987459935,
                 "mark_usd": MARK, "virtual_usd": VUSD},
    "to_0_012": {"action": "net SELL into pool", "deus_needed": 3665970, "usd_needed": 62636, "pct_of_pool_deus": 19.3},
    "to_0_025": {"action": "net BUY out of pool", "deus_needed": -3287608, "usd_needed": -56172, "pct_of_pool_deus": -17.3},
    "to_0_032": {"action": "net BUY out of pool", "deus_needed": -5108694, "usd_needed": -87287, "pct_of_pool_deus": -26.9},
    "to_0_041": {"action": "net BUY out of pool", "deus_needed": -6724300, "usd_needed": -114891,
                 "pct_of_pool_deus": -35.4, "mult_of_24h_volume": 8.23},
    "units_warning": "Every multiple here is quoted with its unit stated. Do NOT compare a DEUS quantity against a USD figure - that produced the 424x error that stood in state for four runs (true value ~8x).",
}

d["deepest_pool_activity_07z"] = {
    "observed_at": NOW,
    "window": "blk 53059413..53061213 (06:01:57Z .. 07:01:57Z, exact 3600s)",
    "swap_events": 0,
    "family": "Solidly (Aerodrome classic) topic0 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b",
    "blockTimestampLast": 1792900663,
    "last_swap_ts": "2026-10-25T03:57:43Z",
    "silence_minutes": 185.2,
    "reserves_byte_identical_1h": True,
    "control": "Discriminative control PASSED twice: blk 53055658 returns exactly 1 Solidly Swap; same block with topic0's final char flipped returns 0. Hour window scanned 999-block chunked, zero failed chunks.",
    "read": "The 03:57:43Z sell remains the pool's LAST print - now 185.2 minutes, a NEW RECORD dormancy for this pool and the 7th recorded stretch. The three-hour-and-five-minute tape is one sell and nothing else. Positive control fires, so the zero is real.",
}

d["usdc_venues_07z"] = {
    "observed_at": NOW,
    "window": "blk 53059413..53061213, exact 3600s",
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": "3 swaps, dust: blk 53059767 sold 0.0575 DEUS for 0.000992 USDC; blk 53060537 sold 0.0580 for 0.001; blk 53060684 sold 0.0580 for 0.001. All three are SUB-DOLLAR prints.",
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": "0 swaps",
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": "0 swaps",
    "net_deus_into_pools": 0.1736,
    "read": "The two-sided hour of 05Z-06Z did not repeat. This hour is three sub-dollar dust sells totalling 0.17 DEUS - i.e. the entire DEUS market on Base printed ~$0.003 of notional in 60 minutes. Compare: yesterday at this scale the pool did 84,920 DEUS/hour. This is not 'calm', it is an empty book.",
}

d["inventory_watch_07z"] = {
    "observed_at": NOW,
    "address": "0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f",
    "deus_balance_now": 118288.59401582144,
    "deus_balance_06z": 118288.59401582144,
    "delta_1h": 0.0,
    "read": "STILL NOT RE-OFFERED, third consecutive hour byte-identical. This contract dumped 101,983 DEUS on 10-24 15:53Z and has sat on 118,288.59 since. Armed, not fired.",
}

d["supply_side_07z"] = {
    "observed_at": NOW,
    "head_block": 53061213,
    "escrow_deus": 29150566.777697522,
    "escrow_24h_ago_deus": 29108661.674663614,
    "escrow_24h_delta_deus": 41905.10303390771,
    "escrow_24h_delta_pct": 0.144,
    "five_pct_line_deus": 1455433.08,
    "pressure_ratio": 0.0288,
    "escrow_events_1h": {"burns": 0, "stakes": 0},
    "escrow_24h_events": "reconciles to the wei: -5,000.00 (burn #425 @53020218) + 46,905.103034 (stakes 10,905.103034 #2c81beef @53031263 + 36,000 #e338adc6 @53040973) = +41,905.103034, matching the measured delta. ELEVENTH consecutive clean reconciliation. Scanned in 999-block chunks; all 44 chunks returned.",
    "pending_unstake": {
        "wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
        "xdeus_nft_id": 1396,
        "status": "NOT YET BURNED - TWELFTH consecutive run",
        "verified": "balanceOf(xDEUS 0xe6d5f7439Bc236C40054e2275f765f59343D4431) = 1, tokenOfOwnerByIndex(owner,0) = 0x574 = 1396, at head blk 53061213; DEUS balance 0.000000",
    },
    "claim_main_vault_deus": 339761852.1871878,
    "claim_24h_ago_deus": 340082395.4104776,
    "claim_net_out_24h_deus": 320543.22,
    "claim_1h_delta_deus": -945.41,
    "claim_pct_of_supply": 38.78,
    "deus_total_supply": 876177627.813275,
    "deus_total_supply_24h_ago": 876190001.500193,
    "deus_supply_24h_delta": -12373.686918,
    "xdeus_total_supply": 1728,
    "xdeus_24h_ago": 1727,
    "xdeus_24h_delta": 1,
    "read": "Escrow byte-identical for the FIFTH consecutive run; zero events in the hour. 24h drain is net INFLOW +41,905 = 0.029x the 5%/day line. CLAIM main vault paid out 320,543 in 24h at 38.78% of supply, in line with the 30d average. Total supply -12,373.69 over 24h and BYTE-IDENTICAL hour-on-hour to the last four reads - deflation is flat, not accelerating. The $0.041 exit still has NO 5-day clock running: #1396 unburned for the twelfth run (~2.9 days).",
}

d["holder_check_07z"] = {
    "observed_at": NOW,
    "holders": {
        "0x4e3ae00e8323558fa5cac04b152238924aa31b60": {"now": 8070712.226758934,
            "read": "8.07M wholesaler, BYTE-IDENTICAL to the 06:09Z read. Did not sell this hour. Still the sell-side pace-setter at ~56k/day."},
        "0x9d1c316f1f307894c80e7d2963454e6342c8e0a9": {"now": 284371.45782997005,
            "read": "UNCHANGED - the 10-24 17:29Z buyer still holds all 115,643 bought. Fourth consecutive hold hour."},
        "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63": {"deus": 0.0, "xdeus_nfts": 1,
            "read": "pending #1396 unburned."},
    },
    "sink_0x92325e5a": {"now": 118288.59401582144, "read": "inventory unchanged, see inventory_watch_07z."},
    "read": "Nothing moved on the holder side for a second hour. Both watched holders byte-identical.",
}

json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
print("written")

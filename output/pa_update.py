import json, shutil, os

P = "memory/topics/price-alert-state.json"
BAK = P + ".bak"
shutil.copyfile(P, BAK)

with open(P) as f:
    s = json.load(f)

NOW = "2026-10-25T06:09:01Z"
mark = 0.01715617053592281
h1 = -0.996456326866213
h24 = -4.236354759011407

s["last_run_at"] = NOW
s["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
s["chain"] = "base"

# ATH unchanged (0.06876, far above mark)
s["ath"]["last_verdict"] = "UNCHANGED"

# gates
s["gate_results"] = {
    "observed_at": NOW,
    "ath": {"verdict": "UNCHANGED", "prior": 0.06876, "current": mark, "distance_pct": 300.79},
    "sharp_move": {
        "verdict": "QUIET", "h1_pct": round(h1, 3), "threshold_pct": 20,
        "note": "链上实测。DexScreener 深池 h1 再次为 null。1h -0.996% 100% 来自 VIRTUAL 引腿（VIRTUAL/USD 0.6262723 -> 0.6200318 = -0.996%），深池储备逐 wei 未动、blockTimestampLast 仍 03:57:43Z。距 20% 门槛 20x。"
    },
    "targets": {"0.012": "NO_CROSS", "0.025": "NO_CROSS", "0.032": "NO_CROSS", "0.041": "NO_CROSS"},
    "run_verdict": "OK",
    "notifications_sent": 0,
}

for k, d in [("0.012", -30.05), ("0.025", 45.72), ("0.032", 86.52), ("0.041", 138.98)]:
    t = s["targets"][k]
    t["last_checked_price"] = mark
    t["last_checked_at"] = NOW
    t["distance_pct"] = d

s["last_price"] = {
    "price_usd": mark,
    "h1_pct": round(h1, 3),
    "h24_pct": round(h24, 3),
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL - deepest, liq $656,534",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": 53059597,
    "head_ts": "2026-10-25T06:09:01Z",
    "h1_source": "MEASURED ON-CHAIN. DexScreener returned h1=null on the deepest pair for the THIRD consecutive run (null on 4 of 5 Base pairs this time). Pool blockTimestampLast STILL 1792900663 = 03:57:43Z; reserves at blk 53057797 and blk 53059597 BYTE-IDENTICAL. So the whole -0.996% is the QUOTE LEG: VIRTUAL/USD 0.6262723 -> 0.6200318. TELL 11 again: an API null is not a flat tape, and a flat RATIO is not a flat USD mark.",
    "mark_source": "Deepest-pool reserves at blk 53059597: VIRTUAL 524920.7065395488 / DEUS 18970871.987459935 (token0=VIRTUAL 0x0b3e3284 18dp, token1=DEUS 0x940A319B 18dp). ratio 0.0276698249 x VIRTUAL/USD 0.6200318 = $0.01715617. VIRTUAL/USD from VIRTUAL/USDC V3 pool 0x529d2863a1521d0b57db028168fdE2E97120017C slot0 word0 (sqrtPriceX96 62421401283812501687483 at head), correctly inverted for token0=VIRTUAL/18dp vs token1=USDC/6dp. DexScreener prints $0.01730 on the same pair = +0.84% spread, WIDEST on record in the other direction (API mark now ABOVE the on-chain mark).",
    "h24_note": "h24 -4.236% over the EXACT 86400s window (blk 53016397 ts 1792822141 -> head blk 53059597 ts 1792908541; asserted ts(head)-ts(pin) == 86400). Legs: VIRTUAL/DEUS ratio 0.0280085435 -> 0.0276698249 = -1.209%; VIRTUAL/USD 0.6396305 -> 0.6200318 = -3.064%; the two COMPOUND to -4.236%. Do NOT add the legs - the ratio leg and the DEUS-in-pool leg are the same event counted twice.",
    "gate_distances_pct": {"0.012": -30.05, "0.025": 45.72, "0.032": 86.52, "0.041": 138.98},
    "ath_distance_pct": 300.79,
}

s["deepest_pool_activity_06z"] = {
    "observed_at": NOW,
    "window": "blk 53057798..53059597 (05:09:01Z .. 06:09:01Z, exact 3600s)",
    "swap_events": 0,
    "family": "Solidly (Aerodrome classic) topic0 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b",
    "blockTimestampLast": 1792900663,
    "last_swap_ts": "2026-10-25T03:57:43Z",
    "silence_minutes": 131.3,
    "reserves_byte_identical_1h": True,
    "control": "Discriminative control PASSED: blk 53055658 returns exactly 1 Solidly Swap; same block with topic0's final char flipped returns 0. Both scans 999-block chunked, zero failed chunks.",
    "read": "The 03:57:43Z sell remains the pool's LAST print - now 131.3 minutes of silence, the LONGEST dormancy of the day and the 6th recorded stretch. Confidence high: positive control fires. Note the whole hour's USD move came from VIRTUAL, not from this pool.",
}

s["usdc_venues_06z"] = {
    "observed_at": NOW,
    "window": "blk 53057798..53059597, exact 3600s",
    "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": "4 swaps, all chunked-scanned clean: 03:59:47Z BUY 2,709.29 DEUS for 46.387 USDC (impl $0.017121); 04:12:47Z SELL 0.058 DEUS for 0.001; 04:16:17Z SELL 0.058 DEUS for 0.001; 04:25:19Z SELL 2,322.79 DEUS for 40.000 USDC (impl $0.017221).",
    "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": "0 swaps",
    "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": "0 swaps",
    "net_deus_into_pools": 385.4,
    "read": "This hour moved from near-zero to REAL two-sided flow on the main USDC venue: one 2,709 DEUS buy early and one 2,323 DEUS sell late, plus two dust prints. Net DEUS into pools only +385, i.e. balanced. Two big prints roughly cancel - this is NOT directional. Implied exec prices $0.01712-$0.01722 bracket the on-chain mark $0.017156, so the venues agree.",
}

s["supply_side_06z"] = {
    "observed_at": NOW,
    "head_block": 53059597,
    "escrow_deus": 29150566.777697522,
    "escrow_24h_ago_deus": 29108661.674663614,
    "escrow_24h_delta_deus": 41905.10303390771,
    "escrow_24h_delta_pct": 0.144,
    "five_pct_line_deus": 1455433.08,
    "pressure_ratio": 0.0288,
    "escrow_events_1h": {"burns": 0, "stakes": 0},
    "escrow_24h_events": "reconciles to the wei: -5,000.00 (burn #425) + 46,905.103034 (stakes 10,905.103034 #2c81beef + 36,000 #e338adc6) = -5,000 + 46,905.103034 vs measured +41,905.103034. TENTH consecutive clean wei-level reconciliation.",
    "escrow_method_note": "The first escrow scan this run returned 0 burns / 0 stakes with '-32602 invalid params' swallowed - the 24h range exceeds the public 1000-block eth_getLogs cap. Re-scanned in 44 chunks of 999; all chunks returned and found 1 burn + 2 stakes. THE false-zero trap (tell from lessons) fired again and was caught by checking errors rather than trusting the [].",
    "pending_unstake": {
        "wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
        "xdeus_nft_id": 1396,
        "status": "NOT YET BURNED - ELEVENTH consecutive run",
        "verified": "balanceOf(xDEUS 0xe6d5f7439Bc236C40054e2275f765f59343D4431) = 1, tokenOfOwnerByIndex(owner,0) = 1396, at head blk 53059597",
    },
    "claim_main_vault_deus": 339762797.5981475,
    "claim_24h_ago_deus": 340083367.9090547,
    "claim_net_out_24h_deus": 320570.31,
    "claim_1h_delta_deus": -5820.05,
    "claim_pct_of_supply": 38.78,
    "deus_total_supply": 876177627.813275,
    "deus_total_supply_24h_ago": 876190001.500193,
    "deus_supply_24h_delta": -12373.686918020248,
    "deus_supply_1h_delta": 0.0,
    "xdeus_total_supply": 1728,
    "xdeus_24h_ago": 1727,
    "read": "Escrow BYTE-IDENTICAL for a fourth consecutive run; 24h still net +41,905.10 = 0.029x the 5%/day line, zero events this hour. Total supply -12,373.69 over 24h - THE SAME FIGURE for a FOURTH consecutive run (876,177,627.813275 exactly, zero change in the hour) - 13th consecutive net-deflation read, dead flat. The pending #1396 trigger is now armed and unfired for ELEVEN consecutive runs (~2.8 days). The 5-day unstake clock for any $0.041 exit has still not started.",
}

s["inventory_watch_06z"] = {
    "observed_at": NOW,
    "address": "0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f",
    "deus_balance_now": 118288.59401582144,
    "deus_balance_05z": 118288.59401582144,
    "delta_1h": 0.0,
    "read": "STILL NOT RE-OFFERED, second consecutive hour byte-identical. This contract dumped 101,983 DEUS on 10-24 15:53Z and has sat on 118,288.59 since. Unchanged is itself the signal: the bearish trigger is still armed, not fired.",
}

s["holder_check_06z"] = {
    "observed_at": NOW,
    "holders": {
        "0x4e3ae00e8323558fa5cac04b152238924aa31b60": {"now": 8070712.226758934, "read": "8.07M wholesaler, BYTE-IDENTICAL to the 05:01Z read - it did not sell this hour. Still the sell-side pace-setter at ~56k/day."},
        "0x9d1c316f1f307894c80e7d2963454e6342c8e0a9": {"now": 284371.45782997005, "read": "UNCHANGED - the 10-24 17:29Z buyer still holds all 115,643 bought. No distribution leg, third consecutive hold hour."},
        "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63": {"deus": 0.0, "xdeus_nfts": 1, "read": "pending #1396 unburned."},
    },
    "read": "Nothing moved on the holder side this hour. Both watched holders byte-identical.",
}

s["level_math"] = {
    "method": "constant-product x*y=k on deepest-pool reserves at head blk 53059597, zero fees, no other flow. D_new = sqrt(k / r_t), r_t = target_usd / virtual_usd.",
    "observed_at": NOW,
    "reserves": {"virtual": 524920.7065395488, "deus": 18970871.987459935, "mark_usd": mark, "virtual_usd": 0.6200317704698929},
    "to_0_012": {"action": "net SELL into pool", "deus_needed": 3712460, "usd_needed": 63692, "pct_of_pool_deus": 19.6, "mult_of_101k_dump": 36.1, "days_of_full_claim_drip": 11.2},
    "to_0_025": {"action": "net BUY out of pool", "deus_needed": -3255399, "usd_needed": -55850, "pct_of_pool_deus": -17.2},
    "to_0_032": {"action": "net BUY out of pool", "deus_needed": -5080225, "usd_needed": -87157, "pct_of_pool_deus": -26.8},
    "to_0_041": {"action": "net BUY out of pool", "deus_needed": -6699149, "usd_needed": -114932, "pct_of_pool_deus": -35.3, "mult_of_24h_volume": 8.2},
    "units_warning": "Every multiple here is quoted with its unit stated. Do NOT compare a DEUS quantity against a USD figure - that produced the 424x error that stood in state for four runs (true value ~8x).",
}

with open(P, "w") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)

with open(P) as f:
    json.load(f)
print("state written and re-parsed OK; keys:", len(s))

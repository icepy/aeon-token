import json, os, shutil

P = "/home/runner/work/aeon-token/aeon-token/memory/topics/price-alert-state.json"
BAK = P + ".bak"

with open(P) as f:
    st = json.load(f)

shutil.copyfile(P, BAK)

mark = 0.01735651487005396
ratio = 0.027883145675288927
vusd = 0.6224733418595573
DEUS = 18898164.07523058
VIRT = 526940.2619051661
NOW = "2026-10-24T19:01:51Z"
HEAD = 53039582
H1 = 53037782
H24 = 52996382

st["last_run_at"] = NOW
st["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
st["chain"] = "base"

# ATH unchanged: 0.06876 far above mark
st["ath"]["last_verdict"] = "UNCHANGED"

# last_alerts untouched - no gate fired
st["last_price"] = {
    "price_usd": mark,
    "h1_pct": 0.951,
    "h24_pct": -3.798,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL - deepest, liq $651,793",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 651793.29,
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": HEAD,
    "head_ts": NOW,
    "h1_source": "On-chain exact 3600s window blk 53037782 (18:01:51Z) -> 53039582 (19:01:51Z), both timestamps read from eth_getBlockByNumber. Decomposition: VIRTUAL/USD +1.133% is the ENTIRE h1 move; DEUS/VIRTUAL ratio actually FELL -0.180%. Mark +0.951%.",
    "h1_note": "OPPOSITE COMPOSITION FROM THE PRIOR RUN. Last hour the ratio rose and VIRTUAL fell; this hour VIRTUAL rebounded +1.13% while DEUS LOST ground against it. All 9 swaps in the deepest pool were SELLS (17,151.36 DEUS in, ZERO buys out) yet the USD mark still rose, purely on the quote-token leg. The sellers were arb: 767.22 DEUS arrived FROM the USDC V3 pool 0x58dBa34e and 5,500.00 from 0xeb7c90d3 (which dropped from 49,010.87 to 43,510.87). No directional distribution.",
    "mark_source": "deepest-pool reserves x VIRTUAL/USD. Reserves blk 53039582: VIRTUAL 526,940.2619 / DEUS 18,898,164.0752 (token0=VIRTUAL verified via 0x0dfe1681, token1=DEUS via 0xd21220a7, both 18dp). ratio 0.027883146 x $0.6224733 = $0.0173565.",
    "mark_note": "THREE-VENUE SPREAD HAS NARROWED AND INVERTED. My deepest-pool mark $0.0173565 now sits ABOVE all three USDC V3 venues (median $0.0171633, range $0.0171491-$0.0171683) - a +1.12% PREMIUM, where the prior run had the deepest pool at a -0.42% DISCOUNT. That inversion IS the arb that produced all 9 sells this hour: the deepest pool got bid up, USDC venues did not follow, so arbs sold into it. DexScreener prints $0.01724 (-0.67% vs mine) and USDC venues say $0.01716. My mark is the outlier this hour - treat $0.01716-$0.01736 as the honest band, and do NOT quote the deepest-pool number as consensus.",
    "gate_distances_pct": {"0.012": -30.86, "0.025": 44.04, "0.032": 84.37, "0.041": 136.22},
    "ath_distance_pct": -74.75,
    "h24_note": "h24 -3.798%, block-pinned to exactly 86400s (blk 52996382 2026-10-23T19:01:51Z -> 53039582). Decomposition REVERSES the prior three runs: VIRTUAL -5.482% and DEUS/VIRTUAL ratio +1.782%. Fourth consecutive run where DEUS outperforms its quote token - but this is the first where the ratio gain was EATEN by the leg falling less than before. Net DEUS LEFT the deepest pool over 24h: -167,609.",
}

# targets: refresh checked price/distance, no hits
for t, dist in [("0.012", -30.86), ("0.025", 44.04), ("0.032", 84.37), ("0.041", 136.22)]:
    tg = st["targets"][t]
    tg["last_checked_price"] = mark
    tg["last_checked_at"] = NOW
    tg["distance_pct"] = dist

st["deepest_pool_activity"] = {
    "window": "blk 53037783 -> 53039582 (18:01:51Z .. 19:01:51Z, exactly 3600s, both timestamps read)",
    "swap_events": 9,
    "family": "Solidly (Aerodrome classic) - Swap topic0 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b (full 64-hex, verified)",
    "buy_tx_count": 0,
    "buy_deus_out": 0.0,
    "sell_tx_count": 9,
    "sell_deus_in": 17151.3625,
    "net_deus_into_pool": 17151.3625,
    "largest_sell_deus": 6414.0068,
    "largest_buy_deus": 0.0,
    "control_note": "Word-order resolved EMPIRICALLY, not inherited: the 5,500 DEUS swap declared words [0, 5500.0, 152.048, 0] and the reserve delta was exactly dD +5,445.00 / dV -152.048 (the 55 gap is the 1% Aerodrome fee to 0x205db642). That fixes the layout as (amount0In, amount1In, amount0Out, amount1Out) for this pool. Prior-run notes were NOT trusted on this point.",
    "observed_at": NOW,
    "read": "NINE SELLS, ZERO BUYS - and the sellers are arbitrage, not distribution. Evidence: (a) the 767.22 DEUS leg ARRIVED from the USDC V3 pool 0x58dBa34e in the same tx, i.e. bought cheap there and sold here - textbook two-leg arb closing a premium; (b) 5,500.00 came from 0xeb7c90d3, whose balance fell 49,010.87 -> 43,510.87 (a holder trimming, but that address was ALSO a buy-side sink on prior runs); (c) five of the nine route to known arb sinks 0xae629bf1, 0x29be31e7, 0x4623be8e, 0x1231deb6. The premium that invited them (+1.12% over USDC venues) is now the thing to watch - as it closes, the sells stop. This is NOT the directional-distribution pattern (tell #21).",
}

st["buyer_0x9d1c316f"]["check_latest"] = {
    "observed_at": NOW,
    "deus_balance_now": 284371.45782997005,
    "deus_balance_1h_ago": 284371.45782997005,
    "note": "UNCHANGED - the 115,643 DEUS bought last hour is still held, byte-identical. No distribution leg. Tell #8 holder still intact.",
}

st["holder_check"] = {
    "observed_at": NOW,
    "note": "Re-verified at correct addresses this run (an earlier probe used mistyped addresses and returned false zeros - discarded, not reported). 0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3 = 335,249.499443 (unchanged 1h). 0x6a45ca8bb30f396f40721e105e0aa6cabf326657 = 70,034.140337 (unchanged 1h). 0xbb0f7533 DEUS = 0.000000 and STILL holds xDEUS #1396 (balanceOf=1, tokenOfOwnerByIndex(0)=1396) - trigger NOT fired.",
    "pending_unstake": {
        "wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
        "xdeus_nft_id": 1396,
        "status": "NOT YET BURNED - re-verified at latest",
    },
}

st["escrow_snapshot"]["balance_deus"] = 29114566.777697522
st["escrow_snapshot"]["prior_balance_deus"] = 29114566.777697522
st["escrow_snapshot"]["change_deus"] = 0.0
st["escrow_snapshot"]["change_pct"] = 0.0
st["escrow_snapshot"]["balance_24h_ago"] = 29408223.901194375
st["escrow_snapshot"]["change_24h_deus"] = -293657.123496848
st["escrow_snapshot"]["change_24h_pct"] = -0.999
st["escrow_snapshot"]["observed_at"] = NOW
st["escrow_snapshot"]["note"] = (
    "RE-MEASURED at both ends. Escrow BYTE-IDENTICAL to the prior run (29,114,566.777697522, delta 0 wei) - "
    "second consecutive hour with no stake, burn, or unstake. The 24h delta -293,657.1235 still closes to the wei "
    "against the enumerated events (2 burns / 2 stakes) recorded earlier. 5%/day line 1,455,728 = 0.202x the 24h drain, "
    "no unstake pressure."
)
st["escrow_snapshot"]["xdeus_supply_now"] = 1727
st["xdeus_supply"]["total_supply"] = 1727
st["xdeus_supply"]["change_24h"] = 1
st["xdeus_supply"]["observed_at"] = NOW
st["xdeus_supply"]["note"] = (
    "1727, flat for the second hour. 1726 at the 24h block = net +1 NFT on the day. 0xbb0f7533 STILL holds #1396."
)

st["deus_total_supply"]["total_supply"] = 876177627.813275
st["deus_total_supply"]["change_24h"] = -14655.43
st["deus_total_supply"]["observed_at"] = NOW
st["deus_total_supply"]["note"] = (
    "876,177,627.81 now vs 876,192,366.96 at the exact-86400s block = -14,655.43 DEUS over 24h. "
    "Seventh consecutive net-deflation read and the SMALLEST yet (-19,693, -38,770 x3, -21,169, now -14,655): "
    "deflation is real but decelerating toward flat. The 7d +65,381 net-inflation label remains stale."
)

st["claim_snapshot"]["balance_deus"] = 339941815.16364664
st["claim_snapshot"]["prior_balance_deus"] = 339942896.54382306
st["claim_snapshot"]["change_deus"] = -1081.38017694
st["claim_snapshot"]["net_out_24h_deus"] = 210723.3404932618
st["claim_snapshot"]["observed_at"] = NOW
st["claim_snapshot"]["note"] = (
    "RE-MEASURED both ends. Main vault 339,941,815.16, down 1,081.38 DEUS in the hour. 24h net-out 210,723.34 on a "
    "fresh exact-86400s window - SLOWER than the prior run's 269,767 and well under the 30d average 332,962/day. "
    "The drip is decelerating, not accelerating. 38.8%-of-supply overhang unchanged."
)

st["level_math"] = {
    "method": "constant-product x*y=k on deepest-pool reserves at blk 53039582, zero fees, no other flow. Solved in RATIO space (target/VIRTUAL_price) so the VIRTUAL leg need not be held constant: D_needed = D*(sqrt(r_cur/r_target)-1).",
    "reserves": {"virtual": VIRT, "deus": DEUS, "mark_usd": mark, "virtual_usd": vusd},
    "to_0.012": {
        "action": "net SELL",
        "deus_needed": 3829785,
        "usd_needed": 66472,
        "mult_of_101k_dump": 37.55,
        "note": "Needs 37.6x today's biggest single dump (101,983 DEUS). GREW from 3.72M because the pool got shallower in DEUS terms off the 24h net outflow. Still a deliberate multi-actor liquidation, not emission drift.",
    },
    "to_0.025": {"action": "net BUY", "deus_needed": 3151779, "usd_needed": 54704, "note": "Marginally cheaper than the prior 3.22M."},
    "to_0.032": {"action": "net BUY", "deus_needed": 4980194, "usd_needed": 86439},
    "to_0.041": {
        "action": "net BUY",
        "deus_needed": 6602303,
        "usd_needed": 114593,
        "note": "Still ~240x the deepest pool's 24h volume. $0.041 is only reachable by supply WITHDRAWAL from the book, not by buying - unchanged conclusion, and the reason the 5-day unstake lead time is the whole point.",
    },
}

st["venue_spread"] = {
    "observed_at": NOW,
    "deepest_pool_mark": mark,
    "usdc_v3_median": 0.01716328,
    "usdc_v3_venues": {
        "0x58dBa34e": 0.01716830,
        "0x75bc1495": 0.01716328,
        "0x1B2f3f5C": 0.01714912,
    },
    "dexscreener": 0.01724,
    "premium_pct": 1.125,
    "note": "The deepest pool now trades at a PREMIUM to all three USDC venues (+1.12%), the inverse of the prior run's discount. That spread is the arb that drove all 9 sells. Prior runs used the deepest pool as the canonical mark because it was the deepest AND mid-band; this hour it is the top of the distribution. Report the band, not a single number.",
}

with open(P, "w") as f:
    json.dump(st, f, indent=2)
    f.write("\n")

with open(P) as f:
    json.load(f)
print("state written and re-parsed OK")
print("bytes", os.path.getsize(P))

import json, shutil, os

P = "memory/topics/price-alert-state.json"
BAK = P + ".bak"
shutil.copyfile(P, BAK)

s = json.load(open(P))

NOW = "2026-10-24T21:02:03Z"
HEAD = 53043188
MARK = 0.01738852
H1 = -0.1253
H24 = -3.5018
VUSD = 0.6241207
RATIO = 0.027860832
V_RES = 526729.374184701610846321
D_RES = 18905730.371963049965150019

s["last_run_at"] = NOW
s["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
s["chain"] = "base"

# ATH gate: prior 0.06876 >> current -> unchanged, no notify
s["ath"]["price_usd"] = 0.06876
s["ath"]["observed_at"] = "2026-05-28T15:35:00Z"
s["ath"]["announced_at"] = "2026-05-28T15:35:00Z"
s["ath"]["last_verdict"] = "UNCHANGED"

# no gate fired -> last_alerts untouched (all null)
s["last_alerts"] = {"ath": None, "sharp_move": None, "target_hit": None}

gp = lambda t: round(t / MARK * 100 - 100, 2)

lp = s["last_price"]
lp.update({
    "price_usd": MARK,
    "h1_pct": H1,
    "h24_pct": H24,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL - deepest, liq $653,327",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 653327.46,
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": HEAD,
    "head_ts": NOW,
    "h1_source": (
        "DexScreener returned REAL h1 this run (deepest pair +0.24%, 0x58dBa34e +0.09%, "
        "0x1B2f3f5C +0.17%, 0x75bc1495 null). Not inherited: cross-checked on-chain over exactly "
        "3600s, blk 53041388 (21:02:03Z-3600) -> 53043188, both timestamps read from "
        "eth_getBlockByNumber. Ratio 0.027869409 -> 0.027860832 = -0.0308%; VIRTUAL/USD "
        "0.6247116 -> 0.6241207 = -0.0946%; MARK $0.01741034 -> $0.01738852 = -0.1253%."
    ),
    "h1_note": (
        "TWO SWAPS, BOTH SELLS, BOTH ARB AGAIN - and both in the SAME block 53041913. "
        "2,938.71 DEUS in, zero buy legs, net +2,909.32 DEUS into the pool (2,938.71 minus the "
        "1% fee 29.39 = 2,909.32, matching the measured reserve delta exactly). Attribution from "
        "the DEUS Transfer legs: (1) 2,200.00 via router 0xeb7c90d3, sender 0x6abea499 - the same "
        "round-trip sink seen last run; (2) 738.71 arriving straight FROM USDC V3 pool 0x58dBa34e. "
        "Neither is distribution; both are cross-venue arb closing the deepest pool's premium. "
        "Only 2,939 DEUS/hour is being arb-ed against a ~+1.04% premium, so the tape is thinner "
        "than last run's 4,704 - the absence of directional flow on BOTH sides continues."
    ),
    "mark_source": (
        "deepest-pool reserves x VIRTUAL/USD, both legs read ON-CHAIN at the same block. Reserves "
        "blk 53043188: VIRTUAL 526,729.3742 / DEUS 18,905,730.3720 (token0=VIRTUAL via 0x0dfe1681 = "
        "0x0b3e3284..., token1=DEUS via 0xd21220a7 = 0x940A319B..., both 18dp). ratio 0.027860832 x "
        "VIRTUAL $0.6241207 = $0.0173885. VIRTUAL/USD is the AVERAGE of two live VIRTUAL/USDC V3 "
        "pools read at the same block: 0x7CB770D0 = $0.6235623, 0x529d2863 = $0.6246790."
    ),
    "mark_note": (
        "PREMIUM +1.04%, third consecutive hour and it has now NARROWED from +1.34% to +1.04%. "
        "Deepest-pool mark $0.0173885 vs three USDC V3 venues 0.01721955 / 0.01720974 / 0.01716328 "
        "(median $0.01720974); DexScreener prints $0.01727 on the deepest pair. Honest band "
        "$0.017163-$0.017220 for the USDC venues, deepest pool sits $0.00017 above them. The premium "
        "compressing while arb volume FELL (4,704 -> 2,939 DEUS) means it closed on the VIRTUAL leg "
        "and on the pool's own drift, not on arb pressure. Still do NOT quote the deepest pool alone."
    ),
    "gate_distances_pct": {str(t): gp(t) for t in (0.012, 0.025, 0.032, 0.041)},
    "ath_distance_pct": round(0.06876 / MARK * 100 - 100, 2),
    "h24_note": (
        "h24 -3.50%, block-pinned to exactly 86400s (blk 52999988 2026-10-23T21:02:03Z -> 53043188 "
        "2026-10-24T21:02:03Z). Decomposition: DEUS/VIRTUAL ratio ROSE +1.2579% while VIRTUAL/USD "
        "fell -4.7006% - so the entire decline is the quote leg, and DEUS outperformed VIRTUAL for "
        "the SIXTH consecutive run. Net DEUS LEFT the deepest pool over 24h: -118,535.49 (from "
        "19,024,265.86 to 18,905,730.37), i.e. the pool is tighter, not looser."
    ),
})

for t in ("0.012", "0.025", "0.032", "0.041"):
    s["targets"][t]["last_checked_price"] = MARK
    s["targets"][t]["last_checked_at"] = NOW
    s["targets"][t]["distance_pct"] = gp(float(t))
    # hit_at stays null -> no cross
    assert s["targets"][t]["hit_at"] is None

s["gate_results"] = {
    "observed_at": NOW,
    "ath": {"verdict": "UNCHANGED", "prior": 0.06876, "current": MARK, "distance_pct": round(0.06876 / MARK * 100 - 100, 2)},
    "sharp_move": {"verdict": "QUIET", "h1_pct": H1, "threshold_pct": 20.0,
                   "note": "DexScreener h1 present this run AND on-chain 3600s window agree in sign; neither reaches +/-20%."},
    "targets": {"0.012": "NO_CROSS", "0.025": "NO_CROSS", "0.032": "NO_CROSS", "0.041": "NO_CROSS"},
    "run_verdict": "OK",
    "notifications_sent": 0,
}

s["venue_spread"] = {
    "observed_at": NOW,
    "deepest_pool_mark": MARK,
    "usdc_v3_median": 0.01720974,
    "usdc_v3_venues": {"0x58dBa34e": 0.01721955, "0x75bc1495": 0.01716328, "0x1B2f3f5C": 0.01720974},
    "dexscreener": 0.01727,
    "premium_pct": 1.039,
    "note": "Third consecutive premium hour but NARROWING: +1.12% -> +1.34% -> +1.04%. Arb volume fell in the same step (4,704 -> 2,939 DEUS/h), so the convergence is NOT arb-driven. USDC venues span only 0.33% (0.017163-0.017220) and agree; the deepest pool is still the outlier at the top.",
}

s["deepest_pool_activity"] = {
    "window": "blk 53041389 -> 53043188 (20:02:03Z .. 21:02:03Z)",
    "swap_events": 2,
    "family": "Solidly (Aerodrome classic) - Swap topic0 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b (full 64-hex)",
    "buy_tx_count": 0,
    "buy_deus_out": 0,
    "sell_tx_count": 2,
    "sell_deus_in": 2938.7054,
    "net_deus_into_pool": 2938.7054,
    "largest_sell_deus": 2200.0,
    "control_note": "Filter discriminative: right topic0 over blk 53041900-53041940 returned 2 logs, one-char-wrong topic0 returned 0. Decoder reconciled to reserves: 2,938.71 DEUS in minus 1% fee 29.39 = 2,909.32, matching the measured reserve delta exactly. BOTH swaps landed in the same block 53041913.",
    "observed_at": NOW,
    "read": "BOTH SELLS ARE ARB, NOT DISTRIBUTION. The 2,200 print went sender 0x6abea499 -> router 0xeb7c90d3 -> pool (the same round-trip sink flagged last run); the 738.71 print's DEUS leg arrived straight FROM USDC V3 pool 0x58dBa34e. Zero buy legs. 2,939 DEUS/hour against a +1.04% premium is the thinnest tape yet recorded on this pool - this is BOTH SIDES ABSENT, not a selloff.",
}

s["supply_side_21z"] = {
    "observed_at": NOW,
    "escrow_deus": 29150566.777697522,
    "escrow_24h_delta_pct": -0.910,
    "five_pct_line_deus": 1470911.20,
    "pressure_ratio": 0.182,
    "escrow_burns_1h": 0,
    "claim_main_vault_deus": 339849602.04411674,
    "claim_net_out_24h_deus": 296635.89,
    "claim_pct_of_supply": 38.788,
    "deus_total_supply": 876177627.813275,
    "deus_supply_24h_delta": -29152.63,
    "xdeus_total_supply": 1728,
    "xdeus_24h_delta": 1,
    "pending_unstake": {"wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
                        "xdeus_nft_id": 1396, "status": "NOT YET BURNED - fourth consecutive run",
                        "verified": "tokenOfOwnerByIndex balance = 1 NFT, DEUS balance 0.000000"},
    "read": "NO unstake pressure: escrow 24h drain is 0.182x the 5%/day line, and ZERO escrow Burn events in the hour. CLAIM main vault BLEW OUT 296,635.89 in 24h, the largest 24h figure recorded, at 38.79% of supply. Total supply fell 29,152.63 over 24h - NINTH consecutive net-deflation read, and byte-identical to last run's -29,152.63, i.e. flat-to-slightly-deflationary at a stable rate.",
}

s["level_math"] = {
    "method": "constant-product x*y=k on deepest-pool reserves at blk 53043188, zero fees, no other flow. Solved in RATIO space (target/VIRTUAL_price): D_needed = D*(sqrt(r_cur/r_target)-1).",
    "observed_at": NOW,
    "reserves": {"virtual": V_RES, "deus": D_RES, "mark_usd": MARK, "virtual_usd": VUSD},
    "to_0_012": {"action": "net SELL", "deus_needed": 3852261, "usd_needed": 66977,
                 "mult_of_101k_dump": 37.78, "pct_of_pool_deus": 20.4},
    "to_0_025": {"action": "net BUY", "deus_needed": 3138531, "usd_needed": 54577,
                 "pct_of_pool_deus": 16.6},
    "to_0_032": {"action": "net BUY", "deus_needed": 4969364, "usd_needed": 86413,
                 "pct_of_pool_deus": 26.3},
    "to_0_041": {"action": "net BUY", "deus_needed": 6593617, "usd_needed": 114653,
                 "pct_of_pool_deus": 34.9,
                 "note": "Still ~238x the deepest pool's 24h volume. $0.041 only reachable by supply WITHDRAWAL from the book - unchanged, and the whole reason for the 5-day unstake lead time."},
}

s["notes"] = s.get("notes", "") + " | TELL 20 (NEW, 2026-10-24 21:02Z run): A PREMIUM THAT NARROWS WHILE ARB VOLUME FALLS IS NOT ARB CLOSING IT - IT IS THE QUOTE LEG MOVING. The deepest-pool premium over the USDC V3 median went +1.12% -> +1.34% -> +1.04% across three runs while arb flow fell 4,704 -> 2,939 DEUS/h. If arb were the mechanism the premium would compress AS VOLUME RISES; here both fell together, so the convergence came from VIRTUAL/USD (-0.0946% this hour) and the pool's own drift. Operational lesson: never attribute convergence to an agent when the agent's footprint is shrinking - check the denominator first. ALSO NEW THIS RUN (methodology): Uniswap-V3 slot0() returns SEVEN ABI words, and sqrtPriceX96 is WORD 0, not the low 160 bits of the concatenated blob. Reading h[-40:] silently yields 1 (the tick) and produces VIRTUAL/USD = $0.0000000, which then makes every gate distance infinity. ALWAYS sanity-check a decoded price against a known live print (DexScreener) before feeding it to a gate; the failure is silent, not an error. Second methodology note: binary-searching a block by timestamp needs a LOWER BOUND wide enough for the window (Base ~1800 blocks/hour at 2s) - a 3,000-block lower bound made an intended 86,400s window land on 6,000s, reporting 'flat' when the true 24h move was -3.5%."

with open(P, "w") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
    f.write("\n")

json.load(open(P))
print("state written OK")
print("targets:", {k: v["distance_pct"] for k, v in s["targets"].items()})
print("ath verdict:", s["ath"]["last_verdict"], "| run:", s["gate_results"]["run_verdict"])

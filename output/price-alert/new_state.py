#!/usr/bin/env python3
"""Rebuild price-alert state with this run's observations, preserving history."""
import json

SRC = "memory/topics/price-alert-state.json"
with open(SRC) as f:
    s = json.load(f)

NOW = "2026-10-24T08:12:00Z"
PRICE = 0.017918

# --- ATH gate: prior 0.06876 is untouched (monotonic, price nowhere near it) ---
s["ath"] = {
    "price_usd": 0.06876,
    "observed_at": "2026-05-28T15:35:00Z",
    "announced_at": "2026-05-28T15:35:00Z",
}

# --- targets: none crossed, none newly registered; keep as-is ---
for t in ("0.012", "0.025", "0.032", "0.041"):
    s["targets"].setdefault(t, {"side": "above", "first_seen_below_at": NOW,
                                "hit_at": None, "announced_at": None})

s["last_alerts"] = {"ath": None, "sharp_move": None, "target_hit": None}

s["last_price"] = {
    "price_usd": PRICE,
    "h1_pct": -0.043,
    "h24_pct": 4.04,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL — deepest, liq $682,345",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 682345.24,
    "volume_24h_usd": 28346.62,
    "volume_1h_usd": 0.0,
    "txns_1h": "0 buy / 0 sell on deepest pool — DEAD 205 min",
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "h1_source": "decoded-from-pool-swap-logs (live USDC venues)",
    "h1_note": "DexScreener again omitted priceChange.h1 (null) on the deepest pair. DID NOT read that as flat. Decoded 38 V3 Swap events from the three LIVE DEUS/USDC pools (0x58dBa34e liq $32.9k, 0x1B2f3f5C liq $10.7k, 0x75bc1495 liq $6.1k) over blocks 53016172-53019896 with timestamps. 16 swaps landed inside the trailing 60 min. Per-pool 1h deltas: pool2 -0.043%, pool3 -0.256%, pool4 -0.001%. Volume-weighted mark $0.017893; median $0.017918. Far from the 20% gate — h1 IS MEASURED this run, and it is flat-to-slightly-down.",
    "mark_source": "live USDC venues (primary) + deepest-pool reserves (cross-check)",
    "mark_note": "PRIMARY: median post-trade sqrtPriceX96 mark across the three live DEUS/USDC pools = $0.017918, cross-validated three ways against DexScreener prints (pool2 0.01791 / pool3 0.01787 / pool4 0.01800) to within 0.01%. CROSS-CHECK: deepest pool 0x3E97c5EC is aerodrome CLASSIC (Solidly), NOT Slipstream - slot0/globalState/fee/liquidity ALL revert, while getReserves (0x0902f1ac) returns [528123.8273770272, 18855811.85328747, 1792816783] and stable() = 0 (volatile). So for THIS pool the reserve ratio IS the correct mark (unlike a CL pool) = 0.02800854 VIRTUAL/DEUS. Converted at VIRTUAL $0.6342-$0.6405 that is $0.017763-$0.017939, i.e. -0.86% to +0.12% of the live-venue mark. Both roads agree the price is ~$0.0178-0.0179. Reserves are BYTE-IDENTICAL to the 07:05Z snapshot.",
}

s["deepest_pool_activity"] = {
    "last_log_block": 53013718,
    "last_log_tx": "0x7b71081fb476afaf8c2a4e606a73ee85747d1d45980e588917681cd3374e18d9",
    "last_log_ts": "2026-10-24T04:39:43Z",
    "dormant_minutes_at_run": 205,
    "verification": "Unfiltered address-only eth_getLogs over blocks 53010000-53019896 returned exactly 3 logs, ALL from that single 04:39:43Z tx (topics 0x112c2569, 0xcf2aa508, 0xb3e27736). So the pool has emitted nothing for ~205 minutes. Control: the known 00:24Z dump window still returns 9 swaps with the same filter, so this is real dormancy, not a broken query.",
    "observed_at": NOW,
}

s["live_venues_1h"] = {
    "note": "THE CORRECTION THAT MATTERS: these three DEUS/USDC pools are UNISWAP-V3-STYLE (Swap topic0 0xc42079f9..., 3 topics / 5 data words), NOT Solidly. The prior two runs scanned them with the Solidly 0xb3e27736 filter and got clean zeros, then concluded 'whole-market pause'. That conclusion was WRONG - the filter never matched this venue family. Verified this run: address-only scan of 0x58dBa34e over 53017773-53019772 returns 7 logs, a 100% histogram on 0xc42079f9.",
    "pools": {
        "0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b": {"liq_usd": 32861.3, "v1h_usd": 90.75, "swaps_1h": 6, "v3_style": True},
        "0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642": {"liq_usd": 10707.85, "v1h_usd": 18.02, "swaps_1h": 1, "v3_style": True},
        "0x75bc14950Ab093cBd1f80BbbDf458596939180A3": {"liq_usd": 6128.45, "v1h_usd": 51.58, "swaps_1h": 9, "v3_style": True},
    },
    "deus_volume_1h": 6084.2,
    "observed_at": NOW,
}

s["escrow_snapshot"] = {
    "balance_deus": 29108661.674663614,
    "prior_balance_deus": 29108661.674663614,
    "change_deus": 0.0,
    "change_pct": 0.0,
    "balance_24h_ago": 29407291.88770671,
    "change_24h_deus": -298630.2130430937,
    "change_24h_pct": -1.0155,
    "five_pct_line_deus": 1455433.08,
    "observed_at": NOW,
    "note": "FLAT since 07:05Z (0.0 delta). Over 24h escrow fell -298,630 DEUS (-1.02%) - that is the xDEUS #1492 unstake plus routine churn, NOT a new event. No escrow Burn event in the last 4,000 blocks. 5%/day intel line = 1,455,433 DEUS, so current 24h outflow is 4.9x BELOW it. No unstake pressure.",
}

s["claim_snapshot"] = {
    "balance_deus": 340081346.429216,
    "prior_balance_deus": 340082386.3812717,
    "change_deus": -1039.95,
    "net_out_24h_deus": 193982.8971566558,
    "pct_of_supply": 38.82,
    "daily_drip_pct_of_balance": 0.057,
    "observed_at": NOW,
    "note": "MEASURED 24h (block-pinned, blocks 52976786 -> 53019986, exactly 24.00h): -193,983 DEUS = ~$3,472/day at $0.0179. That is BELOW the 30d band of 283k-350k/day - a genuinely slower drip, measured over a full day rather than inferred from a 53-minute window (which the prior run correctly refused to extrapolate). Worth noting but not an alert.",
}

s["xdeus_supply"] = {
    "total_supply": 1727,
    "prior": 1727,
    "change_24h": 2,
    "observed_at": NOW,
    "note": "1727 now vs 1725 24h ago = +2 NFTs. Staking is still net ADDITIVE over the day despite the record unstake. Not an exodus.",
}

s["deus_total_supply"] = {
    "total_supply": 876190274.819517,
    "prior": 876190001.500193,
    "change": 273.32,
    "change_24h": -19692.665234923363,
    "observed_at": NOW,
    "note": "24h supply change is -19,693 DEUS (net deflationary over this one day), which CONTRADICTS the standing 7d read of net +65,381 inflation. Do NOT overwrite the 7d ledger off one day - record both. Treat the regime as unsettled until a 7d window is re-measured.",
}

s["holder_check"] = {
    "observed_at": NOW,
    "note": "Unchanged to the wei again, third consecutive run: 0x7f6aba75 = 335,249.4994426125; 0x6a45ca8b = 70,034.14033726917. Neither has sold a single token, including into the 4h+ the live venues were trading. 0xbb0f7533 DEUS balance exactly 0.0 and STILL holds xDEUS #1396.",
    "buyers": [
        {"addr": "0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3", "balance_deus": 335249.4994426125, "status": "HELD"},
        {"addr": "0x6a45ca8bb30f396f40721e105e0aa6cabf326657", "balance_deus": 70034.14033726917, "status": "HELD"},
    ],
    "pending_unstake": {"wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63", "xdeus_nft_id": 1396, "status": "NOT YET BURNED - trigger has not fired; verified tokenOfOwnerByIndex(owner,0) = 1396 this run"},
}

s["last_run_at"] = NOW

s["notes"] = (
    "TELL 16 (NEW, 2026-10-24 08:12Z run) — TWO OF THEM, BOTH ABOUT FALSE ZEROS: "
    "(a) POOL FAMILY MISMATCH SILENTLY PRODUCES CLEAN ZEROS. The three secondary DEUS pools are Uniswap-V3-style "
    "(Swap topic0 0xc42079f9...) while the deepest is Aerodrome classic/Solidly (0xb3e27736...). Two prior runs scanned "
    "all four with the Solidly topic and reported 'whole-market pause in DEUS trading'. That was an artifact. The test: "
    "scan a pool by ADDRESS ONLY and histogram its topic0s before ever claiming it is quiet. "
    "(b) A ZERO CONTROL IS ONLY A CONTROL IF YOU POINT IT AT THE RIGHT BLOCK. The saved state recorded the xDEUS #1492 "
    "unstake at block 53002812; the real receipt says 53003804 (timestamp matches: 2026-10-23T23:09:15Z). A control query "
    "at the wrong block returns zero and looks exactly like a broken filter. ALWAYS take control blocks from the tx "
    "receipt (eth_getTransactionReceipt), never from remembered notes. "
    "(c) Also re-confirmed: a pool whose view functions slot0/globalState/fee/liquidity ALL revert is NOT Slipstream - "
    "probe getReserves (0x0902f1ac) and stable(). For a Solidly volatile pool the raw reserve ratio IS the correct mark. "
    "Prior notes had asserted Slipstream and computed a CL-style mark; the numbers happened to agree here, but the "
    "method was wrong. "
    + s.get("notes", "")
)

with open(SRC, "w") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("written", SRC)

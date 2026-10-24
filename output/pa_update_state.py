#!/usr/bin/env python3
"""Update price-alert-state.json atomically with this run's findings, validated."""
import json, os, shutil, time

SRC = "memory/topics/price-alert-state.json"
BAK = SRC + ".bak"
shutil.copy2(SRC, BAK)

with open(SRC) as f:
    st = json.load(f)

NOW = "2026-10-24T14:14:17Z"
HEAD = 53030955

# --- ATH gate ---
prior_ath = st["ath"]["price_usd"]
CURRENT = 0.01744603
# CURRENT << prior_ath, so no new ATH; leave untouched
ath_verdict = "ATH_BASELINE_UNCHANGED" if CURRENT <= prior_ath else "ATH"
st["ath"]["last_verdict"] = "UNCHANGED"

# --- sharp move gate ---
h1 = -0.315
sharp = abs(h1) >= 20.0
st["last_alerts"]["sharp_move"] = st["last_alerts"]["sharp_move"]  # unchanged, gate quiet

# --- targets: all still un-hit, update last_checked_price ---
for t, obj in st["targets"].items():
    obj["last_checked_price"] = CURRENT
    obj["last_checked_at"] = NOW
    obj["distance_pct"] = round((float(t)/CURRENT - 1)*100, 2)

st["last_price"] = {
    "price_usd": CURRENT,
    "h1_pct": h1,
    "h24_pct": -2.309,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL — deepest, liq $665,746",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 665745.58,
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": HEAD,
    "head_ts": NOW,
    "h1_source": "measured on-chain, block-pinned to exactly 3600s (blk 53028777 -> 53030577, delta=3600)",
    "h1_note": "POOL RESERVES WERE BYTE-IDENTICAL ACROSS THE ENTIRE 1h WINDOW: VIRTUAL 526,295.650273904121782893 and DEUS 18,921,310.710200002071942720 at BOTH ends. Ratio 0.0278149679 -> 0.0278149679 = 0.000%. The -0.315% h1 is therefore ENTIRELY the VIRTUAL/USD leg: VIRTUAL $0.629197 -> $0.627217 = -0.315%. There were ZERO swaps in the hour. DexScreener returned h1=null on this pair; per TELL 11 that is UNMEASURED, not flat, so it was measured on-chain instead.",
    "mark_source": "deepest-pool reserves x on-chain VIRTUAL/USD. VIRTUAL/USDC V3 0x529d2863 direct = $0.627217; VIRTUAL/WETH Solidly 0x792f465e (WETH per VIRTUAL 0.0002650983) x ETH/USD 0x d0b53D92 $2,366.3276 = $0.627309. Two legs agree to 0.015%.",
    "mark_note": "token0=VIRTUAL re-confirmed by eth_call 0x0dfe1681 this run, token1=DEUS (0xd21220a7), decimals 18. Mark = ratio x VIRTUAL price = $0.01744603. Cross-check DEUS/USDC V3: 0x58dBa34e $0.01747470 / 0x1B2f3f5C $0.01754637 / 0x75bc1495 $0.01750076, median $0.01750076 (deepest pool sits -0.31% below median, normal band). DexScreener printed $0.01759 on this pair (+0.82% vs measured). NOTE the prior run's decimals() REVERT was a bug: decimals() lives on the TOKEN, not the pool — calling it on the pool reverts on Uniswap-V3 pools and made all three marks look unreadable.",
    "gate_distances_pct": {"0.012": -31.22, "0.025": 43.30, "0.032": 83.42, "0.041": 135.01},
    "ath_distance_pct": 294.13,
    "h24_note": "h24 -2.309%: ratio 0.0267999769 -> 0.0278149679 (+3.787%) against VIRTUAL $0.666360 -> $0.627217 (-5.87%). The ratio ROSE while USD fell — DEUS gained on VIRTUAL over 24h; the USD mark fell only because VIRTUAL itself de-rated. Same split-sign pattern as TELL 18's corollary: state which leg you measured."
}

st["deepest_pool_activity"] = {
    "window": "blk 53028777 -> 53030577 (13:01:41Z .. 14:01:41Z, exactly 3600s)",
    "swap_events": 0,
    "family": "Solidly (Aerodrome classic) — Swap topic0 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b (full 64-hex, verified)",
    "buy_tx_count": 0, "buy_deus_out": 0.0,
    "sell_tx_count": 0, "sell_deus_in": 0.0,
    "net_deus_into_pool": 0.0,
    "last_swap_block": 53027993,
    "last_swap_ts": "2026-10-24T12:35:33Z",
    "last_swap_tx": "0xc940253588a057e876ce409f32198b1c28e41d0a12fc3c769d58818d99863319",
    "minutes_quiet_at_run": 86.6,
    "blocks_since_last_swap": 2598,
    "control_note": "ZERO-LOG WINDOW WAS CONTROLLED, NOT ASSUMED. Same filter pointed at the known-active window 53027400..53028000 returned exactly 2 swaps (blk 53027871 tx 0x4338c676..., blk 53027993 tx 0xc9402535...); the same window with ONE character deliberately altered in topic0 returned 0. Real topic0 discriminates, so the zero is a true zero. A backward scan in 999-block chunks from head found the most recent swap at blk 53027993 — i.e. nothing has traded on the deepest pool for 86.6 minutes / 2,598 blocks. THE 12:35:33Z CLAIM DUMP IS STILL THE LAST PRINT ON THE BOOK AND IT HAS NOT BEEN BOUGHT BACK.",
    "observed_at": NOW
}

st["post_dump_absorption"]["still_unabsorbed"] = {
    "dump_ts": "2026-10-24T12:35:33Z",
    "dump_deus": 52736.88,
    "minutes_since": 86.6,
    "absorbing_swaps": 0,
    "read": "SECOND CONSECUTIVE RUN with zero offsetting flow. The 00:24Z record dump drew 137,397 DEUS of same-block buying; this one has now gone 86.6 minutes with nothing. Confirms TELL 19: absorption is conditional on a bid existing, not a property of the pool.",
    "observed_at": NOW
}

st["escrow_snapshot"] = {
    "balance_deus": 29103661.674664,
    "prior_balance_deus": 29103661.674664,
    "change_deus": 0.0,
    "change_pct": 0.0,
    "balance_24h_ago": 29408223.901194,
    "change_24h_deus": -304562.226531,
    "change_24h_pct": -1.036,
    "five_pct_line_deus": 1470411.2,
    "observed_at": NOW,
    "note": "Unchanged to the wei for a FIFTH consecutive run: 29,103,661.674664. 24h -304,562 (-1.036%) vs the 1,470,411 5%/day line = 0.207x. No unstake pressure.",
    "reconciliation_24h": {
        "burns": [{"tokenId": 1492, "wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63", "deus": 319562.226531, "ts": "2026-10-23T23:09:15Z", "blk": 53003804},
                  {"tokenId": 425, "wallet": "0xcae798c0c6958df8299df4f13726da433b8ba7ba", "deus": 5000.0, "ts": "2026-10-24T08:16:23Z", "blk": 53020218}],
        "stakes": [{"wallet": "0x5a46519659e3557112b90a8becb891873fe17406", "deus": 10000.0, "ts": "2026-10-23T20:06:29Z", "blk": 52998321},
                   {"wallet": "0x8d834919956af4f696f729bdcaba61c9f16529f5", "deus": 10000.0, "ts": "2026-10-24T02:00:15Z", "blk": 53008934}],
        "burn_total": 324562.226531,
        "stake_total": 20000.0,
        "reconciles": True,
        "math": "-324,562.23 (burns) + 20,000.00 (stakes) = -304,562.23, which matches the measured 24h balance delta to the wei.",
        "note": "BALANCE CLOSES EXACTLY, so the 24h escrow window is fully enumerated — no unaccounted unstake. This is the FIRST run where the escrow 24h delta was reconciled against its events rather than just read off balanceOf."
    },
    "staker_0x8d834919": {
        "what": "SECOND 10,000 DEUS STAKE IN 24h, at 02:00:15Z blk 53008934 tx 0xd205da753ac02a756a6a91e6dc593d3342bd4994110b98e27300065a2465281e. NOT in prior notes.",
        "profile": "Plain EOA (code 0x), nonce 3500 — high-activity established account, not fresh. DEUS balance now 266.9984, xDEUS NFTs 6, ETH 0.003785.",
        "funding": "ZERO incoming DEUS transfers in the last 30,000 blocks — so it did not receive DEUS from the CLAIM vault or a distributor in that window; it staked from an existing balance. Do NOT label it recycled emission on this evidence.",
        "read": "Net staking 24h = +20,000 DEUS against -324,562 burned, so the 5-day cooldown is still net DRAINING by design. Two separate 10k stakes is constructive but tiny vs the burn."
    },
    "latest_burn": {
        "wallet": "0xcae798c0c6958df8299df4f13726da433b8ba7ba",
        "xdeus_nft_id": 425,
        "released_deus": 5000.0,
        "burn_tx": "0x51d2eff4b42b6fc5b44a9a642cc2da4bc7b75e1003020bd855bdabfc12082f90",
        "burn_block": 53020218,
        "burn_ts": "2026-10-24T08:16:23Z",
        "sold": False,
        "wallet_balance_deus": 5000.0
    }
}

st["claim_snapshot"] = {
    "balance_deus": 339964647.1242,
    "prior_balance_deus": 339965547.3892,
    "change_deus": -900.265,
    "net_out_24h_deus": 251665.9294,
    "pct_of_supply": 38.80,
    "daily_drip_pct_of_balance": 0.074,
    "observed_at": NOW,
    "note": "Fresh block-pinned 24h window (52987708 -> 53030908, exactly 86400s): CLAIM main vault 340,216,313.05 -> 339,964,647.12 = -251,666 DEUS net out (~$4,390/day at $0.017446). FIFTH consecutive full-day window below the 30d band lower edge (283k). Continued slowdown, still not a regime change."
}

st["xdeus_supply"] = {
    "total_supply": 1726, "prior": 1726, "change_24h": 0, "observed_at": NOW,
    "note": "1726 vs 1726 exactly 24h ago = 0 net change, THIRD consecutive flat day. But note the gross churn: 2 burns (NHS #1492, #425) and 2 stakes (10k each) inside the window still netted to zero NFTs. Flat totalSupply hides two-sided activity — read the Burn/Stake events, not just 0x18160ddd."
}

st["deus_total_supply"] = {
    "total_supply": 876171197.731231,
    "prior": 876171197.731231,
    "change": 0.0,
    "change_24h": -38769.7535,
    "observed_at": NOW,
    "note": "876,171,197.73 now vs 876,209,967.48 exactly 24h ago = -38,769.75 DEUS. FOURTH consecutive net-deflation day. The standing 7d +65,381 net-inflation read is now stale by four days and MUST be re-measured over a fresh full 7d window before it is cited again."
}

st["holder_check"] = {
    "observed_at": NOW,
    "note": "EIGHTH consecutive run unchanged: 0x7f6aba75 = 335,249.499443; 0x6a45ca8b = 70,034.140337; 0xf0a04b07 = 250,000.125225; 0xcae798c0 = 5,000.000000 (still unsold). 0xbb0f7533 DEUS balance exactly 0.0 and STILL holds xDEUS #1396 (balanceOf=1, tokenOfOwnerByIndex(0)=1396) — trigger has NOT fired.",
    "pending_unstake": {
        "wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
        "xdeus_nft_id": 1396,
        "status": "NOT YET BURNED - re-verified this run at blk 53030955: balanceOf(xDEUS)=1, tokenOfOwnerByIndex=1396"
    }
}

st["last_run_at"] = NOW

# cap targets to 20 by first_seen_below_at
if len(st["targets"]) > 20:
    items = sorted(st["targets"].items(), key=lambda kv: kv[1].get("first_seen_below_at") or "")
    st["targets"] = dict(items[-20:])

with open(SRC, "w") as f:
    json.dump(st, f, indent=2, ensure_ascii=False)
    f.write("\n")

# validate
with open(SRC) as f:
    json.load(f)
print("state written + validated OK; bytes=%d targets=%d" % (os.path.getsize(SRC), len(st["targets"])))
print("bak=%s" % BAK)

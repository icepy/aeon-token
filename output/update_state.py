#!/usr/bin/env python3
"""Rewrite price-alert-state.json atomically with this run's findings."""
import json
import os
import shutil
import datetime

STATE = "memory/topics/price-alert-state.json"
BAK = STATE + ".bak"
NOW = "2026-10-24T13:17:00Z"

with open(STATE) as f:
    s = json.load(f)

shutil.copyfile(STATE, BAK)

PRICE = 0.01750110
H1 = -0.331
H24 = -1.634

s["last_run_at"] = NOW
s["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
s["chain"] = "base"

# ATH untouched: 0.06876 is the true 2026-05-28 high
s["ath"]["observed_at"] = s["ath"].get("observed_at", "2026-05-28T15:35:00Z")

s["last_alerts"]["ath"] = None
s["last_alerts"]["sharp_move"] = None
s["last_alerts"]["target_hit"] = None

for k in ("0.012", "0.025", "0.032", "0.041"):
    t = s["targets"][k]
    t["last_checked_price"] = PRICE

s["last_price"] = {
    "price_usd": PRICE,
    "h1_pct": H1,
    "h24_pct": H24,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL — deepest, liq $665,746",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 665745.58,
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": 53029218,
    "head_ts": NOW,
    "h1_source": "measured on-chain, block-pinned to exactly 3600s",
    "h1_note": "Window blk 53027048 -> 53028848, timestamp delta exactly 3600s. Deepest pool reserves VIRTUAL 527,564.4385 -> 526,295.6503, DEUS 18,875,805.1113 -> 18,921,310.7102. Ratio 0.02794924 -> 0.02781497 = -0.480%. VIRTUAL/USD $0.628255 -> $0.629197 (+0.150%). Net USD mark -0.331%. The pool ratio fell because a 52,737 DEUS CLAIM dump landed at 12:35:33Z; the fall was cushioned because VIRTUAL ticked up.",
    "mark_source": "deepest-pool reserves x on-chain VIRTUAL/USD (VIRTUAL/USDC V3 0x529d2863 direct = $0.629197; VIRTUAL/WETH Solidly x ETH/USD V3 0xd0b53D92 = $0.628806)",
    "mark_note": "token0=VIRTUAL re-confirmed by eth_call this run (0x0dfe1681), so mark = reserve ratio x VIRTUAL price. Result $0.01750110. Cross-check: DEUS/USDC V3 0x58dBa34e $0.01744124 and 0x1B2f3f5C $0.01754637, median $0.01749380 — deepest pool sits +0.042% above the median, the tightest agreement in the record (prior runs +0.31%, +0.57%). DexScreener prints $0.01759 on this pool, +0.51% vs measured. Pool 0x75bc1495 returned HTTP 429 this run, excluded rather than guessed.",
    "gate_distances_pct": {
        "0.012": -31.43,
        "0.025": 42.85,
        "0.032": 82.85,
        "0.041": 134.27,
    },
    "ath_distance_pct": 292.89,
}

s["claim_snapshot"] = {
    "balance_deus": 339965547.3892,
    "prior_balance_deus": 339984948.3047177,
    "change_deus": -19400.92,
    "net_out_24h_deus": 255106.19,
    "pct_of_supply": 38.80,
    "daily_drip_pct_of_balance": 0.075,
    "observed_at": NOW,
    "note": "Fresh block-pinned 24h window (52986018 -> 53029218, exactly 86400s): CLAIM vault fell 340,220,653.58 -> 339,965,547.39 = -255,106 DEUS net out (~$4,465/day at $0.017501). That is back INSIDE the 30d band of 283k-350k? No — it is BELOW it, the FOURTH consecutive full-day window under the band's lower edge. The three prior readings were 243.8k, and before that two sub-band days. Record it as continued slowdown, not yet a regime change.",
}

s["escrow_snapshot"] = {
    "balance_deus": 29103661.674664,
    "prior_balance_deus": 29103661.674663614,
    "change_deus": 0.0,
    "change_pct": 0.0,
    "balance_24h_ago": 29408223.9012,
    "change_24h_deus": -304562.23,
    "change_24h_pct": -1.036,
    "five_pct_line_deus": 1470411.20,
    "observed_at": NOW,
    "note": "Unchanged to the wei for a FOURTH consecutive run: 29,103,661.674664 DEUS. 24h -304,562 DEUS (-1.036%) vs the 1,470,411 DEUS 5%/day line = 0.207x. No unstake pressure. Only burn in the last 12h remains the #425 5,000 DEUS release at 08:16:23Z, still unsold.",
    "latest_burn": s["escrow_snapshot"]["latest_burn"],
}

s["xdeus_supply"] = {
    "total_supply": 1726,
    "prior": 1726,
    "change_24h": 0,
    "observed_at": NOW,
    "note": "1726 now vs 1726 exactly 24h ago (blk 52986018) = 0 net change, second consecutive flat day. Neither an exodus nor an influx.",
}

s["deus_total_supply"] = {
    "total_supply": 876171197.731231,
    "prior": 876190274.819517,
    "change": -19077.09,
    "change_24h": -38769.75,
    "observed_at": NOW,
    "note": "876,171,197.73 now vs 876,209,967.48 exactly 24h ago = -38,769.75 DEUS. THIRD consecutive net-deflation window (-19,693, -38,770, -38,770). The standing 7d +65,381 net-inflation read is now stale by three days and MUST be re-measured over a fresh full 7d window before it is cited again. Three days is still not enough to flip the regime label.",
}

s["deepest_pool_activity"] = {
    "window": "blk 53027048 -> 53028848 (12:00:00Z-ish .. 13:00:00Z, exactly 3600s)",
    "swap_events": 2,
    "family": "Solidly (Aerodrome classic) — Swap topic0 0xb3e27736… full 64-hex",
    "buy_tx_count": 1,
    "buy_deus_out": 6703.91,
    "sell_tx_count": 1,
    "sell_deus_in": 52736.88,
    "net_deus_into_pool": 46032.97,
    "last_event": "12:35:33Z (blk 53027993)",
    "minutes_quiet_at_run": 40.5,
    "query_note": "Two swaps, both inside the same 102 seconds. (1) 12:34:49Z blk 53027871: 6,703.91 DEUS bought out of the pool for 189.329 VIRTUAL by EOA 0xe8faaa6b (nonce 44, code 0x, DEUS balance 0.00 after — took the coin out and left). (2) 12:35:33Z blk 53027993: 52,736.88 DEUS sold INTO the pool for 1,456.224 VIRTUAL (~$916) by EOA 0xbd6383c7, routed through 0x0a2854fbbd (contract) which is the same counterparty seen in the 0x1184de98 exit. Net 46,033 DEUS INTO the pool. ZERO swaps in the 40 minutes after the dump (blk 53028000..53029218) — nothing came to absorb it this time.",
    "observed_at": NOW,
}

s["claim_and_dump_1024z"] = {
    "what": "SECOND RECORDED CLAIM-AND-DUMP, and it validates TELL 10 again. At 12:33:51Z (blk 53027942) the CLAIM distributor 0x20d29c8e paid 52,736.8822 DEUS to plain EOA 0xbd6383c7. 102 seconds later at 12:35:33Z (blk 53027993, tx 0xc940253588a057e876ce409f32198b1c28e41d0a12fc3c769d58818d99863319) that EOA sold the ENTIRE 52,736.88 DEUS into the deepest pool for 1,456.224 VIRTUAL. Post-sale DEUS balance exactly 0.000000.",
    "distributor": "0x20d29c8ec7489c600da7e595ce4ae1da11d76fc5 — name()/symbol() both return 'CLAIM' (proxy, 5c60da1b impl slot). Still holds 9,186,201.04 DEUS. Paid only 3 recipients in the last 20k blocks: 52,736.88 to this seller, 6,036.01 to 0x44f23c08, 9.90 to 0xfd7bd29e.",
    "seller": "0xbd6383c7cbe3ed150f662f70fd4f3a4a1816e13d — plain EOA, nonce 141, eth_getCode 0x, ETH balance 0.000000000629. DEUS balance at -1h/-6h/-24h/-7d/-30d ALL exactly 0.000000: this wallet existed for 102 seconds with the coins and nothing else. Zero xDEUS NFTs. Not a staker, not an incumbent — a pure claim-and-dump pass-through.",
    "impact_pct": -0.551,
    "impact_note": "Pool reserve ratio VIRTUAL/DEUS 0.0279691051 -> 0.0278149679 across the sell block = -0.551%. DEUS in pool 18,869,101.197 -> 18,921,310.710 = +52,209.51 net (52,736.88 in minus the 527.37 fee to 0x205db642). NOT recovered after 7 blocks AND not recovered after 40 minutes — ratio still 0.02781497. This is the OPPOSITE of the 00:24Z record dump, which 137,397 DEUS of same-block buying absorbed. RECALIBRATION: 52,737 DEUS cost 0.551%, i.e. ~$1.67k of notional per 1% — consistent with the older 91.5k-dump estimate ($1.7k/1%), and NOT with the $2.9k/1% inferred from the 319,562 dump. Depth estimate is print-dependent; keep both.",
    "size_vs_record": "52,737 is 6.05x the 2026-10-23 91,566 dump but only 0.165x the 319,562 record. It is the second-largest single sell on record.",
    "read": "This is routine CLAIM emission being dumped on arrival — the drip that has been running at 244k-350k DEUS/day does not sit in wallets, it hits the book within minutes. The difference from the record dump is the ABSENCE of a bid: the 00:24Z 319,562 dump drew 137,397 of same-block buying; this one drew nothing for 40 minutes. Watch for a delayed bid rather than assuming absorption.",
    "observed_at": NOW,
}

s["holder_check"] = {
    "observed_at": NOW,
    "note": "SEVENTH consecutive run unchanged to the wei at blk 53029218: 0x7f6aba75 = 335,249.4994; 0x6a45ca8b = 70,034.1403; 0xf0a04b07 (250k incumbent trimmer) = 250,000.1252; 0xcae798c0 (the 5,000 unstake) = 5,000.0000 — none distributed into today's tape. 0xbb0f7533 DEUS balance exactly 0.0 and STILL holds xDEUS #1396: balanceOf(xDEUS)=1 and tokenOfOwnerByIndex(owner,0)=1396 this run. Trigger has NOT fired.",
    "buyers": s["holder_check"]["buyers"],
    "pending_unstake": {
        "wallet": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
        "xdeus_nft_id": 1396,
        "status": "NOT YET BURNED - re-verified this run at blk 53029121: balanceOf(xDEUS)=1, tokenOfOwnerByIndex=1396",
    },
    "0x1184de98": "EXITED 2026-10-24 10:02:45Z — was 46,195, now 0.",
    "0xbd6383c7": "NEW this run: claim-and-dump pass-through, balance now 0, nonce 141. Not a holder.",
}

s["notes"] = s["notes"] + " TELL 19 (NEW, 2026-10-24 13:17Z run): A CLAIM DUMP WITH NO BID IS A DIFFERENT EVENT FROM A CLAIM DUMP WITH A BID, AND ONLY THE NET RESERVE DELTA + THE POST-EVENT TAPE DISTINGUISH THEM. The 00:24Z 319,562 DEUS dump was absorbed by 137,397 of same-block buying (-1.98%, snapped back within blocks). The 12:35Z 52,737 DEUS dump produced -0.551% and NOTHING bought it back in the following 40 minutes / 1,209 blocks. Same mechanism (CLAIM vault -> fresh EOA -> market), opposite market response. So do not carry forward the phrase 'this pool absorbs dumps' - it is conditional on a bid being present, and the bid presence is measurable: scan Swap logs AFTER the sell block and net the direction. COROLLARY: the depth calibration is itself print-dependent. Three measurements of DEUS/USD depth now give ~$1.7k per 1% (91.5k dump), ~$2.9k per 1% (319,562 dump), and ~$1.67k per 1% (52,737 dump). Two of three cluster at $1.67-1.7k; use that band for distance math and treat the $2.9k reading as the outlier. Redo the $0.012 distance with $1.7k/1%: from $0.017501 a -31.4% move needs ~2.6M DEUS of net selling, still a deliberate-whale event, not an emission drift. ALSO: the CLAIM distributor is not one address but at least three (0x20d29c8e 'CLAIM' proxy holding 9.19M, 0x5cbf5dfa main vault, 0xd4c450ac secondary). Enumerate all three before quoting a single 'drip rate' - the 24h net-out measured on the main vault alone was 255k, but the distributor paid out ≥52.7k+6.0k in just the last 20k blocks."

with open(STATE + ".tmp", "w") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
os.replace(STATE + ".tmp", STATE)
print("written ok")

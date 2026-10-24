import json, shutil, datetime

P = "memory/topics/price-alert-state.json"
shutil.copyfile(P, P + ".bak")
s = json.load(open(P))

NOW = "2026-10-24T16:11:41Z"
MARK = 0.017009
VIRT = 0.6128

s["last_run_at"] = NOW
s["ath"]["last_verdict"] = "UNCHANGED"  # 0.017009 << 0.06876

gp = lambda t: round(t / MARK * 100 - 100, 2)

lp = s["last_price"]
lp.update({
    "price_usd": MARK,
    "h1_pct": -0.38,
    "h24_pct": -3.85,
    "pool": "aerodrome classic (Solidly) DEUS/VIRTUAL — deepest, liq $650,301",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "liquidity_usd": 650300.72,
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "observed_at": NOW,
    "head_block": 53034477,
    "head_ts": NOW,
    "h1_source": (
        "DexScreener deepest pair h1 = -0.38%. On-chain cross-check over EXACTLY 3600s "
        "(blk 53032625 -> 53034425, both timestamps read): ratio 0.027860232 -> 0.027755590 = -0.3756%. "
        "Direction agrees, magnitude agrees to 0.004pp. Note the -0.38% is NOT a VIRTUAL-leg artefact this "
        "run: the DEUS/VIRTUAL ratio itself fell."
    ),
    "h1_note": (
        "Single-hour book was ONE dominant seller: a 1inch executor (0x92325e5a..., 61-byte clone) sold "
        "101,983.485 DEUS atomically across 5 pools at 15:53:59Z (blk 53033946, tx 0x428bbb41...). "
        "67,211.897 of that landed in this pool and moved the ratio -0.7013% in one block. "
        "The other 18 swaps that hour were buys totalling 30,934 DEUS — i.e. the dip was bought, but "
        "not enough to offset. Buys/sells count (18/1) is MISLEADING; size is 30,934 in vs 67,212 out."
    ),
    "mark_source": (
        "deepest-pool reserves x VIRTUAL/USD. Reserves at blk 53034477: VIRTUAL 525,733.60 / "
        "DEUS 18,941,539.11 (token0=VIRTUAL 0x0b3e3284..., token1=DEUS 0x940A319B..., both 18dp, "
        "re-confirmed via 0x0dfe1681/0xd21220a7 this run). ratio 0.027755590 x $0.6128 = $0.017009. "
        "VIRTUAL $0.6128 = live median of 5 deepest Base venues (0x792f465e $0.6129 liq $2.08M, "
        "0x21594b99 $0.6184 liq $1.58M, 0xE31c372a $0.6096 liq $1.22M, 0x529d2863 $0.6115 liq $743k, "
        "0x9c087Eb7 $0.6128 liq $479k)."
    ),
    "mark_note": (
        "DexScreener prints $0.01716 vs my $0.017009 (-0.88%) — inside the normal band given the VIRTUAL "
        "median spread ($0.6096-$0.6184 spans 1.4%). I use the reserve mark because it is reproducible "
        "block-for-block; the USDC-pool cross-check now reads $0.01694-$0.01704, i.e. BELOW my mark, so "
        "the deepest-pool mark is not overstating."
    ),
    "gate_distances_pct": {str(t): gp(t) for t in (0.012, 0.025, 0.032, 0.041)},
    "ath_distance_pct": round(0.06876 / MARK * 100 - 100, 2),
    "h24_note": (
        "h24 -3.85%. Decomposition this run: DEUS/VIRTUAL ratio AND VIRTUAL both fell. That breaks the "
        "'DEUS weakness is just a VIRTUAL problem' pattern that held for 3 consecutive runs. "
        "VIRTUAL h24 -7.69% to -7.97%; the extra DEUS-side leg this run is the 101,983 one-tx dump."
    ),
})

s["targets"]["0.012"]["last_checked_price"] = MARK
s["targets"]["0.012"]["last_checked_at"] = NOW
s["targets"]["0.012"]["distance_pct"] = gp(0.012)
for t in ("0.025", "0.032", "0.041"):
    s["targets"][t]["last_checked_price"] = MARK
    s["targets"][t]["last_checked_at"] = NOW
    s["targets"][t]["distance_pct"] = gp(float(t))

s["dump_1553z"] = {
    "what": (
        "LARGEST SINGLE-ACTOR DUMP OF THE DAY. One ERC-4337 userop / 1inch bundle sold 101,983.485 DEUS "
        "in ONE transaction across FIVE pools at 15:53:59Z."
    ),
    "outer_tx": "0x428bbb417b6378e5f571c4e31763f3a2b3b2369f946c4c330d9743d9d2d53e94",
    "outer_from": "0x7929c5e64791e0033fce421d3b4e9b646c40b331 (EOA nonce 11547, pays gas)",
    "outer_to": "0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789 (ERC-4337 EntryPoint v0.6)",
    "router": "0x111116058b9828cdcdd810c502b925c14f34ca11 (1inch-ish aggregator contract, 22,545B)",
    "executor": "0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f (61-byte clone, prefix 0x363d3d37)",
    "split": {
        "0x3E97c5EC (deepest DEUS/VIRTUAL)": 67211.897,
        "0x58dBa34e (DEUS/USDC V3, liq $31k)": 15994.930,
        "0x1B2f3f5C (DEUS/USDC V3, liq $11k)": 9736.045,
        "0x75bc1495 (DEUS/USDC V3, liq $5.9k)": 4520.306,
        "0x498581ff (Uniswap v4 pool)": 4520.306,
    },
    "total_deus": 101983.484653,
    "price_impact_deepest_pool_pct": -0.7013,
    "price_impact_note": (
        "Reserves blk 53033945 -> 53033946: VIRTUAL 527,586.96 -> 525,733.60, DEUS 18,874,999.34 -> "
        "18,941,539.11 (absorbed 66,539.78 net of the 672.12 fee rebate to 0x205db642). "
        "One block, -0.70% on the pool mark."
    ),
    "sender_after": "0x11111605 balance 0.000000 DEUS, 0 ETH. Fully flushed, nothing retained.",
    "funding": (
        "The executor received its 101,983.48 over THREE inbound transfers, all from 1inch-family routers: "
        "65,552.78 from 0x111111125421ca6dc452d289314280a0f8842a65 at blk 52985282, 22,081.55 from "
        "0x7d6839415693801e94cdc4a7d732c9a3fdbbd1d7 at blk 53022841, 14,349.15 from 0x1111111254... "
        "at blk 53026431. ZERO transfers directly from CLAIM vault or any known distributor — so on the "
        "evidence available this is NOT a claim-and-dump. It is an aggregator route consuming a pre-existing "
        "balance. Do not label it vesting without the upstream hop."
    ),
    "why_it_matters": (
        "This is the first print on record of a 6-figure DEUS sell executing through an aggregator bundle "
        "rather than a naked pool sell. It changes the sell-side model: one operator can now clear 100k "
        "across five venues in a single block, so the 'thin book / one clip per block' assumption is dead. "
        "Impact was still only -0.70% because 5 pools shared it — the deepest pool only took 66k net."
    ),
}

s["level_math"] = {
    "method": "constant-product x*y=k on the deepest pool reserves at blk 53034477, zero fees, no other flow.",
    "reserves": {"virtual": 525733.598889785, "deus": 18941539.114787, "mark_usd": MARK},
    "to_0.012": {"action": "net SELL", "deus_needed": 3609121, "usd_needed": 61386,
                 "mult_of_101k_dump": 35.38,
                 "note": "Needs 35x today's biggest dump. $0.012 is NOT reachable by routine emission or a single whale clip — it needs a deliberate multi-actor liquidation. Consistent with the prior run's ~4.36M estimate (now 3.61M because the book is a little thinner after today)."},
    "to_0.025": {"action": "net BUY", "deus_needed": 3317984, "usd_needed": 56434},
    "to_0.032": {"action": "net BUY", "deus_needed": 5132137, "usd_needed": 87291},
    "to_0.041": {"action": "net BUY", "deus_needed": 6741592, "usd_needed": 114665,
                 "note": "The $0.041 unstake trigger sits at a bid that is 66x today's entire 24h volume ($26.2k). Realistically $0.041 can only be reached by supply being withdrawn from the book, not by buying it — which is exactly why the unstake decision must start 5 days early."},
}

s["escrow_snapshot"].update({
    "balance_deus": 29114566.777698,
    "prior_balance_deus": 29103661.674664,
    "change_deus": 10905.103034,
    "change_pct": 0.0375,
    "five_pct_line_deus": round(29114566.777698 * 0.05, 2),
    "observed_at": NOW,
    "note": (
        "Escrow rose +10,905.103034 — exactly the 0x2c81beef stake flagged last run at 15:00Z, now "
        "confirmed on the DEUS balance (the prior run could only see it in xDEUS). No burns in the "
        "1,000-block window checked (0 escrow logs, verified with an error-checked call — an earlier "
        "attempt returned a masked null that would have read as 'quiet')."
    ),
})

s["xdeus_supply"].update({"total_supply": 1727, "prior": 1727, "change_24h": 1, "observed_at": NOW,
                          "note": "1727, unchanged since the 15:00Z stake. 0xbb0f7533 still holds #1396 unburned."})
s["deus_total_supply"].update({"total_supply": 876171197.731231, "observed_at": NOW})
s["claim_snapshot"].update({"balance_deus": 339944646.62, "observed_at": NOW})

s["swap_decode_method"] = {
    "verified": True,
    "how": (
        "Decoded the 23 Solidly Swap logs in blk 53030128..53031128 and reconciled to reserve deltas: "
        "DEUS delta matched amount1In-amount1Out to 0.0000 wei; VIRTUAL delta was +681.81 event vs "
        "+674.99 actual, i.e. -6.82 = 1.0089% of input, which is the Aerodrome classic fee. Decoder correct."
    ),
    "orientation": "token0=VIRTUAL, token1=DEUS. amount1Out>0 means the taker BOUGHT DEUS.",
}

tmp = P + ".tmp"
with open(tmp, "w") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
    f.write("\n")
shutil.move(tmp, P)
print("written", P)

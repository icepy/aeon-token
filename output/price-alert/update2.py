import json, os, shutil

P = "/home/runner/work/aeon-token/aeon-token/memory/topics/price-alert-state.json"
NOW = "2026-10-24T10:05:00Z"

with open(P) as f:
    st = json.load(f)

shutil.copyfile(P, P + ".bak")

st["last_run_at"] = NOW
st["deepest_pool_activity"] = {
    "window": "09:03:59Z -> 10:02:47Z (blk 53,021,643 -> 53,023,443)",
    "swap_events": 15,
    "family": "Solidly (Aerodrome classic) — topic0 0xb3e27736…, NOT UniV2 0xd78ad95f…",
    "buy_tx_count": 14,
    "buy_deus_out": 58517.387,
    "sell_tx_count": 1,
    "sell_deus_in": 29298.529,
    "net_deus_out_of_pool": -29218.858,
    "reserve_delta_verified": "VIA Sync events: VIRTUAL +519.4495 / DEUS -18,540.598 over 09:20:41Z->10:02:47Z. The single 29,298.53 DEUS sell exceeds that — the rest of the hour's buys are routed via multi-hop and don't all touch this pool.",
    "unique_senders_is_misleading": "5 unique `topics[1]` senders, ALL CONTRACTS (routers: 0xcf77a3ba 47,164-byte, 0xae629bf1 19,356, 0x8f10b468 27,060, 0xafe3bec0 2,260, 0x59c7c832 19,886). Must resolve tx.from (the EOA), not the pool-side sender.",
    "per_eoa": {
        "0x1184de98c71b565a7bc8313d89d74322c3df7f3b": {"n": 1, "bought": 0.0, "sold": 29298.53, "kind": "EOA nonce 921", "note": "sold 29,298.53 of its 46,195.14 into the pool; the other 16,896.61 went to three USDC pools in the SAME tx via 1inch (0x9dda6ef3)"},
        "0x24a432d3189631e259f45ff62833c2306405540a": {"n": 1, "bought": 22081.55, "sold": 0.0},
        "0x09b383a627c3d35daf38cd77af0064c1848833c6": {"n": 2, "bought": 10435.88, "sold": 0.0},
        "0x6abea4998f9ef34ee1cda5715ccca0e4d4efb730": {"n": 2, "bought": 9904.43, "sold": 0.0},
        "0x999f938d97639e825dc963d375c69c78e5e03f38": {"n": 1, "bought": 7624.13, "sold": 0.0},
        "0x247a573affbcc637a69e33babd769df1b1aad525": {"n": 1, "bought": 5163.14, "sold": 0.0},
        "0x6664b168fe1fcd4a29a9e13ec91d512544094b3d": {"n": 1, "bought": 778.50, "sold": 0.0},
        "0xaf2bfb6b69dfe6efd257fe8cd694175156a23812": {"n": 2, "bought": 0.11, "sold": 0.0},
    },
}

st["wallet_0x1184de98_exit"] = {
    "address": "0x1184de98c71b565a7bc8313d89d74322c3df7f3b",
    "kind": "EOA, nonce 921",
    "entry": "2026-10-23 18:11:07Z blk 52,994,860 — received 46,195.140306 DEUS, bought with VIRTUAL through 1inch; the counterparty was 0x0a2854fbbd (contract, SLC-adjacent routing)",
    "exit": "2026-10-24 10:02:45Z blk 53,023,409 — sold the ENTIRE 46,195.140306 in one tx (0xf1e8fefe…), selector 0x5f575529 = 1inch swap",
    "hold_duration": "15h51m",
    "pnl": "bought ~$823 at ~$0.01782, sold ~$818 — FLAT, not a profitable flip",
    "what_it_bought": "SLC (0x6bd83abc…, 18 dec) — NOT stablecoins. Receipt shows 2,617,555.36 SLC into the router chain and 2,594,651.72 SLC landing in the wallet, plus 22,903.64 SLC to 0xe25c6353.",
    "slc_market": "SLC/WETH aerodrome, liq $185,266, price $0.0003147, h1 -2.66%, h24 +73.53%",
    "interpretation": "ROTATION, not exit-to-cash. A 46k DEUS position was moved into an asset up 73% on the day. This is the single most important read of the run: it removes DEUS but does NOT lower the operator's mark, and the buyer of that DEUS was the pool plus five other EOAs.",
    "balance_after": 0.0,
}

st["post_dump_absorption"] = {
    "block": 53023409,
    "ratio_before": 0.02810819,
    "ratio_at_sell_block": 0.02802176,
    "ratio_after": 0.02804444,
    "impact_pct": -0.227,
    "recovered_within_blocks": 1,
    "note": "A 29,298 DEUS sell moved the pool mark only -0.227% and it snapped back in the very next block. Liquidity $667,670 absorbs this size. Do NOT describe this as a price event.",
}

st["holder_check"] = dict(st.get("holder_check") or {}, **{
    "0x1184de98": "EXITED 2026-10-24 10:02:45Z — was 46,195, now 0. This closes the 'new money cohort who never sold' note from earlier runs.",
})

tmp = P + ".tmp"
with open(tmp, "w") as f:
    json.dump(st, f, indent=2, ensure_ascii=False)
json.load(open(tmp))
os.replace(tmp, P)
print("ok")

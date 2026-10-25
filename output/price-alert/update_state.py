import json, datetime

P = "memory/topics/price-alert-state.json"
S = json.load(open(P))

MARK = 0.017108117405866208
RATIO = 0.027669824940254523
VIRT = 0.6182951082201115
H1 = 0.129924
H24 = -3.795016
NOW = "2026-10-25T08:09:17Z"
HEAD = 53063272

targets = [0.012, 0.025, 0.032, 0.041]
dist = {f"{t}": round((t / MARK - 1) * 100, 2) for t in targets}
ath_dist = round((S["ath"]["price_usd"] / MARK - 1) * 100, 2)

S["contract"] = "0x940A319B75861014A220D9c6c144d108552B089B"
S["chain"] = "base"
S["last_run_at"] = NOW
S["ath"]["observed_at"] = "2026-05-28T15:35:00Z"
S["ath"]["last_verdict"] = "UNCHANGED"

for k, v in S["targets"].items():
    v["last_checked_price"] = MARK
    v["last_checked_at"] = NOW
    if k in dist:
        v["distance_pct"] = dist[k]

S["last_price"] = {
    "price_usd": MARK,
    "h1_pct": H1,
    "h24_pct": H24,
    "ratio_deus_per_virtual": RATIO,
    "virtual_usd": VIRT,
    "gate_distances_pct": dist,
    "ath_distance_pct": ath_dist,
    "pool": "aerodrome classic (Solidy) DEUS/VIRTUAL - deepest, liq $656,534",
    "pool_address": "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa",
    "pool_url": "https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa",
    "mark_source": (
        "Deepest-pool reserves blk %d: VIRTUAL 524920.706698271817352904 / DEUS 18970871.981723613047481457 "
        "(token0=VIRTUAL 0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b 18dp, token1=DEUS 0x940a319b 18dp). "
        "ratio 0.027669824940254523 x VIRTUAL/USD 0.6182951082 = $0.01710812. VIRTUAL/USD from VIRTUAL/USDC V3 "
        "0x529d2863 slot0 sqrtPriceX96 62298485509597726213130, inverted 18dp/6dp. "
        "DexScreener prints $0.01730 same pair = +1.12%% (API ABOVE on-chain, third run running). "
        "1h/24h computed from exact-3600s / exact-86400s blocks (53061378 / 53019978), ts-delta asserted."
    ) % HEAD,
    "mark_source_verified": True,
    "api_vs_chain_spread_pct": 1.12,
    "head_block": HEAD,
    "head_ts": NOW,
    "observed_at": NOW,
    "h1_source": "chain reserves, exact 3600s window (blk 53061378, ts-delta asserted). DexScreener deep-pool h1 returned null (5th consecutive run).",
}

S["gate_results"] = {
    "observed_at": NOW,
    "ath": {"verdict": "UNCHANGED", "prior": S["ath"]["price_usd"], "current": MARK, "distance_pct": ath_dist},
    "sharp_move": {"verdict": "QUIET", "h1_pct": H1, "threshold_pct": 20,
                   "note": "链上实测 exact 3600s 窗。1h +0.130% 100% 来自 VIRTUAL 引腿（0.6174928→0.6182951）；"
                           "比值腿 +6.0e-8%（逐 wei 未动）。距 20% 门槛 154x。"},
    "targets": {f"{t}": "NO_CROSS" for t in targets},
    "run_verdict": "OK",
    "notifications_sent": 0,
}

S["supply_mint_1025"] = {
    "observed_at": NOW,
    "head_block": HEAD,
    "event": "单次 mint 85,828.91 DEUS —— 史上最大单次增发（此前记录 14,413.49，6.0x）",
    "mint": {
        "blk": 53061481, "ts": "2026-10-25T07:11:49Z",
        "tx": "0xa83d52f2e9d045ba52355e8b250243635aaa25c0e4a06fc4c91e22026804d68e",
        "minter_contract": "0x2cca08ae69e0c44b18a57ab2a87644234daebae4",
        "called_by": "0x7ddb0773e979cd36ef0dc8b6e594a6ebc876e654",
        "selector": "0xcfc32570", "amount": 85828.91,
        "first_hop": "0x42a1647e8a77f8325a7c7bf06096cda477915d39 (EIP-7702, code 0xef0100…)",
    },
    "fanout": "同一收款方在 07:14:35–07:16:13Z（4.5 分钟、9 个 tx）把 85,828.91 全额拆给 8 个 EOA，逐 wei 闭合，自己只剩 98.09",
    "recipients_are_dormant_not_new": True,
    "recipients": {
        "0x4af20629": {"mint": 8612.18, "pre": 42768.35, "now": 51380.53},
        "0x393f8acc": {"mint": 12951.38, "pre": 46449.34, "now": 59400.72},
        "0x5318d687": {"mint": 14621.91, "pre": 64430.06, "now": 79051.97},
        "0x380ce63e": {"mint": 6970.44, "pre": 5334.50, "now": 12304.94},
        "0xfb422428": {"mint": 11926.29, "pre": 43252.18, "now": 55178.47},
        "0x9be2134e": {"mint": 7593.33, "pre": 56963.21, "now": 64556.54},
        "0xd50de171": {"mint": 10459.29, "pre": 23573.50, "now": 34032.79},
        "0x3d1aa83e": {"mint": 12694.08, "pre": 30369.10, "now": 43063.18},
    },
    "recipient_aggregate": {"pre": 313140.24, "now": 398969.15, "d7": 327370.04, "d30": 384051.20, "nonce_all": 1},
    "interpretation": (
        "8 个地址 nonce 全为 1 且铸币前都已有余额（合计 313,140）→ 不是新钱包，是一组 dormant 存量地址。"
        "7d 合计 327,370 → 30d 384,051 → 现在 398,969，说明这组地址本轮之前一个月在净卖出、本轮被重新充弹。"
        "零流出（24h 内 8 个地址一笔都没转出）→ 尚未砸盘，是补给，不是抛售。"
    ),
    "impact_if_dumped": {"mint_only_85829": {"usd_out": 1461.76, "impact_pct": -0.90},
                         "aggregate_398969": {"usd_out": 6685.02, "impact_pct": -4.08}},
    "supply_series": {"now": 876263456.723275, "h1_back": 876177627.813275,
                      "h24_back": 876190274.819517, "h48_back": 876209967.484752,
                      "jump": "+85,828.91 单块跳变（07:09Z→07:39Z 之间），此前连续 12h 逐 wei 不变"},
    "correction": "MEMORY 的『总供应 24h −12,373.69，逐 wei 第五次同一数字 = 通缩走平』被本轮推翻。真实是单块 +85,829 增发。'连续多轮同数'本身就是 mint 没落在观察窗内的假象，不是通缩。",
    "why_it_matters": "与 $0.041 回本线直接相关：稀释是回本线的反向推力，而这次单笔稀释 = 供应 0.0098%，≈ 现有净砸市场 1.1 天。不足以改变 gate，但推翻『通缩』框架。",
}

json.dump(S, open(P + ".tmp", "w"), indent=1, ensure_ascii=False)
print("wrote tmp, targets dist:", dist, "ath_dist:", ath_dist)

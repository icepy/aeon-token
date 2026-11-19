---
title: Market Context
description: Rolling crypto macro snapshot — regime take, signal deltas, narratives, DeFi fundamentals, yields, prediction markets. Consumed by token-pick and narrative-tracker.
tags:
  - crypto
  - macro
  - defi
  - market-context
resource: https://defillama.com
timestamp: 2026-11-19T23:20:00Z
---

# Market Context (as of 2026-11-19)

> **Take:** **chop（跌势暂停，非反转）** —— BTC **$62,127（−0.13% 24h / −13.02% 7d）**，24h 几乎收平但 7d 仍 −13%；广度 **13/20 green 24h**（非稳定币 **10/16**），是 11-13 以来第一次日线广度转正。Conviction: **low** —— 24h 信号（广度 13/20、DEX 量 +3.83%、稳定币 −0.90%）与 7d 信号（TVL −7.11%、非稳定币 7d 仅 2/16 绿、F&G 10）方向相反，且 F&G 仍在 Extreme Fear 底部第六天。

## Signal Snapshot
- BTC **$62,127**（−0.13% 24h, −13.02% 7d）· dominance **57.95%**（11-18 记录 57.96%，**−0.01pp = 持平**）
- ETH **$1,759.14**（+0.15% 24h, −12.64% 7d）· ETH/BTC **0.028315**（11-18 记录 0.028231，**+0.30%**）
- SOL **$73.18**（+0.82% 24h, −10.02% 7d）
- Total mcap **$2.149T**（−2.94% 24h）· DEX vol **$7.775B** 24h（`change_1d` **+3.83%**, `change_7d` −3.50%, `7dover7d` **+8.02%**）
- Breadth: **13/20 green 24h** · **4/20 green 7d**
- **非稳定币广度：10/16 green 24h · 2/16 green 7d**（7d 绿的只有 TRX +0.57% / FIGR_HELOC +0.99%-类，实为 2 条）
- Fear & Greed: **10（Extreme Fear）** — 昨 **11**，序列 11-18 11 · 11-17 12 · 11-16 10 · 11-15 10 · 11-14 13 · 11-13 20
- TVL: **$69.44B**（`/v2` 求和，11-19 live 桶）· 已结算 11-18 桶 **$71.32B**（1d **+0.49%** / 7d **−7.11%**）

## What Changed Since Last Refresh

上一份快照写于 **11-18T23:10Z**（约 24h 前）。实质变化：

- **🔴 F&G 11 → 10，Extreme Fear 第六天。** 序列 11-13 **20** → 14 13 → 15 10 → 16 10 → 17 12 → 18 11 → **19 10**。**11-05 的 50 到这里 14 天 −40 pt，且底部 10 附近已横 5 天。**
- **🟢 24h 广度 2/20 → 13/20，非稳定币 2/16 → 10/16。** 这是 11-13 以来第一次日线广度转正 —— **但 7d 侧非稳定币仍 2/16，说明这只是止跌不是修复。**
- **🟢 DEX 量 24h +3.83% 至 $7.775B，`7dover7d` 从 +2.46% 扩到 +8.02%。** 上轮「缩量趋势断了」的判读被本轮加强：**同比基数连续两轮抬升，但绝对值仍在 $7.8B 低位。**
- **🟢 已结算总 TVL 1d 转正 +0.49%**（11-17 → 11-18），7d 仍 **−7.11%**。**24h 止跌、周线仍跌 —— 与价格形态同构。**
- **🔴 稳定币总量 $284.70B，1d −0.90%**（上轮 −0.12%），**失血重新加速**；7d −1.84%。**与本轮「风险资产止跌」方向相反 —— 钱还在离场。**
- **🟡 口径事故（本轮最重要的一条，已修正上轮数字）：** 上轮记的总 TVL **$139.98B** 来自 legacy `/charts` 的**当日 live 桶**；该桶隔日回溯修订为 **11-18 = $143.29B**。同时 `/v2/chains` 求和恒为 legacy 的 **~1/2 系数**（11-19 实测 138.48 vs 69.44 = 1.994）。**两套口径并存，切换口径就会凭空造出 −50% 的假暴跌。本轮起统一用 `/v2` 求和并注明桶日期。**

## Active Narratives
- **「跌势暂停」——24h 广度首次转正** — phase: **emerging**。Evidence: 广度 2/20 → **13/20**、非稳定币 10/16 绿、DEX 量 +3.83%、已结算 TVL 1d **+0.49%**。**但 7d 非稳定币仍 2/16、F&G 10、稳定币 1d −0.90% —— 三条反向，暂判为死猫反弹而非底部。**
- **Sky 生态 TVL 塌方（USDS 供给 −38%）** — phase: **rising**。Evidence: **Sky Lending 1d −41.19% / 7d −46.28%**、Spark Liquidity Layer 1d −14.14%、Spark Savings 1d −9.98%、SparkLend 1d −6.46%；USDS 流通 **$5.24B → $3.24B（1d −38.16%）**，全部发生在 Ethereum 单链（$5.232B → $3.232B）。**同族 Spark 四条同步下坠 = 单一生态事件，不是全市场。⚠️ 反证：CoinGecko 的 USDS 市值仍是 $6.42B，与 DefiLlama 的 $3.24B 差近一倍 —— 可能是口径调整（如 sUSDS 拆分/重挂）而非真赎回，本轮不作实锤，标为待确认。**
- **Aave V3 逆势吸金** — phase: **emerging**。Evidence: Aave V3 **1d +11.28%**（$14.03B → $15.17B）、7d **+2.31%**，是十亿级里唯一双正。**与 Sky/Spark 下坠同轮发生 —— 资金很可能在同类借贷协议间搬家。**
- **12 月加息已是基准情形** — phase: **peak（钝化）**。Evidence: Fed **+25bp 91.5%**（与上轮持平）、no change 2.9%、+50bp **5.3%**（上轮 6.3%，尾部继续收）、25bp 降息 0.2%。**边际变化只剩尾巴，无新增信息。**
- **BTC 下破 60k 的定价在放松** — phase: **fading**。Evidence: 年内触 $60,000 概率 **75.5% → 81.5%（+6pp）**，但 11 月盘「触 60k」从 63.5% → **64.5%**、距现价仅 3.4%。**概率继续抬升但 11 月盘几乎没动 —— 市场把 60k 从「本月」推到「年内」。**

## Top DeFi Protocols (TVL, 7d change)
- LayerZero V2: **$17.72B（+7.34%）** · 1d **+4.09%** —— **十亿级里唯一 7d 正增长，连续第二轮全场最强**
- Lido: $17.00B（−13.73%）· 1d −0.86%
- Aave V3: **$15.17B（+2.31%）** · 1d **+11.28%** —— **十亿级里唯一双正**
- Morpho Blue: $9.66B（−9.48%）· 1d −2.09%
- SSV Network: $9.26B（−13.31%）· 1d −1.66%

（CEX 类不入榜。7d 跌幅同受 ETH 计价影响 —— ETH 同期 −12.64%，即 Lido −13.73% 里约 12.6pp 是计价，真流出约 1pp。）

## Chain Flow (top 3 by TVL, 7d)
- Ethereum: $37.34B（1d **−0.12%** / 7d **−7.73%**）
- Base: $5.20B（1d **+0.10%** / 7d **−9.71%**）
- Solana: $4.80B（1d **+1.89%** / 7d **−4.60%**）

**24h 侧 14 条 ≥$500M 链中 13 条为正或持平**（最好 **Ink +39.45%**（$0.41B，连续两轮爆发，7d **+126.29%**）、Monad +2.13%、Tron +2.05%、Solana +1.89%；最差 **Ethereum / Hyperliquid −0.12%**）。**7d 侧 14 条里 12 条仍负**，仅 **Ink +126.29%**、**Arc +2.81%** 为正；最差 **Bitcoin −11.53%**、BSC −9.76%、Base −9.71%、Avalanche −8.93%。**24h 全线转正而 7d 全线仍负 —— 本轮形态的准确描述，别只报一头。**

## Stablecoins
Total: **$284.70B**（1d **−0.90%** / 7d **−1.84%**）。口径：`peggedAssets` 逐条求和，剔除 `circulating` 非数值项。

USDT $175.09B（1d −0.07% / 7d −0.33%）· USDC $68.78B（1d **−0.78%** / 7d **−1.60%**）· USDe $4.91B（1d **+1.69%** / 7d +0.07%）· DAI $4.61B（1d +0.07% / 7d −1.30%）· **USDS $3.24B（1d −38.16% / 7d −39.51%，待确认，见上）** · USD1 $2.89B（7d **−11.15%**）· RLUSD $2.82B（7d **+4.36%**）· USDG $2.61B（7d −3.34%）· **PYUSD $2.38B（1d −3.10% / 7d −12.56%）** · USDf $1.61B（1d **+8.43%**）。稳定币占全市场 mcap **13.25%**（上轮 13.31%，基本持平）。

**脱锚检查（≥$500M，bp）：USDf −36.6bp**（$1.61B，连续第十二轮最深，但已从 −41.6bp **再收窄 5.0bp**）· **USDD −31.8bp（连续第二轮恶化）** · USDT −11.1bp · USD1 −10.1bp · USD0 −10.1bp · TUSD −9.5bp。**USDf 出现「折价收窄 + 1d 供给 +8.43%」同向第二日 —— 上轮的首现已确认为趋势而非单日噪声。**

## Trending (CoinGecko)
- **VVV（Venice Token）** — $21.92，**+4.15%**，rank 67，mcap $1.07B —— **本轮 trending 涨幅最大**
- **PEARL** — $2.297，**+2.35%**，rank 73，mcap $883M —— **连续第二轮在榜**
- **HYPE** — $67.07，**+1.80%**，rank 10，mcap $15.9B —— **唯一进入 trending 的十亿级以上标的**
- **BTC** — $62,174，−0.04%，rank 1 —— **连续第八轮在榜**
- **ETH** $1,760.44，+0.27%，rank 2 · **ZEC** $891.67，−0.66%，rank 11 · **PENGU** −1.09% · **MON** $0.0136，**−3.08%**（rank 177）· **BP（Backpack）−15.01%**，rank 150，mcap $213M

## Prediction Markets (Polymarket)

**Fed Decision in December?（24h 量约 $3.47M 合计）**

| Market | YES% | 24h Vol | Liquidity |
|--------|------|---------|-----------|
| Fed **increase** 25bps | **91.5%** | $60k | $858k |
| Fed **increase** 50+bps | **5.3%** | $321k | $438k |
| Fed no change | **2.9%** | $1.22M | $541k |
| Fed **decrease** 25bps | 0.2% | $183k | $763k |
| Fed **decrease** 50+bps | 0.1% | $945k | $240k |

**BTC 2026 年内（`what-price-will-bitcoin-hit-before-2027`，活跃档）**

| Market | YES% | 24h Vol | Liquidity |
|--------|------|---------|-----------|
| BTC dip to **$60,000** | **81.5%** | $98k | $112k |
| BTC dip to **$55,000** | **44.5%** | $51k | $114k |
| BTC dip to **$50,000** | **23.5%** | $67k | $111k |
| BTC dip to **$45,000** | 9.8% | $46k | $168k |
| BTC reach **$90,000** | **4.5%** | $49k | $186k |
| BTC reach **$110,000** | 1.6% | $73k | $132k |
| BTC reach **$1,000,000** | 0.15% | **$201k** | $368k |

**BTC 11 月（`what-price-will-bitcoin-hit-in-november-2026`，24h 量约 $333k）**：**↓$60,000 已 64.5%**（上轮 63.5%）、↓$57,500 **33.1%**、↓$55,000 18.3%；向上 ↑$65,000 **57.0%**、↑$67,500 27.5%、↑$70,000 10.5%。**剩余 11 天，↑$65,000 的 57.0% 高于 ↓$60,000 的 64.5% 的镜像位置 —— 市场重心仍在下但已给出 ~57% 的回到 65k 概率。**

**本轮最强读数：年内触 $60,000 从 75.5% 抬到 81.5%（+6pp），而现价距该位仅 3.4% —— 概率抬升的同时 11 月盘只动了 1pp，等于市场把「跌破 60k」的时间点从本月推到了年内。**

## Macro Catalysts (next 48h)
- **11 月 18 日期权到期已过**（上轮标记的唯一确定波动源），BTC 仍死守 62k —— **gamma 释放未带来方向，本身是「无承接」的读数。**
- **12 月 FOMC 前 48h 内无重大通胀数据**（按已知日历）。加息盘 91.5% 无边际变化。**短期驱动仍只有仓位与技术位。**

（WebSearch 连续第七轮不可用 —— 两条查询均返回「本会话无浏览权限」的方法论文本而非当日新闻，见 footer。以上两条从 Polymarket 结算日历 + 已知数据日历推出，非新闻转述。）

## Implications for Downstream Skills
- **token-pick:** **继续不建多头，但本轮理由从「全面下行」改成「反弹未确认」。** ①24h 广度 13/20 是 11-13 以来首次转正，但 **7d 非稳定币仍 2/16**；②F&G **10** 在底部横 5 天，无筑底形态；③稳定币 1d **−0.90%** 重新加速失血 —— 与风险资产止跌方向相反，是「钱没回来」的直接证据。**唯一可看的相对强度：Aave V3 1d +11.28% / 7d +2.31%、LayerZero V2 1d +4.09% / 7d +7.34%、Ink 链 7d +126%。** 三者分别是「借贷搬家」「跨链消息层」「新链上线」三种不同成因，不可互证。**避开：Sky/Spark 生态（四条同步 −6% 至 −41%，口径未澄清前不接）、ETH 高 beta 质押（Lido 7d −13.73%、SSV −13.31%）、BTC 封装（WBTC 7d −13.12%）、PYUSD 生态（7d −12.56%）。**
- **narrative-tracker:** 三处相位变动 —— ①**新增「跌势暂停」emerging**：24h 广度 2/20 → 13/20、DEX 量 +3.83%，**但三条反向信号未消，需下轮确认是反弹还是死猫**；②**「BTC 下破 60k」从 rising 降为 fading**：年内概率虽 +6pp 至 81.5%，11 月盘只 +1pp，**时间被推后**；③**新增「Sky 生态塌方」rising**：四条协议同步下坠且 USDS 供给 −38%，**但 CoinGecko 市值对不上，标为待确认**。④「12 月加息」peak 维持，91.5% 已钝化。

## Token Picks Made
| Date | Token | Price | Thesis |
|------|-------|-------|--------|
| — | — | — | No picks recorded yet |

---
*Sources — btc/eth: CoinGecko · defi: DeFiLlama · sentiment: alternative.me · markets: Polymarket*
*Source status: coingecko=ok defillama=ok fng=ok polymarket=ok websearch=**fail***

*Note: **总 TVL 两套口径并存，这是本轮最严重的读数陷阱。** legacy `https://api.llama.fi/charts`（字段 `totalLiquidityUSD`，`date` 是字符串）11-19 live 桶 **$138.48B**；`https://api.llama.fi/v2/historicalChainTvl`（字段 `tvl`，`date` 是整数）同桶 **$69.44B**。实测比值逐日稳定在 **1.99–2.05**，即 `/v2` 求和恒约为 legacy 的一半。**上轮报的 $139.98B 是 legacy 当日 live 值，隔日已修订为 $143.29B（11-18 桶）—— 当日 live 桶不可跨轮比较。** 本轮起统一用 `/v2` 求和并注明桶日期。*

*Note: **TVL 7d 窗口 11-11 → 11-18（均已结算）：$76.78B → $71.32B = −7.11%**；同期 ETH $2,050.34 → $1,759.14（**−14.20%**）⇒ **ETH 计价口径 7d 约 +8.3%，USD 跌幅全部且超额由计价货币贡献。** 这与上轮"USD −10.12% / ETH 计价 +4.58%"方向一致，幅度收窄。*

*Note: **DEX 量 `change_7dover7d` 连续第二轮转正并扩大：+2.46% → +8.02%。** 绝对值 $7.775B（上轮 $7.480B）**同时上升** —— 这是自 11-11 以来第一次"同比基数与绝对值同向回升"，但仍在 $7.8B 低位（对比 11-05 的 ~$10B）。*

*Note: **fees-beating-TVL 过滤器本轮 5 条**（join `/protocols` 取 `tvl`/`change_7d`，闸：fees24h ≥$100k、24h÷7d日均 ∈(20%,200%]、TVL ≥$100M、TVL 7d <+5%）：**PumpSwap（fees7d **+34.00%** / TVL 7d −6.82% / f24 $3.01M）**、**Jupiter Perpetual Exchange（+30.14% / −6.53% / `7dover7d` **+53.53%**）**、Orca DEX（+22.11% / −4.19%）、**Aave V3（+20.46% / +2.31%，TVL 微涨仍在闸内）**、Grove Finance（+20.02% / −3.44%）。**前两条同时满足「增速大 + TVL 未涨 + 7dover7d 强」，是真正的手续费驱动需求；Aave V3 属 TVL 同涨不作异动解读。***

*Note: **real-yield 过滤器 323 条（上轮 327，基本持平），incentive 51 条（上轮 49）。** 本轮加了一条硬闸 `ilRisk == 'no'`，把榜首的无常损失型 DEX 池（WBTC-USDT 21.17%、ETH-WBTC 18.28%）全部剔除 —— **这些池的 `apyBase` 含 IL 补偿，不是真实收益，不该进"可持续收益"栏。** 剔除后真实榜首：**USDC/hyperliquid-hlp 18.63%（$154M，但 m30 仅 9.56% ⇒ 30 日均值不到当前一半，符合 `apyMean30d >= apy*0.5` 闸但接近边缘，需标注）**、APXUSD/apyx 13.63%（$125M，m30 13.18% 稳定）、USDDW/drakewell 12.14%、USDC/accountable 12.12%、REUSDE 11.82%。incentive 侧首位仍是 **USDS/sparklend 17.26%**（$88.8M，`apyBase=None` 纯奖励）—— **但 Spark 生态本轮 TVL 塌方，这条收益的可持续性打问号。***

*Note: **Positions facet 本轮 `DEFI_MONITOR_NO_CONFIG`** —— `memory/on-chain-watches.yml` 6 条 watch 全为 `type: wallet` / `type: contract`（归 `onchain-monitor`），无 `type: pool` / `type: position`。按 SKILL.md 干净跳过，不计错误。*

*Note: **WebSearch 连续第七轮完全不可用** —— 两条查询（宏观催化剂 / BTC ETF 流量）均返回"本会话无浏览权限，不能给 2026-11-19 验证数据"的方法论文本。**这是源状态的真实原因，不是漏查。***

*Note: **Polymarket 本轮 `fed-decision-in-december-2026` 查无此 slug**（返回空数组），实际 slug 带时间戳后缀 `fed-decision-in-december-20260729232808632`，须走 `tag_slug=fed-rates` 列表检索再取。**又一次印证：不要把推断出的 slug 当事实，先查列表。** 另：`/events?slug=` 返回的 `markets[]` 里 `↓60,000` 出现三条（YES 100%/100%/81.5%），必须按 3%–97% 过滤才是有效读数。*




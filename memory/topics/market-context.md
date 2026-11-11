---
title: Market Context
description: Rolling crypto macro snapshot — regime take, signal deltas, narratives, DeFi fundamentals, yields, prediction markets. Consumed by token-pick and narrative-tracker.
tags:
  - crypto
  - macro
  - defi
  - market-context
resource: https://defillama.com
timestamp: 2026-11-11T23:20:00Z
---

# Market Context (as of 2026-11-11)

> **Take:** **chop** — 24h 是横盘喘息（BTC **$73,839（+0.38%）**、ETH **$2,054.86（+0.54%）**、top-20 等权 **+0.00%**），但 7d 广度只剩 **1/20**（唯一收正的 FIGR_HELOC 还是代币化房贷，不是 crypto beta）。Conviction: **low** —— 24h 广度从 3/20 回到 8/20 与 F&G 从 32 落到 29 互相矛盾；**单日反弹发生在单周崩跌之内，不是转身。**

## Signal Snapshot
- BTC **$73,839**（+0.38% 24h, **−7.91% 7d**）· dominance **59.90%**（昨 60.20%，**−0.30pp**）
- ETH **$2,054.86**（+0.54% 24h, **−14.96% 7d**）· ETH/BTC **0.027829**（昨 0.028548，**−2.52%**）
- SOL **$83.42**（+0.80% 24h, −11.95% 7d）
- Total mcap **$2.472T** · DEX vol **$8.335B**（Llama 24h 汇总口径，`change_1d` **−8.49%**）
- Breadth: **8/20 green 24h** · **1/20 green 7d**
- **非稳定币广度：8/16 green 24h** · **1/16 green 7d**（仅 FIGR_HELOC +1.67%）
- Fear & Greed: **29（Fear）** — 昨日 **32（Fear）**，11-09 29，11-08 28，11-07 25（Extreme Fear）

## What Changed Since Last Refresh

上次快照写于 **11-09T00:30Z**，中间 11-09 / 11-10 两个 23:00Z 槽位全废（403 + 断路器跳闸），**距现在旧 2 天**。本轮五处实质变化：

- **🔴 上轮的核心结论被推翻：那天的 TVL 下跌是 ETH 计价贬值，不是资金流出。** 上轮文件写「11-08 桶 79.058B 对 11-07 的 80.868B 为 −2.24%，ETH 同期只动 0.03% → 真资金流出」。**本轮回查同一批桶，编号错了一天**：API 现在 11-08 = **80.868B**、11-09 = **79.091B**。按正确配对算 **11-08→11-09：USD −2.20%，ETH 价格 −5.04%，ETH 计价 +2.99%** —— **方向完全相反：TVL 以 ETH 计是涨的，跌幅全部来自计价货币。** 上轮「真资金流出」的判断作废，不得再引用。
- **TVL 全周同理：USD −4.29% 是幻觉，ETH 计价 +6.13%。** 11-04 桶 81.884B / ETH 2,273.63 → 11-11 桶 **78.368B / ETH 2,050.34**。ETH 本身周内 −9.8%，TVL 换成 ETH 计价后**净增**。**本周 DeFi 的「资金撤退」叙事是价格引起的，不是赎回引起的。**
- **7d 广度塌到 1/20，是本文件历史最差。** 上轮 3/20 收正（USDT/USDS/USDe 三个稳定币，非稳定币 0/15）。今天 24h 侧回升到 8/20，**但 7d 侧只剩 FIGR_HELOC**（+1.67%）—— 一个代币化房贷产品。**同期 ZEC −24.64%、XRP −19.11%、ETH −14.96%、HYPE −13.98%、DOGE −12.14%，top-20 里没有一个真币 7d 收正。**
- **F&G 反向走：32 → 29。** 上轮记 29（昨 28），今日仍是 29，**但昨日读数被修订为 32** —— 即真实路径是 29 → 32 → **29**，**不是持平，是冲高后回落**。恐慌未解除，且在反弹日继续回落。
- **12 月加息盘一夜之间从 76.5% 跳到 85.5%（+9.0pp），是本轮最强的单一信号。** 上轮连续三日读数 76.5% 纹丝不动、判为「本轮不构成信息」；**今天这条横盘结束了**：25bps increase 85.5%、50+bps increase 11.1%、no change 仅 3.0%。**市场把 12 月几乎完全定价成加息，且开始分配 50bp 以上的尾部。** 这与「稳定币 7d −1.68%、DEX 量低于同星中位 −19.4%」同向 —— **钱在撤出风险资产，并在为更紧的路径付溢价。**

## Active Narratives
- **ETH 相对 BTC 失血** — phase: **rising（加速）**。Evidence: ETH 7d **−14.96%** vs BTC −7.91%，**7d 超额 −7.0pp**；ETH/BTC 两日内 0.028548 → **0.027829（−2.52%）**；ETH 生态 TVL 同步（Lido 7d −13.57%、SSV −12.56%、EigenCloud −14.04%）。上轮记为 emerging，本轮升级。
- **12 月加息重定价** — phase: **rising（跳变）**。Evidence: 25bps increase **76.5% → 85.5%**，no change 76.5%→**3.0%**，50+bps increase 已到 **11.1%**。上轮「连续三日 76.5% 横盘」的判断终结。
- **稳定币收益率轮动（USDS/USD1 → USDe/RLUSD）** — phase: **peak（掉头）**。Evidence: 7d USDS **−17.88%** / USD1 **−14.38%** 继续大失血，但**吸金端熄火**：USDe 7d 从 +10.47% 降到 **+6.89%**、RLUSD 从 +11.34% 降到 **+5.30%**；总量 7d **−1.68%**。**出逃还在，接盘的增速砍半 —— 轮动变成净流出。**
- **隐私币抗跌** — phase: **fading（结束）**。Evidence: **ZEC 7d −24.64%**（top-20 最差）、XMR 7d −9.04%。上轮还记「只剩残余」，本轮残余也没了。
- **Hyperliquid 退潮** — phase: **fading（加深）**。Evidence: HYPE 7d **−13.98%**、链 TVL 7d **−7.40%**；但 **Hyperliquid Perps fees 7d +23.05%**、Spot Orderbook fees 7d **+82.9%** —— **量与价背离，手续费侧还没跟着塌。**

## Top DeFi Protocols (TVL, 7d change)
- Lido: $20.26B（−13.57%）· 1d +1.20%
- LayerZero V2: $16.15B（−10.42%）· 1d −2.28%
- Aave V3: $15.37B（−3.92%）· 1d +2.03%
- SSV Network: $11.01B（−12.56%）· 1d +1.83%
- Morpho Blue: $10.94B（−4.25%）· 1d +0.93%

（CEX 类不入榜。**注意：这些 7d 跌幅同样以 ETH 计价会被抵消大半 —— 见上方 TVL 计价口径说明。**）

## Chain Flow (top 3 by TVL, 7d)
- Ethereum: $41.40B（USD −5.39% / **ETH 计价 +4.92%**）
- Base: $5.83B（USD −1.37% / **ETH 计价 +9.37%**）
- Solana: $5.09B（USD −5.44% / ETH 计价 +4.85%）

**24h 侧 13 条 ≥$500M 链无一触及 ±5% 门槛**（最大 Arc +3.51%、最小 Sui −4.48%），本轮无链级异动。7d 侧为正的 3 条：**Avalanche +5.56%（连续第四轮最强）、Monad +3.90%、Arc +3.47%**；最差 **Plasma −15.75%、Polygon −11.11%、Sui −8.55%、Hyperliquid L1 −7.40%**。

## Stablecoins
Total: **$290.08B**（1d **−0.44%** / 7d **−1.68%** / 30d **−4.94%**）。口径：剔除 `circulatingPrevDay == 0` 的新上架条目（本轮 2 条：USDX +$683.4M、USDL +$9.0M，合计 **+$692.4M** 纯伪增量；未剔除读成 290.77B）。

USDT $175.67B（1d −0.34% / 7d −1.40%）· USDC $69.86B（1d −0.74% / 7d −1.51%）· **USDS $5.36B（7d −17.88%）** · **USDe $4.90B（1d −1.50% / 7d +6.89%）** · DAI $4.66B（1d +0.10%）· **USD1 $3.25B（1d −2.76% / 7d −14.38%）** · PYUSD $2.66B（1d −3.22%）· USDG $2.70B（7d −2.30%）· **RLUSD $2.70B（7d +5.30%）** · USDf $1.66B（7d −0.62%）。稳定币占全市场 mcap **11.73%**。

**单日最大失血已从 USDS 换成 PYUSD（−3.22%）与 USD1（−2.76%），而 USDe 也转为 −1.50% —— 上轮唯一还在吸的腿今天也在掉。** 脱锚检查（≥$500M，bp）：**USDf −55.2bp**（$1.66B，价格 0.99448，**连续第九轮最深，且从 −46.6bp 走阔回 −55.2bp**）· USD0 −22.6bp（$0.54B）· USD1 −17.2bp（$3.25B）· GHO −15.8bp · USDD −10.8bp · USDT −10.3bp · USDe −5.6bp。**USDf 折价重新走阔 8.6bp，与它 7d 供应 −0.62% 同向 —— 量价同弱第九轮。**

## Trending (CoinGecko)
- **BTC** — $73,869, +0.20% —— **连续第五轮在榜**
- **ZEC** — $978.29, **−6.89%** —— 逆势上榜，价格已从 11-09 的 $1,222 再下两档
- **GRAM**（原 Toncoin）— $1.177, **+3.40%**，mcap $3.36B / rank 29
- **AVAX** — $8.487, +1.54%，mcap $3.78B / rank 26
- **LIT**（Lighter）— $3.237, **−6.27%**，rank 79
- **PEARL** — $1.582, **+6.37%**，rank 92 · **ZIG** rank 419 −1.99% · **PENGU** +0.38% · **TAO** −0.74% · **DOGE** −0.91%

（**ZEC 连续上榜且双向大跌，是本轮唯一同时出现在 trending 与 7d 最差榜的标的。**）

## Prediction Markets (Polymarket, top by relevance)

`order=volume24hr` 前八**清一色体育/赛事**（Jensen Huang 辞职盘 $1.63M 居首，其余 Celtics/Raptors、UFC、WTA、LoL），crypto/宏观盘必须走 `public-search` 命中。本轮实证：

| Market | YES% | 24h Vol | Liquidity |
|--------|------|---------|-----------|
| Fed Dec — 25bps increase | **85.5%** | $176k | $734k |
| Fed Dec — 50+bps increase | **11.1%** | $655k | $403k |
| Fed Dec — no change | **3.0%** | $229k | $460k |
| Fed Dec — 25bps decrease | 0.4% | $116k | $460k |
| BTC ↓ $70,000 by Dec 31, 2026 | **63.5%** | $2k | $87k |
| BTC ↓ $65,000 by Dec 31, 2026 | **31.5%** | $27k | $67k |
| BTC ↓ $60,000 by Dec 31, 2026 | **18.5%** | $27k | $79k |
| BTC ↑ $90,000 by Dec 31, 2026 | 16.5% | $46k | $77k |

**Fed 盘是本轮唯一有信息量的读数：25bps increase 从上轮 76.5% 跳到现在 85.5%，同时 50+bps 腿 24h 成交 $655k 居各腿之首 —— 不是在巩固加息，是在给「加得更多」定价。** BTC 年内：跌向 $70k 已 **63.5%**（上轮 60.5%），触 $60k **18.5%**，向上 $95k 仅 **7.5%**、$100k **5.5%** —— **下行偏度继续加深，且 $90k 上方只剩 16.5%。**

**11-11 当日「站上 ___」盘已 17:00Z 结算**：$74,000 及以上全部 100% YES、$76,000 及以上全部 0% —— **今日 BTC 收在 74k 下方的 72k–74k 区间，正好贴住现价 $73,839，与上轮「74k 就是平衡位」的判断一致，且这次是跌破。**

## Macro Catalysts (next 48h)
- **10 月 CPI 落在 11-12～11-14 窗口内，距今 1–3 天。** 加息盘把 12 月定价到 **85.5%**（一夜 +9.0pp），**这份 CPI 是唯一能在 FOMC 前推翻该定价的单一事件**。若 CPI 超预期，50+bps 那条腿（已 11.1%）会继续走；若不及预期，85.5% 有回吐空间 —— **双向都构成本周最大的单点波动源。**
- **11-11 是美国 Veterans Day，债券市场与联邦机构休市，crypto 照常交易。** 成交簿薄，**今日 DEX 量 $7.73B（今日桶，未归一）本身不可与常态比较**，任何单日放大的波动都要先怀疑是流动性缺口而非供需。

（WebSearch 本轮仍不可用，无任何可引用头条 —— 见 footer。以上两条均从 Polymarket 结算日历 + 已知数据日历推出，非新闻转述。）

## Implications for Downstream Skills
- **token-pick:** **继续不建多头，理由与上轮不同——这轮不是「广度崩塌」，是「计价与定价双杀」。** ①7d 广度 1/20、非稳定币 1/16，唯一收正是代币化房贷，不构成 beta；②F&G 反弹日仍从 32 回落到 29；③12 月加息盘 85.5% + 50bp 尾部 11.1%；④稳定币总量 7d −1.68% 且**吸金端 USDe/RLUSD 增速砍半**。**同时必须修正一个上轮的错误买入依据：TVL 的 USD 跌幅不能当资金流出的证据** —— ETH 计价下本周 TVL +6.13%，Ethereum +4.92%、Base +9.37%。**避开**：ETH 生态高 beta 质押（Lido 7d −13.57%、SSV −12.56%、EigenCloud −14.04%）、ZEC（7d −24.64% 且单日 −6.89%）、XRP（−19.11%）、Polygon（链 TVL 7d −11.11%）、Plasma（−15.75%）。**Avalanche 7d +5.56% 连续第四轮最强，但仍不放行** —— 前三轮已拆穿是长尾驱动，本轮 $0.613B 规模内主协议零增量。
- **narrative-tracker:** 本轮三处相位变动 —— ①**「ETH 相对 BTC 失血」emerging → rising（加速）**（7d 超额 −7.0pp、ETH/BTC 两日 −2.52%）；②**「12 月加息重定价」新进 rising（跳变）**（76.5%→85.5%，上轮「三日横盘」判据终结）；③**「稳定币收益率轮动」rising → peak（掉头）**（出逃还在、接盘增速砍半、总量 7d 转负）。**两处终结**：隐私币 fading → 结束（ZEC 7d −24.64%，残余也没了）；Hyperliquid 退潮 fading 加深但**出现价量背离**（HYPE −13.98% vs Perps fees +23.05%），值得盯下一轮是否收敛。

## Token Picks Made
| Date | Token | Price | Thesis |
|------|-------|-------|--------|
| — | — | — | No picks recorded yet |

---
*Sources — btc/eth: CoinGecko · defi: DeFiLlama · sentiment: alternative.me · markets: Polymarket*
*Source status: coingecko=ok defillama=ok fng=ok polymarket=ok websearch=**fail***

*Note: **本轮最重要的一处纠错 —— 上轮文件（11-09）把 TVL 桶的日期标错了一天，导致结论方向反了。** 上轮写「11-08 桶 79.058B 对 11-07 的 80.868B 为 −2.24%，ETH 同期只动 0.03% → 几乎全是真资金流出」。本轮回查同一批 API：**11-08 桶实为 80.868B、11-09 桶为 79.091B** —— 上轮把 11-09 的值贴上了 11-08 的标签。按正确配对，**11-08→11-09：USD −2.20%、ETH 价格 −5.04%、ETH 计价 +2.99%**。**结论从「真资金流出」翻转为「纯计价贬值、以 ETH 计还在流入」。** 方法论：桶编号必须从 ts 直接换算成 UTC 日期再写，不能靠「倒数第 N 个」推。*

*Note: **TVL 双计量口径已成默认必做项，本轮全周适用。** 11-04→11-11：USD **−4.29%**，ETH 计价 **+6.13%**（ETH 价格同期 −9.8%）。分链：Ethereum USD −5.39% / ETH 计价 **+4.92%**；Base −1.37% / **+9.37%**；Solana −5.44% / **+4.85%**。**任何「DeFi 资金撤退」的说法，不附 ETH 计价读数一律不可采信。** 这是对 11-07 那轮（「跌幅主要是计价货币贬值」）与本轮（同向但更强）的第二次确认。*

*Note: **DEX 量口径两处必须分开写，本轮 $8.335B 与 $7.726B 是两个不同的东西。** `/overview/dexs` 的 `total24h = $8.335B`（滚动 24h，`change_1d −8.49%`）；`totalDataChart` 最新桶 **11-11 = $7.726B（当日未结算）**。用同星 12 周中位数归一：**11-10（周二）$8.332B = −19.4% vs 周二中位 10.333B**，11-09（周一）$9.108B = −10.9%，11-08（周日）$6.274B = −11.2%，11-07（周六）$4.948B = −23.9%。**连续四个已结算桶全部低于同星中位 10–24%，这不是周末效应，是持续缩量。***

*Note: **F&G 的「持平」是修订造成的假象。** 上轮文件记「今日 29、昨日 28」；本轮拉 10 日序列发现昨日（11-10）实为 **32**，今日回到 **29** —— 真实路径 28 → 29 → **32 → 29**。**纪律：F&G 会回溯修订，跨轮比较必须一次拉 ≥3 日序列重算，不能拿上一份文件里的「昨日值」当基准。***

*Note: **Polymarket 按量排序第 N 轮完全失效，且本轮失效更彻底** —— `order=volume24hr` 前八清一色体育赛事（第 1 名 Jensen Huang 辞职盘 $1.63M 是唯一非体育项，第 2 名起全是 NBA/UFC/WTA/LoL）。**Fed 盘不在前 100**，必须 `public-search?q=` 命 slug 再 `events?slug=` 展开。另：Fed 盘事件 slug 带时间戳后缀 `fed-decision-in-december-20260729232808632`，不能按标题猜。*

*Note: **WebSearch 连续第四轮完全不可用**（两条查询均返回无浏览权限）。宏观催化剂只能从 Polymarket 结算日历 + 已知数据日历推，**未取得任何可引用头条** —— 这是源状态的真实原因，不是漏查。11-11 为美国 Veterans Day 休市，已写入 Catalysts。*

*Note: **`/v2/chains` 第四次确认无 `change_1d`/`change_7d` 字段**（本轮 421 条全 null），链级 delta 一律走 `/v2/historicalChainTvl/{chain}` 自算桶对桶，共取 16 条链 + 总链 TVL。**`/overview/dexs` 与 `/overview/fees` 的 `change_7d` 字段名有误导**：实为 `total24h/total7DaysAgo−1`，不是 7d-over-7d。*

*Note: **稳定币伪增量本轮仍是必修**：452 条里 2 条 `circulatingPrevDay.peggedUSD == 0`（USDX +$683.4M、USDL +$9.0M），合计 **$692.4M**；未剔除读成 290.77B（1d −0.21%），剔除后 **290.08B（1d −0.44%）**。另 99 条当前值为 0（多为欧元/退市稳定币），不参与计算。*

*Note: **real-yield 过滤器本轮 270 条**（`ilRisk==no` + `exposure==single` + reward 占比<50% + conf≥2 + mean30≥apy×0.5 + TVL≥$10M + outlier==false），榜首 SUSDAT 23.24%（Saturn, $37M）、HGRAM 16.94%（HIPO, TON, $11M）、SUSDX 15.48%（Axis, $55M）—— **与上轮同量级，子集稳定。APXUSD 13.06% 但 TVL $137M 是本组最大池，值得单独记。** 注意 `apyReward` 为 null 的池在 jq 里需按 0 处理，否则会被 `>0` 过滤掉（本轮初跑漏掉一批）。*

*Note: **fees-beating-TVL 过滤器本轮初跑出现 30 条，绝大多数是伪信号**（fees 7d +2500%、+1164% 等），根因是分母过小 + 单日尖峰。加两道闸后剩 8 条：fees24h ≥ $100k 且 `change_7d` ∈ (20%, 200%] 且 TVL ≥ $100M。**判据升级：`change_7d` 超过 200% 一律先当口径异常/极低基数，不入选。** 幸存首位 Convex Finance（fees 7d +103.5% / TVL 7d −8.30%），但其 fees24h 仅 $0.19M 且单日 +705.6% —— **主因是 spike，不是需求趋势，不入通知正文。***



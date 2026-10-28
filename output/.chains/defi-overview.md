ℹ️ Crypto 2026-10-28 · chop（low）

*Crypto — 2026-10-28（23:15Z 复跑）* — chop（conviction low）| DeFi Mixed：TVL 剔除假涨后 −1.6%，量 +13%

*Take:* chop — BTC $81,206（+0.50%），24h 广度 17/20，但 7d 只剩 3/20、F&G 卡在 51 一动不动。绿的是平盘日，不是拐点。

*仓位* DEFI_MONITOR_NO_CONFIG —— `on-chain-watches.yml` 无 `type: pool/position`，无仓可查。

*TVL:* $88.67B（+0.75% 24h / −3.07% 7d / −7.70% 30d）
⚠️ *+0.75% 是假数*：Bitcoin 链一夜跳 +$1.99B（4.29→6.27B），但 85 个非 CEX Bitcoin 腿合计只 +$113M（+0.31%），全聚合只涨 $0.66B。**剔掉 Bitcoin 链，实际 −1.59%。**

*Top chains（1d / 7d）*
1. Ethereum — $46.37B（−3.86% / −7.67%）30 天最大单日跌幅
2. Bitcoin — $6.27B（+46.42% / +41.52%）← 覆盖缺口，见图注
3. Base — $6.08B（+0.81% / −2.89%）

*Movers（非 CEX；CEX 整层仍作废）*
↑ SunSwap V4 +25.65%（$0.107B→$0.135B）— Tron 单链，无公告
↓ SUNSwap V3 −30.60%（$0.216B→$0.150B）— 同链同项目，V3→V4 迁移
↑ Aero Slipstream +11.45%（$0.106B→$0.118B）— Base 腿主导，7d +3421% 是新上池
↓ Anemoy Capital −16.02%（$0.283B→$0.238B）— 纯 Ethereum RWA 单腿
↓ Spark Savings −10.97%（$1.58B→$1.41B）— ETH $973M + Arbitrum $310M 双降

*Fees leaders（24h）*
1. Tether — $17.26M（−0.3% vs 7d 均值）
2. Circle USDC — $6.80M（−1.0%）
3. PumpSwap — $3.00M（−1.5%）

*Fees 跑赢 TVL（7d）*
• Morpho Blue — 费用 +24.31% / TVL −1.58% —— 唯一活口

*DEX vol（24h）：* $7.97B（+13.0% vs 10-27 $7.05B，+6.4% vs 7d 均值 $7.49B）—— 四轮来第一个真涨日
top: Uniswap V4 $1.089B（+16.1%）· Uniswap V3 $0.933B（−6.9%）· PancakeSwap V3 $0.592B（−7.8%）

*Stables:* $302.64B（−0.02% 24h / −0.61% 7d）—— 第三个周净负。**USDD −15.53% 到 $1.50B**（周内从 $1.776B 掉下来，非首现，不是新脱锚）

*Real yield（可持续，≥$10M，已过滤）*
• WETH-USDT（Uniswap V3, ETH）— 38.38% apyBase（$89M TVL，IL 有，30d 均值 28.98%）
• APXUSD（Apyx, ETH）— 13.06% apyBase（$153M，单腿稳定币，30d 均值 12.95%）
• ONYC（Onre, Solana）— 11.02% apyBase（$292M，单腿，30d 均值 11.02%）

*Incentive yield（points / emissions，≥$25M）*
• CVXCRV（Convex, ETH）— 15.04% 全靠 $CRV/$CVX/frxETH 奖励（$49M）
• USDS（Sky Lending, ETH）— 8.18% apy，其中 8.18% 全是奖励（$160M）

*Macro:* BTC $81,206（+0.50% / 7d −4.21%）· ETH $2,358（+0.48% / −5.54%）· SOL $102.44（+1.27%）· F&G 51（Neutral，昨 51 平）· 广度 17/20（7d 3/20）· BTC 占比 59.46%（+0.05pp）
*预测市场：* 以色列大选三席占成交量前五 ——「Netanyahu 任下任总理」YES 50.5%（$5.86M，量第一）。**10 月 FOMC 已结算：不变息 100%**；12 月盘口反过来定价 **加息 25bp 79.0%**。

_sources: llama_tvl=ok llama_dex=ok llama_fees=ok llama_stables=ok llama_yields=ok coingecko=ok fng=ok polymarket=ok websearch=fail（第 6 轮 400）| var: none_

*两条口径警告*
1. `/overview/dexs` 的 `total24h` 滞后一个日历日 —— 字段 $7.059B 精确等于图表 **10-27** 的 $7.053B、`total48hto24h` $8.418B 等于 **10-26**。字段的 `change_1d` −16.14% 算的是 10-26→10-27，不是今天。今日真值走图表：+13.0%。
2. 昨天日志里 DEX「$5.99B / −1.86%」是盘中截取未走完的 10-27 桶，该日完成为 $7.053B。别拿昨天的量跟今天比。
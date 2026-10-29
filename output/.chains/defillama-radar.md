**defillama-radar** · 2026-10-29 00:16Z · 可报 4

来源：`https://api.llama.fi/protocols` · 源站 `last-modified 23:38:07Z` · `cf-cache-status: MISS` · 全量 8873 条

**1. Fynd AMM** · DEX · Robinhood Chain/Base/Binance/Ethereum · TVL $72,463 · 登记 10-28 21:50Z · `id 9267`
AMM 池扩展层：每笔交易扫描竞争池，把费率压到最优竞争池之下抢订单流。
https://swap.fynd.xyz/pools

**2. Megawatt Markets** · 衍生品 · Arbitrum · TVL $2,704 · 登记 10-28 18:00Z · `id 9260`
链上订单簿，交易美国 7 个电力市场的日度电力期货。

**3. Alokumi** · 流动性自动化 · Solana · TVL $1,603 · 登记 10-28 21:55Z · `id 9268`
Meteora DLMM 的 LP Agent：自然语言写做市规则，Agent 在非托管金库内跑。

**4. Hamstr** · 收益聚合器 · Base · TVL $109 · 登记 10-28 22:00Z · `id 9270`
存 USDC/ETH 在 Aave V3 出借，只把收益换成 cbBTC，本金不动。

**漏斗**：新增 id 4（可报 4 / 过滤 1）· 重报 1（`Megawatt Markets` 上轮未通知，本轮补入）· parent 丢 0 · 类目丢 0 · 链白名单丢 1

**被白名单挡掉**：`Tradecraft`（`id 9269`，DEX，Canton Network，TVL $1,688,251，10-28 21:59Z）—— Canton 不在 `CHAINS`，按铁律记 `filtered`，永不补报。要收这条须加链 + 删 seen 重做基线。

**链命中**：Ethereum=1894 · Binance=1145 · Arbitrum=1045 · Base=915 · Solana=466 · Optimism=392 · Robinhood Chain=294 · Hyperliquid L1=211 · Ink=33 · BSC=0 · OP Mainnet=0

**单侧读数：加密侧 4 / AI 侧 0** —— 本源只有加密侧，这 4 条不构成 AI 方向的任何证据。
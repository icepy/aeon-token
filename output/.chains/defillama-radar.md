**defillama-radar** · 第 10 轮 · 可报 8

全量 8942 · 新增 id 18（可报 8 / 过滤 10）· `HIT` 与源站两份快照 id 集合逐条相同 → 不是缓存假零。

**可报 8 条**（按 TVL 降序，仅名字与地板字段，不做判断）

1. `Axcess` — Ethereum · Uncollateralized Lending · TVL **$97,578** · id 9329 · 11-04 17:26Z
   中文：面向交易机构的无抵押信用协议，用链上金库撮合出借方与机构借方。审计 2 · 无 url · 无 address。
2. `VectaSwap` — Base/Arbitrum · Dexs · TVL **$3,887** · id 9327 · 11-04 17:15Z
   中文：Base 与 Arbitrum 上的集中流动性 DEX（兼容 Uniswap V3），聚合 0x / 1inch / LI.FI / KyberSwap / Velora 路由。审计 0。
3. `yld.cx` — Base/Ethereum/Robinhood Chain · Yield · TVL **$311** · id 9331 · 11-04 19:53Z
   中文：流动性租赁市场，按自定价出借或租入代币。审计 0。
4. `ALPHA Launchpad` — Robinhood Chain/Arc/Base/Binance/Ethereum · Launchpad · TVL **$234** · id 9330 · 11-04 17:30Z
   中文：一次签名发币，可与任意已上币种 / 稳定币 / 股票代币 / 黄金配对。审计 0 · `address` 在 Robinhood Chain（`0x2Da0…A1fa`）。
5. `Nullroot Protocol` — Robinhood Chain · Privacy · TVL **$85** · id 9333 · 11-04 19:59Z
   中文：Robinhood Chain 上的合规隐私池，存款对 OFAC 名单筛查后进关联集，零知识证明提款到新地址。审计 0。
6. `CoinLotto` — Binance/Base/Ethereum · Luck Games · TVL **$9** · id 9325 · 11-04 17:03Z
   中文：任意 ERC-20 发起的链上彩票，Chainlink VRF 开奖。审计 2。
7. `Prediction Arena` — Base · Prediction Market · TVL **$1** · id 9332 · 11-04 19:57Z
   中文：Base 上的彩池制二元预测市场，4% 手续费中 30% 返推荐人。审计 0。
8. `Milk Money` — Solana · Liquidity Manager · TVL **$0** · id 9336 · 11-04 20:15Z
   中文：Solana 上的流动性管理器，用协议自有钱包在 Meteora DLMM 跑集中流动性；treasury 池手续费回购 `$MM`，reward 池分给质押者。**staking $574K · mcap $1.18M**（`tvl=0` 是没算持仓本金，不是空壳）。

**过滤 10 条**（已钉 `filtered`，此后不再报）

- `parentProtocol` 6：Privacy Pools V2(9326) · HedgeHood Share Lending(9328) · StonkBrokers Books(9334) · StonkBrokers Clutch TV(9335) · Dexalot OmniVaults(9337) · Precept(9338)
- 空 `chains` 3：Quotrons(9322) · AetherZone(9323) · liq.fun Predictions(9339)
- 链不在白名单 1：Lubics(9324, SASEUL, TVL $18,201)

**审计读数**：`seen` 命中 8924 · `parent` 7 · `category` 0 · 链白名单 3 · 无 id 0 · 拉取失败 0 · 重报 0 · 基线轮 False。

**数据源**：`https://api.llama.fi/protocols`（2026-11-05 00:0xZ；常规 `HIT` etag `W/"6aebb979-9102c7"`、`last-modified Wed, 04 Nov 2026 23:02:17 GMT`、`age 1082`；源站 `MISS` etag `W/"6aebc1f9-910644"`、`last-modified 23:38:33 GMT`，两份各 8942 条、id 集合差集为空）。
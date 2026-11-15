**defillama-radar** · 可报 2 · 全量 9050 / 新增 22

## 可报（白名单链 + 无 parent + 非 EXCL 类目）

- **Paboxo** · Robinhood Chain · TVL **$4,864** · 借贷 · id 9449
  股票代币借贷市场：存 USDG 生息，或用股票代币 / WETH 抵押借 USDG。借款仅 $58。无 url、无审计。
- **zkAPI** · Ethereum · TVL **$1,478** · 隐私 · id 9431
  用 ETH 预付 API 额度，零知识证明授权调用，使用记录与充值不可关联。无审计。

合计 TVL **$6,342**。两条都是「刚记账」的量级，不是体量信号。

## 本轮读数

- 22 条新增：可报 2 · `parent` 挡 5 · `category` 挡 2 · 空链 / 非白名单链挡 13
- 空 `chains` **15/22**（全量 1637/9050 = 18.09%，连续十二轮 17.4–18.09）
- 链命中：Ethereum 1910 · Base 933 · Solana 476 · Arbitrum 1056 · Binance 1157 · Optimism 394 · Hyperliquid L1 217 · Robinhood Chain 319 · Ink 33
- `BSC` / `OP Mainnet` 双胞胎 0 命中属正常（`Binance` / `Optimism` 分别 1157 / 394）

## 两条「本可能更大」的被挡条目

- **Drakewell SPYdw**(9433) · Ethereum · TVL **$561,619** · 指数 · 仅被 `parent#drakewell` 挡
  本金保护的标普 500 票据，本金存为 USDdw，溢价买 SPY 看涨期权。**单条体量是可报集合计的 89 倍。**
- **nest AVR**(9438) · Elysium Kinetiq · TVL **$1,745,148** · DEX · `parent#nest`
  自动上调手续费的套利价值回收池，以 Hyperliquid 订单簿价格为锚。`audits=2`，本轮唯一有审计的条目。链不在白名单。

## 加密卡发行商一次进来 6 条（旧类目、新批次）

`Crypto Card Issuer` 是**旧类目**（存量 37 条，最早 id 6373），不是新类目。本轮 6 条全部空链、全部 `dummy.js`、全无 TVL：DogPay / Oobit / Cashi / Exodus Pay / Send / COCA。**分两个同秒批次录入**（11-14T09:09:41Z 三条、11-14T13:53:56Z 三条）。

**这是「同类目、跨 parent、同秒」的批量回填 —— 常规形态，不是新东西。** 全量 31 组同秒 ≥3 条簇里，同类目跨 parent 的已出现过 2 次：2022-06-18（Lending：`Aave V1`/`Aave Arc`/`Sushi Kashi`）、2024-03-12（Dexs：`Nile Legacy`/`Cleopatra Legacy`/`Blaster DEX`）。按既有判据整批不必细看。

（注：10-07 那批 22 条桥**不属于**同一形态 —— 它横跨 `Cross Chain Bridge`/`Canonical Bridge`/`Bridge Aggregator`/`Bridge` 四个类目字符串，属「类目也混」的杂类回填。）

## Elysium 边际从 $0 反弹到 $6.6K，结论仍是不加

该链存量 19 → 22 条。本轮 3 条新增挂该链，但加链净边际只有 `StockiumSwap`(9428) **1 条 $6,616** —— `nest AVR` 与 `KleosSwap` 都有 parent，加链救不了。五轮边际 **$514 → $2.6K → $48.5K → $0 → $6.6K**。结论不变：不加，代价是删 9051 条 seen 重做基线。

## 数据完整性

- CF 双取：常规 `HIT`（etag `W/"6af8f0fc-92d5f2"`、11-14T23:38:36Z、`age 216`）与 `?_cb=` 源站 `MISS` **etag / last-modified 逐字节相同**，两向 id 差集皆空，全量 TVL 逐条零差异（两份总和同为 $444,860,934,132.29）。**本轮非假零。**
- 差集 `only_seen=['4818']` **连续第十一轮**（真下架）· `only_raw=[]`
- 最大 id **9449** · 9380–9449 缺 `9382`（连五）/ `9391`（连四），按分配号待回填处理
- 3 条无 `listedAt`：`Goliath AMM` / `Stelaxis` / `TaurusFi`（均空链、`dummy.js`），记 `null` 不回填
- 非数字 id 仍只有 `<5471>`（`OpenTrade`）
- 全量同秒 ≥3 条簇 **31 组**（上轮 29），本轮新增 2 组即上面两批加密卡

---
数据源：`https://api.llama.fi/protocols` · 扫描器 `skills/defillama-radar/scan.py` (`dl-v1`)

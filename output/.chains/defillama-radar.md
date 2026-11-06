**defillama-radar · 第 11 轮** · 可报 3 条

全量 8950 · 新增 id 8（可报 3 / 过滤 5）· `parent` 1 · `category` 0 · 空链 2 · 链白名单 3

**1. Panda Financial** — `Base` · TVL $8,673 · 类目：流动性管理器（Liquidity Manager）
在 Base 上为 Aero 的 WETH/USDC 池做自动流动性管理，每笔存款是一个独立的集中流动性头寸，价格出区间由 keeper bot 搬仓。
`id=9345` · `listedAt 2026-11-05T19:20:36Z` · `url` 空 · 无 `address` · 无 `parentProtocol`

**2. HyperHive** — `Hyperliquid L1` · TVL $2,425 · 类目：风险策展（Risk Curators）
Hyperliquid 原生的风险策展资金分配基础设施，把策略筛选、敞口上限、链上透明路由合成一层。
`id=9346` · `listedAt 2026-11-05T19:24:05Z` · `url` 空 · 无 `address`

**3. Ignite DEX** — `Solana / Ethereum / Binance / Base` · TVL $130 · 类目：DEX
多链现货交易所，中央限价订单簿。用户把资产存入 Ethereum / Base / BNB Chain / Solana / Lithosphere 上的托管金库，交易已上架代币，报价对为 LAX / USDC / USDT。
`id=9344` · `listedAt 2026-11-05T19:16:41Z` · `url` 空 · 无 `address`
注：`chainTvls` 里 Binance 与 Base 均为 0，TVL 全在 Ethereum $44.8 / Solana $85.0。

**本轮被过滤的 5 条（只列名字，不展开）**
`Brighter`(zkLighter, Yield, $20.1K) · `OnOne`(空链, Launchpad) · `GlazeCorp Launchpad`(Robinhood Chain, parent#glazecorp, $17.6K) · `The River`(空链, Trading App) · `LDEX`(Luxa, Dexs, $1.71)

**校验**
- CF 校验：常规 `HIT`（etag `W/"6aed0b01-913c44"`，`last-modified 2026-11-05T23:02:25Z`，`age 1005`）与 `?_cb=` + `no-cache` 源站 `MISS`（etag `W/"6aed1362-913ce3"`，`last-modified 23:38:10Z`）两份 8950 个 id 逐条相同，`only_hit` / `only_miss` 均空 → 不是缓存假零。
- 8 条新增在两份快照上的 `parentProtocol` / `category` / `chains` 全部一致，无 11-03 那种翻转。
- 反向差集 `only_seen=['4818']`，`only_raw` 空 → 上轮已记的下架痕迹，非解析异常。
- `listedAt` 跨度 19.87h（11-04 23:39:13Z → 11-05 19:31:20Z），最小间隔 209s，同分钟 ≥3 条批量指纹 0 组。
- id 9339 → 9340–9347 连续无缺口，连续三轮无「暂未回填的分配号」。

**原始来源**：`https://api.llama.fi/protocols`（id 9344 / 9345 / 9346 / 9347 / 9340–9343）
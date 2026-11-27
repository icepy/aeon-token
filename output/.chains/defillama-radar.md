**defillama-radar** · 第 32 轮 · 可报 2 / 新增 8

全量 **9123**（上轮 9115，+8）· 新增 id **8**（可报 **2** / 过滤 6）· 重报 0 · 拉取失败 0 · `STATUS: DEFILLAMA_RADAR_OK`，无 degraded、无 ⚠️。CF 双取已过（HIT/MISS 两份 id 集全同、字段差 0）。

## 可报 2 条

- **`Own`**（Robinhood Chain · **CDP** · TVL **$113,825.60**）- 任何人都能在 Robinhood Chain 上铸造 eUSD：抵押品是代币化股票、ETH，以及 stock/eUSD 的 LP 仓位。`own-money/index.js` 自建适配器 · `audits=2` · `gecko_id=own-money`（symbol `MONEY`）· **`mcap` $91,811.92 低于 TVL** · `robinhood:0x0a8b4763c71ac39101b3b8a97e62da0b81549a4f`。staking 另有 $1,139.41（sMONEY 金库，不计入主 TVL）。
- **`Tine`**（Ethereum · **Yield** · TVL **$1,662.92**）- wstETH 储蓄协议：存款人拿 TINE，可选锁定期分享池内质押收益。`module=tine/index.js`，但 `tvlCodePath` 指向通用 `registries/sumTokens.js`（**与 11-26 那三条全自建不同**）· `audits=null` · 无 `gecko_id` · `0x2809cB5f9Fb1BB934dBF5f6f5e6F568bB48Cd8aa`。

合计 **$115,488.52**。本轮新增里 TVL 最大的一条就在可报集内 -- 连续 6 轮的「可报集 TVL ≠ 新增体量」本轮**不成立**（被挡 6 条 TVL 合计仅 $18,751）。

## 过滤 6 条（无一值得追）

| id | 名称 | 链 | TVL | 被哪个桶挡 |
|---|---|---|---|---|
| 9516 | `VoltSwap Aggregator` | `[]` | - | `parent` + 空链（双帽） |
| 9523 | `YeNo Perps` | `[]` | - | `parent` + 空链（双帽） |
| 9517 | `Blast Fun` | `[]` | - | 空链（`listedAt=null`） |
| 9522 | `PRIVO` | `[]` | - | 空链（`address` 是 robinhood 前缀） |
| 9519 | `Guanaco` | `Bitcoincash` | $18,042.22 | 链不在白名单（全量 14 条） |
| 9520 | `POPULAR` | `Sui` | $709.12 | 链不在白名单（全量 137 条） |

**`parent` 桶读数 2、真边际 0**：这两条去掉 parent 后仍被空链挡 -- 与 11-19、11-21 同形。**`链白名单=4` 里只有 2 条真是「链不在白名单」**，另 2 条是空链（`if not hit` 单条件双语义，老问题再现）。

## 结构读数

- `chains=[]` 1680 → **1684（+4）** = 本轮新增内空链条数 **4/8**，逐条对上（`9516`/`9517`/`9522`/`9523` 全 `dummy.js` + `tvl=None`）。**报此判据须同时给新增总数 8。**
- `tvl=None` 2536 → **2540（+4）**，与上一条同源。`listedAt` 缺失 1678 → **1679（+1，仅 `9517`）**；两者交集 980 → 981（**仍不是等式**）。
- 同秒 ≥3 簇 **31（+0）** · 未来 `listedAt` **0（连续第六轮）** · 非数字 id 仍只有 `<5471>` · `max_id=9523` · 数字 id 9122 · ≥9000 缺口仍 4 个（`9135`/`9257`/`9382`/`9391`）。
- 新增 8 条的 `listedAt` 跨 **22.78h**（`11-26T00:36Z`→`23:23Z`），**不是批量指纹**：相邻间隔最大 34256s，只有 `9521 Own`↔`9522 PRIVO` 相隔 214s 且为逆序。
- 滚动秒窗直方图 `[7,9,9,4,5,3,6,5,4,11,5,5]` → 7d **43**、30d **265**、90d **986**（上轮 41 / 265 / 984）。**30d 一格未动而 7d +2 = 有两条滑出 30d 窗。**
- `Hyperliquid Builder` 全量 **240（+0）** · 7d **10**（上轮 11）· 30d **28（+0）** · 90d 137 -- **30d 不动 ⇒ 仍是窗口滑动，不是新流**。`Polymarket Builder` 25 / 7d 1 / 30d 5 / 90d 8 全未动。
- 两个方向差集：`only_raw=[]` · `only_seen=['4818','5496']`（下架残留，非损坏）。
- **链命中数不是新增数的函数**：`Hyperliquid L1` 217 → **218** 本轮无该链新增；`Robinhood Chain` 330 → **333** 而新增里只有 `Own` 一条真挂该链 ⇒ 都是老条目补 `chains`。

原始数据源：`https://api.llama.fi/protocols`（本轮 1 次请求；CF 双取校验副本 `?_cb=20261127a` + `no-cache`）。
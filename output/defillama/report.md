**defillama-radar** · 2026-11-28 · 全量 9128 · 新增 5 · 可报 **1** · 过滤 4

## 可报 1 条

**`Stoxes.fun`** · `Binance`（BSC）· Launchpad · TVL **$8,952.50**

- 一句话：BNB Chain 上的**代币化股票 / RWA 发射台** —— 代币以 BNB 或 Binance 代币化股票（`BNCB` / `NVDAB` / `SPCXB` / `ANTB` 等 bStocks）计价走联合曲线，毕业后进 PancakeSwap。
- 合约 `bsc:0x95c7bd108fd67ae14705577ead2361c3abfb9999` · `symbol=STX` · `module=stoxes-fun/index.js` · `listedAt=2026-11-27T09:58:07Z` · `audits=null` · 无 `gecko_id` · `mcap=null`
- 取数口径（DefiLlama 原文要点）：只算 Stoxes.fun Portals 持有的计价代币（BNB + `BNCB`/`NVDAB`/`SPCXB`），**排除**已毕业进 PancakeSwap 的流动性和已发代币库存 → 该 TVL 是「曲线里还没毕业的钱」，不是平台总规模。
- 原始读数：`change_1h=+94.1%` · `change_1d=null`（新条目无日桶）· `chainTvls` 仅 `Binance`
- 数据源：`https://api.llama.fi/protocols` · id `9528`

## 被挡 4 条（只报名字与挡它的桶，判断留给第三层）

| 名称 | 类目 | TVL | 被哪一桶挡 |
|---|---|---|---|
| `Pear Vaults` | Yield | **$1,288,789.94** | 只被 `parentProtocol`（`parent#pear-protocol`） |
| `RAVN DEX Aggregator` | DEX Aggregator | `null` | `parentProtocol`（`parent#ravn` + 空链） |
| `RAVN Bridge Aggregator` | Bridge Aggregator | `null` | `parentProtocol`（`parent#ravn` + 空链） |
| `Carbium` | DEX Aggregator | `null` | 空 `chains`（Solana 聚合器，`dummy.js`） |

## 读数（事实，非判断）

- **本轮最大新增落在被挡桶里，差额 144 倍**：可报 $8,952.50 vs 被挡 `Pear Vaults` $1,288,789.94。上一轮（11-27）方向相反（最大新增 `Own` 在可报集内）—— 这条差额是「最大新增是否恰被挡」的函数，不是固定偏差。
- **`parent` 桶 3 条里，`Pear Vaults` 是唯一有真量的**，且 `parent#pear-protocol` 的母协议本体**不在** `/protocols`（另两条同族 `Pear Perps` / `Pear Interface` 均 `tvl=null` + 空链，基线轮入库）。即这条在数据上与一个独立协议不可区分，只被一个事后补录的字段挡下。
- **新增 5 条 `listedAt` 跨 7.61h**（11-27T02:21:40Z → 09:58:07Z）。`9524`/`9525`/`9526` 三条落在 **11 秒内**（02:21:40 / 47 / 52），但前两条同 parent、第三条不同 parent ⇒ 是「同批录入」，不是「同族铺开」。
- `chains=[]` 1687 / `tvl=null` 2543，空链 ⟺ `dummy.js` ⟺ `tvl=null` 等式本轮仍成立（1687/1687）。

原始来源：DefiLlama `/protocols`（本轮常规取 `HIT` 与 `?_cb=` 源站 `MISS` 双取，etag `W/"6b0a14ba-9476be"`、`last-modified Fri, 27 Nov 2026 23:39:38 GMT` 逐字符相同，9128 个 id 两向差集均空、逐条字段差异 0 条）。

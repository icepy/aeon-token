**defillama-radar** · 第 25 轮 · 可报 1

## 可报（1 条）

**Enmonetic** · Ethereum · TVL **$14.51** · `Yield Aggregator`
- 收益型稳定币金库：资金分配到私募信贷、代币化国债、DeFi 借贷，另有抵押品风险引擎逐笔筛查。
- `listedAt` **2026-11-19T00:53:14Z** · 无 `parentProtocol` · `module=enmonetic/index.js`（自建适配器，非 dummy）
- https://enmonetic.com · x.com/enmonetic · 审计链接 0 条
- 口径：`chainTvls` 只有 Ethereum 一档，与 `tvl` 完全相等，无上轮 `Coffer` 那种 borrowed/tvl 3.94 倍的错配。
- 尺度参照：`Yield Aggregator` 全量 238 条，中位 TVL $3,152，207 条在 $1M 以下 —— $14.5 属极早期，是「名字先到、量未到」。

## 过滤（4 条，全部为首见即钉 `filtered`）

| id | 名字 | 桶 | 实际形状 |
|---|---|---|---|
| 9478 | `BIMA Lending` | `parent` | **本轮 parent 桶唯一有真边际的一条**：去掉 parent 后链（Binance/Ethereum/Base）、类目（`Lending`）、TVL $5.79 全部通过 |
| 9479 | `Wallet V Routing` | `parent` | `chains=[]`、`tvl=None`，去掉 parent 也被空链挡，真边际 0 |
| 9477 | `Vesper by SypherScore` | `category` | `Interface` + 空链 + `tvl=None` 三帽，与 11-17 结构一致 |
| 9476 | `Rushr` | `链白名单` | `Trading App`、`chains=[]`、`tvl=None` |

**读数纪律：** `parent` 桶的 2 条里只有 1 条真被它挡住，`BIMA Lending` 是母协议铺子的子条目、遮挡正确，但「可报集 TVL 不代表本轮新增体量」这条继续成立——本轮新增里体量最大的是它。

## 结构与差集

- 全量 **9079**（上轮 9075，+4）· 新增 id **5**（`9475`–`9479` 连号，无缺口）· 重报 0 · 拉取失败 0。
- **连号 + `listedAt` 跨度 17.4 小时**（`9475` 11-19T00:53Z → `9479` 11-19T18:14Z）⇒ 不是同一次录入，延续 11-18 的反例判据。
- `only_seen = ['4818', '5496']`：`4818` 连续第十六轮下架；**`5496` 本轮新增下架（首次）**。`only_raw = []`。
- `max_id=9479` · 非数字 id 仍只有 `<5471>` · ≥9000 缺口不变：`9135` / `9257` / `9382`（连十轮）/ `9391`（连九轮）。
- `chains=[]` **1658/9079 = 18.26%**（上轮 1658/9075 = 18.27%）。**绝对数持平、比率因分母增长微降 —— 不是反转，别读成见顶。**
- 空链 ⟺ `module=dummy.js` **第八轮两向完全相等（1658/1658）**；空链中 `tvl` 非空 0 条、带 parent 659、`category∈EXCL` 未变。
- `listedAt` 缺失 **1678**（上轮 1679）· `tvl=None` **2508**（持平）· 同秒 ≥3 条簇 31 组（+0）· `listedAt` 恰为 UTC 整日的 3 条。
- 全量 TVL **$442.56B**（上轮 $442.77B，−$0.21B / −0.05%，**连续第三轮回落**，取源站 `MISS` 份）。
- 近 7d 登记 **51**（上轮 59）· 近 30d **293**（上轮 300）。
- 链命中：Ethereum=1910 · Base=933 · Solana=477 · Arbitrum=1056 · Ink=34 · Binance=1161 · Optimism=394 · Hyperliquid L1=217 · Robinhood Chain=325；孪生 `BSC`/`OP Mainnet` 仍为 0（正常，已收 `Binance`/`Optimism`）。

## 取数校验

CF 双取通过：默认取 `cf-cache-status: HIT`（etag `W/"6aff8866-936e52"`、last-modified `Thu, 19 Nov 2026 23:38:14 GMT`），`?_cb=` + `no-cache` 得源站 `MISS`，同为 9079 行；两向 id 差集空、`tvl` 逐条差异 0 ⇒ **非假零**。

## 已知缺陷（未修，第六次暴露）

`scan.py:301` 的 `本次通知` 字段硬编码，本轮可报 1 却在审计行打印「跳过（零可报）」，与现实相反。读法不变：以 `可报 N` 与 `STATUS` 为准。

---
来源：`https://api.llama.fi/protocols`（本轮 9079 条）· 记录 `memory/defillama-seen.json`（9081 条）

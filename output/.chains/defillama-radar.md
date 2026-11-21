**defillama-radar** · dl-v1 · 第 26 轮 · 可报 2

全量 **9085**（上轮 9079，+6）· 新增 id 6（可报 2 / 过滤 4）· 无 degraded、无 ⚠️

## 可报 2 条

**Biribi** · `Luck Games` · Arbitrum · TVL **$1,996**
链上轮盘协议，在 Arbitrum 上分设 BRB / USDC / DAI 三个 bankroll 金库，存款人提供承担风险的博彩流动性、收益浮动。id 9482 · 自建适配器 `biribi/index.js` · 无 parent · `listedAt 2026-11-20T18:00:01Z` · `url` 空

**Gmoon** · `Launchpad` · Robinhood Chain · TVL **$2.58**
Robinhood Chain 上的发币台，建锁仓的 Uniswap v4 池，把交易手续费换成代币化股票 / ETF / 加密资产分给持币人。id 9485 · 自建适配器 `gemoon/index.js` · 无 parent · `listedAt 2026-11-20T20:11:00Z` · https://gmoon.trade/

## 被挡 4 条（逐条拆桶）

| id | 名称 | 类目 | 撞的桶 | 边际 |
|---|---|---|---|---|
| 9480 | `Kasseal` | Launchpad | 空链（`chains=['Kaspa']`，不在白名单） | 唯一，TVL $4,200 是新增里最大的一条 |
| 9481 | `True Markets Swap` | DEX Aggregator | parent + 空链 + `tvl=None` | parent 边际 0 |
| 9483 | `lockin Perps` | **Interface** | parent + EXCL + 空链 | 三帽 |
| 9484 | `LPStation` | DEX Aggregator | 空链 + `tvl=None` | 唯一 |

`parent` 真边际 **0/2**，`category` 桶名义 0 但**真实读了 1 条**（`lockin Perps` 是 Interface，被 parent 先吃掉）-- 桶序有损第九次复现。

## 口径校验

- **CF 双取通过，非假零**：常规取 `HIT`、`?_cb=` + `no-cache` 取到 `MISS`，**etag 与 last-modified 两份完全相同**（`W/"6b00d9cf-937a1c"`、`Fri, 20 Nov 2026 23:37:51 GMT`），9085 个 id 两向差集空、`tvl` 逐条差异 **0 条**。
- **连号但非批量**：9480-9485 连号无缺口，`listedAt` 从 `11-20T02:55:41Z` 跨到 `20:11:00Z`，**跨度 17.3 小时**，不构成同秒批量指纹（同秒 ≥3 簇仍 31 组、最近仍 11-14）。
- **体量对照**：本轮新增里最大的 `Kasseal` 被链白名单挡掉（Kaspa 不在白名单），延续「可报集 TVL 不代表本轮新增体量」第四次成立。

## 单侧读数

加密侧 2 / AI 侧 0 -- 本源只有加密，**别把这 100% 命中率读成词表变准**，那是源偏差。

## 全量 TVL 大幅回落：是行情，不是口径

`$442.56B → $425.88B = −3.77%`，明显大于前四轮（−0.44% / −1.90% / −0.05%）。交叉核对 `api.llama.fi/v2/historicalChainTvl`：**11-19 $70.30B → 11-20 $66.61B = −5.25%，三日前→今日 −6.14%**。方向与量级一致 ⇒ **本轮是全市场下跌，不是本份 payload 的假动**。（注：两套口径绝对值差约 6.4 倍 -- `/protocols` 逐条 `tvl` 求和 vs `/v2/historicalChainTvl` 是全市场口径，且两者的时间点不同（前者为最新快照、后者为 11-20 00:00 UTC 日桶）。**只比方向与量级，不比绝对值。**）

## 差集

`only_raw=[]` · `only_seen=['4818','5496']` -- `4818` 连续第十七轮下架、`5496` 第二轮下架。`max_id=9485` · 数字 id 9084 条 · 非数字仍只有 `<5471>` · ≥9000 缺口不变：`9135` / `9257` / `9382` / `9391`。

## 结构读数

- `chains=[]` **1664/9085 = 18.32%**（上轮 1658/9079 = 18.27%）-- 分子 +6、分母 +6，绝对数与比率同向微升，与本轮新增 6 条里的空链条数吻合。
- 空链 ⟺ `module='dummy.js'` **第九轮两向完全相等（1664/1664）**；空链中 `tvl` 非空 **0 条**、带 parent **662**。
- `listedAt` 缺失 1678（持平）· `tvl=None` 2514（上轮 2508）· 日精度回填仍 4 条（`Monster Gameverse` / `Bebop Aggregator` / `Pons V1` / `Pons V2`，本轮无新增）。
- 近 7d 登记 **51** 条（可报 2 = **3.9%**，上轮 2.0%）· 近 30d **284** 条（上轮 293）。

## 审计行缺陷第七次暴露

`scan.py:301` 硬编码，本轮可报 2 却在审计行打印「本次通知 跳过（零可报）」，与现实相反。**以 `可报 N` 与 `STATUS` 为准，`本次通知` 字段不可信。** 修法只需判断 `out` 是否非空，可单独提 PR。

---
来源：`https://api.llama.fi/protocols`（`?_cb=` 源站份，etag `W/"6b00d9cf-937a1c"`）· `https://api.llama.fi/v2/historicalChainTvl`
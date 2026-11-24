本轮完成。

## defillama-radar · 第 29 轮（2026-11-24）

**结论：可报 0，未发通知、未覆写 `report.md`（按铁律）。**

| 指标 | 读数 |
|---|---|
| 全量 | 9096（上轮 9092，+4） |
| 新增 id | 4 · 可报 **0** · 过滤 4 |
| 丢弃桶 | `parent`=1 · `category`=3 · 链白名单=0 · 无 id=0 |
| 重报 / 拉取失败 | 0 / 0 |
| `STATUS` | `DEFILLAMA_RADAR_OK`，无 degraded、无 ⚠️ |

### 新增 4 条全明细（四条全部空链、`tvl=None`、`module='dummy.js'`）

| id | 名称 | 类目 | 链 | `listedAt` | 撞的桶 |
|---|---|---|---|---|---|
| 9493 | `ATLASX Perps` | Interface | `[]` | 11-22T22:26:40Z | category（+空链双帽） |
| 9494 | `XOXNO Aggregator` | DEX Aggregator | `[]` | 11-23T16:48:31Z | **parent 唯一** |
| 9495 | `EasyPerp` | Interface | `[]` | 11-23T16:51:18Z | category（+空链双帽） |
| 9496 | `LiLLyTrade` | Interface | `[]` | 11-23T17:19:11Z | category（+空链双帽） |

### 三条判据级发现

1. **`链白名单=0` 不等于今天没有空链条目。** 本轮空链条目 4/4，但都在更早的 `parent`/`category` 桶被 `continue` 掉了。这是「桶名比桶语义窄」的又一例（11-08 同源），读数时不能反推。

2. **`Hyperliquid Builder` 标签独占 3/4 新增，且该流在加速。** 全量 234（上轮 227）· 近 7d **7** · 近 30d **19→22** · 90d 131。全部 `Interface`、空链 233、`tvl` 非空始终只有 `LiquidBots` $68.8K 一条。30d 占同期登记 8.1%（上轮 6.5%）—— **加速的是录入模板流，不是可报面。**

3. **`9494 XOXNO Aggregator` 三处互斥**：`description` 说 Stellar、`address` 是 `elrond:`、`chains=[]`；同父另两条子条目对链的写法也各不相同（`['Elrond','Stellar']` / `['Elrond']` / `[]`）。但 `Elrond` 与 `Stellar` 都不在白名单，**无论怎么修链都不可报**——这是白名单覆盖面问题，不是链口径问题。

### 口径校验

- **CF 双取通过，非假零**：`HIT`（etag `W/"6b04ce5a-93da78"`，`last-modified` 23 Nov 23:38:02Z）vs `?_cb=` 源站 `MISS` —— etag / last-modified 逐字符相同、9096 个 id 两向差集均空、`tvl` 差异 0 条、`parentProtocol` 翻转 0 条。
- **全量 TVL −1.21%**（$443.80B → $438.43B）。关键：**11-22 桶隔轮被下修 −2.11%**（$69.31B → $67.85B），远超 0.5% 未定稿判据线 —— 上轮把它标成「不得当趋势引用」是对的，这是首例 >2% 的隔轮修订。11-20/11-21 两桶仍分文未动。
- 结构：空链 **1671/9096 = 18.37%**，净增 +4 恰等于新增空链条数（该判据**连续第二轮正向命中**）；空链 ⟺ `dummy.js` 两向完全相等（12 轮）；`only_seen=['4818','5496']`（下架残留，非损坏）；7d/30d = **37 / 270**，两窗口精确配平。
- `scan.py:301` 的 `本次通知` 缺陷本轮未暴露（可报 0，打印正确）。补丁需求不变，仍未改脚本。

## Summary

- **执行**：`python3 skills/defillama-radar/scan.py`（`var` 为空 = 正式轮），一轮、一次 `/protocols` 请求。
- **结果**：可报 0，按铁律**未通知**、未覆写 `report.md`。
- **文件**：`memory/defillama-seen.json`、`output/defillama/{out.json,audit.log}`（脚本写）· `memory/logs/2026-11-24.md`（新建）· `memory/topics/defillama-radar.md`（新增第 29 轮节，timestamp 已 bump）· `memory/MEMORY.md`（更新索引与时间戳）。
- **跟进**：① `scan.py:301` 的 `sent` 四态补丁待开 PR；② 若日后要收 `Stellar`（全量 47 条、42 条有真实 TVL）进 `CHAINS`，须按 SKILL.md 删 `seen` 重做基线，届时 `9494` 会重灌成 `baseline`、仍不进报告。

第 22 轮已完成。以下是本轮结果。

## defillama-radar 第 22 轮（`dl-v1`）

**`STATUS: DEFILLAMA_RADAR_OK`** · 全量 **9056** · 新增 id **1** · 可报 **0** · 无 degraded、无 ⚠️

报告级 0 → **未发通知**，`report.md` 按铁律保持第 21 轮内容未覆写。

### 漏斗读数

| 项 | 读数 |
|---|---|
| 全量 / `seen` 命中 | 9056 / 9055 |
| 新增 id | **1**（可报 0 / 过滤钉 `filtered` 1） |
| `parent` 桶 | 0 |
| `category` 桶 | **1** |
| 空 `chains` / 链白名单桶 | 0 |
| 无 id / 拉取失败 / 重报 | 0 / 0 / 0 |

唯一新增 **`Liqwall`**(9457)：`category='Interface'`、`chains=[]`、`tvl=None`、`parentProtocol=None`、`listedAt=1794870502`（2026-11-16T23:08:22Z）、`tags=['Hyperliquid Builder']`、`https://liqwall.com`、`audits='0'`。

**它是「空链 + EXCL 类目双帽」**：桶序上先撞 `category`，所以 `链白名单=0` **不代表今天没有空链条目**。11-08 记的「桶名比桶语义窄」第四次复现。

### 本轮首次摊开 `EXCL_CATEGORY` 三类的结构 —— 它们完全不是一回事

| category | 存量 | 空 `chains` | 带 parent | `tvl` 非空 |
|---|---|---|---|---|
| CEX | 84 | 4 | 1 | **79** |
| Chain | 85 | 58 | 0 | 23 |
| **Interface** | **380** | **374（98.4%）** | 252 | **6** |

全量 EXCL 549 条里 436 条空链（79.4%），Interface 独占 374。**推论：`category='Interface'` 与「空 `chains`」高度共线，该桶对 Interface 是重复计数而非独立信号；且 Interface 类目下可报面基本为空（仅 6 条有 TVL，其中 3 条还带 parent），所以「Interface 一律过滤」的损失面是零。**

### `Hyperliquid Builder` 标签：近 30d 19 条、占同期登记 6.5%，是当前最密的单标签流 —— 但不是发现信号

全量该标签 **227 条全部 `Interface`**、空链 226、有 TVL 仅 `LiquidBots` $68.8K。带 `listedAt` 的 126 条里近 7d **4** / 近 30d **19** / 近 90d **124**，30d 那 19 条**全部 `chains=[]` 且 `tvl=None`**，占同期 30d 全量登记（293 条）的 6.5%。

记下来是为两件事：① 若将来把「`tags` 含该标签 ⇒ 视作挂 `Hyperliquid L1`」的旁路做实，这 19 条会一次性涌进可报面；② 它们体量不可知，**不能当成「Hyperliquid 生态在扩张」的证据** —— 是同一张录入模板的产物。

### CF 双取通过，非假零

`HIT`（etag `W/"6afb93ea-92f029"`、11-16T23:38:18Z、`age 291`）与 `?_cb=1763337600` + `no-cache` 源站 `MISS`：9056 个 id 两向差集空、`tvl` 逐条零差异、etag/last-modified 逐字节相同。`max-age=300` 连续第三轮。

**新读数：`Liqwall` 的 `listedAt` 23:08Z 早于快照的 23:38Z** —— 它是随日更发布一起进 `/protocols` 的，不是扫描时刚好被写入。

### 差集与 id 连续性

`only_seen=['4818']` **连续第十三轮**（真下架）· `only_raw=[]` · `max_id=9457` · 数字 id 9055 条。

**9000 以上缺口首次出现尾部连号空洞 `9455`–`9456`**，夹在 9454（`Hookr`，11-15 登记）与 9457（`Liqwall`）之间 —— 按 11-03 修正判据属「暂未回填的分配号」，下轮或数日内可能出现，届时算真新增。这是给下一轮的一条预告，不是异常。其余缺口 `9135` / `9257` / `9382`（连七）/ `9391`（连六）延续。非数字 id 仍只有 `<5471>`。

### 其余结构读数

- `chains=[]` = **1648/9056 = 18.20%**（上轮 18.10%，**连续第二轮创新高**；十三轮区间 17.4–18.20）
- 空链 ⟺ `module='dummy.js'` 第五轮复核仍完全相等（1648/1648）；空链中 `tvl` 非空 0 条、带 parent 652、`category∈EXCL` 436
- 同秒 ≥3 条簇 **31 组**（+0），最近仍 2026-11-14T13:53:56Z（`Exodus Pay`/`Send Card`/`COCA Card`）
- 整分 `:00` 值 69/7377 = 0.94%；`listedAt` 缺失 1679 条；`tvl=None` 2500 条
- 全量 TVL **$453,328,350,251.35**（上轮 $450,273,746,143.23，+$3.05B / +0.68%）
- 刚补的「连号子段 + `listedAt` 跨度 ≤30 分钟」判据**本轮不适用**（差集仅 1 条）
- 审计行 `本次通知` 缺陷（`scan.py:301` 硬编码）因可报恰好 0 而显示正确，**缺陷未修**；只在「可报 >0 且未带 `send`」时暴露

## Summary

- 执行 `skills/defillama-radar/scan.py`，第 22 轮完成，`STATUS: DEFILLAMA_RADAR_OK`，可报 0，未发通知。
- 核验非缓存假零：`HIT` 与 `?_cb=` 源站 9056 条 id 两向差集空、`tvl` 逐条零差异。
- 唯一新增 `Liqwall`(9457) 被 `category` 桶挡掉（`Interface` + 空链双帽），入库钉 `filtered`。
- 新发现一：`Interface` 380 条里 374 条空链、仅 6 条有 TVL ⇒ 该桶与空链共线，一律过滤不损失发现面。
- 新发现二：`Hyperliquid Builder` 近 30d 19 条、占同期登记 6.5%，全空链无 TVL，是同模板录入潮而非生态扩张证据。
- 新发现三：尾部首现连号空洞 `9455`–`9456`，标记为下轮待回填预告。
- 改动文件：`memory/topics/defillama-radar.md`（新增本轮节 + 更新 timestamp + citations）、`memory/logs/2026-11-17.md`（新建）、`memory/MEMORY.md`（更新发现层条目并压到 8.1KB 以下）；脚本自身写入 `memory/defillama-seen.json`(9057 条)、`output/defillama/{out.json,audit.log}`。
- 后续动作：`report.md` 未覆写（符合铁律）；`scan.py:301` 审计行缺陷仍需走 PR 修复；下轮重点看 `9455`/`9456` 是否回填。

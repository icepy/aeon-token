MEMORY.md now within all caps (7898 B / 53 lines / no line >300). Skill produced zero reportable items, so per the skill's rule no notification is sent. Final report:

## defillama-radar · 第 2 轮

**`VERSION: dl-v1`** · var 为空 · 单请求 `https://api.llama.fi/protocols` · 1s

### 全量与四桶

| 桶 | 计数 |
|---|---|
| 全量 payload | **8859**（distinct id 8859，无重复、无空 id） |
| `seen` 命中 | **8859** |
| `parentProtocol` 丢 | 0 |
| `category ∈ {CEX, Chain}` 丢 | 0 |
| 链白名单外 丢 | 0 |
| 无 id | 0 |
| **新增 id** | **0**（可报 0 / 过滤标记 0）· 重报 0 |

四桶全 0 是因为没有任何新增条目进到过滤器；不是过滤器在放行东西。

### 链命中

Ethereum=1891 · Binance=1145 · Arbitrum=1044 · Base=912 · Solana=465 · Optimism=392 · Robinhood Chain=292 · Hyperliquid L1=210 · Ink=33 · **BSC=0 · OP Mainnet=0**

白名单校验通过，审计无 ⚠️ 行。

### 单侧读数

加密侧 0 / AI 侧 0。本源只有加密。**这个 0 不能读成「AI 侧没动静」**——那条通道不在这个数据源里；也不能读成词表失效。

### 可报明细

**0 条。** 未发通知，`report.md` 未重写（符合铁律）。

### 本轮的判据级发现

**① 这个 0 差点是假零。** 响应头 `age: 751` · `cf-cache-status: HIT` · `last-modified: 05:39:24Z`，而基线轮 06:22Z 吃的是同一份 Cloudflare 边缘快照——两轮之间源站没被问过。加 `?_cb=` + `no-cache` 复取源站（`MISS`、`last-modified: 06:02:09Z`、etag 变）后：**1255/8859 条 `tvl` 已变（全量 TVL −$610M），id 集合完全相同**。所以 0 为真，但**必须先证明绕过缓存才成立**。已记入 lessons「第四种假零」。

**② `id` 单调递增已证实** —— 7186 条样本按 id 排序相邻对 `listedAt` 逆序仅 **2.6%**；id 最小 200 条中位 2021-11-04、最大 200 条中位 2026-10-19；10-20 起 91 条连续 id 9164–9254、缺口 0。第 1 轮待办 ③ 结案。附带新校验：差集里若出现小于历史最大 id 的条目，那是下架再上架的回流，不是新登记。

**③ `Interface` 不该进 `EXCL_CATEGORY`（第 1 轮待办 ① 结案，结论「不」）。** 350 条里 232 条带 `parentProtocol`（已被 parent 桶吃掉），剩下 118 条里仅 **6 条**有 `chains`。即噪声已被「chains 为空」自然挡掉 98.3%。加进 EXCL 反而会永久屏蔽预测市场前端这类可能的真信号。

**④ 近 48h 真实新登记 36 条，过全部过滤的可报 4 条，本轮一条未报** —— 它们全在基线轮之前，是被基线吃掉的沉积层，不是漏报。明细：`Mezzanine`（Ethereum·Yield·$2.19M）· `Overlayer`（Ethereum·Yield·$40.4K）· `Olive Exchange`（Solana·Options·$24.8K）· `DoublePlus`（Robinhood Chain·Launchpad·$53.9）。下一轮起才是干净增量。

**⑤ `★清单内` 判别力更糟了（待办 ② 复核）。** 清单 5 词，名字级命中 **1** 条（`Robinhood Chain Bridge`）、描述级命中 **192** 条，比例 1:192。建议改为只在 `name` 字段匹配。

## Summary

- **执行**：`scan.py` 正式轮（非 dry-run、非基线）。新增 id 0，可报 0，按 SKILL「零可报不发通知」未调用 `./notify`。
- **改动文件**：`memory/logs/2026-10-28.md`（追加第 2 轮一节）· `memory/MEMORY.md`（更新 defillama 条目、去重、加「假零八」、压回 8 KB/300 字符上限）· `memory/topics/lessons.md`（新增「第四种假零」）· `memory/topics/defillama-radar.md`（**新建**，承载细节）· 脚本自写的 `output/defillama/{out.json,audit.log}`。**未改 `scan.py`**。
- **结案**：第 1 轮三条待办中 ①③ 已结（结论均为「不改」），② 需你拍板。
- **待办（要人决定）**：`memory/universe-names.txt` 的匹配要不要改成只匹配 `name` 字段 —— 这是 `scan.py` 一行改动，你说改我就开 PR。
- **未做**：没跑 `mark-sent`（无可报项）；没发通知（零可报）。

验证完成。`report.md` 未动（符合铁律），`out.json` 为空数组属正常。

## 第十二轮 · 全量 8956 · 新增 6 · **可报 0**

**本轮不发通知** —— 报告级 0，按铁律不重写 `report.md`、不推 `./notify`。

### 6 条新增全被 `parent` 桶挡掉

| id | 名称 | 链 | 类目 | TVL | parent |
|---|---|---|---|---|---|
| 9348 | Sparkling Hyperliquid | — | Interface | — | `parent#sparkling` |
| 9349 | Sparkling Lighter Perps | — | Interface | — | `parent#sparkling` |
| 9350 | Sparkling Lighter Predict | — | Interface | — | `parent#sparkling` |
| 9351 | Sparkling Prediction Markets | — | Interface | — | `parent#sparkling` |
| 9352 | pump.fun Perps | — | Interface | — | `parent#pump` |
| 9353 | Vesper V2 | Ethereum | Yield Aggregator | **$10.02M** | `parent#vesper` |

四条 `Sparkling *` 共用站点 `sparkl.ing`，7.9 小时内连登、间隔 166–538s（逐条录入，非同秒批量）。全轮体量最大的 `Vesper V2` 是老协议的行为版本铺开 —— 正是「版本号铺开是最大噪声源」要挡的东西，遮挡正确。

### 判据级发现 ①：桶序是有损链，`category=0` 是假象

`scan.py` 的判定序是 `seen` → `parent` → `category` → `chain`，每桶 `continue`，**一条记录只记进它撞上的第一个桶**。本轮读数是 `parent=6 / category=0 / 空链=0`，看起来「parent 是唯一问题」，实际不是：

6 条里 **5 条是双帽 `Interface`** —— 去掉 `parent` 它们照样被 `category` 挡。**`parent` 的边际贡献只有 1/6**（只有 `Vesper V2`），而 `category` 桶真实读了 5 条、审计显示 0。

同一份 payload 重算的重叠率：

| 窗口 | `listedAt` 有值 | 带 parent | 其中 category∈EXCL |
|---|---|---|---|
| 7d | 63 | 24 | 11（46%） |
| 30d | 420 | 225 | **137（61%）** |
| 90d | 916 | 384 | 142（37%） |
| 全时段 | — | 2668 | 247（9.3%） |

30d 里 EXCL 类目共 178 条，不带 parent 的只有 41 条 → **该桶在 30d 尺度的可观测面仅 23%**。反过来 `parent` 也同理：它吞掉 61% 本该记给 `category` 的条目，「parent 占比升高」可能只是「Interface 类铺子协议变多」的同一个事实换了名字。

**不改代码** —— 多标签计数会让 `drop` 各桶之和 > 新增数，破坏「新增 = 通过 + 过滤」的闭合式。纪律改为：任何单桶占比读数必须注明桶序，且不可跨桶做减法。

### 判据级发现 ②：`listedAt=null` 不能反推「老条目」

`Vesper V2`(9353) 是最新 id 却 `listedAt=null`，两份快照都是 null —— 顶撞旧结论「`listedAt` 在近期新登记覆盖完整」。实测 id≥9300 的 54 条里 null 只有 2 条（`Imperial` 9300、`Vesper V2` 9353）= **3.7%**，id 9330–9353 共 24 条里 1 条 = 4%。

修正：近 30d 覆盖 ~96% 但**非 100%**，`id` 求差主结论不变且更需要它；null 有两个来源（老条目从未补录 / 新条目录入漏填），单看 null 分不出来。

### 校验与其他读数

- **CF 校验通过**：`HIT`(etag `6aee5c93`、lm `11-06 23:02:43Z`、age 967) vs `?_cb=` 源站 `MISS`(etag `6aee64e2`、lm `23:38:10Z`)，两份 **8956 id 逐条相同**，`only_hit`/`only_miss` 空 → 非缓存假零。6 条新增的 `parentProtocol`/`category`/`chains`/`tvl` 两快照**零差异**，11-03 的 parent 翻转**连续三轮未复现**。
- `only_seen=['4818']`、`only_raw=[]` **连续第三轮** → 真下架。seen 8957 = 8956 命中 + 1 残留。
- `listedAt` 跨度 7.88h、最小间隔 166s、同分钟 ≥3 条批量指纹 **0 组**；id 9347 → 9348–9353 连续无缺口，**连续四轮无「暂未回填的分配号」**。
- 链命中 `BSC=0` 与 `OP Mainnet=0` 同时为 0，但孪生组不空（`Binance=1152` / `Optimism=394`）→ 命名已统一到孪生侧，非拼错，审计未报警，印证 `CHAIN_TWINS` 整组判零的设计。

## Summary

- 执行 `skills/defillama-radar/SKILL.md` 第 12 轮正式扫描：全量 8956、新增 6、可报 0、`STATUS: DEFILLAMA_RADAR_OK`。**零可报，未发通知、未重写 `report.md`**（符合铁律）。
- 做了三项交叉核对（均写进判据）：CF 双快照逐条比对（非缓存假零）、桶序掩蔽定量（parent 边际仅 1/6，30d 重叠 61%）、`listedAt` 覆盖实测（新 id 也会 null，3.7%）。
- 文件改动（均为默认行为、无需跟进）：
  - `memory/topics/defillama-radar.md` — 新增「桶序会掩盖读数」「`listedAt=null` 两种来源」两节 + 本轮漏斗口径 + 6 条 Citations，`timestamp` 升至 2026-11-07。
  - `memory/logs/2026-11-07.md` — 新建，本轮日志。
  - `memory/MEMORY.md` — 第 16 行更新到第 12 轮（8090 B / 42 行 / 0 超长行，仍在 8KB 内）。
  - `memory/topics/index.md` — defillama 索引行补两条新判据。
  - `output/defillama/` — `out.json`（脚本写成 `[]`）、`audit.log`、`seen.dry` 未动；新增三个校验脚本 `audit21*.py`。
- **建议的下一步（非本轮职责）**：`scan.py` 若要两桶都可读，需改成多标签计数并同步改审计行语义 —— 但这会破坏现有闭合式，且收益仅在审计可读性，建议先观察两轮再定。

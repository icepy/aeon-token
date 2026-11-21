## arxiv-radar 第 53 轮

**`VERSION: vM`** · 窗口 **30 天**（默认）· 26 词 · 原始 **67** · 幸存 **0** · `STATUS: ARXIV_RADAR_OK`（无 `_DEGRADED`，无查询失败）

### 漏斗
| 阶段 | 数量 |
|---|---|
| 原始命中 | 67 |
| 丢弃 seen(记忆) | 67 |
| 丢弃 seen(本轮重复) | 0 |
| 丢弃 EXCL / carrier | 0 / 0 |
| 查询失败 | 0 |
| **幸存** | **0** |

67 条全部是 `arxiv-seen.json` 里已有的旧命中。零故障、零过滤器损耗 —— 这是**结构性零**，不是扫描出问题。

### 六分类（单位 = 词，合计 26）
- **未测到（试过失败）: 0**
- **未尝试（熔断跳过）: 0**
- **窗口内零命中: 11**
- **低频探针: 2**（`verifiable inference` · `restaking`）
- **全已见（饱和）: 13**
- **有新增: 0**

索引最新收录 **2026-11-19**（周四，距今 2 天）—— 按节律正常，周末不公告，不算滞后。

### 判据级发现

**11-20 预告的结构性归零，本轮兑现。** 上轮记录「AI 侧召回宽度只剩 `egocentric` 一条，它一吃干就结构性归零 —— 换窗无用、须加词」。本轮 `ti:"egocentric"` raw **20 → 19**、新收 **0**，`maxpub` 停在 **11-19**（仍在近 30 天窗口内 ⇒ 话题活着，是 `seen` 吃干了它，不是流量消失）。

**13 个饱和词同形：raw 有量，新收全零。** `maxpub` 分布 11-07 ~ 11-19，无一停在 60 天前：

| 词 | raw | maxpub |
|---|---|---|
| `ti:"egocentric" AND cat:cs.RO` | 19 | 11-19 |
| `ti:"consensus" AND cat:cs.DC` | 11 | 11-18 |
| `ti:"human data" AND cat:cs.RO` | 2 | 11-18 |
| `robot data` | 6 | 11-17 |
| `ti:"data generation" AND cat:cs.RO` | 4 | 11-17 |
| `ti:"human demonstration" AND cat:cs.RO` | 4 | 11-13 |
| `ti:"data engine" AND cat:cs.RO` | 1 | 11-12 |
| `verifiable computation` | 1 | 11-12 |
| `ti:"hand-object" AND cat:cs.RO` | 4 | 11-10 |
| `proof-of-useful-work` | 1 | 11-09 |
| `zero-knowledge` | 6 | 11-09 |
| `embodied AI` | 7 | 11-07 |
| `verifiable training` | 1 | 10-23 |

⇒ 无一该降温，但 11 个 `maxpub` ≥ 11-13 说明流量真实存在而 `seen` 已全覆盖。**这是「词有量但已饱和」，与「词写错打不中」是两件事。**

### 跨窗结论（`cross_windows()`，非 probe）

11 个窗口内零命中的词，**全部跨窗有命中** → 「窗口太短，别删」，无一进入删词档。

`auditable training` 2/3 · `automated market maker` 2/3 · `cat:cs.CR AND ti:"MEV"` 1/3 · `embodied data` 1/3 · `ti:"EIP-1559"` 2/2 · `RWA` 0/2 · `robot manipulation data` 0/2 · `proof of training` 1/1 · `light client` 0/1 · `data availability sampling` 1/1 · `ti:"staking" AND (cat:cs.CR OR cat:cs.DC OR cat:q-fin.GN)` 1/1

（格式为 60d/90d。本轮窗口即 30d，故 90d 列是真读数，不是「无档可比」。）

### 待办

1. **AI 侧必须加词或换写法。** `egocentric` 已吃干、本方向结构性归零。换窗无效 —— `days:90` 只会把已见过的 67 条再拉一遍。`directions.md` 第五节里 `世界模型` 至今 **0 词**，是最明显的召回空洞。
2. **`days:90` 补历史仍未跑**（第五轮挂起）；14 词缺 carrier 表（第六轮）。
3. `ti:"human data"` 连续第二轮新收 0 —— 11-20 记的「上轮 2 条是一次性补录」本轮二次确认，不是持续流量。

按铁律：零幸存 ⇒ 未写 `arxiv-labels.tsv`、未发通知。

## Summary

- **执行**：`python3 skills/arxiv-radar/scan.py ""`（默认 30 天窗口，vM 口径），一次跑完写入 `output/arxiv/out.json`、`audit.log`、`memory/arxiv-seen.json`。
- **结果**：67 → 0。六分类为 11 零命中 / 2 低频 / 13 饱和 / 0 有新增 / 0 未测到 / 0 未尝试。结构性零，非故障。
- **文件修改**：`memory/logs/2026-11-21.md` 追加 `### arxiv-radar（第 53 轮）` 一节。
- **未做的事**：零幸存 ⇒ 无 labels 写入、无 notify（符合 SKILL.md 铁律）。
- **后续需要**：给 AI 侧补词（优先 `世界模型` 方向），并跑一次 `days:90` 补历史。

这轮完成。主分支的 `scan.py` 保持原样（改动只在 PR #25 的分支上），`memory/logs` 已写好第 46 轮记录。

---

## arxiv-radar 第 46 轮 · 2026-11-14

**`STATUS: ARXIV_RADAR_OK`** · 窗口 30 天 · 26 词 · 耗时 164s

### 漏斗

| 阶段 | 数量 |
|---|---|
| 原始命中 | 72 |
| `seen`(记忆) 丢弃 | 72 |
| `seen`(本轮重复) | 0 |
| `EXCL` / `carrier` | 0 / 0 |
| 查询失败 | 0 |
| **幸存** | **0** |

### 六分类（单位=词，分开记）

未测到(试过失败) **0** · 未尝试(熔断跳过) **0** · 窗口内零命中 **12** · 低频探针 **0** · 全已见(饱和) **14** · 有新增 **0**

**两侧失败类全 0 = 读数干净，可用于判断。** 索引滞后正常：窗口内最新收录 11-12（周四，距今 2 天，周末不公告）。

### 零幸存是结构性的

72 条 raw 全部命中 `seen`（上轮 76 条里 71 已见、5 条新收）。**不是 `_DEGRADED`，不是词表失效** —— preflight 未失败、熔断未触发。

### 跨窗与换写法级（本轮主要动作）

零命中 12 词里 **10 个跨窗有命中 → 窗口太短，不许删**：`auditable training`(60d=2/90d=3)、`proof of training`(1/1)、`light client`(0/1)、`data availability sampling`(1/1)、`staking`(1/1)、`MEV`(3/3)、`RWA`(0/2)、`embodied data`(1/3)、`robot manipulation data`(2/2)、`human data`(6/7)。

剩下两个跨窗皆 0，本轮走完上轮留的「换写法」待办：

**`verifiable inference`** — `all:"verifiable inference"` 四档 0/1/2/2，已见 0/2。有货但极稀疏，60d=2 低于采用门槛（60d total 5–60）→ 降为低频探针，不删（`可验证计算` 方向仍有 `verifiable computation`、`proof of training` 扛召回）。

**`restaking`** — 四种写法全期零命中：`ti:` / `all:"restaking"` / `all:restaking` / `abs:restaking` 均 90d=0。**不是假零**，有三条证据：① 同场次 crypto 词有判别力（`zero-knowledge` raw=9、`consensus` raw=12、`MEV` 60d=3）；② 判别力对照——真词 `abs:blockchain` 7d=11/领域 11/11，故意拼错的 `all:restakinq` 7d=0；③ 这四条是**成功响应**返回 0（限流会让 `total_of` 返 -1 并打印「查询失败」，对照组 30/60/90d 正是这样），所以没有被 429 吞成假零。按「换写法 → 降频 → 删」只进第②级，**本轮不跳到删词**。

### 饱和侧（14 词）

maxpub 全在 30 天内 → **无降温候选**。最旧 `automated market maker` 10-16（29 天）；最新 `verifiable computation`、`egocentric` 均 11-12。**饱和 = `seen` 吃干，不是话题死了。**

### 召回读数

`egocentric` raw=**18** 连续两轮最大召回词，其次 `consensus` 12、`zero-knowledge` 9、`embodied AI` 7、`hand-object` 7。**加密侧本轮窗口零命中**（12 个零命中词里 5 个是加密词），上轮 3 条的召回未延续 —— 与 github-radar 加密侧十连轮 0 同向，但按「跨通道只在有效域内比较」的既有判据，不据此判词表坏，只记读数。

`carrier` 丢弃 0，14 词仍未配 carrier 表（连十一轮空转）→ 过滤器至今无判别力证据，维持 Observation。

### 产出

- labels：**零幸存，无写入**（`memory/arxiv-labels.tsv` 维持 174 行）
- 通知：**未发**（SKILL.md 规定幸存 > 0 才发；本轮 0）
- 词表改动：**PR #25**（分支 `arxiv-radar-lowfreq-r46`），只动 `LOW_FREQ`，不改 `TERMS`/过滤逻辑/不删词，`ast.parse` 通过
- 日志：`memory/logs/2026-11-14.md` 第 46 轮整节

### 待办

1. **PR #25 待合并** —— 合并后 `restaking` / `verifiable inference` 才真正从饱和/零命中计数里移除。
2. **`restaking` 下一轮确认**：若合并后再连续一轮零命中，才够资格进「删词」第③级；本轮刻意没跳。
3. **预算超支**：本轮因补做 6 个 `check:` 用到约 30 次工具调用，超出日常 30d 档 7 次上限。超支全部来自判据级补测而非重复读产物；下轮若词表无待办应回到 ≤7 次。
4. **carrier 空转未解**（十一轮）：需要单独一轮把 14 个词的表配齐，否则 `carrier` 这条过滤线在本通道等于没有。

## Summary

- 跑完 arxiv-radar 第 46 轮（30 天窗、26 词）：原始 72 → 幸存 0，两侧失败类全 0，零幸源于 `seen` 结构性饱和而非故障。
- 完成上轮遗留的「换写法」判据级动作：`verifiable inference` 与 `restaking` 走完全部同义写法实测，双双降为低频探针（第②级），未跳级删词。
- 首次加入判别力对照实验（真词 `abs:blockchain` vs 拼错 `all:restakinq`），把「四档全 0」钉成真零而非限流假零。
- 修改 `skills/arxiv-radar/scan.py` 的 `LOW_FREQ`（+9 行注释与两条词），开 PR #25；未改 `TERMS`、未删词、未动过滤逻辑。
- 写入 `memory/logs/2026-11-14.md` 第 46 轮整节。未发通知、未写 labels（均因零幸存）。
- 后续待办：合并 PR #25；`restaking` 删词需再一轮确认；下一轮把工具调用收回到 ≤7；carrier 空转需单独一轮补齐。

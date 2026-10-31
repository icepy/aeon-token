## arxiv-radar · 第 32 轮

**口径**：`scan.py ""` · 30 天窗 · 26 词 · 130s · `STATUS: ARXIV_RADAR_OK`（无降级 / 无 429 / 无熔断）

**漏斗**：原始 84 → 幸存 **0**
丢弃 seen(记忆)=83 · seen(本轮重复)=0 · EXCL=1 · carrier=0 · 查询失败=0

### 六分类（分开写）
| 分类 | 词数 |
|---|---|
| 未测到（试过失败） | 0 |
| 未尝试（熔断跳过） | 0 |
| 窗口内零命中 | 7 |
| 低频探针 | 0 |
| 全已见（饱和） | 19 |
| 有新增 | 0 |

### 跨窗结论
7 个零命中词在 60d/90d **全部有命中** → 全判「窗口太短，别删」：

`verifiable inference` 0/0/1 · `verifiable computation` 0/1/1 · `light client` 0/1/1 · `restaking` 0/0/1 · `MEV` 0/3/5 · `RWA` 0/1/2 · `robot manipulation data` 0/2/2

与第 30、31 轮**逐值完全相同，第四轮落同一档**。判词三级不许跳级，仍卡在「换写法」之前未动。

### 饱和 19 词（上轮 16）
上轮「有新增 3」的三个词本轮全部转入饱和，故 +3。19 词的 raw 最新发布日期**全在近 30 天内**：`consensus cs.DC` / `robot data` / `egocentric` = 10-29，`hand-object` 10-27，`embodied AI` 10-25，最旧 `proof of training`、`embodied data` = 10-06。**无一个该降温。**

### 索引节律
窗口内最新收录 **2026-10-29（周四，距今 2 天）** —— 与上轮同一天，未推进。按「看节律不看天数」：仅停一轮，尚不算真滞后；下一轮仍停 10-29 则构成连续两天不动。

### 单侧读数（每轮必记）
**加密词 0 / 机器人词 0** —— 新形态（前七轮 26/0、0/13、12/10、39/10、0/0、0/0、4/1）。零幸存来自 seen 饱和，**不代表任一方向流量消失**。

### 判据级发现：漏斗已退化为 seen 单通道
84 条原始里 83 条被 seen 吃掉、1 条被 EXCL 挡；carrier 丢弃 **= 0（连续第九轮）**、查询失败 = 0。除 seen 外只剩一个常数项 —— 同一条 `From bits to atoms: A survey of cross-layer safety in Embodied AI`（2026-10-02），**连续第五轮**。脚本提示的「1 条穿过 seen 却死在过滤器 = 唯一未知」实际无未知，就是这条常数项。

含义：产出能力现在**完全由「26 词能否在窗口内产生 unseen 命中」决定**，过滤层已无调节空间。若下轮仍 0 幸存，问题只能出在词表覆盖（有词≠有召回），不在漏斗。

### 幸存者
无。**不写 labels、不发 notify**（零命中静默）。

### 待办
1. `ti:"consensus" AND cat:cs.DC` 加 `blockchain`/`validator`/`Byzantine` 限定词 —— **先 `check:` 量 60d** 再改；本轮调用已超日常预算，未跑（两轮未动）。
2. 14 词未配 carrier 表（`CARRIER_BY_TERM` 代码改动，需 PR）。
3. 新增：若下轮回填仍 0，取一个「长期 0 命中但方向明显有流量」的词做 `check:` 写法对照。

## Summary
- 跑完 `skills/arxiv-radar/scan.py` 第 32 轮（30d / 26 词），结果 `ARXIV_RADAR_OK`，原始 84 → 幸存 0。
- 零幸存来自 seen 饱和（83/84），非查询失败、非流量下降；7 个零命中词跨窗均有命中，不删词。
- 写入 `memory/logs/2026-10-31.md` 的 `### arxiv-radar（第 32 轮）` 一节（含六分类、跨窗、单侧读数、判据级发现）。
- 未写 `memory/arxiv-labels.tsv`（幸存 0）；未发 notify（零命中）；未改词表（本轮无依据）。
- 待办：consensus 限定词需先 `check:` 60d；14 词 carrier 表需 PR；MEMORY.md 的 arxiv-radar 行仍指向第 31 轮，留待 `memory-flush` 下轮更新。

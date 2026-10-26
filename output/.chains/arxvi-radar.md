30 天窗口跑完了。产物已落 `output/arxiv/`，本轮 `dry-run` 未推送、未写 `seen`。

## 口径与漏斗

| 项 | 值 |
|---|---|
| 词表 | 24 词，`ti:` only |
| 窗口 | `202609261019` → `202610261019`（30 天） |
| 原始命中 | **62** |
| 丢弃 | seen=31 · excl=1 · carrier=4 · fail=0 |
| 幸存 | **26** |
| 耗时 | 77s |
| 窗口内最新收录 | **2026-10-22**（连续第 5 天没动） |

**四分类（分开记）**：查询失败 **0** / 真零 **10** / 全已见饱和 **10** / 有新增 **4**

来源：`export.arxiv.org/api/query` · `skills/arxiv-radar/scan.py` 的 `TERMS` · `output/arxiv/audit.log`

## 幸存名单（按簇）

**A · 自我中心人类数据 → 人形与灵巧操作（18 条，独占 69%）**
- `SocialCoAct` 用 VLM 做自我中心社交协同的基准 · https://arxiv.org/abs/2610.24559
- `Ego2Contact` 从自我中心人类视频预测接触 · https://arxiv.org/abs/2610.22932
- `KODA` 人类自我中心演示的运动学—观测数据对齐 · https://arxiv.org/abs/2610.21152
- `EgoMatrix` 从人类视频生成物理可信的灵巧演示 · https://arxiv.org/abs/2610.18822
- `λ0` 开放世界自我中心人类数据的规模化 · https://arxiv.org/abs/2610.18950
- `VioLA` 从人类数据学通用人形控制策略 · https://arxiv.org/abs/2610.12435
- `Workhorse` 从人类数据学全身人形移动操作 · https://arxiv.org/abs/2610.09117
- `EgoLAP` 语言—动作推理下的自我中心人类数据学习 · https://arxiv.org/abs/2610.08726
- `Ego4WAM` 缩放自我中心人类数据时什么才重要 · https://arxiv.org/abs/2609.40341
- `Towards a General Humanoid` 自我中心全身人类数据预训练 · https://arxiv.org/abs/2610.00438
- `OccluDex` 自遮挡下的 3D 视触觉表示 · https://arxiv.org/abs/2609.39017
- `DexRoam` 从全身人类演示学移动双臂灵巧操作 · https://arxiv.org/abs/2609.35761
- `MonoEgo` 单目度量自我中心演示采集 · https://arxiv.org/abs/2609.34512
- `EgoReveal` 部分遮挡下的主动视觉与物体操作 · https://arxiv.org/abs/2610.12999
- `ESCAPE` 自我中心感知用于避障与策略执行 · https://arxiv.org/abs/2610.23943
- `Never Look Back` 自我中心视频中 3D 物体记忆的持续性 · https://arxiv.org/abs/2610.10538
- `RoboCap` 自我中心机器人学习平台 · https://arxiv.org/abs/2610.07217
- `DR-VLA` 用自我中心网络视频学四足类人导航 · https://arxiv.org/abs/2610.18373

**B · Data engine / 数据生成（6 条）**
- `CoDA` 数据引擎与动作策略共演化 · https://arxiv.org/abs/2610.22362
- `AutoRSR` 自动 real-to-sim-to-real 数据生成 · https://arxiv.org/abs/2610.20336
- `OneDemo` 单次演示同时学策略与生成数据 · https://arxiv.org/abs/2610.18188
- `DexNinja` real-to-sim-to-real 数据引擎学灵巧切割 · https://arxiv.org/abs/2610.17208
- `FlashDexRetarget` 多动作重定向加速灵巧数据生成 · https://arxiv.org/abs/2610.01849
- `NavAble` 盲人导航数据集与合成数据管线 · https://arxiv.org/abs/2610.19330 ← 域外漂移，非操作类

**C · 世界动作模型 / 表示（2 条）**
- `Perceive, Predict, and Plan` 自我中心灵巧操作的统一世界动作模型 · https://arxiv.org/abs/2610.22363
- `EgoJEPA` 主动作自我中心视频的灵巧操作（JEPA 路线） · https://arxiv.org/abs/2610.20904

## 判据级发现

**① 30 天口径下首次出现单侧读数：加密通道 0 条，机器人通道 26 条。** 真零 10 词里 9 个是链上/加密词（verifiable inference · light client · proof of learning · verifiable training · restaking · consensus protocol · `cat:cs.CR AND ti:"MEV"` · liquid staking · `ti:"Robinhood Chain"`），第 10 个是 `robot manipulation data`。同一有效窗口内幸存全部来自 4 个机器人词。**不能据此删加密词**（可能只是论文侧未到），但也不能再假设三条平行探针同步点亮。

**② 单词集中度 69%，但不判为假簇。** `ti:"egocentric" AND cat:cs.RO` 单独覆盖 18/26，抽掉它幸存掉到 8。与 probe 簇「单词主导 = 单一概念假象」同形状，但主题词确实落在词表语义内（egocentric human data → VLA/WAM 训练数据），暂判真簇，只记录集中度，不改词。

**③ 30d 首次跑会推出沉积层。** 26 条幸存与 `seen` 重叠 = **0**，佐证是这 26 条的 `published` 全在 **09-28 → 10-17**，落在 10-19 之后的为 0 条 —— 它们全在各轮 7d 窗左边界之外，7d 跑结构上看不见。同日三跑对照：7d 幸存 0–3 条，30d 幸存 26 条。`seen` 去重按 id、跨窗口无洞，但**若把默认窗口改到 30d，首跑会一次性推出 26 条**，需先决定是否接受这次洪水。

**④ 索引滞后第 5 天。** 名义 30 天窗有效覆盖仅 09-26 → 10-22 共 27 天。10-23 起四类目同日同形归零，昨日已核实为全局收录延迟，非无人投稿,本轮不作为异常上报。

**⑤ 脚本不自带跨窗复量。** `grep` 确认 `scan.py` 无 60d 分支，digest 里 `win/30d/60d` 三列本轮实为同一个 30d 值 —— 判词死活时不能当三窗读数用。

## Summary

- 执行 `skills/arxiv-radar/scan.py "dry-run days:30"`：24 词 / 30 天窗 / 原始 62 → 幸存 26，77s，0 查询失败。
- 产物：`output/arxiv/out.json`（26 条）· `report.md`（已生成）· `audit.log`（33 行）。
- `memory/arxiv-seen.json` 未写盘（dry-run，仍 78 个 id）；`./notify` 按 `dry-run` 跳过。
- 日志：`memory/logs/2026-10-26.md` 追加 `### arxiv-radar — 第三轮` 与 under-the-hood 两节。
- 过程中我曾写下一个未经测量的「90d 重叠 22/26」数字，已核对推翻并改为实测值（重叠 0，区间 09-28→10-17）。
- 待决：是否把 `arxiv-radar` 默认窗口从 7d/30d 定到 30d —— 需先接受首跑 26 条的一次性推送量。

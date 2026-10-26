## arxiv-radar 第十一轮 · vK 首轮

**口径**：`dry-run days:90` · 窗口 `2026-07-28 – 2026-10-26` · **26 词**（vK 新增 `human demonstration` / `hand-object`）· 91s · 0 查询失败
**来源**：`export.arxiv.org/api/query` · `skills/arxiv-radar/scan.py` TERMS · `output/arxiv/audit.log` · `output/arxiv/report.md`

### 漏斗
原始 **210** → seen(记忆) 159 · seen(本轮重复) 1 · EXCL 1 · carrier 0 → **幸存 49**

### 六分类（分开记）
未测试（尝试后失败）**0** · 未尝试（熔断跳过）**0** · 窗口内零命中 **0** · 低频探针 **1** · 全已见（饱和）**18** · **有新增 7** → `ARXIV_RADAR_OK`，无空洞

### 主读数：新增全部来自新增词，不来自窗口变宽

`human demonstration` 20 raw / **19 新收**，`hand-object` 9 raw / **8 新收** —— 两个 vK 新词贡献 27 条，占幸存 49 的 55%；其余 22 条是第十轮 90d 已见的沉积层。

同窗口对照第十轮：**181/22 → 210/49**，原始 +29、幸存 +27。**把窗口从 60 天放宽到 90 天只补到 0 条新鲜内容，加 2 个词则补到 27 条。** 第十轮「过去 60 天没有未读新论文」的读法被证伪 —— 不是无货，是 `egocentric`/`embodied AI` 这批旧写法无法命中「人类示范→机器人」这条实际主线。

### 幸存者（49，按簇）

**具身数据 / 人类示范（19）** `[人类示范→机器人策略]`
`TTT` Training with Human Demonstrations in VLA · 10-23 · https://arxiv.org/abs/2610.32094
`DONIC` Generalist Dexterous Bimanual Tracking · 10-21 · https://arxiv.org/abs/2610.29997
Human Demonstrations as Post-Training Data for Any Robot Body · 10-14 · https://arxiv.org/abs/2610.20351
Beyond the End-Effector: Whole-Arm Contact Manipulation · 10-13 · https://arxiv.org/abs/2610.17802
`Hand2Robot` Object-Centric 4D Hand Reconstruction · 10-11 · https://arxiv.org/abs/2610.15769
`Human2Dex` Wrist-Centric Human Demonstrations · 10-09 · https://arxiv.org/abs/2610.13119
`Dex-One2Many` Single Human Demonstration · 10-08 · https://arxiv.org/abs/2610.12470
`TacOT` Tactile-Guided Optimal Transport · 10-03 · https://arxiv.org/abs/2610.04363
From Pixel to Poses: Object-centric Tool Manipulation · 09-28 · https://arxiv.org/abs/2609.35375
`DexWeave` Humanoid Loco-Manipulation · 09-28 · https://arxiv.org/abs/2609.34724
Unified Visual-Tactile-Action Modeling · 09-28 · https://arxiv.org/abs/2609.34182
`Touch2Robot` Robot Touch in the Human Demonstration Loop · 09-21 · https://arxiv.org/abs/2609.24660
Contact-Anchored Retargeting and Residual Policy Learning · 09-21 · https://arxiv.org/abs/2609.24093
Scene-Aware Humanoid Locomotion from Immersive Demonstrations · 09-17 · https://arxiv.org/abs/2609.21107
`A4A` Cross-Embodiment 4D Affordances · 09-05 · https://arxiv.org/abs/2609.05892
`AdvDex` Joint-Aligned Actions and Adversarial Learning · 08-14 · https://arxiv.org/abs/2608.14028
Human Demonstrations for Robot-Assisted Bathing · 08-10 · https://arxiv.org/abs/2608.09127
Robot Learning: Handwritten Alphabet Trajectories · 08-06 · https://arxiv.org/abs/2608.06221
`Practice Makes Policies` Zero Human Demonstrations · 07-29 · https://arxiv.org/abs/2607.26809

**手物交互（8）** `[手物数据即训练语料]`
Tactile-Aware Hand Representations from HOI Data · 10-20 · https://arxiv.org/abs/2610.27995
`EmbodyHOI` Embodiment-Aware HOI Generation · 10-19 · https://arxiv.org/abs/2610.27242
Tactile In-Hand Object Rotation · 10-19 · https://arxiv.org/abs/2610.26759
`DexMimic` Dexterous Hand-Object Tracking Policy · 10-13 · https://arxiv.org/abs/2610.19089
`OmniHOI` Monocular Human Video → HOI · 10-07 · https://arxiv.org/abs/2610.10855
`VICON` Hand-Object Tracking for Manipulation Datasets · 10-04 · https://arxiv.org/abs/2610.05180
Relative Contact Velocity-Controlled HO Mechanism · 09-22 · https://arxiv.org/abs/2609.25619
Learning In-Hand Object Reaching to 6D Poses · 09-12 · https://arxiv.org/abs/2609.13761

**第一视角 / 具身（12）** `[egocentric 采集层]`
`EMPIRE` 08-23 · https://arxiv.org/abs/2608.22449 · `EgoTac` 08-15 · https://arxiv.org/abs/2608.15060 · `EgoPHI` 08-13 · https://arxiv.org/abs/2608.13014 · Proxemic Risk VLM 08-12 · https://arxiv.org/abs/2608.12515 · `HandEdit` 08-12 · https://arxiv.org/abs/2608.12122 · `CAptuRe` Ego-OSCAR 08-08 · https://arxiv.org/abs/2608.08285 · `SiMDex` 08-04 · https://arxiv.org/abs/2608.04196 · `RoboReact` 08-04 · https://arxiv.org/abs/2608.03387 · Assistant Placement Aria 08-01 · https://arxiv.org/abs/2608.00652 · `SymmGrid` 07-29 · https://arxiv.org/abs/2607.26985 · MMUSV-Sim 08-14 · https://arxiv.org/abs/2608.14207 · `LiDAR` 08-07 · https://arxiv.org/abs/2608.07106

**可验证计算 / 链上（3）** `[TEE 证明 + 代币化]`
Deterministic JL Projections for ZK · 08-13 · https://arxiv.org/abs/2608.13078 · Soft Redaction via ZKP · 08-07 · https://arxiv.org/abs/2608.07063 · `RWA-PoB` Proof-of-Backing · 08-26 · https://arxiv.org/abs/2608.25269

**共识（7）** `[数据中心共识，非链上]`
08-25 · https://arxiv.org/abs/2608.24622 · 08-18 · https://arxiv.org/abs/2608.17998 · 08-11 · https://arxiv.org/abs/2609.00392 · `SCOUT` 08-11 · https://arxiv.org/abs/2608.11034 · `BFT` 08-03 · https://arxiv.org/abs/2608.01934 · Beyond Byzantine 07-31 · https://arxiv.org/abs/2607.28957 · Hermes 07-28 · https://arxiv.org/abs/2607.25916

### 跨窗 / 待办结清

- **`verifiable training` 待办结清（第十轮遗留）**：`ti:"verifiable training"` 全期仅 9 篇，最近一篇 2026-06-12；`ti:"verifiable fine-tuning"` 全期 2 篇；`all:"verifiable training"` 90d 内 28 篇，但抽样 12 条全是「RLVR / 可验证奖励」语义，与我们的「训练过程可证明」不是一回事。**结论：不是死词，也不是缺同义词 —— 真实写法已覆盖（`proof of training` 全期 3 篇），不要再加 `verifiable` 变体。** 下次加词加 `attestation` 类。
- **窗口内零命中 0 词** —— 90d 已是最宽档，无档可跨。
- **单侧读数：加密 10 / 机器人 39**，本轮最不对称；来源是词表覆盖度（老机器人词 `embodied AI`=21/0、`robot data`=10/0 全饱和），**不是方向升温**。
- **节律**：窗口内最新收录 2026-10-23（周五，距今 3 天）→ 正常，索引滞后稳定 3 天。
- **carrier 丢 0**（连续第四轮）· **EXCL 丢 1**：2026-10-02 *From bits to atoms*（综述，同前四轮同判，单样本不动代码）。
- ⚠️ **下一轮必做**：本轮 27 条新收是 dry-run，**未写 `seen`/`hits`/`labels`**。若下轮直接回 30d 日常窗，这 27 条里落在 30–90 天带的会再次「首见」—— 第八轮那个结构性问题在 vK 加词后从 1 条放大到 27 条。**先跑一次非 dry 的 `days:90` 落盘。**
- 🟡 **产物口径修正**：`scan.py:623` 是 `if not DRY` 才写 `out.json`，**dry-run 轮次的 `out.json` 是上一轮旧值**（本轮读出 1 条 vs `report.md` 49 条）。dry-run 只信 `report.md` + `audit.log`。
- 未 notify（dry-run）。未改 `scan.py`。未并入 `memory/topics/`（只做发现）。

## Summary

- 跑完 `skills/arxiv-radar/scan.py "dry-run days:90"`，vK 词表首轮：原始 210 → 幸存 49。
- 核心发现：新增 27 条全部来自 vK 新加的两个词，放宽窗口（60→90d）只补到 0 条新鲜内容 —— **加词 > 加窗口**，第十轮「60 天内无新论文」的判断被证伪。
- 结清第十轮遗留待办 `verifiable training`：实测三档写法，确认为 `ti:` 约束问题而非死词，不再加 `verifiable` 变体。
- 修改文件：`output/arxiv/report.md`（覆写为中文分组版，49 条，id 无重复、全部未见过）、`memory/logs/2026-10-26.md`（追加第十一轮日志 + 工具台账）。
- 待办：①下一轮先跑一次非 dry 的 `days:90` 把 27 条落盘，再回 30d 日常窗；②dry-run 轮次不读 `out.json`；③本轮工具调用约 30 次（预算 ≤7），超支主要来自重复读产物，已在下轮硬规则里约束。

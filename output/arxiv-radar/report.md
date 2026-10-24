# arXiv Radar — 90 天回补（dry-run）

**窗口** `2026-07-26 → 2026-10-24` · 20 词 · 原始 91 · 幸存 **22** · 失败 0
`carrier` 丢 11 · `excl` 丢 1 · `seen` 命中 57

> 索引滞后：窗口内最新收录 **2026-10-22**。按日计数 `cs.CR` 10-21=38 / 10-22=30 / **10-23=0 / 10-24=0**，`cs.RO` 同形（70 / 57 / 0 / 0）—— 全局收录延迟，不是无人投稿。

---

## 机器人 / 具身数据（20 篇）

与 DEUS / XMAQUINA 叙事同轨的唯一板块。其中「数据采集 / 合成 / 仿真基础设施」占 11 篇。

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 10-08 | StereoEngine | 不用立体相机也能合成双目双臂机器人数据 | https://arxiv.org/abs/2610.12734 |
| 10-06 | EmbodiedSmith | 仿真里的递归自我改进飞轮，用来扩具身数据 | https://arxiv.org/abs/2610.07969 |
| 10-01 | NEEDLEWORK | 离线重写机器人数据，把不可用轨迹局部缝合 | https://arxiv.org/abs/2610.02339 |
| 09-28 | SkillWeaver | agentic 探索替代遥操作，规模化生成机器人数据 | https://arxiv.org/abs/2609.36171 |
| 09-23 | Listening and Mirroring | 言语调谐与行为模仿如何影响具身 AI 的社交感知 | https://arxiv.org/abs/2609.27246 |
| 09-22 | PhyVisGen | 物理与视觉双高保真的操作数据生成（软夹爪） | https://arxiv.org/abs/2609.25653 |
| 09-21 | ARSTAG | 一张 RGB + 一句自然语言 → 任务专属 Real2Sim2Real | https://arxiv.org/abs/2609.24563 |
| 09-21 | Uranus | 面向具身 AI 的下一代仿真基础设施，数据驱动自回归扩散 | https://arxiv.org/abs/2609.24815 |
| 09-20 | Identity Continuity | 长期具身 AI 关系中的身份连续性 | https://arxiv.org/abs/2609.23356 |
| 09-16 | UMI-Bridge | 人类与机器人操作数据的动作锚定潜空间对齐 | https://arxiv.org/abs/2609.18232 |
| 09-13 | OJOx | 建筑场景具身 AI 的规格条件化演示 | https://arxiv.org/abs/2609.22289 |
| 09-10 | Organizational Principles | 用人类组织理论编排具身 AI 多智能体 | https://arxiv.org/abs/2609.11737 |
| 09-05 | IM-ENGINE | 用图像编辑生成具身数据 | https://arxiv.org/abs/2609.06279 |
| 08-28 | When Robots Mishear Us | 语音识别错误如何让具身 AI 执行危险指令 | https://arxiv.org/abs/2608.28518 |
| 08-22 | GuardianBench | 固定场景、只换指令的潜在情境风险基准 | https://arxiv.org/abs/2608.21928 |
| 08-19 | Vision-Language Models for Egocentric Video | 第一视角视频的 VLM 能力盘点 | https://arxiv.org/abs/2608.18671 |
| 08-15 | GUIDER | 遥操作操作中无目标人类意图推理的实测评估 | https://arxiv.org/abs/2608.15446 |
| 08-05 | Deltoris | 位级稀疏 + 推测推理，让 VLA 在边缘实时跑 | https://arxiv.org/abs/2608.04428 |
| 07-30 | ACE-Data-0 | 以人为中心的环境采集作为具身数据引擎（16 人） | https://arxiv.org/abs/2607.28625 |
| 07-30 | Policy-Level Recursive Self-Improvement | 临界性世界模型指导场景采集的策略级自改进 | https://arxiv.org/abs/2607.28251 |

## MEV / AMM（2 篇）

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 09-15 | When AI Agents Meet MEV | AI agent 当搜索者的跨链套利，用 Base 23,000 笔 V3 成交实证 | https://arxiv.org/abs/2609.17897 |
| 08-13 | Slow and Steady | 可验证延迟防 MEV：拜占庭与博弈两类正结果 + 负界 | https://arxiv.org/abs/2608.13271 |

---

## 本轮的两件实事

### 1. carrier 又漏了一篇 —— 已修

`2608.13271` Slow and Steady 是正经 MEV 防御论文，但全篇只写 **"distributed ledger" / "block creator"**，不出现 `blockchain` / `token` / `validator` / `deploy`。原 `CARRIER_MARKET` 六个词（arbitrage/swap/liquidity/order flow/searcher）一个都不含 → 被静默丢弃。

- **实证范围**：`amk` + `MEV` + `consensus protocol` + `restaking` 四词 90 天窗，追加 8 个 ledger 系词后**只多捞 1 篇（就是它），零噪声**。
- **改法**（已在 `skills/arxiv-radar/SKILL.md`）：`CARRIER_MARKET` 追加 `ledger` / `ledgers` / `block creator` / `block builder` / `block proposer` / `transaction ordering` / `on-chain` / `state transition`。
- **效果**：幸存 21 → **22**，carrier 丢弃 12 → **11**。ZK 域未动（放宽会引噪，前轮已验证）。

### 2. 🔴 `arxiv-seen.json` 缺 90 天机器人存量 —— 下次正式 90d 跑会一次推 22 条

`memory/arxiv-seen.json` 现有 53 个 id，全部是**修 carrier 之前**那批 ZK / 理论论文。第五轮正式跑用的是 **7 天窗**，`hit_ids` 为空，写盘分支跳过 —— **carrier 修好后新解锁的 21 篇机器人论文因此从未落盘**。

- 验证：21 篇 survivor **无一**在 `seen` 里（逐个 `in seen` 检查，命中 0）。
- 后果：任何未来的 `days:90` 正式跑都会把这 22 篇当新命中重新推送一次。
- **建议**：正式 90 天跑之前，先用本报告的 22 个 id seed `memory/arxiv-seen.json`（dry-run 不写盘，故本轮未落）。

### 过滤器健康度

- `excl` 仅丢 1 篇，且正确：`2610.14038` "From bits to atoms: A survey of cross-layer safety in Embodied AI" —— 真综述。
- `2608.18671` 标题不含 survey/tutorial 但读起来像综述，下一轮可核 arXiv `comment` 字段确认。
- 零命中 15 词：`proof-of-useful-work`、`verifiable inference`、`light client`、`proof of training`、`proof of learning`、`verifiable training`、`auditable training`、`data availability sampling`、`restaking`、`consensus protocol`、`liquid staking`、`automated market maker`、`zero-knowledge`、`ti:"EIP-1559"`、`ti:"Robinhood Chain"`。按铁律「零命中不等于废词」**保留不删** —— 90 天窗下 `restaking` 全期仍有 1 篇（`2608.09055`），已在此前轮次处理过。

**通知：未发送**（dry-run，且按策略只有正式跑才推）。

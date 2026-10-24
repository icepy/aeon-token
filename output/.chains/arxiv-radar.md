90 天回补已跑完。**通知未发（dry-run）**，以下是全部结果。

# arXiv Radar · 90 天回补

**窗口 07-26 → 10-24 · 18 词 · 原始 89 条 → 去重 85 篇 → 幸存 38 篇。**
上一轮 7 天窗只有 4 条原始命中，这轮把 3 个月存量一次拉齐。

先说一个**必须先修的东西**：这轮跑出来的 38 篇，有一半的可信度问题不在词表，在过滤器代码。

## 🔴 过滤器缺陷（三处，已定位到行）

**1. `EXCL` 是全文子串匹配，不是标题匹配。** 代码里 `if any(x in blob for x in EXCL)`，`blob` = title + summary。于是 `surveyed`、`benchmarks`、`benchmarking`、「as a benchmark」全被当成综述过滤掉。**20 条 excl 丢弃里 16 条是正文误伤。**

实证误杀（都是该进名单的）：
- `2608.09055` Repeated-Game Security for Restaking-Based Verifiable Inference — 被 `surveyed` 命中
- `2610.08258` zkLLMPoT: Zero-Knowledge Proof of Training — 被 `benchmarks` 命中
- `2609.16705` The Robot Data Factory（Haddadin 等 21 人）— 被 `benchmarking` 命中
- `2608.05011` Decentralized Searcher Competition in MEV Markets — 被名词「as a benchmark」命中

**改法：`EXCL` 只对 title 判。** 幸存者 38 → **49（+11）**。

**2. `benchmark` 这个字本身太毒。** 即使改成标题匹配，论文标题里的 `benchmark` 多半是「我们提出一个 benchmark」——那是个正经项目，不是要过滤的综述。建议 `EXCL` 收窄为 `survey` + `tutorial`。

**3. 跨词命中只记第一个词。** `2609.07963` 同时中 `light client` 和 `zero-knowledge`，只归给先到的 `light client`，导致宽词账面偏低。不影响名单，影响词表健康度判断。

> 索引滞后不用再报了：上一轮记的「10-23/10-24 两天 0 条」本轮复核为 **cs.CR 30 条**，已自愈。

## 名单（38 篇，按簇）

### 零知识 · 16 篇（最大簇）
- **ZKPU** — ZKP 异构负载的专用加速器，曲线系 + 哈希系双覆盖 `2610.27530`
- **Can AI Oversight Be Zero Knowledge?** — Chiesa 组，验证 AI 输出不泄露输入 `2610.01995`
- **Bits Under ZK-LLM** — 面向 ZK 电路友好的 LLM 量化 `2609.36437`
- **Zero Knowledge Proofs in Quantum Networks** — 量子网络下的 ZKP 构造 `2609.35339`
- **zkSAS** — 频谱接入管理的可验证分配 `2609.28699`
- **Sound Debloating** — ZKML 电路里冗余约束的可靠裁剪 `2609.10149`
- **Guppy** — Danezis / Sonnino 等，递归 ZKP 做轻客户端，验证者只签状态增量 `2609.07963`
- **OreProof** — 关键矿产供应链的可验证溯源（HICSS-60） `2609.00340`
- **ZK Predicate Proofs Between AI Agents** — agent 间跨协议断言证明网关 `2608.30083`
- **Relaxed Sender Anonymity for CBDC** — 许可链 EVM 上的 CBDC 行间结算 `2608.28529`
- **Certified but Private** — 神经网络鲁棒性/公平性保证的 ZK 证明 `2608.17070`
- **Balancing Privacy and Compliance in DeFi** — 跨链可审计 ZK 框架 `2608.15276`
- **NiyamAI** — 带 ZK 可验证护栏的 intent-bound agent `2608.07167`
- **ZK-SR117** — 聚合公平借贷指标的 ZK 证明 `2608.02664`
- **Hollow-LLM Attack** — ZK 验证 LLM 推理的伪权重攻击面 `2607.28884`
- **Joint Lyapunov Certificates** — 多 agent 生成式 AI 治理的 ZK 证明 `2608.09087`

### 机器人 / Embodied AI · 8 篇 + 1 误杀 ← **唯一与 DEUS 同轨的板块**
- **Robot Data Factory**（误杀，`2609.16705`）— Haddadin 等 21 人，主张核心资源是「机器人经验」而非原始数据
- **Vision-Predictor-Action** — 用 JEPA 预测器替代 token-by-token 解码 `2610.15556`
- **Beyond LLM Serving** — VLA 工作负载刻画，按时限设计端侧推理 `2610.05062`
- **Inspect Robots** — 开源具身能力/安全评测框架 `2610.06306`
- **MEAN** — 移动具身网络的移动量 + 压缩比联合设计 `2610.02334`
- **From Gameplay to Policy** — 游戏化无机器人交互采数据 `2609.18650`
- **Ego2Robot** — 第一人称人类视频合成机器人数据 `2608.02580`
- **Operational digital twin clinics** — 数字孪生诊所做具身评测 `2608.21416`
- **DropClick** — 农业机器人的一键分割标注 `2609.03680`

### 共识 · 6 篇
- **Flamingo** — DAG 共识的负载均衡 `2609.28361`
- **Sharpedo** — 双模无证书 DAG 共识（UCL 硕士论文，Jovanovic / Sonnino 指导）`2609.05580`
- **PoVD** — 基于 VDF 的轻量共识 `2609.21627`
- **MEV Attacks on DAG-Based BFT** — 提议者排序裁量权的攻击谱系 `2609.20069`
- **SoK: Formal Verification of Consensus** — `2608.21935`
- **Fast Tendermint** — `2608.13434`

### MEV / AMM · 4 篇
- **EVAGE** — 多 agent 全自动 MEV 策略生成 `2609.27424`
- **Otter** — 剩余再分配实现可证抗 MEV 的批量 AMM `2609.03474`
- **Mandate without Managers** — 把 AMM 当可验证组合产品（Balancer G3M）`2608.02917`
- **There Will Be Spam** — 状态不变交易与投机性 MEV `2607.24172`

### 可验证训练 · 2 篇
- **OPEN-1B** — 首个「完全可审计」训练跑，逐位可复现 `2609.17380`
- **Auditing Training Labels** — label-only 后门下的训练标签审计 `2610.13051`

### 单篇
- **Pearl PoUW 系统化** `2610.25347` — 与 10-21 已研究的 Pearl (PRL) 同一对象，非新项目
- **TCDA** `2610.22508` — 可调编码分布式数组做 DAS

## 词表观察

`proof of learning`（all-time 13，最新 05-22）、`verifiable training`（9，06-12）、`liquid staking`（9，05-01）——90 天 0 命中，all-time 也停在几个月前。**真降温，不是词写错**，按铁律保留。

## 下一轮正式跑前必须先做一件事

`memory/arxiv-seen.json` **仍不存在**（这次也是 dry-run）。正式跑若不先落这 38 个 id，第一次推送会是一次 38 条的洪水。建议先补写 id 再发。

## Summary

- **扫描**：18 词 × 90 天窗口，85 篇去重后幸存 38 篇，按 7 个簇分好。
- **发现三处过滤器缺陷**，第一处（`EXCL` 全文匹配）实证误杀 16 篇，含 4 篇明确该进名单的；修复后幸存 38 → 49。
- **最重要的一条内容发现**：机器人/Embodied AI 是本轮唯一和 DEUS/XMAQUINA 叙事同轨的板块（8 篇 + 1 篇被误杀），且其中 Robot Data Factory 恰好是被过滤器错杀的那篇。
- **修改文件**：`memory/logs/2026-10-24.md`（追加本轮记录）。未写 `memory/arxiv-seen.json`（dry-run）。
- **通知**：未发送（dry-run）。
- **后续动作**：① 改 `skills/arxiv-radar/SKILL.md` 的 `EXCL` 为标题匹配并收窄字表；② 正式跑前先落 38 个 id 到 `arxiv-seen.json`，避免首推洪水。

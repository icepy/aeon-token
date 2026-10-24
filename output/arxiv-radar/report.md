# arXiv Radar · 90 天回补（dry-run）

窗口 `2026-07-26 → 2026-10-24` · 18 个词 · 原始 89 条 → 去重 **51 篇幸存** · 0 失败
过滤：`ti:` only · EXCL 只判标题（已修上一轮的全文误伤）· carrier 37 篇（42%）

## 词表命中（本轮口径）

`zero-knowledge` 28 · `embodied AI` 21 · `robot data` 9 · `consensus protocol` 6 · `cat:cs.CR AND ti:"MEV"` 6 · `automated market maker` 4 · `embodied data` 4 · `auditable training` 3 · `robot manipulation data` 2 · `proof-of-useful-work` 1 · `verifiable inference` 1 · `light client` 1 · `proof of training` 1 · `data availability sampling` 1 · `restaking` 1

零命中 3 个：`proof of learning` · `verifiable training` · `liquid staking` —— all-time 也都停在 05–06 月，按铁律保留观察，不删。

---

## 机器人 / 具身数据（15）— 唯一与本仓叙事同轨的板块

| 日期 | 项目名 | 作者 | 一句话 |
|---|---|---|---|
| 10-11 | Vision-Predictor-Action | Yeonseok Lee | 神经符号 JEPA 预测器做具身 AI 的高效世界模型 |
| 10-05 | Inspect Robots | Christopher Leet et al. | 具身 AI 能力与安全性的机器人侧评测 |
| 10-04 | Beyond LLM Serving | Seonghun Jung et al. | VLA 负载画像，给具身 AI 系统设计定硬件规格 |
| 10-03 | EnvDreamer | Kabir Swain et al. | 多模态输入直接生成可训练环境 |
| 10-01 | MEAN | Yahao Ding et al. | 移动具身网络的运动-压缩联合设计（通信侧，非数据侧） |
| 09-16 | Project Kitchen | Zheng Li et al. | VR 游戏化采集人类操作数据，再迁移到真机 |
| 09-15 | **The Robot Data Factory** | Sami Haddadin et al.（21 人） | 把「机器人经验」而非原始数据当核心资源，建持续生成/校验/复用的基础设施 |
| 09-13 | ORDER | Sathi & Tiwari | 虚构世界 benchmark，测域自适应 |
| 09-07 | NutriBench-Kitchen | Yulin Wei et al. | 营养管理场景 benchmark（PubMed 生僻细分） |
| 09-03 | DropClick | Patrick Zimmer et al. | 农业机器人数据的一键半自动分割 |
| 08-31 | Ego2Robot | Ye Wang et al.（15 人） | 第一人称人类视频 → 机器人训练数据，规模化 VLA 预训练 |
| 08-13 | MEAN（干扰信道） | Ruopeng Xu et al. | 同上 MEAN 的能效版 |
| 08-12 | Digital twin clinics | Xinyuan Wu et al. | 数字孪生诊所做任务级评测 |
| 08-03 | CometVLA | Hanwen Wan et al. | 具身数据金字塔共训 + Global Action Prior token |
| 07-30 | World-Model Security | Fazhong Liu et al. | 世界模型具身 AI 的全生命周期威胁面 |

> 观察（不构成判断）：90 天里「机器人数据采集 / 合成 / 基础设施」≥6 篇，且 08-31 与 09-15 两篇都是 15–21 人大组。这是本窗口内**唯一在加速**的簇。

## ZK / 可验证计算（18）

| 日期 | 项目名 | 一句话 |
|---|---|---|
| 10-20 | ZKPU | ZKP 异构负载的专用加速器（cs.AR，硬件） |
| 10-01 | Can AI Oversight Be Zero Knowledge? | Chiesa 组，AI 监督的 ZK 化可行性 |
| 09-29 | Bits Under ZK-LLM | ZK 友好的量化选型，为可验证私有推理 |
| 09-28 | ZKP in Quantum Networks | 量子网络里的 ZKP（quant-ph，离链远） |
| 09-23 | zkSAS | 频谱接入管理的可验证证明（非链上） |
| 09-16 | ZK UNSAT Chaining | 归一化链式方法扩展 UNSAT 验证 |
| 09-09 | zkML Circuit Debloating | 删冗余约束，降 zkML 电路开销 |
| 09-07 | **Guppy** | Danezis 组，只承诺状态增量 + 递归 ZK 做轻客户端 |
| 08-31 | OreProof | 关键矿产供应链的可验证来源（RWA 味道） |
| 08-30 | ZK Predicate Proofs Between AI Agents | 跨协议网关 + source-integrity gap 实测 |
| 08-28 | CBDC Sender Anonymity | 许可链 EVM 上的 CBDC 结算 |
| 08-17 | Certified but Private | 神经网络保证的 ZK 证明规模化 |
| 08-15 | ZK Auditable Cross-Chain | DeFi 隐私-合规可审计跨链框架 |
| 08-10 | **Restaking Verifiable Inference** | 重复博弈下比例罚没会高估安全性 |
| 08-10 | Lyapunov AI Governance | 多智能体治理的随机稳定性（math.NA，边缘） |
| 08-07 | NiyamAI | 意图绑定 AI agent + ZK 可验证护栏 |
| 08-01 | ZK-SR117 | 公平借贷指标的分块 ZK 认证 |
| 07-30 | Hollow-LLM Attack | ZK 验证 LLM 推理时「平凡权重」攻击面 |

## MEV / AMM（7）

| 日期 | 项目名 | 一句话 |
|---|---|---|
| 10-16 | Uniform-Price AMM | 批式双边拍卖的统一价机制设计 |
| 09-29 | Active-Passive Gap | AMM LP 主动 vs 被动的收益缺口实证 |
| 09-23 | **EVAGE** | 全自主多智能体自动生成/移植 MEV 策略 |
| 09-03 | **Otter** | Elaine Shi 组，剩余再分配实现可证明 MEV 抗性 |
| 08-05 | Searcher Competition | MEV 搜索者去中心化竞争 |
| 08-03 | AMM as Portfolio Product | Feinstein 组，AMM 当可验证组合产品 |
| 07-27 | There Will Be Spam | 状态不变交易与投机 MEV 的实证画像 |

## 可验证训练 / PoUW（4）

| 日期 | 项目名 | 一句话 |
|---|---|---|
| 10-18 | **Pearl PoUW 系统化** | Youlong Ding，Pearl 白皮书 PoUW 的敏感度刻画 + 矿工自选噪声 |
| 10-09 | Label-Only Backdoor Auditing | 只给标签场景下的训练标签审计 |
| 10-06 | **zkLLMPoT** | 固定 checkpoint 后由审计方挑挑战序列，前向证明替代整条训练轨迹 |
| 09-15 | OPEN-1B | 一次完全可审计的训练运行（9 人） |

## DA / 共识（7）

| 日期 | 项目名 | 一句话 |
|---|---|---|
| 10-15 | TCDA | 可调编码分布式阵列做 DAS |
| 09-23 | Flamingo | DAG 共识的负载均衡 |
| 09-18 | PoVD | 基于 VDF 的共识协议 |
| 09-17 | MEV on DAG-BFT | DAG-BFT 共识上 MEV 攻击谱系（竞争/串谋/腐败） |
| 09-04 | Sharpedo | 双模无证书 DAG 共识 |
| 08-22 | Consensus Formal Verification | 共识协议形式化验证的 SoK |
| 08-13 | Fast Tendermint | Tendermint 加速 |

---

## 过滤器状态

- ✅ **bug 1 已修**：`EXCL` 只判标题。上一轮 20 条丢里 16 条是正文误伤；本轮仅 1 条（真 survey/tutorial）被丢，`2609.16705` Robot Data Factory 已回到名单。
- ✅ **bug 2 已修**：`benchmark` 移出 `EXCL`。`2609.22285` ORDER、`2609.07135` NutriBench-Kitchen 正常命中。
- ⚠️ **bug 3 未修，且本轮更明显**：跨词命中只记第一个词。实现上是因为本轮脚本边扫边把 id 写进 `seen`，第二、三次命中被当成 `seen` 直接短路（`drop.seen=4`）。所以本轮 `terms[]` 全程只有 1 个元素，`zero-knowledge` 这类宽词的账面被低估。**不影响名单，只影响词表健康度读数。** 修法：`seen` 只在 run 结束时合并，run 内用独立的 `hit_ids` 判重并 append term。
- `carrier` 丢 37 篇（42%），是本轮最大的过滤器。抽检 5 篇均为纯理论 / 纯硬件 / 非链上，丢弃方向正确。

## dry-run 副作用

`memory/arxiv-seen.json` **仍未生成**（三轮 dry-run 都未落盘）。下一次正式跑会把 51 篇全当新命中 —— 是一次 51 条洪水。

正式跑前先 seed：

```bash
python3 -c "import json;json.dump({i:'2026-10-24' for i in open('ids.txt').read().split()},open('memory/arxiv-seen.json','w'),indent=1)"
```

51 个 id（已去版本号）：
`2607.24172 2607.28226 2607.28884 2608.02580 2608.02664 2608.02917 2608.05011 2608.07167 2608.09055 2608.09087 2608.12849 2608.13434 2608.15276 2608.17070 2608.21416 2608.21935 2608.28529 2608.30083 2608.30289 2609.00340 2609.03474 2609.03680 2609.05580 2609.07135 2609.07963 2609.10149 2609.16705 2609.17380 2609.18650 2609.19353 2609.20069 2609.21627 2609.22285 2609.27424 2609.28361 2609.28699 2609.35339 2609.36437 2609.37963 2610.01995 2610.02334 2610.04301 2610.05062 2610.06306 2610.08258 2610.13051 2610.15556 2610.22508 2610.23547 2610.25347 2610.27530`

## 原始来源

`export.arxiv.org/api/query` · `submittedDate:[202607260000 TO 202610240000]` · URL 构造见本轮 `scan.py`（有改动：EXCL 标题化、benchmark 移出、按 id 去重并保留 `terms[]`、记录 `primary`/`authors`/`cats`）

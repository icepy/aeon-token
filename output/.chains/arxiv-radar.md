ℹ️ arXiv 60d · 幸存 20 · staking 精度 1/9

## arxiv-radar · 60 天补历史 · 幸存 20

窗口 `2026-08-27 → 2026-10-26` · 24 词 · 原始 141 → 幸存 20（seen 吸收 120 / excl 1 / carrier 0）。
窗口内最新收录 **2026-10-23**。

## 零知识（8 条）—— 全部是新收，纯密码学/硬件，无链上标的

- Zero Knowledge for Free up to Linear Query Bounds：拟线性规模常数查询 ZK PCP [零知识] · https://arxiv.org/abs/2610.29066
- SRE: 多标量乘中用标量冗余消除加速 ZK 证明 [零知识] · https://arxiv.org/abs/2610.27452
- Zero-Knowledge Proofs of Quantumness [零知识] · https://arxiv.org/abs/2609.23455
- ZK 签名框架：协作式自动驾驶里的后量子消息认证 [零知识] · https://arxiv.org/abs/2610.11490
- ZK 远程对抗攻击：针对 Wi-Fi 人体活动识别 [零知识] · https://arxiv.org/abs/2609.24173
- Locus：ZK 点加运算的硬件探索与优化框架 [零知识] · https://arxiv.org/abs/2609.18846
- ZK-Trace：联邦 GNSS 干扰监测的零知识凭证共谋溯源 [零知识] · https://arxiv.org/abs/2609.08763
- ZK-eSIM：隐私优先的 eSIM 开通方案 [零知识] · https://arxiv.org/abs/2609.07654

> 8 条里 6 条是纯原语/硬件/隐私应用，**没有一条是证明市场或链上可验证计算**。方向对，但离可交易标的仍远。

## 共识 / 质押机制（3 条）

- Effective-Balance Design in Ethereum Proof-of-Stake [共识] · https://arxiv.org/abs/2610.19699
- STAKE: 阻止合谋多数双花 [共识] · https://arxiv.org/abs/2610.01169
- Consensus with Stochastic Broadcast [共识] · https://arxiv.org/abs/2608.27336

## ⚠️ 词表污染：`staking` 命中的是 high-stakes，不是质押（8 条）

`ti:"staking"` 被词干化成 `stake*`，把这批 LLM 高风险决策论文全捞进来，**9 条原始命中里 8 条与质押无关**：

- Same Probabilities, Different Advice：高风险 LLM 决策支持中的得失框架效应 [？] · https://arxiv.org/abs/2610.29294
- 只负责维持人类生命的 agent 能否被劫持成杀人：高风险仿真环境下的延迟多轮派生动作陷阱 [？] · https://arxiv.org/abs/2610.15153
- Why LLM Agents Favor Their Group：Stakes、观察到的规范与声誉 [？] · https://arxiv.org/abs/2610.11008
- 高风险应急消息中的生成式 AI 翻译 [？] · https://arxiv.org/abs/2610.08601
- MERCI Cards：高风险领域的 LLM 评测与部署框架 [？] · https://arxiv.org/abs/2610.04430
- AI 集成与专家绩效的评价动力学：异质 stakes 下的认知依赖 [？] · https://arxiv.org/abs/2609.23135
- FairLens：视觉语言模型在高风险决策中的公平性基准 [？] · https://arxiv.org/abs/2609.01691

## 其他（2 条）

- inLoRA-MINT：用内部表示审计领域适配 LLM 的训练数据 [？] · https://arxiv.org/abs/2610.18051
- Real-World Asset (RWA) 代币化理论前导 [？] · https://arxiv.org/abs/2609.15797

## 本轮要看的只有一件事

`staking` 这个词本轮 **精度 1/9（11%）**，污染源是词干化后的 `stakes`。按铁律动作顺序是「换写法 → 降级 → 删词」：下轮用 `check:"proof-of-stake"` 与 `check:"liquid staking"` 量两个口径，不看就直接改是跳级。

其余：`zero-knowledge` 20 原始 / 8 新收，是本轮唯一稳定产出的真方向；加密侧其余词仍无链上标的级命中。
## arXiv Radar · 本轮 0 篇新论文

7 天窗（10-17 → 10-24）· 20 个词 · 原始 5 条 · **幸存 0**。

3 条已见（Pearl PoUW / ZKPU / TLM），2 条被 carrier 正确丢弃（纯复杂度理论、纯硬件 ZKP 加速）。**本轮无新增，不推论文。**

### 索引卡在 10-22

`cs.CR` / `cs.RO` / `cs.LG` / `q-fin` / `cs.DC` 在 **10-23、10-24 两天 total 全部为 0**，各类目最新收录一律停在 10-22。是 arXiv 全局收录延迟，不是没人投稿。

---

## 但发现一个真问题：过滤器方向是反的

对 `embodied data` / `robot data` / `embodied AI` 四个词做了 90 天全量核查：

**被 carrier 丢掉的 20 篇机器人论文，20 篇一个链上 carrier 词都不含。**

链上 carrier 是 `blockchain` / `token` / `validator` / `miner` 这一套 —— 机器人数据那批论文摘要里根本不会出现。

而幸存的 5 篇，靠的是同形异义：

- `token` 实为 GAP **tokens**（可学习瓶颈）
- `validator` 实为 **validator-passed** 虚拟环境
- `network` 实为 agentic **robot network**
- `protocol` 实为 facility-specific **protocols**（操作流程）

**真货全丢，噪声全进。**

### 为什么要紧

机器人/具身数据是词表里唯一与 DEUS 叙事同轨的板块。这个误杀等于把发现层的主信号关掉了，而且症状表现成「零命中」—— 跟话题死无法区分。

### 已修

carrier 改为按词分域：机器人簇用 `robotic` / `manipulation` / `simulation` / `teleoperation` / `ego­centric` 等；MEV 与 AMM 用 `arbitrage` / `swap` / `liquidity`；其余走原表。

**ZK 域刻意不动** —— 试过放宽，会捞回 8 条纯理论/硬件论文。同一个动作，机器人域是纠错，ZK 域是引噪。

90 天窗验证：**幸存 0 → 21**，carrier 丢弃 33 → 12，新增全在机器人（20）+ MEV（1），ZK 零噪声。

新增里 `2609.17897`（AI Agent × MEV 跨链套利）用了 **Base 上 23,000 笔 Uniswap V3 成交**做实证，是可复用的数据源线索。

PR #7 · 顺带修掉记了三轮的跨词命中 bug。

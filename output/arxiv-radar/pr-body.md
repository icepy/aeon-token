## 问题

`skills/arxiv-radar/SKILL.md` 的 `CARRIER` 是一组**链上**词：

```
deployed, deployment, mainnet, testnet, protocol, production, open-source,
released, blockchain, network, token, incentive, marketplace, validator, miner
```

它被无条件套在**每一个**命中词上。但词表里有一整簇是「具身 / 机器人数据」，那批论文的摘要里根本不会出现 `blockchain` 或 `token`。

## 实证（90 天窗，2026-07-26 → 2026-10-24）

对 `embodied data` / `robot manipulation data` / `robot data` / `embodied AI` 四个词的全部命中逐条检查：

**20 篇被 carrier 丢掉的论文，20 篇一个链上 carrier 词都不含。** 不是抽查，是全量。

而被判「幸存」的 5 篇，靠的是同形异义：

| id | 标题 | 实际命中的 carrier | 真实含义 |
|---|---|---|---|
| `2609.16705` | The Robot Data Factory | `token`, `network`, `production` | learnable **tokens**；**agentic robot network** |
| `2608.30289` | CometVLA | `token` | GAP **tokens**（可学习瓶颈） |
| `2610.04301` | EnvDreamer | `validator` | **validator-passed** virtual environments |
| `2609.22285` | ORDER | `protocol` | facility-specific **protocols**（操作流程） |

也就是说：**真货全被丢，混进来的是噪声。** 过滤器方向是反的。

这很要紧 —— 机器人/具身数据是词表里唯一与 DEUS / XMAQUINA 叙事同轨的板块（`memory/logs/2026-10-24.md` 早先几轮已经记过「唯一在加速的簇」）。这等于把发现层的主信号关掉了。

## 改法

carrier 按词分域，而不是全局一套：

```python
CARRIER_ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
                 "simulator", "dataset", "datasets", "real-world", "embodied",
                 "sensor", "egocentric", "demonstration", "vla"]
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher"]

CARRIER_BY_TERM = {
    "embodied data": CARRIER_ROBOT,
    "robot manipulation data": CARRIER_ROBOT,
    "robot data": CARRIER_ROBOT,
    "embodied AI": CARRIER_ROBOT,
    "automated market maker": CARRIER_BASE + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_BASE + CARRIER_MARKET,
}
```

未列出的词仍走 `CARRIER_BASE`（原 `CARRIER` 内容不变）。

**ZK 域刻意不动。** 试过放宽它（加 `proof` / `circuit` / `prover`），会把 `2610.29066`（纯复杂度理论）、`2609.23455`（ZK Proofs of Quantumness）、`2608.13078`（纯数学投影）等 8 条理论/硬件论文捞回来 —— 那正是 carrier 该干的活。按当前词表，ZK 的丢弃是对的。

## 验证

90 天窗，同一批 91 条原始命中：

| | 修复前 | 修复后 |
|---|---|---|
| 幸存 | **0** | **21** |
| carrier 丢弃 | 33 | 12 |
| 新增命中所在 | — | 机器人 20 + MEV 1 |
| ZK 噪声 | — | 0 |

新增的 21 条逐条核对过，全部是机器人数据生成 / 合成 / 遥操作 / 仿真基础设施，以及一篇用 Base 23,000 笔 Uniswap V3 成交做实证的 MEV 论文。

7 天窗（当前主窗口）仍是 0 幸存 —— 索引卡在 2026-10-22，10-23 / 10-24 全 arXiv 各类目都是 0 条，属收录延迟。本次修复对**未来**的投稿生效。

## 顺带修掉的第二个 bug

原脚本在扫描循环里就写 `seen[aid] = ...`，同一篇被第二个词命中时会被当成「已见」短路 —— 跨词命中只记第一个词，词表健康度读数因此偏低（早先几轮日志记过三次，一直没修）。

改为 run 内 `hit_ids` 判重，run 结束才 merge 进 `seen`；`terms[]` 可完整累积，并新增 `per_term` 命中分布输出。

## 影响面

- 只改 `skills/arxiv-radar/SKILL.md` 的扫描脚本，不动词表 `TERMS`、不动 `memory/arxiv-seen.json` 格式（向后兼容，`seen` 仍是 `{id: date}`）。
- `names` 模式走 `CARRIER_BY_TERM.get(term, CARRIER_BASE)`，名字词拿到的仍是原 carrier，行为不变。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

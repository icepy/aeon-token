# 方向标签表（受控）

> **用途**：比对表的**行** = 这张表的标签。narratives 的分节标题也用它。
>
> **规则**
> ① 模型只能从这里挑，**不能自造**；② 一个条目只归一个方向；③ 挑不出来就留空；
> ④ 写进命中流水后**冻结**，不因后续证据改；⑤ 加/删标签只能人来。
>
> **加标签的门槛**：不是凭空想缺什么，而是「**已经有条目属于它，但现有标签装不下**」。
> 凭空加会让表变宽而没数据。

## 一、AI / 机器人

| 标签 | 定义 | 算 | 不算 |
|---|---|---|---|
| `具身数据` | 采集/对齐人类演示，喂给机器人策略 | 遥操作采集、egocentric human data、动作重定向、数据引擎 | 纯仿真环境、纯数据集整理 |
| `世界模型` | 学习环境的未来状态表示 | world model、WAM、rollout、JEPA | 单帧感知、纯检测 |
| `抓取与操作` | 机械臂抓取与 manipulation | manipulation、grasping、pick-and-place、平行夹爪 | 多指手/触觉（→灵巧操作） |
| `灵巧操作`（无词） | 多指手、接触级操作 | dexterous、in-hand、视触觉、多指手 | 平行夹爪抓取 |
| `遥操作` | 人类远程操控机器人采集 | teleop、动捕手套、主从臂 | 自主策略 |
| `sim-to-real` | 仿真训练迁移到真机 | domain randomization、real2sim2real | 纯 sim 基准 |
| `VLA` | 视觉-语言-动作统一策略 | VLA、action token、语言条件策略 | 纯 VLM / 纯 LLM |
| `agent`（无词） | 工具调用、多步自主体 | agentic、tool use、MCP、长程规划 | 单次推理 |

## 二、加密

| 标签 | 定义 | 算 | 不算 |
|---|---|---|---|
| `可验证计算` | 证明推理/训练算对了 | verifiable inference、PoUW、zkML、proof of training | 通用 zk 电路（→零知识） |
| `零知识` | zk 证明系统本身 | zkSNARK、circuit、prover | zkML 应用 |
| `数据可用性` | DA 层与采样 | DA sampling、celestia、blob | 一般存储 |
| `再质押` | 复用质押安全 | restaking、AVS | 普通质押 |
| `流动性质押` | 质押凭证可流通 | LST、LRT | 原生质押 |
| `交易排序` | 排序权与价值捕获 | MEV、block builder、searcher | 普通 swap |
| `共识` | 共识协议与最终性 | consensus、finality、fork choice | 应用层 |
| `意图路由` | 用户意图求解与撮合 | intent-based、solver、order flow | 普通 AMM（→做市） |
| `做市` | 自动做市与流动性曲线 | AMM、x·y=k、LP、集中流动性 | 意图撮合 |
| `手续费市场` | 费用机制与拍卖 | EIP-1559、base fee、priority fee | 代币经济 |
| `轻客户端` | 不存全量的链状态验证 | light client、state proof、sync committee | 全节点 |
| `应用链` | 应用专属链 | appchain、rollup、Robinhood Chain | 通用 L1 |

## 三、只有叙事侧有（探针暂无对应）

`btc-range` · `hyperliquid` · `privacy-coin` · `rwa` · `meme` · `fed` · `美股-半导体`

> 这几行在比对表里必然是单侧。`open-model` / `ai-agent` 若出现，先试着并到 `VLA` / `agent`，别急着新开标签。

## 四、覆盖自检

> 对着 `skills/*/words.py` 核的。**改词后重跑这一节。**

**有词（18 个标签）**：具身数据 · 世界模型 · 抓取与操作 · 遥操作 · sim-to-real · VLA · 可验证计算 · 零知识 · 数据可用性 · 再质押 · 流动性质押 · 交易排序 · 共识 · 意图路由 · 做市 · 手续费市场 · 轻客户端 · 应用链

**无词（待补）**：`灵巧操作` · `agent` · 叙事侧全部 7 个

**跨通道（两边都有词，能真正量滞后）**：只有 **5 行** —— `具身数据` · `可验证计算` · `数据可用性` · `再质押` · `交易排序`

**单侧缺口的优先补词方向**：
- `世界模型` 只有 github 有词 → **arxiv 侧缺**（AI 侧最大的洞）
- `意图路由` 只有 github 有词 → arxiv 侧缺
- `灵巧操作` / `agent` 两边都缺 → 这是两个在热但词表全盲的方向

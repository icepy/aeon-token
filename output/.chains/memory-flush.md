memory-flush 已完成，水位线已推进到 2026-11-27。

## 扫描窗口与预算

- 窗口 `2026-11-26 → 2026-11-27`（state-file 水位，读 2 个日文件），无 >14 天缺口、未 clamp；日志轮转 0 个月（38 个日文件，阈值 45）。
- MEMORY.md：**8,121 → 8,122 字节 / 42 → 43 行 / 0 条超 300 字符**，在预算内。中途编辑一度到 8,311 字节（超 119），逐句压缩后收回。中文行按字节算，1 汉字 = 3 字节，300 字符线约合 100 汉字 —— 这是本轮压缩的主要约束。

## 提升进长期记忆的四个事实

| 来源 | 事实 | 落在哪 |
|---|---|---|
| `arxiv-radar` 第 58 轮（11-26 晚档） | 84 → 7。`egocentric` raw 24 / 新收 **0 = 首次吃干**，但 AI 侧没有结构性归零：7 条改由 `robot data`×2 / `hand-object` / `latent dynamics` / `embodied AI` 带出，第 54 轮加的具身词连三轮零新收后**首次独立扛召回**；`verifiable inference` 与 github 第 36 轮同篇 `FlashProve-Next` 双通道命中，是本窗口唯一可做跨通道对照的点 | lessons 新子条 + MEMORY arxiv 行 + index |
| `github-radar` 第 37 轮（11-26 晚档） | 2110 → 37 → **17**。raw 仅 +0.9%、幸存 −14%，而转化率 **0.77%→0.81% 回升** ⇒ 上轮「报告级新高靠分母膨胀」不可外推；`world action model` 报告级/raw 4.9% vs `world model` 0.41% = 12 倍；加密四词全饱和、报告级仅 `proof of useful work` ⇒ 成熟度阶梯在加密侧倒挂 | github-radar 新整节 + MEMORY github 行 + index |
| `defillama-radar` 第 32 轮 | 9123 / 新增 8 / 可报 2。**「可报集 TVL ≠ 新增体量」连续 6 轮后首次不成立** ⇒ 该差额是「最大新增是否恰被挡」的函数；新增 8 条出现 id 序与时间序相反的近邻（`9522` 早于 `9521` 214s）⇒ 批量只能按 `listedAt` 逐对算 | defillama 正文已由 skill 自写，只补 index 摘要 |
| `heartbeat` 11-27 | **窗口内唯一 P0：`defi-overview` 连败 2 次、两次签名不同**（`timeout` → `403`），`num_turns:11` + 无权限拒绝 ⇒ 网关层不是 skill 回归 | ops-plumbing 新整节 + MEMORY 该行改写 |

## 两条新判据（写进 topic，不进 MEMORY 速查表）

1. **同一 skill 连续失败可出自不同签名** —— timeout 属网络层、403 属鉴权/路由层，所以「签名相同」不能当「根因相同」的前提，反向也不成立。真正可用的对照是**跨 skill**（`hivemindos 403` 同时打挂三个停用 skill 才是共享依赖的正样本）。
2. **`carrier=437` 是「词-仓对」计数，不是唯一仓数** —— `sidhunt/tesla-world-model-tri-shield` 同时出现在 `dropped.json` 与 `out.json`（一处被丢一处放行）⇒ 误杀率分母含逐词重复，不可与幸存数直接做比例。

## 剪枝

`gh pr list --state open` = `[]`（连续第二轮），`improve:` 检索同样为空 ⇒ 无 Open Improvement PRs 段，PR 队列行 tag 换到 11-27。未删任何既有 lesson：四条都是新增实证，`egocentric` 那条写成子条而非改写第 52 轮原文，保留「预警兑现一半」的历史。未触发 topic 归档（发现层 3 行、Lessons 11 行，均在 10–15 行预算内）。

## 需要说明的一处操作事故

编辑 `index.md` 第 12 行时一度把第 36/37 两节插进行中段造成重复（`第三十六轮` 出现 2 次），已定位并删除前一份，复查确认每节各 1 次。

## Summary

- **改了**：`memory/MEMORY.md`、`memory/topics/{github-radar,lessons,ops-plumbing,index}.md`、`memory/logs/2026-11-27.md`、`memory/memory-flush-state.json`（stamp 已执行）。
- **内容**：4 个事实提升、5 条新判据（吃干但未归零 / 加词须等三窗 / 报告级回升可非分母 / 宽词守门窄词出货 / 不同签名同 skill 连败）、2 个 topic 新增整节、3 行 index 扩写。
- **遗留待办**（已记日志，未处理）：`scan.py:301` 审计行四态缺陷（第 12 次暴露）、`dropped.json` 缺 `term`（第 6 轮）、github digest 缺覆盖率百分比、`具身安全` 标签加格、`arxiv-radar` cron-state 孤儿条目（第 30 轮）、health issue 死线程与未闭环项、三处工作区遗留文件（`on-chain-state.json.new` / `price-alert-state.json.bak` / `D AGENTS.md`）。
- **未推送通知**：meta 技能，无操作员信号。

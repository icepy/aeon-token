## 记忆整理（memory-flush）完成 — 扫描窗口 2026-11-15 → 2026-11-16

**窗口与预算**
- watermark 始值 `2026-11-15`，读 2 个日文件（11-15、11-16），无 >14 天缺口、未 clamp；日志轮转 0 个月（27 个日文件，阈值 45）。
- MEMORY.md 起点 **8,429 字节 / 43 行 / 1 条超长行（第 7 行 342 字符）已 OVER BUDGET 237 字节**，终点 **8,156 字节 / 43 行 / 0 条超长（余 36 字节）**。削的是冗余表述（`aeon-update`、`defi-overview`、`github-radar` 三条发现层行 + 过滤器空转、过程事故两例、行情口径 ① 共 5 条长行），**事实与 `[source:]` 标签一条未丢**。

**本轮 promote 的四件事**
1. **`defi-overview` 破 chronic 线**（改写 MEMORY「待盯」行 + ops 新增 11-16 小节）：成功率 **49%（19/39）**、`consecutive_failures=5`，`success_rate<0.5` ∧ `total_runs>=5` 首次成立 —— 11-15 记的是「再败 1 轮即破线」，那一轮已发生。错误码从抖动**收敛为持续 `403`**（`402`→`402`→`max_output_tokens`→`403`→`403`），末条原文 `Gateway cascade failed (hivemindos): Failed to authenticate. 403 All target providers failed`，job 26s 起止 = 请求没出网关。**保留并加固 11-15 判据：收敛到一个码 ≠ 定因**，cascade 全 provider 失败仍可能是配额/路由/密钥任一。`market-context.md` 48.3h → **72h**，唯一写入者就是它，冻结按天累加。
2. **新类事实：挂着未合的 PR 会让 skill 自己的审计数字失真**（MEMORY 新增 About This Repo 一行）。PR #25 跨过 24h stalled 线，而 `arxiv-radar` 的「低频探针 N=0」实为「降级改动没合进 main」的状态灯 —— 此前只把 PR 队列当流程债。
3. **`github-radar` 第 27 轮**（MEMORY 发现层行改写 + topic 新增整节）：421/21/9。`30d==7d` **9 条里 8 条成立、1 条例外** → 继续当「候选仓龄全 <30 天」的样本条件读。新判据：★2 的 `lucidrains/PMW-pytorch` 经 `contents` 复核根目录仅 `.gitignore`/`LICENSE`/`README.md` = **「先占坑」仓，★与作者身份都不作数，「无 language + 根目录无代码骨架」应并入页面规则**。carrier 两侧存活率 97% vs 100% 接近 ⇒ 无证据误杀活跃仓。加密侧四词连 2 轮报告级 0。
4. **`defillama-radar` 第 21 轮**（行改写 + index）：9055/5/可报 1（$15.7K，已发）。**判据级：「同秒 ≥3 条」抓不到「14 分钟窗 + id 连号」的批量录入** → 补互补判据「**差集内部**连号子段 + `listedAt` 跨度 ≤30min ⇒ 同一次批量录入」，已用全量 231 段连号验过（最紧 19.4 / 21.5 分钟）。首次把 Stellar / Flare 算成加链候选，**结论都是不加**（Stellar 只救 1 条 $277K，代价是删 `seen` 重做基线）。可报集 vs 最大被挡条倍数 89 → 17.7 倍，**区间 17–89 倍，不能当稳定量级引用**。

**剪枝**
- `gh pr list --search "improve:"` = `[]`（连续第十四天）→ 无 Open Improvement PRs 段可清；全量 open PR 仍 1 个（#25，非 improve 类，已记 WATCH）。
- 未删任何 lesson：本轮无被推翻项，ops 的 11-15 条保留原文、11-16 以新增小节更正。各节未超 10–15 行，未触发归档。

**文件改动**：`memory/MEMORY.md`、`memory/topics/ops-plumbing.md`（+11-16 小节，timestamp bump）、`memory/topics/github-radar.md`（+第 27 轮整节，timestamp bump）、`memory/topics/index.md`（三行）、`memory/logs/2026-11-16.md`、`memory/memory-flush-state.json`（stamp 到 `2026-11-16`，MEMORY 镜像行已同步）。

**没推送通知** —— 记忆整理是元操作，无可执行的仓位动作；STRATEGY 的「只在触发条件成立时推送」照旧。

## Summary
- 执行 memory-flush：窗口 2026-11-15 → 2026-11-16，扫 2 个日文件，11 条候选逐条做 subject 级 dedup。
- MEMORY.md 从 8,429 字节（超预算）压到 8,156 字节，0 条超长行；三处发现层行原地改写而非新增。
- 新增 1 节（ops 11-16 心跳）、1 节（github-radar 第 27 轮）、1 条 MEMORY 新事实（PR 未合会污染 skill 读数）。
- 剪枝：improvement PR 队列为空、无 lesson 可删、无节超行需归档。
- 已在 `2026-11-16` 日志写入 `### memory-flush` 记录并执行 `memory_prep.py stamp`。

**需要 OPERATOR 处理的（延续项）**
- `defi-overview` 已破 chronic 线，两条修复（cron 挪离 `0 23`、削减单轮输出量）仍未落地 —— 需拍板补余额或 pin 换 provider。
- 合并 PR #25，否则 `arxiv-radar` 的词表降级不生效，审计数字持续失真。
- `defillama-radar` 的 `scan.py:301` 审计行硬编码缺陷待开 PR（连续两轮复现）。

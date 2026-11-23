Memory flush complete.

## 扫描与提升

扫描窗口 `2026-11-22 → 2026-11-23`（watermark 11-22，读 2 个日文件），无 >14 天缺口，轮转归档 0 个月（34 个日文件，阈值 45）。

**提升进长期记忆的五条事实：**

1. **arxiv-radar 第 54 轮** — 「该加词」本身有量纲门槛。`world model`(30d 88) 和 `world-action model`(30d 48) 看似完美补位，但加进日常 30d 词表会把几十条沉积当「新」一次推出去，等于伪造一轮增量。判据：按 60d total 分档，5–60 进 `TERMS`，>60 只能 `days:90` 单次补历史。唯一合规的 `ti:"latent dynamics" AND cat:cs.RO` 已落地。

2. **defi-overview 四条** — ① fees 绝对值须与 `total7d/7` 对量级：上轮 Tether 记 $170.7M，同源回读 $17.02M，**10 倍错位而所有比值全对**，本仓首次数据错误回溯；② live 桶双向都偏（第 4 次实证首次反向，下修 1.8%）⇒ 一律不可引用；③ real-yield `apyReward=null` 被当失败值剔除，误杀 230 条纯 base 池（97→327）；④ Polymarket slug 带时间戳后缀会变，须先 `public-search` 再取。

3. **defillama-radar 第 28 轮** — 批量指纹判据改写：连号加总跨度既不能证实也不能否证批量，只有**逐对间隔**能（9489–9492 跨 9.5h，但 9490/9491 间隔恰为 0s）。旧「连号 + 跨度 ≤30 分钟」判据作废。

4. **github-radar 第 33 轮** — `seen/raw<5%` 误记饱和的修复落地一半：`data availability` 已正确分到损耗栏，`intent-based` 仍错。根因是 `dropped.json` 无 `term` 字段，两词都归不了因。

5. **aeon-update** — `CLEAN-MERGE 3` 仍是净变更为零（本地手工同步超前基线）；5 条 CONFLICT 全是技能计数漂移，只有 `keep_local` glob 能止住重现。PR #28 待合。

## 剪枝

`improve:` 类 PR 为空；PR 队列行更新为「#28 待合」；未删任何 lesson（唯一被推翻的批量指纹判据在原位改写而非删除）；发现层 3 行、Lessons 11 行均未过归档阈值。

## Summary

- 修改 `memory/MEMORY.md`（5 行就地改写 + 1 行新增队列状态）：**8,019 → 8,140 字节，41 行，0 条超长**，在 8192 预算内
- 修改 `memory/topics/lessons.md`（+4 条：第 54 轮量纲门槛、fees 量级校验、live 双向偏、Polymarket slug）
- 修改 `memory/topics/defillama-radar.md`（批量指纹判据原位改写）
- 修改 `memory/topics/github-radar.md`（新增第三十三轮整节）
- 修改 `memory/topics/ops-plumbing.md`（新增 Update (11-23) 小节）
- 修改 `memory/topics/index.md`（四行原地扩写）
- 四个 topic `timestamp` bump 至 `2026-11-23T18:20:00Z`；`memory-flush-state.json` 与 MEMORY.md 镜像已 stamp 到 2026-11-23
- 日志已写入 `memory/logs/2026-11-23.md` 的 `### memory-flush`

**后续待办（延续未处理）：** `scan.py:301` 审计行缺陷第九次（须走 PR）、`dropped.json` 补 `term` 字段、arxiv 两个宽词单独跑 `days:90` 补历史、`arxvi-radar` cron-state 孤儿条目、6 个未闭环 health issue 线程。

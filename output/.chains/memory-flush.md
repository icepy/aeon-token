memory-flush 完成。窗口 `2026-11-20 → 2026-11-21`（watermark 由 11-20 前进到 11-21），未 clamp、无轮转。

## Promote（8 条新判据）

- **`defi-overview` 三连绿出 chronic 线：22/44 = 50.0%** —— `last_success=2026-11-20T23:09:22Z`、cf 0、`total_runs` 43→44，11-18 的「砍单轮输出」修法三连兑现。**但只是踩线**：阶梯判 `success_rate < 0.5`，下一次失败即 22/45 = 48.9% 重回 🔴。44 轮里 22 次失败几乎全在 11-14→11-17 的单次 7 连败 ⇒ **今后读它只看 cf 与最近三轮，不看均值**。原「待盯（OPERATOR）」行已到期，本轮改写。→ [ops](/topics/ops-plumbing.md)
- **arxiv 第 52 轮：饱和即结构性归零。** 上轮出货的 `consensus` 与 `human data` 本轮双双进饱和栏（raw 13→11 / 新收 0），AI 侧召回宽度只剩 `egocentric` 一条（raw 20、maxpub 11-19）。**它一吃干，AI 侧会在话题仍活着时结构性归零 —— 换窗无用，须加词或换写法。** `human data` 新收 0 也说明上轮那 2 条是一次性索引补录。→ [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)
- **过程陷阱：checkout 后 mtime 不可判新旧。** `output/arxiv/audit.log` 的 mtime 是检出时刻、内容仍是 HEAD 里上一轮版本（74→4）。**先 `git status --porcelain output/<skill>/` 确认本轮真写过，再看内容** —— 本仓每 run 全新 checkout，未改动文件的 mtime 永远是新，mtime 只能证明「被写过」。
- **`/v2/chains` 的 `change_1d`/`change_7d` 现值恒为 `null`**，SKILL.md B1 的「直接用现成 delta」失效 ⇒ **字段名存在 ≠ 字段有值**。已就地并入 10-23 的同族记录，不留重复条。
- **成交量的方向由广度决定：** 同一 `+11.17%` 配 0/20 广度是放量杀跌，`+3.83%` 配 13/20 是回暖 —— 「同数两解」第二例。附：F&G 10→12 而价格创新低 = 恐慌钝化，不支持「恐慌见底」。
- **github 第 31 轮（2028/37/13）：** ① `data availability` 3/65 = 4.6%、`intent-based` 4/51 = 7.8% 同轮被记进饱和栏，是 `seen<raw 5%` 误读的第二、三例且均未归因（该补分母不是补调用）；② `chengjianglong` 单 owner 占 3/13 同一 Qwen3-VL 脚手架 ⇒ **报告级 owner 去重后按 10 读趋势**；③ `30d==7d` 12/13，三轮合并看是 paper code release 的属性不是窗口定律；④ carrier 误杀 38% vs 幸存 100%，维持不放宽。
- **defillama 第 26 轮**只核不写（topic 已由 skill 自写到位），补一条新判据：**「连号 + 跨度 ≤30 分钟」才是批量指纹，缺同秒不能反推条目彼此无关。**

## 剪枝

`gh pr list --search "improve:"` = `[]`（连续第十九天），无 Open Improvement PRs / Next Priorities 段可清。**未删任何 lesson** —— 本轮无被推翻的现行判据。发现层 3 行、Lessons 11 行均未过归档阈值。

## 预算

7,888 → 8,155（中途 2 条超长）→ **7,808 字节 / 41 行 / 0 条超长**，余 384。压回靠删注解码（不删 `[source:]` 标签、不增行数）。

## Summary

- 写入：`memory/topics/ops-plumbing.md`（+`Update (11-21)` 小节）、`memory/topics/lessons.md`（+3 条，含 1 条就地扩写）、`memory/topics/github-radar.md`（+第 31 轮整节）、`memory/topics/index.md`（四行原地扩写）、`memory/MEMORY.md`（发现层 3 行 + 待盯行）、`memory/logs/2026-11-21.md`（本 skill 条目）
- 时间戳：`lessons` / `ops-plumbing` / `github-radar` → `2026-11-21T18:20:00Z`
- watermark：`memory-flush-state.json` + MEMORY.md 镜像均盖为 `2026-11-21`
- 延续待办：`defi-overview` 50.0% 踩线；`scan.py:301` 审计行缺陷；`github-radar` 的 NEG 变体表与过滤损耗归因；`arxiv-radar` `days:90` 第五轮未跑 + `egocentric` 须备换写法；`arxvi-radar` cron-state 孤儿条目
- 本次未发通知（无 OPERATOR 级新事实，`defi-overview` 踩线属预告的终点延续）

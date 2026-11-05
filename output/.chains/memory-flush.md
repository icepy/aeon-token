**记忆整理完成**（`memory-flush`）。

## 扫描窗口与预算

窗口 `2026-11-04 → 2026-11-05`，读了两个日志文件。起点 8,115 字节 / 44 行 / 1 条超长行 → 终点 **8,171 字节 / 45 行 / 0 条超长行**（上限 8192，余 21 字节）。中途因写入新判据一度冲到 8,695 字节，靠四轮压缩压回，并把 433 字符的行情口径行拆成「口径 + 聚合字段口诀」两条。

## 提升到长期记忆的内容

| 来源 | 条数 | 落点 |
|---|---|---|
| `arxiv-radar` 第 36 轮 | 4 条 | `topics/lessons.md` |
| `github-radar` 第 17 轮 | 5 条（#79–#83） | `topics/github-radar.md` 新增「第三十一轮」节 |
| `defi-overview`（11-04） | 3 条 | `topics/lessons.md` |
| `defillama-radar` 第 10 轮 | 补 MEMORY 第 16 行 | 已在 topic 自写 |

最值钱的三条：

1. **`jepa` + `world model` 占 21/53 = 40% 幸存者，raw 合计 1117 = 全轮 53%** —— 词表首次触及「双通道」阈值，已给下轮立判据：若 `jepa` 新收仍 ≥10 而其余 17 词 ≤10，就该按「出口分散度」复核而不是继续加词。
2. **「0 新增」必须拆成两种成因** —— `restaking`/`intent-based`/`data availability` 是 seen 饱和（删词会丢覆盖），只有 `maximal extractable value`（raw=1 / seen=0）是过滤损耗、才是删词候选。
3. **`/protocols` 的 `hallmarks` 可直接反查事件成因** —— 11-04 扫全表命中 Balancer V1–V4 + CoW AMM 同日标注「pools withdrawals-only」，DEX 量翻倍不用猜。WebSearch 已连 13 轮 `400 All target providers failed`，这是可靠替代。

另记：**fees 增速 19 条候选剔尖峰后只剩 2 条**（Curve DEX 甚至符号反转 +205% → −26%）；**链端点与协议腿可差 10 倍以上、不可互验**（LayerZero V2 的 Polygon 腿 $10.80B > 整条 Polygon 链 $0.641B）；**加细分 arXiv 写法常是重复付费**（`robot data` 7 条 vs `robot manipulation data` 0 条）。

## 剪枝

`gh pr list --state open --search "improve:"` = `[]`，open PR 总数 = 0（连续第三日），无 Open Improvement PRs 段可清。Lessons Learned 无失效条目：`arxvi-radar` 孤儿条目与 `on-chain-state.json.new` 遗留物均未解决，保留。轮转归档 0 个月（16 个日文件，阈值 45）。

整理过程中一度写出重复的 lessons 索引行，已回读删除并验证。

## Summary

- **做了什么：** 执行 `memory-flush`，扫描 11-04/11-05 两个日志，提升 12 条新判据到 topic 文件，压缩 MEMORY.md 回预算内，更新索引三行，写入运行日志，最后 `memory_prep.py stamp` 把水位线推进到 `2026-11-05`。
- **修改的文件：** `memory/MEMORY.md`（压缩 + 两处换新事实）、`memory/topics/lessons.md`（+6 条，timestamp → 11-05）、`memory/topics/github-radar.md`（新增第三十一轮 5 条，description/timestamp 同步）、`memory/topics/index.md`（三行）、`memory/logs/2026-11-05.md`（`### memory-flush` 一节）、`memory/memory-flush-state.json`（由 stamp 写入）。
- **遗留待办：** `memory/on-chain-state.json.new` 遗留物（所属 skill 已停用）；`arxvi-radar` cron-state 孤儿条目；`memory/topics/` 下 10 个 `.py` 临时脚本与 `price-alert-state.json.bak` 待 PR 删除；defillama「改过滤器是否触发基线重做」的语义边界仍未确认。

Memory flush complete. Here's what was done.

## 扫描与预算

窗口 `2026-11-03 → 2026-11-04`（watermark 推进了 1 天），读 2 个日志文件。无 >14 天缺口，轮转归档 0 个月（15 个日文件，阈值 45）。

起点 8,049 字节 / 46 行 / **1 条超长行**（第 17 行 301 字符），余量只剩 143 字节。终点 **8,051 字节 / 46 行 / 0 条超长行**，余 141 字节 —— 净增 2 字节。

靠合并两条 `defi-overview` 行情口径行（并把「广度须连续三日同向才作趋势读」并进去）腾出空间，再压缩 `arxiv-radar`、`github-radar` 两行的冗余修饰。第 17 行是 step 0 点名的超长行，压缩后入界，顺手去掉与第 30 行重复的「carrier 连三轮 0 丢弃」（该事实在第 30 行以更完整的「连九轮 + 14 词未配 carrier 表」形式保存）。

## 提升的判据

`github-radar` 第 16 轮 → [github-radar](/topics/github-radar.md) 新增「第三十轮」四条：

1. **7 天窗比 30 天窗幸存更多、报告级更少**（439→35→报告级 7 vs 30d 的 33→9）。窗口不只是成本旋钮，还改变报告级分布，跨窗口这两个数不可直接相减。
2. **`commits_7d == commits_30d` 第三次成立，形式最硬** —— 7/7 全等、7/7 ★0。
3. **carrier 误杀对照在 7 天窗下两侧恒 100% = 测不到误杀**，指标只在长窗可读。这条给「跨窗口比必得假信号」补了反方向例子：窄窗不是「没有误杀」，是「测不出来」。
4. **`supermimic` 132 仓 / 99 owner 从正样本退为异质撞名** → `gh-v4` 正样本判据改为「同 owner 多仓」。

另一条此前只在日志里的运维判据进了 [ops-plumbing](/topics/ops-plumbing.md)：**`Write` 打进已存在的 `memory/logs/*.md` 是破坏性操作**（11-03 那次抹掉当天 6 个章节，靠 `git checkout HEAD --` 复原）。修法是先 `Glob` 判存在、再 `Read`+`Edit` 追加；`Write` 只用于某 UTC 日的第一次写入。

## 剪枝

`gh pr list --state open` = 0、`--search "improve:"` = `[]`，无 Open Improvement PRs 段可清。MEMORY.md 无 Next Priorities 段。Lessons 无失效条目 —— DEUS 期「链上速查」仍通用，`arxvi-radar` 孤儿与 `on-chain-state.json.new` 遗留物均未解决，不删。

## Summary

- **扫描窗口** 2026-11-03 → 2026-11-04，读 2 个日志文件；MEMORY.md 8,049 → 8,051 字节（余 141）、46 行、超长行 1 → 0。
- **修改文件**：`memory/MEMORY.md`（压缩合并 2 行、重写 arxiv-radar / github-radar 2 行）、`memory/topics/github-radar.md`（第三十轮 #75–#78 + frontmatter）、`memory/topics/ops-plumbing.md`（日志 append-only 一节 + frontmatter）、`memory/topics/index.md`（三行更新）、`memory/logs/2026-11-04.md`（`### memory-flush` 追加）、`memory/memory-flush-state.json`（watermark → 2026-11-04，MEMORY.md 镜像行同步）。
- **未处理的三项遗留**（连续多轮）：`memory/on-chain-state.json.new`、`arxvi-radar` cron-state 孤儿条目、`memory/topics/` 下 10 个临时 `.py` 与 `price-alert-state.json.bak` 待 PR 删除。
- **状态**：MEMORY_FLUSH_OK。

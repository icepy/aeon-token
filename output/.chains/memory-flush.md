Memory flush 完成。窗口 `2026-10-29 → 2026-10-30`，读了 2 个日志文件。

## 本轮最重要的两件事：两条旧结论被新证据改写

**1. 「`data availability` 结案 = 窗口把 57 压成 16」只对了一半。**

第 10 轮换到 30 天窗后看到 raw=57、seen=1，于是判定「悬案结案，是窗口截断」。第 11 轮同窗口再跑：raw=56 / seen=1 / 新收 0 —— **raw 没变，seen 只吃了 1 个**。那 56 个仓既不是被 seen 吃掉的（那才叫饱和），也不是窗口压的，而是被某条丢弃规则常年挡在门外。第 10 轮只追了 35 个幸存者的来源，没追这 56 个的去向。

新判据：**`有新增=0` 且 `seen 命中 < raw 的 5%` 时不许记成「饱和」，必须单独归因到具体丢弃规则。** 同类可疑项还有 `intent-based`（55/3）。

**2. carrier 偏严从「猜测」升为「可复现判据」。**

第 10 轮丢弃侧存活 36% vs 放行侧 97%，当时用「跨窗口比必得假信号」把结论压下去了。第 11 轮在同一 30 天窗内跑出 35% vs 96% —— **同窗口、同参数、两轮几乎重合，那个解释不再适用。** 这是 carrier 表偏严的真信号。改表仍需走 PR，且改前先抽检两行。

## 写入位置

| 文件 | 改动 |
|---|---|
| `memory/MEMORY.md` | `github-radar` 状态行推到第 11 轮 + 两条新判据；`arxiv-radar`、`defi-overview` 两行压措辞并更新验证轮次 |
| `memory/topics/github-radar.md` | 新增「第二十五轮」整节（#57–#59）：完整漏斗、9 词新收、8 饱和词、形态告警 |
| `memory/topics/lessons.md` | 补 3 条进「过滤器设计」节，均带 `[source: logs/2026-10-29#github-radar（第 11 轮）]` |
| `memory/topics/defillama-radar.md` | 只补来源标签 —— 空 `chains` 一节上轮已写全，无新事实，不重复新增 |
| `memory/logs/2026-10-30.md` | `### memory-flush` 条目 |

## 剪枝与其他

- Open PR：`gh pr list --state open` 与 `--search "improve:"` 均返回空，无 Open Improvement PRs 段可清。
- MEMORY.md 无 Next Priorities 段；`memory/on-chain-state.json.new`、`arxvi-radar` 孤儿条目仍挂在 ops-plumbing，属待办不改。
- 未新建 topic 文件，`topics/index.md` 无需改。`narratives.md` 2 节，未超 4 节上限。
- 水位已盖章：`2026-10-30`（`memory-flush-state.json` + MEMORY.md 镜像）。

**预算：8,192 → 8,172 字节 / 53 行 / 无超长行，余量只剩 20 字节。** 起点就已经顶格 —— 上一轮收尾时还有 147 字节余量，被后续 skill 的追加吃掉了。**flush 是唯一的回收点，两次之间只增不减。** 另外顺序上我又重犯了上一轮记过的错误：先改内容涨到 8,257 才发现超了，再回头压。下次应该在读完 MEMORY 后先把可压缩项砍到 7,800 以下再动内容。

## Summary

- 执行 `skills/memory-flush/SKILL.md` 全流程（步骤 0 → 8），扫描窗口 `2026-10-29 → 2026-10-30`。
- 修正了一条会被后续轮次误用的旧结论（`data availability` 归因），并把 carrier 判据从猜测升级为可复现判据。
- 修改：`memory/MEMORY.md`、`memory/topics/lessons.md`、`memory/topics/github-radar.md`、`memory/topics/defillama-radar.md`、`memory/logs/2026-10-30.md`，并盖章 `memory/memory-flush-state.json`。
- 待跟进：MEMORY.md 余量仅 20 字节，下一次任何 skill 写 MEMORY 都会越线；`memory/topics/` 下 10 个临时 `.py` 与 100KB 的 `price-alert-state.json.bak` 仍需走 PR 删除。

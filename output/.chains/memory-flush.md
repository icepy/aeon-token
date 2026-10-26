Flush complete and verified. MEMORY.md is at 8,191 / 8,192 bytes, watermark stamped.

## Summary

**扫描窗口** `2026-10-25 → 2026-10-26`（watermark 来源 `memory-flush-state.json`），读取 `memory/logs/2026-10-25.md`（845 行，约 30 个 skill 段落）。无 >14 天缺口、未触发 clamp；日志轮转归档 0 个月。

**做了什么**

1. **减重回预算** — 起点 8,188 / 8,192 字节（零余量）。上一轮刚压到 8,096，但当天后续运行又填满了。本轮按步骤 3d 做「下沉 + 合并」而非新增：把 10-25 全部 8 轮 price-alert 的逐小时盘口细节整理成 5 个新章节写进 `deus-orderflow.md`；两条同一 subject 的 NOTE 行合并；About / Reference / 监控清单 / 预警框架 / 输出语言五处去冗余。终点 **8,191 字节 / 69 行，无超 300 字符的行**。

2. **新增 4 条 lesson**（一行式进 MEMORY.md，全文进 `lessons.md`）：「流出」要成为「卖压」须三条全中；增量型变量反复读到同一数字 ≠ 走平；**已合并 ≠ 已生效**（PR MERGED 后 refactor 可基于旧副本静默覆盖）；单个 409 空仓不能触发认证降级。

3. **github-radar 新判据**：换词前先量两口径的 `total_count` + 重叠度 —— `vla`→全称双赢（污染 22%→1.4%）、`jepa`→全称损失 94.6%。第八/九轮的反例（`PER_TERM_CAP` 低估 3.85×、`pages` 两侧都判错、`jepa` ★0 但 commit 最狠）补进 `github-radar.md` 第 16/16b/16c 节。

4. **剪枝**：`gh pr list --state open` 返回 `[]`，无 Open Improvement PRs 段；arxiv-radar PR #10/#11 均已 MERGED，「待合 PR」类条目不再需要。

**修改的文件**
- `memory/MEMORY.md` — 合并去重 + 4 条新 lesson，回到预算内
- `memory/topics/lessons.md` · `github-radar.md` · `deus-orderflow.md` · `index.md` — 承接下沉的细节（github-radar 首次登记进 index）
- `memory/logs/2026-10-26.md` — 新建本轮日志
- `memory/memory-flush-state.json` — 已 stamp 至 2026-10-26

**遗留**：`memory/on-chain-state.json.new` 仍是 git 跟踪文件、内容停在 10-21。属 `onchain-monitor` 写盘边界问题，不属 MEMORY.md 合并范围，本轮未碰。

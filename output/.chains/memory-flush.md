Flush complete. Structure intact (the two "blank-before-heading" hits are the original template shape: `# Long-term Memory` → date line → `## About This Repo`).

## memory-flush — 2026-11-19

**扫描窗口：`2026-11-18 → 2026-11-19`**（watermark 自动读取，读 2 个日文件，无 >14 天缺口、未 clamp；轮转未触发，30 个日文件 / 阈值 45）。

### 提入长期记忆的四条

- **`defi-overview` 已自愈，是「砍单轮输出」修法的首轮兑现。** `last_success` 11-18T23:14:04Z、`consecutive_failures` **7 → 0**、`total_runs` 41 → 42。上一轮死于 `num_turns:138` / `output_tokens:147604` vs 128000；本轮 **48 tool calls**、取数全在 python 聚合只打摘要行。11-18 定的病因与修法同轮兑现 ⇒ 该病可修，不必换网关。
  - 附带：`market-context.md` 解冻（`11-13T00:15Z` → `11-18T23:10Z`，~120h 冻结结束）。
  - **但成功率仍 20/42 = 48%，在 50% 线下** —— 文件恢复写入 ≠ 成功率恢复，两者分开记；`STATUS_PAGE` 只升到 🟡 WATCH。
- **arxiv-radar 第 50 轮：11 个零命中词第二轮全数复现 11/11 落「窗口太短」，词级数字逐条相同。** 结论升级 —— 这是这批词的稳定属性，不是单轮样本；**该动的是窗口（`days:90`）不是词表**。本轮 3 条幸存全来自 `robot` carrier 且全是数据侧贡献，加密侧 0（单侧 AI 3 · 加密 0）。
- **github-radar 第 29 轮：`30d==7d` 三轮三值（9 中 8 → 0/9 → 9/9），落定为「整批同源」判据。** 9 条 desc 全是论文句式 ⇒ paper code release；先看 desc 再读「7d==30d」。报告级 9 条 ★ 全 ≤1 且未按 star 排序 ⇒ 真分布，star 不该进排序。
- **defi-overview 三条接口口径事故（新 lesson）**：`/markets?slug=` 恒回空数组须走 `/events?slug=` 展开；`groupItemTitle` 混已结算档必须按 3%–97% 过滤（BTC 年内盘 47 条只有 6 条有效）；`tag_slug=crypto` 带排序返 406；`historicalChainTvl` 字段是 `tvl`、`/charts` 的 `date` 是字符串。

### 剪枝

`gh pr list --state open` = `[]`（连续第十七天）→ 无 PR 段、无 Next Priorities 段可清。**未删任何 lesson** —— 本轮无被推翻项，三条旧判据全被复现强化。各节均未过 10–15 行归档阈值。

### 预算

**7,973 → 7,838 字节 · 41 → 41 行 · 超长行 1 → 0**（余 354 字节）。压回全靠同义压缩，细节落 topic，事实与 `[source: ...]` 标签一条未丢。另修复了一处自动编辑吞掉的空行（`## Lessons Learned` 前）。

### 文件

- 修改：`memory/MEMORY.md`、`memory/logs/2026-11-19.md`、`memory/memory-flush-state.json`、`memory/topics/index.md`、`memory/topics/lessons.md`、`memory/topics/ops-plumbing.md`
- `lessons.md` / `ops-plumbing.md` 的 `timestamp` 已 bump 到 `2026-11-19T18:10:00Z`；`github-radar.md`（11-18T22:45Z）与 `defillama-radar.md`（11-19T00:10Z）已新于来源，未动。
- 未新建 topic / archive，故索引只做四行原地扩写。

### 遗留（延续，非本轮新增）

`defi-overview` 须连绿数轮才可出 chronic 口径；`scan.py:301` 审计行缺陷（第五次暴露）；`intent-based` 过滤损耗未归因；arxiv 14 词缺 carrier 表 + 11 词该跑 `days:90`（连两轮提，未执行）；`arxvi-radar` cron-state 孤儿条目（第二十二轮）；health issue `#9`/`#13` 未闭环。

**STATUS: MEMORY_FLUSH_OK**，watermark 已 stamp 到 2026-11-19。

## Summary

- 按 `skills/memory-flush/SKILL.md` 执行完整 flush：步骤 0 由 `memory_prep.py window` 定窗口，步骤 8 由 `memory_prep.py stamp` 落 watermark。
- 提入四条（`defi-overview` 自愈 + 修法兑现、arxiv 第 50 轮窗口属性二次证实、github 第 29 轮同源批次判据、defi-overview 三条接口口径），剪枝零删除，MEMORY.md 压回预算内。
- 修改六个 memory 文件，未新建 topic。无 PR 可清，无归档触发。

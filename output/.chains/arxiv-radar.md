## arxiv-radar · 第 47 轮

**`vM`** · 窗口 30 天 · 词 26 · `var` 空 · `STATUS: ARXIV_RADAR_OK` · 耗时 313s

### 漏斗
原始 **70** → `seen(记忆)` 扣 70 · `seen(本轮重复)` 0 · `EXCL` 0 · `carrier` 0 · 查询失败 0 → **幸存 0**。hits 未追加，labels 无写入（174 行不变），**未发通知**（规则：幸存 > 0 才发）。

### 六分类（单位 = 词）
未测到（试过失败） **0** · 未尝试（熔断跳过） **0** · 窗口内零命中 **13** · 低频探针 **0** · 全已见（饱和） **13** · 有新增 **0**

### 跨窗结论（判据顺序未跳级）
- **11 词跨窗有命中 → 窗口太短，不许删**：`auditable training` 2/3 · `proof of training` 1/1 · `light client` 0/1 · `data availability sampling` 1/1 · `staking` 1/1 · `MEV` 2/3 · `automated market maker` 2/3 · `RWA` 0/2 · `embodied data` 1/3 · `robot manipulation data` 1/2 · `human data` 6/7
- **2 词跨窗皆 0 → 换写法级**：`verifiable inference` · `restaking`。换写法第 46 轮已做完，写进了 PR #25 —— 本轮不重做，也不升级到删词。

### 幸存者
无。零幸存是**结构性的**：70 条原始全部命中 `seen`，两侧失败类均为 0，饱和侧 maxpub 全在近 30 天内（最新 `egocentric` / `verifiable computation` = 11-12）。不是故障，不是话题降温。

### 两个判据级发现
1. **「低频探针 = 0」其实是「降级有没有合进 main」的状态灯。** 第 46 轮把两个词降进 `LOW_FREQ`，但改动只活在 **PR #25（仍 OPEN）**里，main 的 `scan.py` 至今 `LOW_FREQ` 只有 `verifiable training` 一条 —— 两词仍在主力词表里跑。写完 ≠ 生效。
2. **窗口滑一天就能把饱和翻成零命中。** `automated market maker` 上轮饱和、`maxpub` = 10-16，唯一那篇恰好卡在窗口起算日（10-15 → 10-16 之后）。这是本轮「零命中 12→13、饱和 14→13」的唯一差额来源，不是词表失效。

### 待办
- **合 PR #25**（词表降级至今未生效）。
- 索引连两轮停在 **11-12**；周日 + 周末不公告属正常节律，**周一若仍停 11-12 即判真滞后**，届时查 arXiv API 状态而非改词表。
- `carrier` 过滤连十二轮空转、14 词未配表 —— 维持 Observation，不动词表。

## Summary

- 跑了 `skills/arxiv-radar/scan.py`（30 天窗、26 词），原始 70 → 幸存 0，`STATUS: ARXIV_RADAR_OK`，无 degraded、无失败类。
- 修改文件：`memory/logs/2026-11-15.md`（追加第 47 轮整节）、`memory/topics/lessons.md`（+2 条判据、bump `timestamp`）、`memory/MEMORY.md`（发现层 arxiv 行原地改写，8,149 字节在 8KB 预算内）。
- 脚本产物：`output/arxiv/audit.log`、`output/arxiv/out.json` 由脚本自写；`report.md` 未覆写（零幸存）。
- 未发通知、未写 labels —— 均因幸存为 0，符合 SKILL.md 规则。
- 需要动作：**合并 PR #25**，否则第 46 轮的两个词降级永远不生效。

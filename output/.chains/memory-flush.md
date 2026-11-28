Memory flush 完成。

## 扫描窗口
`2026-11-27 → 2026-11-28`（watermark `2026-11-27`，state-file 来源，读 2 个日文件）。无 >14 天缺口、未 clamp；轮转归档 0 个月（39 个日文件，阈值 45）。起点 8,112 字节 / 43 行 · within budget。

## 提升到长期记忆的五件事

1. **arxiv-radar 第 59 轮** — 83 → 0，损耗 100% 在 `seen`，两侧失败类与过滤损耗全 0 ⇒ 这是**饱和的满格形态（healthy saturation），不是降级**，本轮不许据此动词表。关键反证：上轮「四条具身窄词扛起召回」本轮全窄词 raw>0 / 新收 0 ⇒ 一次性、不可外推。
2. **github-radar 第 38 轮** — 2102 → 25 → 10。连续三轮 raw / 幸存 / 报告级 / 转化率**四个量全换方向**（升→降→腰斩，转化率 0.81%→0.48%）⇒ 30d 窗逐轮比较没有可用趋势。宽窄词出货比从 12 倍扩到 17 倍。
3. **defillama-radar 第 33 轮** — 9128 / 新增 5 / 可报 1（`Stoxes.fun` $8,952.50）。被 `parent` 挡的 `Pear Vaults` $1.29M 是可报的 144 倍 ⇒ 「可报集 TVL ≠ 新增体量」得到第二个反号样本，判据钉死。新判据：`parent#` 家族母协议本体 98.9% 不在 `/protocols`。
4. **heartbeat** — `defi-overview` cf=4 跳闸，根因 `max_output_tokens`（复发），不是网关。最有价值的新判据：5 条 `permission_denials` 全部同因（`&&` 复合命令），而 skill 文档明写一条一次 ⇒ agent 执行方式错，不是环境问题。
5. **手工 merge-upstream** — 上游 `f99eabb8` → `883a1ae4`，4 冲突解到本地真值 97 skills；旧基线 `f94f39e` 的 92→93 计数漂移判据作废。

## 剪枝
- `gh pr list --state open`（含 `improve:` 搜索）连续第三轮为 `[]` ⇒ 无 Open Improvement PRs 段，PR 队列行 tag 换到 11-28。
- 未删旧 lesson：本轮四条都是新增实证或正面反证，第 58 轮原文保留、第 59 轮以子条推翻。

## 结果
`MEMORY_FLUSH_OK` · 8,112 → **8,097 字节** · 43 行 · 0 条超 300 字符（编辑中一度 8,101 字节且第 18 行 302 字符，压回预算内）

## Summary

**做了什么**：执行 memory-flush 技能全部 8 步 —— 读取 scan window、扫描 2 个窗口内日志、去重比对、提升五个事实、剪枝 PR 段、扩写索引、记录运行、打 watermark。

**修改的文件**：
- `memory/MEMORY.md` — 4 行就地改写（arxiv / github 发现层行、`aeon-update` 基线行、PR 队列行），镜像日期由 stamp 更新
- `memory/topics/lessons.md` — 新增第 59 轮子条，timestamp bumped
- `memory/topics/github-radar.md` — 新增第三十八轮整节置顶，timestamp bumped
- `memory/topics/ops-plumbing.md` — 新增 merge-upstream 整节，timestamp bumped
- `memory/topics/index.md` — 三行原地扩写 + github-radar 行首计数改「三十八轮」
- `memory/logs/2026-11-28.md` — 追加 `### memory-flush` 记录
- `memory/memory-flush-state.json` — stamp 写入 `2026-11-28`，15 个日志指纹

**需跟进**：`defillama-radar` `scan.py:301` 审计行缺陷（第 13 次暴露，须走 PR）；`github-radar` `dropped.json` 缺 `term` 字段（连第七轮）；`arxiv-radar` 下轮须盯 `maxpub` 是否仍为 11-25，若第三次相同转索引滞后排查；`883a1ae4`/`f99eabb8` 不在本仓 git 历史（合并发生在另一副本），MEMORY 那行仅作上游基线事实记录。

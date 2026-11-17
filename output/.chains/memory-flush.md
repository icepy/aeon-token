## memory-flush 完成 — 扫描窗口 2026-11-16 → 2026-11-17

**窗口与预算**：watermark = `2026-11-16`，读 2 个日文件（11-16、11-17）；无 >14 天缺口、未 clamp；轮转归档 0 个月（28 个日文件，阈值 45）。MEMORY.md 起点 **8,187 字节 / 44 行**（距 8 KB 只剩 5 字节）→ 终点 **7,805 字节 / 42 行 / 0 条超长行**。中途第 8 行改写一度冲到 8,530，压回手段是把 6 条长 lesson 的细节留在 topic、MEMORY 只留判据，并合并「漏斗退化成单通道」与「过滤器空转」两条同族条目 —— 事实和 source 标签一条未丢。

### 提升进长期记忆的四条

1. **网关级故障，而不是两个 skill 各自的回归（本轮最重要）。** 11-16T23:00–23:31Z 半小时内两个 enabled skill 撞同一堵墙，失败签名逐字相同（`hivemindos … 403 All target providers failed`）：`defi-overview` 23:01:11Z（cf 5→6，19/40 = 48%）、`github-radar` 23:31:22Z（cf→3，40/52 = 77%，last_success 停在 11-15T22:33Z）。同窗口 `arxiv-radar`(22:06Z)/`memory-flush`(18:05Z)/`defillama-radar`(11-17T00:09Z) 全绿 ⇒ **间歇性拒绝，非宕机、非单 skill 回归**。此前「挪 cron / 砍单轮输出」是针对错对象的低层修法。附带两条判据：设计意图里的「23:00 后集中跑」正好落在故障带内；**分母增长让 chronic 自我加固**（19/39 → 19/40，分子不动），所以「恢复一次」不等于出线。`market-context.md` 冻结 72h → ~96h。

2. **缺口轮次不计入「连续 N 轮」序列判据。** `github-radar` 第 28 轮是没跑成，不是零命中 — 11-15 记的「加密侧连 2 轮空转」到此必须停在 2。

3. **`defillama-radar` 第 22 轮：`EXCL_CATEGORY` 三类首次摊开。** `Interface` 380 条里 374 空链（98.4%）、有 TVL 仅 6、带 parent 252 ⇒ 该桶对 Interface 是重复计数而非独立信号，且「Interface 一律过滤」的损失面是零。`Hyperliquid Builder` 标签全量 227 条全 `Interface`、近 30d 19 条（占同期登记 6.5%）全无链无 TVL，是同一模板批量录入，**不是生态扩张证据**。「空链 + EXCL 双帽」先撞 `category` 桶 ⇒ `链白名单=0` ≠ 今天没有空链条目（11-08「桶名比桶语义窄」第四次复现）。尾部首现连号空洞 `9455`–`9456` = 待回填预告。

4. **PR 队列清零。** 核实 `gh pr view`：#25 `MERGED` 11-16T01:10:30Z、#27 `MERGED` 11-16T11:42:57Z；`gh pr list --state open` 为 `[]`，两条 WATCH 全部闭环 — 是就地更正旧条目，未新增。

### 剪枝

`gh pr list --search "improve:"` = `[]`（连续第十五天），无 Open Improvement PRs 段可清；MEMORY 无 Next Priorities 段；各节均未超 10–15 行，未触发归档；无 lesson 被推翻，未删条目。

### 文件

- `memory/MEMORY.md`（42 行 / 7,805 字节）· `memory/topics/ops-plumbing.md`（新增 `Update (11-17)` 小节 + description/timestamp bump）· `memory/topics/github-radar.md`（新增「轮次缺口」节 + timestamp bump）· `memory/topics/defillama-radar.md`（skill 已自写，未重复）· `memory/topics/index.md`（三行追加）· `memory/logs/2026-11-17.md`（`### memory-flush` 条目）· `memory/memory-flush-state.json`（stamp = 2026-11-17）

### 待办（延续，均需 OPERATOR）

`defi-overview` 的修法对象已从「改 skill」上移为「查共用网关」，须在补余额 / pin 换 provider / 拉长时间窗之间选；`github-radar` 第 28 轮需补跑才恢复序列；`defillama-radar` 的 `scan.py:301` 审计行缺陷（连续三轮，仅「可报>0」时暴露）；`memory/on-chain-state.json.new` 遗留物；`arxvi-radar` cron-state 孤儿条目（连报二十轮）；`memory/topics/price-alert-state.json.bak` 待删。

## Summary

- 执行 `memory-flush`：窗口 11-16→11-17，读 2 个日文件。
- MEMORY.md 从 8,187 压到 7,805 字节（44 → 42 行，0 超长行），四条 skill 事实入库其中一条整条重写，并新增一条判据（缺口轮次 ≠ 零命中）。
- 修改：`memory/MEMORY.md`、`memory/topics/{ops-plumbing,github-radar,index}.md`、`memory/logs/2026-11-17.md`；`memory_flush.py stamp` 已把 watermark 推到 2026-11-17。
- 未发通知（无新可执行动作，符合「正常别吵我」）。
- 后续需 OPERATOR 决策：网关侧修复路径 + `github-radar` 第 28 轮补跑。

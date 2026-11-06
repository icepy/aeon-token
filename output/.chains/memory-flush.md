Flush is done and stamped. Here's the report.

## memory-flush — 2026-11-06

**扫描窗口 `2026-11-05 → 2026-11-06`**（watermark 起点 11-05，state-file 为源），读 2 个日志文件，无 >14 天缺口、未 clamp，轮转归档 0 个月（17 个日文件 / 阈值 45）。

**预算：8,187 → 8,126 字节（余 66）· 45 → 42 行 · 超长行 1 → 0。** 中途冲到 8,374 字节超限，靠三步压回：删掉「归档：取数 / watch 框架」整节（唯一有效内容移入 [ops-plumbing](/topics/ops-plumbing.md) 新节，MEMORY 只留指针）、压缩三条发现层行、合并两条同主题判据。这是本轮唯一的结构性删减。

### 晋升的判据（细节全在 topic 文件，MEMORY.md 只留索引）

**defi-overview 11-05（5 条 → [lessons](/topics/lessons.md#行情取数形状defillama--coingecko)）** — 这一轮最值钱的是拆开了三个「看起来是数据、其实是口径」的假信号，全部指向同一方向（市场没那么差），照抄会得出完全错误的 risk-on 结论：
1. **暴跌日 TVL 桶滞后来自上游刷新周期，不是 CDN 缓存** —— 链 TVL −1.22% 而 ETH −8.47%；`no-cache` + `?_cb=` 双取差 0.000%、live 端点同值，排除缓存与假零。当日真实换手只能读 DEX 量。
2. **价格单日 |Δ|>5% 时当日 F&G 一律作废** —— 34 → 50 看着像情绪修复，实为 00:00 UTC 快照早于 15:00 暴跌。补上「广度只在连续三日同向时可读」的另一半：广度日内更新，F&G 不是。
3. **昨日 TVL 复现不出 = live 值与日结算桶混用** —— 同端点回查 11-04，Ethereum 43.757B vs 昨记 45.69B、总 81.896B vs 84.73B。昨日「+3.44% 站上上沿」是口径产物。
4. **fees 尖峰剔除必须「剔后按日均比较」** —— 46 条候选最后剩 2 条，且都是清算换手非有机增长；Maple 从 +182% 翻成 −44.9%。
5. **CoinDesk RSS + WebFetch 拿到宏观成因**（WebSearch 连挂 14 轮来首次），建议写进 skill B2 作正式 fallback。

**arxiv-radar 第 37 轮（4 条）** — 85 条原始只剩 2 条幸存，**且两条全是污染**。核心是 **carrier「0 丢弃」不是安全，是空转**：`circuit` / `network` 对超导电路论文和分布式 ML 论文同样成立，等于用歧义词假装挡住了。另记 `cat:cs.DC` 是弱约束（同时收分布式 ML）、脚本 `-1` 与 `None` 双哨兵导致两格失败被误归「窗口太短」、以及 `?` 首次 100%（指向「词写错」而非「表缺格」）。

**github-radar 第 18 轮（5 条 → [github-radar](/topics/github-radar.md) 新增第三十二轮）** — 上轮立的「`jepa`+`world model` 双通道退化」判据**被自己否掉了**：`jepa` 新收 13→7、其余 17 词 21→29，两个条件同时反向 = 单轮回摆。教训是占比类判据不稳，须两条件同时成立。另记 `maximal extractable value` 连两轮 raw=1/seen=0 是「靶子稳定」而非饱和；`teleoperation` 首次成为最大报告级入口（验证入口词换代）；carrier 第八次同向 36% vs 94%。

### 剪枝与索引
- `gh pr list --search "improve:"` = `[]`，无 Open Improvement PRs 段、无 Next Priorities 段可清；Lessons Learned 无失效条目（DEUS 期链上速查仍通用）。各节均未超 10–15 行，未触发归档。
- `memory/topics/index.md` 三行更新：lessons 补 11-05 八条、github-radar 改「双通道退化」为「判据被否」并补 teleoperation 换代、defillama-radar 补 `chains`/`chainTvls` 与「两轮连续读数」。
- 未新建 topic / archive 文件，索引无孤儿。

### 未处理（延续，非本轮职责）
`memory/on-chain-state.json.new` 遗留物（连续第十四轮）、`arxvi-radar` cron-state 孤儿条目（连报十轮）、`memory/topics/` 下 `.py` 临时脚本与 `price-alert-state.json.bak` 待 PR 删除、defillama「改过滤器是否触发基线重做」语义边界、以及 arxiv-radar 的 `circuit`/`network` 判别力抽检（下轮）。

**STATUS: MEMORY_FLUSH_OK** · watermark 已由 `memory_prep.py stamp` 推进到 `2026-11-06`（state-file + MEMORY.md 镜像同步）。

## Summary

- 执行 `python3 scripts/memory_prep.py window`（窗口 11-05→11-06，未触发轮转）与 `stamp`（已推进 watermark 到 2026-11-06）。
- 修改 7 个文件：`memory/MEMORY.md`（选题更新 + 删一节，8,187→8,126 字节 / 45→42 行）、`memory/topics/lessons.md`（+9 条判据）、`memory/topics/github-radar.md`（+第三十二轮 5 条 + frontmatter）、`memory/topics/ops-plumbing.md`（+watch 重开种子节）、`memory/topics/index.md`（三行）、`memory/logs/2026-11-06.md`（追加 `### memory-flush`）、`memory/memory-flush-state.json`（stamp）。
- 无 notify（meta skill，无对外信号）。
- 后续：下轮需复查 arxiv-radar 的 `circuit`/`network` 判别力抽检与两处失败格；`arxvi-radar` 孤儿条目与 `on-chain-state.json.new` 仍待清理。

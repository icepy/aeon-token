Consolidation complete. Here's the run result.

## memory-flush · 2026-11-02

**扫描窗口 2026-11-01 → 2026-11-02**（watermark 起点 11-01，读 2 个日志文件共 246 行）。无 >14 天缺口、未 clamp；日志轮转 0 个月（13 个日文件，阈值 45）。

**预算：8,149 → 8,086 字节 / 51 行 / 无超 300 字符行，余 106 字节。** 起点如同上轮必然超预算（上轮压到 8,093，被其他 skill 吃掉 56），本轮全程先压后写，没有一行是重复追加。

### 本轮最值钱的一条：推翻自己两天前写的判据

10-31 / 11-01 记的「`description` 旁路 +38% 优于 `url` +39%」是把**两个不同分母**的结果并排写。第 7 轮同源重算：召回 `url` 44 vs `desc` 31（url 反而更高），去桥后**打平**（21 vs 23），真增量只存在于**并集**（净 36）。[defillama-radar](/topics/defillama-radar.md) 该节整段重写。

**方法论：凡两轮之间「改进了 X%」的结论，下一轮必须回到同一分母重算。**

### lessons 增补 4 条 + 修正 1 条（全部来自 11-02 `defi-overview`）

1. **DeFiLlama 历史点 `T00:00Z` = 前一日收盘** —— 用「实时端点 vs 历史末点」的不等式检验证出（$43.9849B ≠ $43.8925B），不解文档猜。这条解释了前几轮「今日/昨日」口径漂移的根因。
2. **用子集加总证伪聚合端点** —— Avalanche +10.24%，但 418 条协议腿合计 −0.10%，腿加总/链端点差 3.5 倍 → 端点口径不同，不进结论。假涨家族第三种。
3. **残桶修正幅度随桶变老收敛，<0.5% 即已结算**（−22.0% / +0.02% / −0.27% 三个读数），把「当日桶不可信」补成可操作判据。
4. **单日广度在 ±0.5% 行情里是噪声**（14/20→6/20 掉 8 点而指数动 0.3%），且「改善」方向也会骗人 —— 7d 的 9/20 扣掉 3 个稳定币后只剩 6/17。
5. **修正**「`total7d/total24h ≈ 1` 指纹」：该阈值扫全表在下一轮命中 0 条，指纹只在首次出现那轮可见，改判为找「同一协议连续两天反向 >50% 的跳变对」。

### 其余更新

- **[github-radar](/topics/github-radar.md) 新增第二十八轮（#66–#69）**：报告级首次 100% 落机器人侧、加密侧归零 · `jepa` 扩散而 `world model` 饱和（看新收/返回比值）· **11/12 的 `commits_7d == commits_30d` = 新仓潮**（与第十轮「爆完即停」互为镜像）· carrier 误杀**第五次**同窗口复现（32% vs 97%，五轮序列 36→35→36→34→32）。
- **[ops-plumbing](/topics/ops-plumbing.md) 新增「没人会合 PR」**：`aeon.yml:18` 的 `auto-merge` 是 `enabled: false`，写入型 skill 的 PR 会无限期停着。#21/#22 躺 3 天 → `market-context.md` 在 main 上停更 ~73h，而 skill 每轮都报成功。**诊断口径：读目标文件在 main 上的 `timestamp:`，不要读 run status。**
- **剪枝**：`gh pr list` 现在只有 #23（11-02 新建）；#21/#22 已于 11-02T09:26Z / 09:29Z 由操作员手合 → MEMORY.md 的 pending 表述与 `aeon-update` 基线（`6eddd85`→`ec7a50c`）均已更新。
- **索引**：github-radar 行「二十七轮→二十八轮」「四轮→五轮」；defillama-radar 行改记 id 永久空洞与两条旁路同族。未新建 topic / archive 文件。

### 未处理（延续，非本轮可剪项）

`memory/topics/` 下 10 个 `.py` 临时脚本与 `price-alert-state.json.bak`（100KB）待 PR 删除；`memory/on-chain-state.json.new` 与 `arxvi-radar` 孤儿条目待清；defillama 的「改过滤器是否触发基线重做」语义边界从 11-01 挂到现在仍未确认。

未发送通知（meta skill，无可执行信号）。watermark 已 stamp 到 2026-11-02。

## Summary

- 执行 `memory-flush`：窗口 11-01→11-02，读 2 个日志文件，无缺口、无轮转。
- MEMORY.md：8,149 → 8,086 字节，51 行，无超长行（预算内，余 106）。
- 修改文件：`memory/MEMORY.md`、`memory/topics/lessons.md`（+4 条 / 修 1 条）、`memory/topics/github-radar.md`（第二十八轮 + frontmatter）、`memory/topics/ops-plumbing.md`（新增 auto-merge 一节 + Citations）、`memory/topics/index.md`、`memory/logs/2026-11-02.md`、`memory/memory-flush-state.json`（stamp）。
- 最重要的判断：推翻两天前自设的 defillama 旁路结论（不同分母并排写），并把 DeFiLlama 历史时间戳语义这条根因写进 lessons。
- 待跟进：`auto-merge` 是否开启需操作员决定；defillama 过滤器改动的基线语义边界仍未确认。

MEMORY_FLUSH 完成。

## memory-flush · 2026-10-27

**扫描窗口** `2026-10-26 → 2026-10-27`（watermark 起于 `2026-10-26`，state-file 来源），读入 2 个日志文件：`2026-10-26.md`（614 行 / 约 76 段）与 `2026-10-27.md`（202 行 / 约 25 段）。无 >14 天缺口、未触发 clamp；日志轮转归档 0 个月（7 个日文件，阈值 45）。

**预算** 起点 7,228 字节 / 50 行，2 行超 300 字符（第 20 行 352 字、第 21 行 305 字）→ 终点 **7,243 字节 / 51 行，无超 300 字符的行，在 8 KB 预算内**（余量 949 字节）。行数 51 略多于「~50」的软指标，字节余量充足。

### 动作：下沉 + 合并，不是新增行

两条超长状态行（`arxiv-radar` / `github-radar`）压回一行式，细节移入 topic。

**新增 [github-radar](/topics/github-radar.md)「第十八—二十二轮」一节，六条编号判据（#43–#48）。** 10-27 一天内跑的五轮此前只散在日志里、完全没有 topic 落档。其中三条有长期价值：

| 判据 | 内容 |
|---|---|
| #43 | **「窗口是流量旋钮不是语义轴」第二次拿到算术证据。** 18 轮 90d dry-run 报告级 64 → 19 轮 7d 写 `seen` 恰好 34 幸存 / 10 报告级 → 20 轮同口径 90d 幸存 −33、报告级 −10，那 10 个全部消失。**差值完全由 `seen` 吸收解释，不是扫描回归。** 推论：90d 跟在 7d 后跑等于空转，日跑回 7 天窗。 |
| #44 | **脚本尾部崩溃 ≠ 本轮没产出。** `scan.py:910`/`:921` 把 `c.get(...)` 写成 `c[...]`（元组下标），崩溃点在落盘**之后**——产物是新的、`report.md` 是旧的、stdout 像跑挂了。三者互相撒谎，先看 `out.*.json` 的 mtime 再决定重跑。 |
| #47 | `supermimic` 61 仓 / 61 owner 维持判假——「单 owner 多仓不构成趋势」的镜面对称：多 owner 单仓同样不构成。 |

另外三条：#45 `SITE_SUFFIX` 补 `-web`/`_web` 后端到过杀 0；#46 dry-run 不再覆盖 `report.md`、真零改为跨 7/30/60 三窗判定；#48 无 language 字段 ≠ 非代码仓，需 `contents` 调用才能归因。

### 新增 8 条 lesson

**取数侧（[lessons](/topics/lessons.md) 行情节）**
- 跨 series 做 diff 必须**按日期取键**，不能各取尾部两点。判别式：per-chain delta 总和必须等于 aggregate delta。10-27 复算 Uniswap V4 时踩过，差点把真实的 −21.6% 判成伪影。
- **单腿读数恰为 0 → 先当快照缺口。** 10-27 一天三个实例：OKX −40.3%（Bitcoin 腿 $11.93B → $0.00 → $11.96B）、LayerZero Polygon 腿 −$478M（比整条链的 −$41M 还大）、DEX `change_1d` +40.3%（与自家序列 −3.6% **符号相反**）。三者几小时内全部自愈。
- 第三方聚合 JSON 字段类型会变：`binnedConfidence` 可能是 `None` 而非缺键，`chainTvls` 的值不全是 dict。先 `type()` 采样再写解析。

**arXiv 侧（[lessons](/topics/lessons.md) arXiv 节）**
- **零命中要按跨窗归档。** 7 个零命中词跨窗量后全落「窗口太短」档，**无一个「跨窗皆 0」→ 零删词候选、零换写法候选**。加密侧 6 词全在此档。
- **饱和词要配 maxpub 判降温。** 12 个饱和词的 raw 最新发布全在 10-06~10-23（近 30 天内）→ **全是「话题活着、`seen` 吃干」，无一该降温**。饱和 ≠ 降温，降温看最新发布日期离今天多远。
- 「低频 ≠ 死词」成立，但**「写作已被覆盖」会单独被证伪**：`verifiable training` 本轮回火 1 条（`WebUniverse` 写的是 `Verified Training Data`）。复归判据是「连续两轮开火」，不是单轮。
- 新词红利期结束信号 = **raw 仍在、新收归零**（`human demonstration` 12/0、`hand-object` 6/0，首轮是 95%/89%）。
- 同一形态连续两轮落「未分类」= **标签缺口，不是污染**——该扩受控表，不是动过滤器。动作方向相反。

### 剪枝

- `gh pr list --state open` 返回 `[]`，无 Open Improvement PRs 段可清。
- `gh pr list --state all` 八条（#10/#11/#14/#15/#16/#17/#19/#20）**全部 MERGED** → MEMORY.md 无需保留任何「待合 PR」条目。
- 无已完成的 Next Priorities 可删；DEUS/NOTE 归档段按 operator 显式指令（「勿再展开」）保持原样未动。

### 索引

未新建 topic 文件，无需注册新行。#19 登记表里 `index.md` 的 github-radar 行顺手从「十七轮」更新到「二十二轮」。

### 未处理项（沿用上轮，仍未碰）

`memory/topics/` 下 10 个 `.py` 临时脚本与 `price-alert-state.json.bak`（100KB）属 price-alert 停用遗留，删除需走 PR，不在 MEMORY.md 合并范围。`memory/on-chain-state.json.new` 同理 —— 它是 `onchain-monitor` 的写盘边界问题，**重开该 skill 前必须处理**。

## Summary

- **扫描**：窗口 `2026-10-26 → 2026-10-27`，读 2 个日志文件；无缺口、无轮转。
- **修改**：`memory/MEMORY.md`（7228 → 7243 字节，无超长行，预算内）· `memory/topics/github-radar.md`（新增第十八—二十二轮 #43–#48 + frontmatter 更新）· `memory/topics/lessons.md`（新增 8 条 + timestamp）· `memory/topics/index.md`（github-radar 行更新）· `memory/logs/2026-10-27.md`（本 skill 条目）· `memory/memory-flush-state.json`（watermark → 2026-10-27）。
- **STATUS: MEMORY_FLUSH_OK**
- **后续动作**：无必须项。可选 —— 把 `memory/topics/` 的临时 `.py` 与 `.bak` 清掉（需开 PR）；`consensus` 标签缺口已在 MEMORY.md 记为待办，交由 arxiv-radar 下次跑时处理。

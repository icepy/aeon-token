The flush is complete. Watermark advanced to 2026-11-13, MEMORY.md within budget.

## Summary

**扫描窗口**：`2026-11-12 → 2026-11-13`（watermark = 11-12），读 2 个日文件；无 >14 天缺口、未 clamp；轮转归档 0 个月（24 个日文件，阈值 45）。

**预算**：8,041 字节 / 42 行 / **3 条超长行（353、306、308 字符）** → **8,127 字节 / 43 行 / 0 条超长行**，余 65 字节，`within budget`。压缩的是三条超长行（发现层 arxiv-radar 行、行情口径 ①②），只削修饰词，事实与 source 标签一条未丢。

**promote 三处（全部原地改写，无新增重复段）**
1. **arxiv-radar 第 44 轮**：原始 75 → 幸存 0。关键判断是**零来自 `seen` 吃干，不是词表失效** —— 12 个零命中词里 10 个跨窗有命中，窗口太短不许删；仅 `verifiable inference`/`restaking` 跨窗皆 0（第三轮），同义写法四窗也全 0，但按「换写法→降频→删词」不跳级，下一步放开 `ti:` 查 `all:`。→ MEMORY 行 + lessons 一条。
2. **github-radar 第 25 轮**：420/33/12，核验 33/33。`30天=`≡`7天=` **12/12 第六轮** → 降为既成前提；加密侧**第十连轮** 0 且 `mev` 缩写仍未量；入口换代到 `robot manipulation`（新收 8，`world model` 返回 147 但新收仅 5）；★8 是 7d 窗自第 20 轮最高，`min:0` 地板不动。→ MEMORY 行 + topic 整节。
3. **defi-overview 11-13 三条口径 + 一条 ops**：`/overview/fees` 的 `protocols[]` 无 `tvl` 字段（筛出 0 条与「无信号」同形）、`/global/market_cap_chart` 是 PRO-only（401）、real-yield 计数 270→235 是收益率收缩不是池子变少；ops 补 `defi-overview` 成功率 0.56（19/34），再一段连败即破 chronic 线。

**剪枝**：`gh pr list --search "improve:"` = `[]`（连续第十一天），无 PR 段可清；无 Next Priorities 段 → 新增一条**「待盯」**行收唯一 OPERATOR 决策（cron `0 23` + WebSearch 缺位）；未删任何 lesson（本轮均为判据加强，无被推翻项）；各节未超 10–15 行，未触发归档。

**文件改动**：`memory/MEMORY.md`、`memory/topics/lessons.md`、`memory/topics/github-radar.md`、`memory/topics/ops-plumbing.md`、`memory/topics/index.md`（四行）、`memory/logs/2026-11-13.md`（`### memory-flush`）、`memory/memory-flush-state.json`（已 stamp 至 2026-11-13）。

**待跟进**：`defi-overview` 的两条病根（cron 挪离 `0 23`、削减单轮输出量）仍是 OPERATOR 决策，本轮未擅自改；`arxvi-radar` cron-state 孤儿条目与 `on-chain-state.json.new` 遗留物继续挂起。

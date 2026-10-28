整理完成，MEMORY.md 在预算内。以下是本轮记录：

## memory-flush · 2026-10-28

**扫描窗口** `2026-10-27 → 2026-10-28`。8 个日志文件，未轮转（阈值 45）。

### 提升到长期记忆

**github-radar 第 9 轮**（此前只散在日志里）→ `memory/topics/github-radar.md` 新增「第二十三轮」一节，四条判据（#49–#52）：

- **star 第 12 次失效，但形态变了**：报告级 8 个 ★全 0，且除 `marionette` 外 `commits_30d == commits_7d`。这说明「所有提交都在近 7 天」，即**本周新建、当周爆完**，不是老仓回温。判据从「它有多活跃」改成「它存在多久」。
- `data availability` 连两轮 raw=16 / seen=0、数字一字未变 → 是**过滤损耗**不是饱和（饱和要求 `seen` 命中有数），下一轮 `--full` 定位。
- 7 天窗不足以判词死活：`robotics data engine` 相邻两轮从「饱和 1/1」翻成真零。
- carrier 误杀对照两侧都顶到 100%（46/46、18/18）时**失去分辨力**——只能记「未观察到误杀」，不能反推规则安全。

**lessons.md** 增 3 条、合并 3 组重复：

- arXiv **IP 级 429**：诊断法是打一条无日期条件的查询——无窗 200 + 有窗 429/503 = 限流不是故障。degraded 分支 `sys.exit(0)` 不写 `out.json`，重跑前必须 `stat` 产物 mtime。
- **某过滤器长期「0 丢弃」先查有多少输入真经过它** —— carrier 空转六轮的真因是 26 词里 14 个没配 `CARRIER_BY_TERM`。这条同时作废此前「零假阴本身有价值」的表述。
- **标签缺口被真实流量填上 = 扩受控表**，不是改过滤器。
- 合并：跨 series 日期对齐（原 3 条同义）、单腿归零（2 条）、DEX 口径冲突（补 10-28 第二次复现）。

**ops-plumbing.md** 新增「补跑时移」一节：三个 cron 22:00/22:30/23:45 UTC 的技能在 10-28 同一秒 `04:15:45Z` 触发，**「昨天几点跑」不能当 cron 时间读**；孤儿 `arxvi-radar` 条目说明。

**decisions.md** 给 10-28 那条「carrier 只当摄像头」加了限定。

### 剪枝

`gh pr list --state open` = `[]`；`--state all` 八条全 MERGED。MEMORY.md 无待合 PR 条目可删。`defillama-radar` 那个 topic 自建立起**从未登记进 index**（孤儿），已补；github-radar 行从「二十二轮」更新到「二十三轮」。

### 预算

起点 7,898 → 中途一度 8,647（超 455）→ 回落到 **8,175 字节 / 54 行，无超 300 字符行**（余量 17 字节）。行数比「~50」多 4 行。

已 `stamp` 写入 watermark `2026-10-28`。

**未处理**：`memory/topics/` 下 10 个 `.py` 临时脚本与 100KB 的 `price-alert-state.json.bak` 仍是 price-alert 停用遗留，删除要走 PR；`memory/on-chain-state.json.new` 连续第五轮挂着，只在重开 `onchain-monitor` 前需处理。

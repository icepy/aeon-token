Flush complete. Watermark stamped, MEMORY.md within budget.

## memory-flush — 2026-10-28 → 2026-10-29

**扫描窗口**：2 个日志文件（`2026-10-28.md` 272 行 / `2026-10-29.md` 60 行），无 >14 天缺口，日志轮转归档 0 个月（9 个日文件，阈值 45）。

### 本轮最重要的发现：`github-radar` 的「7 天窗」从未在调度链路上生效

`skills/github-radar/SKILL.md:7` 声明 `var: "days:7"`、正文也写「默认 7」，但 `scan.py:184` 的 `DAYS` 默认值是 **30**，`scan.py:193` 只在显式传 `days:N` 时才覆盖。**frontmatter 的 `var:` 不注入运行环境** —— 第 9 轮那个「7 天窗」是运行内手动传参的结果，不是日跑默认行为。

这条直接作废了 MEMORY.md 里「日跑回 7 天窗」的结论，也意味着第 9 轮（7d）与第 10 轮（30d）的数字**不可相减**。已写进 [ops-plumbing](/topics/ops-plumbing.md) 新节，并并入 MEMORY.md 的调度那条。

### MEMORY.md 变更

| 项 | 变化 |
|---|---|
| 起点 | 8,275 B / 54 行（**已超预算 83 B**） |
| 中途 | 8,472 B（改写涨的） |
| 收尾 | **8,045 B / 53 行**，无超 300 字符行 |

三条状态行全部推到最新轮：`arxiv-radar` 第 29 轮、`defillama-radar` 第 3 轮、`github-radar` 第 10 轮。字节回收全部靠压缩，没有整节下沉：删掉 DEUS 归档段里与 Reference 段**重复的五条 topic 链接**（−230 B），`defi-overview` 那条 lesson 的后半本就全文在 `lessons.md`（#168/#170），MEMORY 只留判据 + 指针（−250 B）。

### topic 增补

- **[github-radar](/topics/github-radar.md) 新增第二十四轮（#53–#56）** —— ①`data availability` 悬案结案：「两轮数字一字未变」**是窗口假象的指纹**（7d 窗把 57 压成 16），不是哪条规则在吃；②carrier 误杀对照**跨窗口比必得假信号**（本轮 36% vs 97%，上轮 100%/100%）；③`proof of useful work` 30d 窗首次产出，与 defillama 词表 `Pearl Blockchain` 同源 = **两条通道首次交集**；④第 9 轮 `30d==7d`「本周新建当周爆完」是 7 天窗产物，不是 10 月末的普遍形态。旧的 #50 已标注「被 #53 推翻」，原文保留存档误判链。
- **[lessons](/topics/lessons.md) 增补 3 条** —— 窗口截断假象 + 跨窗口对照失效；`EXCL` 不进 seen = 漏斗常数项；`有新增0 + 全已见19` = 纯 saturated 轮不是断流轮。
- **[defillama-radar](/topics/defillama-radar.md) 新增白名单漏口一节** —— `Tradecraft`（Canton）TVL $1,688,251，比同轮 4 条可报项加起来还大 20 倍；记下「加链必须同时删 seen 重做基线，否则等于没加」。

### 剪枝

`gh pr list --state open` 与 `--search "improve:"` **均返回 `[]`**，无待合 PR 段。`narratives.md` 现 2 节，未超 4 节上限，无需清理。

## Summary

- 执行 `memory-flush`，窗口 2026-10-28 → 2026-10-29，读 2 个日志文件，无 clamp。
- 修改 `memory/MEMORY.md`（8,275 → 8,045 B，54 → 53 行，预算内）、`memory/topics/github-radar.md`（+第二十四轮 #53–#56，修正 #50）、`memory/topics/lessons.md`（+3 条，合并 1 条）、`memory/topics/defillama-radar.md`（+Canton 漏口）、`memory/topics/ops-plumbing.md`（+`var:` 不注入）、`memory/logs/2026-10-29.md`（本 skill 日志）。
- 已 `stamp`：watermark 2026-10-29，MEMORY.md 镜像同步。
- **未通知** —— 无触发条件，按 STRATEGY「正常别吵我」静默。
- 待办（延续，未动）：`memory/topics/` 下 10 个 `.py` 临时脚本与 `price-alert-state.json.bak`（100KB）需走 PR 删除；`memory/on-chain-state.json.new` 只在重开 `onchain-monitor` 前处理；`github-radar` 是否把 `days:7` 写进 `aeon.yml` 的调度参数（或把 `scan.py` 默认值改成 7）需要拍板 —— 当前状态是文档与实现对不上。

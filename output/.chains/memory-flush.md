本日 `memory-flush` 完成。校验通过：stamp 写入的指纹（剥离本 skill 自身小节后）与两份日志均精确匹配，空闲门不会误判。

## 扫描窗口

`2026-11-23 → 2026-11-24`（watermark = `2026-11-23`，读 2 个日文件）。无 >14 天缺口、未 clamp；轮转归档 0 个月（35 个日文件，阈值 45）。

**本窗口的关键时序事实：`2026-11-23.md` 在 18:00 上次 stamp 之后哈希又变了**（`d40a40f1…` → `b99960ff…`）—— `arxiv-radar` 第 55 轮与 `github-radar` 第 34 轮都跑在 18:00 之后、追加进同一天日志。所以这一轮实际多覆盖了四块内容，不是常规的一天窗口。

## 推广的四条

**① arxiv-radar 第 55 轮 — `seen` 吃干是暂时态，不是方向死**
未加任何新词，66 → 5，5 条**全部来自旧词**（`egocentric` 4 / `consensus` 1，raw 19→22）。第 54 轮「结构性归零须加簇」只对当时那个窗口成立，不能外推。但反向风险同时成立：第 54 轮加的四条具身词本轮零新收 = 与 `egocentric` 重叠，**AI 侧召回宽度仍 = 1 词**。判据：方向按产出物（数据 vs 方法）拆，不按词拆。

**② defillama-radar 第 29 轮 — `链白名单=0` ≠ 无空链条目**
4 条新增全空链，但 4/4 在更早的 `category` 桶就 continue，桶读数 0 是「桶名比桶语义窄」新一例。`Hyperliquid Builder` 独占 3/4（30d 19→22，加速但仍 0 可报）。`9494 XOXNO` 三处互斥（`description` 说 Stellar / `address` 前缀 elrond / `chains=[]`，同母协议四子条目四种链口径）⇒ **`chains` 缺失是录入缺口，不是部署事实**。11-22 桶隔轮下修 −2.11% ⇒ 「未定稿可真被大改」再取一例。口径差记一笔：滚动窗 day0 跨两个日历日、日历桶 day0 只是当天至今，不可互读。

**③ github-radar 第 34 轮 — `pages_root=6` 创记录**
此前最多 5、多数轮 0–1 ⇒ 根目录静态站规则确在挡量（页形态 28/139）。报告级 14 条但 owner 仅 13（`Dash-organisation` 一拆代码仓+报告仓）⇒ 读趋势按 13 不按 14。`intent-based` 18/1 = 5.6% 连三轮卡 5% 线落饱和栏、归因仍未做。

**④ 11-24 heartbeat — `defi-overview` 连第三轮脱线 25/47 = 53.2%**
cf **0**、11-18→11-23 六连绿 ⇒ 判据不变（只看 cf 与最近三轮）= 无故障。PR **#28** 开 ~13.4h 未到 24h 线；`aeon-update` 周一槽已完成，下次 11-30。

## 剪枝

- `gh pr list --search "improve:"` = `[]` → 无 Open Improvement PRs 段；全部 open PR 仅 #28 一条，队列行换 source 到 11-24 heartbeat。
- 未删任何 lesson（第 55 轮是新增实证、非推翻）；未触发归档（发现层 3 行、Lessons 11 行都在预算内）。
- 9 条 open issue 仍全为无标签 health 线程，MEMORY 无对应节，不新建。

## 预算

`8,149 → 8,163 字节 / 41 → 41 行 / 超长 0 → 0`（余 29）。增量只来自 heartbeat 行的 53.2%/六连绿与 PR 行的时间戳，未新增行。

未发通知 —— 干净轮次，无新事实需推。延续待办（`scan.py:301` 四态缺陷、`dropped.json` 缺 `term`、两个宽词欠 `days:90`、`arxvi-radar` 孤儿条目、死 health 线程）已在日志记录，不重复推。

## Summary

- **执行**：`memory-flush`，窗口 2026-11-23 → 2026-11-24，`STATUS: MEMORY_FLUSH_OK`
- **修改文件**：`memory/MEMORY.md`（2 行就地改写）· `memory/topics/lessons.md`（+第 55 轮子条，bump timestamp）· `memory/topics/index.md`（4 行扩写）· `memory/topics/ops-plumbing.md`（bump timestamp）· `memory/logs/2026-11-24.md`（追加 `### memory-flush` 记录）· `memory/memory-flush-state.json`（stamp）
- **新增判据 4 条**：`seen` 吃干是暂时态 / 召回宽度仍 1 词 / `链白名单=0` 非无空链 / 滚动窗与日历桶 day0 不可互读
- **后续动作**：`scan.py:301` 审计行四态补丁须走 PR；`dropped.json` 加 `term` 字段；校验已确认 stamp 指纹与日志匹配，空闲门正常

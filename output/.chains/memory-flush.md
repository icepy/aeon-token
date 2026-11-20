Memory flush complete. Scan window was 2026-11-19 → 2026-11-20 (2 daily files, no gap/clamp, 0 months rotated).

## 本轮晋升的四条事实

**1. 总 TVL 有两套并行口径 —— 混用会造出 −50% 假暴跌**（11-19 defi-overview）
legacy `api.llama.fi/charts`（`totalLiquidityUSD`，`date` 是字符串）11-19 live 桶 **$138.48B**；`/v2/historicalChainTvl`（`tvl`，`date` 是整数）同桶 **$69.44B**。逐日比值 11-05 **2.049** → 11-19 **1.994**，稳定在 2 附近不是偶发。11-18 报的 $139.98B 是 legacy live 值、隔日修订为 $143.29B；直接拿 /v2 的数对它做 delta 会得 −50.4%。**判据：比 delta 前先验字段名同源。**

同轮另两条：USDS −38% 是单源突变（CoinGecko 报 $6.42B / −0.21%，差近一倍 ⇒ 更像 sUSDS 剥离再挂，同族 Spark 四条同步下坠不构成独立验证）；BTC 期权到期后 −0.09% 无方向 = 无承接盘，事件到期而无波动本身是读数。

**2. arxiv「10 月断流」判定被推翻**（11-19 第 51 轮）
上轮记的 `ti:"human data" AND cat:cs.RO` 断流不成立 —— 本轮 30d 窗内新收 2 条、2/2 全幸存，零命中集从 11 缩到 10，少的那一个正是它。**是延迟入索引，不是话题停。** 判据：`30d=0 / 60d=6` 只证明「30 天内没有新索引」，不证明「没有新论文」。出货词组从 `robot` carrier 换成 `human data`/`egocentric` 系仍落同一簇 ⇒ 数据侧召回是整簇属性。

**3. `NEG_BY_TERM["jepa"]` 漏同源变体，漏网者排报告级第一**（11-19 第 30 轮）
`codelady-ship/jeparla` 是阿塞拜疆语珠宝店电商。现有表 `["jepang","jepara","jepan"]` 不含 `jeparla`（`jepar-la` ≠ `jepar-a`）—— 不是匹配失效，是逐变体未覆盖。另：`data availability` seen/raw = **4.7%** 仍被记进「真饱和」栏，违反既存 `seen < raw 5%` 判据。

**4. cf 计数不因 skill 停用而衰减**（11-20 heartbeat）
`price-alert` cf=5 / `onchain-monitor` cf=4 / `token-movers` cf=3 全部 `enabled: false`、停在 10-25、同一网关错误签名 ⇒ **cf 是账本不是状态灯**。`defi-overview` 连绿第二轮，**21/43 = 49%，再绿一轮即 22/44 = 50.0% 出 chronic 线**。

## 剪枝与预算

PR 队列连续第十八天空（`improve:` 搜索返回 `[]`）→ 无可清段落。无 lesson 被删除；唯一被推翻的 arxiv「断流」**就地加子条标注推翻并保留原文**，因为「索引计数 vs 论文日期」这层区分本身仍有价值。未触发 3d 归档（各节均未过 10–15 行阈值）。

预算从中途冲高 8,099（3 条超长行）压回 **7,887 字节 / 41 行 / 0 超长**，余 305 字节。压缩全靠删副项（`hallmarks`、`/v2/chains`、`market-context` 解冻半句），这些细节都还在 lessons 与 ops 全文里，事实和 `[source:]` 标签一条未丢。

## Summary

- **MEMORY.md** — 发现层三行（arxiv / defillama / github）整条改写、「待盯（OPERATOR）」行重写、行情口径 ② 并入两套 TVL 口径；7,887 字节 / 41 行 / 0 超长
- **`memory/topics/lessons.md`** — +3 条行情口径、+1 条 arxiv 推翻子条、+1 条整簇属性子条
- **`memory/topics/github-radar.md`** — 新增「第三十轮」整节
- **`memory/topics/ops-plumbing.md`** — 新增 `Update (11-20)` 小节
- **`memory/topics/index.md`** — 四行原地扩写
- **`memory/logs/2026-11-20.md`** — `### memory-flush` 条目
- **`memory/memory-flush-state.json`** — 水印已推进到 2026-11-20（step 8 已执行）

**待办（延续，未处理）**：`arxiv-radar` 的 `days:90` 补历史已提四轮未执行；`github-radar` 的 `NEG` 表须补 `jeparla` 等同族变体；`defillama-radar` 的 `scan.py:301` 审计行缺陷第六次暴露，可单独提 PR。

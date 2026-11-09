# Long-term Memory
*Last consolidated: 2026-11-09*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**；`arxvi-radar` 孤儿待清。**`auto-merge` 关着 = 没人会合 PR**。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS / NOTE 的价格监控已停，下面归档。
- **`aeon-update` 上游基线**（11-03 合入）：`aeonfun/aeon` HEAD `ec7a50c`；PR #23 只推水位线、不搬内容。[source: logs/2026-11-02#aeon-update]
- **预算纪律：MEMORY.md 只在两次 flush 之间增长。** 超 8KB 先砍已归档节。[source: logs/2026-11-01#memory-flush]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **归档，勿再展开。** 阈值以 `STRATEGY.md` 为准，盘口细节在 `memory/topics/`，重开前先读 `memory/decisions.md`。DEUS `0x940A319B75861014A220D9c6c144d108552B089B`（base）· `0xbb0f7533` 持 xDEUS #1396 → 5 天 clock 未启动。**NOTE** 待命 480,000，扳机 = 第一笔 ETH 入账。已停：`price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一方向的不同成熟度：论文（~4 个月）→ 代码（~1–2 个月）→ 代币（未建）。**同一个词在几条通道上依次点亮，那个次序才是信号。**
- `arxiv-radar` ✅ 07:30 · 26 词 · 11-08 第 40 轮 **73 → 0**（seen 吃干 100%，**连续两轮**）→ 有新增连续三轮 0，**通道只测饱和度不测流量**；**「0 幸存 = 词表失效/话题降温」两个结论都不成立**。跨窗判死只剩 `verifiable inference` / `restaking`（60d=90d=0），下一步换同义写法不删。`staking` 11-09 滑出 30d，**滑出≠降温**，须补测 60d。[source: logs/2026-11-08#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-09 第 14 轮 8966 / 新增 1 / **可报 0**。9→1 单轮不作趋势读（前例 18→8→6）。唯一 `Bitty Vaults`(9363) parent+空链**双帽，真边际 0/1**。`only_seen=['4818']` **连续五轮** = 真下架。`id` 非整数（`<5471>`）→ `str()` 做键；`<N>`↔`N` 会重报。**加链必删 seen 重做基线。**[source: logs/2026-11-09#defillama-radar]
- `github-radar` 22:30 · 18 词 · gh-v3。**cron 不注入 `var` → 7d 仅在手动 `days:7` 时成立**；第 20 轮（11-07）手动 7d：452 → 35 → 12，**`30天=`≡`7天=` 12/12 → 两栏退化成「仓龄」，「爆完即停」须改看首末提交日间隔**；12/12 ★0 → star 只能 `min:0`；`jepa` 占 5/12 多为复现仓；加密侧五连轮近零。11-06 第 33 轮：静态站逃逸、carrier 九轮 → 结案。[source: logs/2026-11-07#github-radar]


## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。判据速查：

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0，像清仓**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类事后补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号（`x·y=k`：`D>0` 才是净买）。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址必须左补零且全小写。** 买单真伪只认一条：终点余额升高且留住。**门槛数学先核对分子分母同单位；24h 涨跌幅别用 `ohlcv_list[0]`。** 细节 [lessons](/topics/lessons.md)
- **行情口径：** 跨日 >2% 先做「同日期重述分解」；DEX 量/fees 有 ~23% 星期效应须先归一；跨 series diff 按日期对齐（per-chain delta 总和 = aggregate）；历史点 `T00:00Z` = 前一日收盘。**只用桶结算值，live 不参与 delta；当日桶双向可修（11-07 DEX 桶 2h −13.4%）；7d/30d 必须脚本算。** [lessons](/topics/lessons.md#行情取数形状defillama--coingecko) [source: logs/2026-11-07#defi-overview]
- **聚合字段口诀：先说清它量的是什么，再决定信不信。** `/protocols` 的 `change_1d` = 当日 00:00 桶内值，不是今昨差；`/v2/chains` 已删 `change_1d`/`change_7d` → 旧写法静默拿缺省值，链涨跌只能走 `/v2/historicalChainTvl/{chain}` 自算。**成因查 `/protocols` 的 `hallmarks`**（协议级）；宏观崩盘用 CoinDesk RSS + WebFetch。[source: logs/2026-11-05#defi-overview]
- **`/overview/fees` 的 `change_7d` 实为 `total24h/total7DaysAgo−1`**，真 7d-over-7d 在 `change_7dover7d`；算涨跌自取 `tvl`/`totalDataChart` 按日期对齐；报 fees 增速先剔单日尖峰（>14 日中位数 3 倍）**且剔后按日均比**，否则等于没剔。**广度只在连续三日同向时作趋势读；价格单日 |Δ|>5% 时当日 F&G 一律作废（采样早于波动）。**[source: logs/2026-11-05#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它，再查它是不是用歧义词假装挡住了** —— `arxiv-radar` carrier 连九轮空转（14 词没配表），第 37 轮又证明 `circuit`/`network` 对超导/ML 同样成立 = 无判别力。「零假阴」≠ 规则安全。**某桶占比升高 ≠ 该桶杀伤力升高**。**报宽口径的分母，动手要窄口径的分子。**[source: logs/2026-11-05#arxiv-radar]
- **漏斗退化成单通道时，0 输出的责任在词表召回，不在过滤器** —— 过滤层已无调节空间；零幸存来自饱和 ≠ 任一侧流量消失。[source: logs/2026-10-31#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`（11-06 两次 403 次日自愈 → [ops](/topics/ops-plumbing.md)）。
- **脚本尾部崩溃 ≠ 本轮没产出** —— 产物在崩溃点之前写出时 stdout 像「跑挂了」而 `out.*.json` 其实是新的；**先看产物 mtime 再决定重跑**。
- **「0 新增」≠「废词」** —— 逐词单查 total_count 才分清「饱和」与「查询打不中」；长窗首跑推沉积、次跑归零 = `seen` 吃干；**`seen < raw 5%` 不许记饱和，须归因到具体规则**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫，别下结论。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-10-26#arxiv-radar]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) —— 含「watch 重开须先建 `on-chain-state.json`、`last_block` 设当前块，否则重放历史」

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
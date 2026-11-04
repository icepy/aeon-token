# Long-term Memory
*Last consolidated: 2026-11-03*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**（`github-radar` 实跑 30d）；`arxvi-radar` 孤儿待清。**`auto-merge` 关着 = 没人会合 PR**。→ [ops-plumbing](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS / NOTE 的价格监控已停（价格自己每天看），下面归档。
- **`aeon-update` 上游基线**（11-03 合入）：`aeonfun/aeon` HEAD `ec7a50c`；PR #23 只推水位线、不搬内容，已 merge。 [source: logs/2026-11-02#aeon-update]
- **预算纪律：MEMORY.md 只在两次 flush 之间增长。** 每次 flush 先压后写；超 8KB 先砍已归档节。[source: logs/2026-11-01#memory-flush]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **归档，勿再展开。** 阈值以 `STRATEGY.md` 为准；盘口细节在 `memory/topics/`；重开前先读 `memory/decisions.md`。
- **DEUS** `0x940A319B75861014A220D9c6c144d108552B089B`（base）· `0xbb0f7533` 持 xDEUS #1396 未烧 → 5 天 unstake clock 从未启动。**NOTE** 待命 480,000，扳机 = 第一笔 ETH 入账。
- 已停：`price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一方向的不同成熟度：论文（~4 个月）→ 代码（~1–2 个月）→ 代币（未建）。**同一个词在几条通道上依次点亮，那个次序才是信号。**
- `arxiv-radar` ✅ 07:30 UTC · 26 词 · 11-03 第 35 轮（30d）84 → 幸存 4（95% seen 单通道；carrier 连三轮 0 丢弃）。零命中 7 词 90d 全有命中，6 词 60d=90d → 沉积在 60–90d，补历史直接 days:90。饱和 15 词 maxpub 全在 10-06~10-30 → 全保活。幸存数看**几个词贡献**：单入口 ≥3 = 方向热，多入口各 1 = 覆盖面起作用。`consensus`+cs.DC 疑系统性降入分布式系统，待复核。[source: logs/2026-11-03#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-04 第 9 轮 8924 / 新增 5 / 可报 1（已发）。**「永久 id 空洞」作废**：同分钟 ≥3 条即批量回填、仍算真新增。**`parentProtocol` 跨快照翻转**，对登记 <1h 条目失效。**`address` 不可替代 `chains`**（6.1% 噪声）。**`filtered` 不可逆性首次咬到清单内协议**（XMAQUINA 9317 空链被钉死；恢复只能单删 seen 那条，不必重做基线）。[source: logs/2026-11-04#defillama-radar]
- `github-radar` cron 07:45 UTC · 18 词 · gh-v3。**「日跑 7 天窗」从未生效**（`var` 不注入 → `scan.py:184` 吃 30d）。第 15 轮 30d：2039→33→**报告级 9 全落机器人侧、加密侧连两轮归零**；入口换代（`teleoperation` 新收 14，上轮是 `jepa`）。**8/9 的 `commits_7d == 30d` = 新仓潮复现**。carrier 误杀第六次 → 放宽可动手。[source: logs/2026-11-02#github-radar]

## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。这里只留判据速查。

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0，像清仓**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类事后补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号（`x·y=k`：`D>0` 才是净买）。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址必须左补零且全小写。** 买单真伪只认一条：终点余额升高且留住。**门槛数学先核对分子分母同单位；24h 涨跌幅别用 `ohlcv_list[0]`。** 细节 [lessons](/topics/lessons.md)
- **跨日「大幅变化」先问是变化还是重述，再问重述集中在哪个分项**（70.9% 曾是 Bitcoin 链端点自己下修）；**DEX 量/fees 有 ~23% 星期效应，跨星期比必先归一**。**跨 series diff 按日期对齐**（判别式：per-chain delta 总和 = aggregate）；**历史点 `T00:00Z` = 前一日收盘**。[source: logs/2026-11-02#defi-overview]
- **`/protocols` 的 `change_1d` = 当前值 vs 当日 00:00 桶（日内），不是今天 vs 昨天**（11-03 四次验证）。**`/overview/fees` 的 `change_7d` 实为 `total24h/total7DaysAgo−1`，真 7d-over-7d 在 `change_7dover7d`。** 算涨跌自取 `tvl`/`totalDataChart` 按日期对齐；**报 fees 增速先剔单日尖峰（>14日中位数 3 倍）**。[source: logs/2026-11-03#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它** —— `arxiv-radar` carrier 连九轮空转，真因是 26 词里 14 个没配 carrier 表。「零假阴」≠ 规则安全。**某桶占比升高 ≠ 该桶杀伤力升高**（空链占比 85% 但旁路实救 0 条）。**报宽口径的分母，动手要窄口径的分子；「A 口径优于 B」必须同分母重算。**[source: logs/2026-11-02#defillama-radar]
- **漏斗退化成单通道时，0 输出的责任在词表召回，不在过滤器** —— 过滤层已无调节空间；零幸存来自饱和 ≠ 任一侧流量消失。[source: logs/2026-10-31#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。
- **脚本尾部崩溃 ≠ 本轮没产出** —— 产物写在崩溃点之前时 stdout 像「跑挂了」而 `out.*.json` 其实是新的；**先看产物 mtime 再决定重跑**。
- **有 seen 基线后「0 新增」≠「废词」** —— 逐词单查 total_count 才分得清「窗口饱和」与「查询打不中」；**换长窗首跑推沉积层、次跑归零 = `seen` 吃干**。**`seen < raw 5%` 不许记饱和，须归因到具体规则**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫，别下结论。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-10-26#arxiv-radar]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md)

## 归档：取数 / watch 框架
- **链上取数**：Base 走 `base.gateway.tenderly.co`（`eth_getLogs` 限 1000 块）；RH 4663 免 key。过期字段口径见 [lessons](/topics/lessons.md#行情取数形状defillama--coingecko)。**watch（5 个，已停）重开须先建 `on-chain-state.json` 条目、`last_block` 设为当前块**，否则重放历史。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
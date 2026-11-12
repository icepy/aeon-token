# Long-term Memory
*Last consolidated: 2026-11-11*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**；`arxvi-radar` 孤儿待清。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS / NOTE 的价格监控已停，下面归档。
- **`aeon-update` 基线 = `2ff25a3`**：PR #24 **已关未合，内容由 12:32Z catalog commit 直落 main**（ICP 三件套在库、catalog 96、lockfile 99）。**待决策：上游 `aeon.yml` 5 条新技能未抄（全 disabled）。** [source: logs/2026-11-09#aeon-update]
- **预算纪律：MEMORY.md 只在两次 flush 之间增长**，超 8KB 先砍已归档节。

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **勿再展开。** 阈值见 `STRATEGY.md`，细节见 [deus](/topics/deus-orderflow.md)。DEUS `0x940A319B75861014A220D9c6c144d108552B089B`（base）。**NOTE** 待命 480,000，扳机 = 首笔 ETH 入账。已停：`price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一方向的不同成熟度：论文（~4 个月）→ 代码（~1–2 个月）→ 代币（未建）。**同一个词在几条通道上依次点亮，那个次序才是信号。**
- `arxiv-radar` ✅ 07:30 · 26 词 · 11-10 第 42 轮 **80 → 7**，六分类两侧失败类全 0 = 读数干净；**ZK 侧占 3/7 证明召回活着**（单轮不作趋势）。14 词仍未配 carrier 表（同 37 轮结论）。收录停 11-09 = 正常。跨窗皆 0 仍只剩 `verifiable inference`/`restaking`，换写法不删。[source: logs/2026-11-10#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-12 第 17 轮 9012 / 新增 22 / **可报 4**（$32.9K）。**主读数 = `parent` 桶首上双位数、真边际首过半 4/11**：`Pendle Loop` $42.0M vs 可报和差 1279 倍。**`listedAt` 整分 `:00` 值是人手填的，算跨度先剔**；高号 `9412–9415` 缺席 = 同样待回填。→ [topic](/topics/defillama-radar.md) [source: logs/2026-11-12#defillama-radar]
- `github-radar` 22:30 · 18 词 · gh-v3。**cron 不注入 `var` → 7d 仅在手动 `days:7` 时成立**。11-10 第 23 轮 447/25/12：`30天=`≡`7天=` **12/12 第四轮**（=仓龄，判据缺陷）· **★ 分布首破全 0**（1★1，`min:0` 不动）· 加密侧**第八连轮** 0 · probe 真簇 `teleop`。→ [topic](/topics/github-radar.md) [source: logs/2026-11-10#github-radar]


## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。判据速查：

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0，像清仓**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类事后补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号（`D>0` 才是净买）。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址必须左补零且全小写。** 买单真伪只认：终点余额升高且留住。**门槛数学先核对分子分母同单位；24h 涨跌幅别用 `ohlcv_list[0]`。**[lessons](/topics/lessons.md)
- **行情口径 ①（结算纪律）：** 只用桶结算值，live 不参与 delta；**当日桶 24h 内视为未结算，隔日复查才可当历史引用**（11-07 桶次日下修 −17.1%、11-06 −13.4%）；跨日 >2% 先做「同日期重述分解」；7d/30d 必须脚本算；跨 series diff 按日期对齐（per-chain delta 总和 = aggregate）。[lessons](/topics/lessons.md#行情取数形状defillama--coingecko) [source: logs/2026-11-09#defi-overview]
- **行情口径 ②（字段与噪声）：** `change_7d` 实为 `total24h/total7DaysAgo−1`，真 7d-over-7d 在 `change_7dover7d`；DEX 量/fees ~23% 星期效应须先归一；fees 增速先剔单日尖峰（>14 日中位数 3×）**且剔后按日均比**；广度只在连续三日同向时作趋势读；价格单日 |Δ|>5% 当日 F&G 一律作废。[source: logs/2026-11-09#defi-overview]
- **聚合字段口诀：先说清它量的是什么，再决定信不信。** `/protocols` 的 `change_1d` = 当日 00:00 桶内值，不是今昨差；`/v2/chains` 已删 `change_1d`/`change_7d` → 旧写法静默拿缺省值，链涨跌只能走 `/v2/historicalChainTvl/{chain}` 自算。**成因查 `hallmarks`**（协议级）；宏观崩盘用 CoinDesk RSS + WebFetch。[source: logs/2026-11-05#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它，再查它是不是用歧义词假装挡住了** —— `arxiv-radar` carrier 连九轮空转（14 词没配表），第 37 轮又证明 `circuit`/`network` 对超导/ML 同样成立 = 无判别力。「零假阴」≠ 规则安全。**某桶占比升高 ≠ 该桶杀伤力升高**。**报宽口径的分母，动手要窄口径的分子。**[source: logs/2026-11-05#arxiv-radar]
- **漏斗退化成单通道时，0 输出的责任在词表召回，不在过滤器** —— 过滤层已无调节空间；零幸存来自饱和 ≠ 任一侧流量消失。[source: logs/2026-10-31#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。**但失败签名不止一种：** 403 是 23:00–23:31Z 配额窗口；`max_output_tokens` 是另一病因。**断路器 cf≥3 后连 30min 重试也守门**（只剩 360m probe）→ 「等重试自愈」失效，间歇故障变结构性卡死 → [ops](/topics/ops-plumbing.md)。
- **脚本尾部崩溃 ≠ 本轮没产出** —— 产物在崩溃点之前写出时 stdout 像「跑挂了」而 `out.*.json` 其实是新的；**先看产物 mtime 再决定重跑**。
- **「0 新增」≠「废词」** —— 逐词单查 total_count 才分清「饱和」与「查询打不中」；长窗首跑推沉积、次跑归零 = `seen` 吃干；**`seen < raw 5%` 不许记饱和，须归因到具体规则**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫，别下结论。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-10-26#arxiv-radar]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) —— 含「watch 重开须先建 `on-chain-state.json`、`last_block` 设当前块，否则重放历史」

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
# Long-term Memory
*Last consolidated: 2026-11-01*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch` 和 `logs/`。补跑会让整批技能同一秒触发 → **「几点跑」不能当 cron 时间读**；**frontmatter 的 `var:` 不注入运行环境**（`github-radar` 因此实跑 30d）；孤儿 `arxvi-radar` 待清。→ [ops-plumbing](/topics/ops-plumbing.md)
- **2026-10-25 起主线 = 发现层。** DEUS / NOTE 的价格监控已停（价格自己每天看），下面归档。
- **`aeon-update` 上游基线已锚定**（2026-10-26）：`aeonfun/aeon` HEAD `6eddd85`，本地 `ahead=0`（`behind=603` 全是本仓自动化提交）。
- **预算纪律：MEMORY.md 只在两次 flush 之间增长。** 上轮压到 8,190，本轮起点 8,327（被其他 skill 吃掉 137）—— 每次 flush 先压后写。[source: logs/2026-11-01#memory-flush]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **归档，勿再展开。** 阈值以 `STRATEGY.md` 为准（那里是权威），盘口细节在 `memory/topics/`；重开任一已停 skill 前先读 `memory/decisions.md`。
- **DEUS** `0x940A319B75861014A220D9c6c144d108552B089B`（base）· `0xbb0f7533` 持 xDEUS #1396 至今未烧 → 5 天 unstake clock 从未启动。**NOTE** 待命 480,000，三钱包 nonce 0 / ETH 0，扳机 = 第一笔 ETH 入账。
- 已停：`price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一方向的不同成熟度：论文（~4 个月）→ 代码（~1–2 个月）→ 代币（未建）。**同一个词在几条通道上依次点亮，那个次序才是信号。**
- `arxiv-radar` ✅ 07:30 UTC · 26 词 · vM · 10-31 第 32 轮（30d）84 → 幸存 0：**漏斗退化为 seen 单通道**（83 条被 seen 吃、EXCL 连五轮、carrier 连九轮 0）。饱和 19 词 maxpub 全在近 30 天内，无一降温。待办：`consensus` 加 `blockchain` 词（先 check 60d）。[source: logs/2026-10-31#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-01 第 6 轮 8892 / 新增 4 / 可报 0。**判新度只认源站 id 差集**。**空 `chains` = 已确证漏报**（`Daejin` 描述写 Binance/Ethereum/Solana，`chains` 却 `[]`）。**description 旁路优于 url**（+38% vs +39%，桥噪声 23% vs 46%）；**空chains 占被挡 41.5% vs 白名单 14.8%，旁路收益 3 倍**。[source: logs/2026-11-01#defillama-radar]
- `github-radar` cron 07:45 UTC · 18 词 · gh-v3。**「日跑 7 天窗」在调度链路从未生效**（`var` 不注入 → `scan.py:184` 吃 30d）。第 13 轮 30d：2049→34→10，**报告级 10 个全 ★0、9/10 落机器人侧**。**carrier 误杀第四次复现（丢弃侧 34% vs 放行 97%）= 结论成立，放宽可动手**；`seen<raw 5%` 同词对复现。[source: logs/2026-10-31#github-radar（第 13 轮）]


## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。这里只留判据速查。

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0，像清仓**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— `api.llama.fi` 走 CF，两轮同吃一份 `last-modified` 就可能「0 新增」。**差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取**。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **Solidly Swap 字序 `(a0In, a1In, a0Out, a1Out)`**，按 UniV2 解会把卖读成买 → 用储备差对照符号。**x·y=k：`D>0` 才是净买。**
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d 全 0；单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **`eth_getCode`=`0x` 才是 EOA；`0xef0100…` 是 EIP-7702。** 地址左补零且全小写。**view revert 先怀疑 selector。**
- **门槛数学先核对分子分母同单位**（曾把 DEUS 数量除以美元金额，424 倍 vs 真值 8.2 倍）；**24h 涨跌幅别用 `ohlcv_list[0]`**。
- **跨 series 做 diff 按日期对齐**（判别式：per-chain delta 总和 = aggregate）；**`dexs`/`fees` 字段整列滞后一日** → 真值取图表末两点。**单腿恰为 0 = 快照缺口；当日桶是残桶、修正双向（10-31 实测 −32.4%，推翻「只上修」）；`total7d/24h≈1` = 新接入序列。** 详见 [lessons](/topics/lessons.md#假零与断层)。[source: logs/2026-10-31#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它** —— `arxiv-radar` carrier 连九轮空转，真因是 26 词里 14 个没配 carrier 表。「零假阴」≠ 规则安全。[source: logs/2026-10-31#arxiv-radar（第 32 轮）]
- **漏斗退化成单通道时，0 输出的责任在词表召回，不在过滤器** —— 第 32 轮 84 条里 83 条被 `seen` 吃、其余格恒定，过滤层已无调节空间。零幸存来自饱和 ≠ 任一侧流量消失（饱和词 maxpub 全在近 30 天内）。[source: logs/2026-10-31#arxiv-radar（第 32 轮）]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。
- **脚本尾部崩溃 ≠ 本轮没产出** —— 产物写在崩溃点之前时，stdout 像「跑挂了」而 `out.*.json` 其实是新的；**先看产物 mtime 再决定重跑**（`scan.py:910` 元组下标事故，10-27）。
- **有 seen 基线后「0 新增」≠「废词」** —— 逐词单查 total_count 才分得清「窗口饱和」与「查询打不中」；**换长窗首跑推沉积层、次跑归零 = `seen` 吃干**。**`seen < raw 5%` 不许记饱和，须归因到具体规则**；同窗口连跑不作趋势。[source: logs/2026-10-29#github-radar（第 11 轮）]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫（60d 轮 16/24 死于 429），别下结论。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-10-26#arxiv-radar（60d 第四/七轮）]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md) · [market-context](/topics/market-context.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.md)

## 归档：取数 / watch / 预警框架
- **链上取数**：Base 打 `base.gateway.tenderly.co`（`eth_getLogs` 限 1000 块）；RH 4663 免 key、24k 块窗口。见 [base-rpc-access](/topics/base-rpc-access.md)。
- **watch（5 个，已停）与预警框架**：重开必须先建 `on-chain-state.json` 条目并把 `last_block` 设为当前块，否则重放历史；框架见 `memory/alert-framework.md`（相对量、不用绝对美元阈值）。细节见 [lessons](/topics/lessons.md#watch-configuration)。
- **过期字段口径**（`/v2/chains` 无 `change_1d`、`/global` 24h mcap 不可信）见 [lessons](/topics/lessons.md#行情取数形状defillama--coingecko)。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
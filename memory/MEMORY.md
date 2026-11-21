# Long-term Memory
*Last consolidated: 2026-11-20*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS/NOTE 价格监控已停，下面归档。
- **`aeon-update` 基线 `7b20c95`**（PR #27 已合 11-16T11:42Z）：50 条提交**净变更为零**。判据 `CLEAN-MERGE>0` + `git diff --stat` 空 ⇒ 没改；6 冲突全是技能计数漂移 → `keep_local`。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-16#aeon-update]
- **待盯（OPERATOR）：`defi-overview` 连绿两轮（cf 0，21/43 = 49%），再绿一轮即 22/44 = 50.0% 出 chronic 线。** 修法「砍单轮输出」两轮兑现。**cf 不因 skill 停用而衰减** —— `price-alert`/`onchain-monitor`/`token-movers` 的 cf 5/4/3 是 10-25 网关故障的账未清，非当前故障。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-20#heartbeat]
- **预算纪律：MEMORY.md 只在两次 flush 间增长**，超 8KB 先砍已归档节。
- **PR 队列会反过来影响读数语义**：词表/阈值改动只在合进 main 后才算数，挂着就是没生效。队列现为空（#25/#27 均 11-16 合）。[source: logs/2026-11-17#heartbeat]
## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **勿再展开。** 阈值见 `STRATEGY.md`，细节见 [deus](/topics/deus-orderflow.md)。**NOTE** 待命 480,000。

## 发现层（主线）
三条**平行**探针测同一成熟度阶梯：论文（~4 月）→ 代码（~1–2 月）→ 代币（未建）。**同一个词依次点亮，次序才是信号。**
- `arxiv-radar` ✅ 07:30 · 26 词 · 11-19 第 51 轮 74 → 4。**10 词「窗口太短」第三轮复现；`ti:"human data"` 本轮 30d 新收 2 条全幸存 ⇒ 上轮「10 月断流」推翻，是延迟入索引**（窗口内零 ≠ 话题停）。出货词组换但同簇 ⇒ 数据侧召回是整簇属性。→ [lessons](/topics/lessons.md#arXiv-检索arxiv-radar) [source: logs/2026-11-19#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-21 第 26 轮 9085 / 新增 6 / 可报 **2**（`Biribi` Arbitrum 轮盘 $1,996 · `Gmoon` Robinhood Chain 发币台 $2.58）。**TVL −3.77% 经 `/v2/historicalChainTvl`（−5.25%）证实是行情非口径，两源 6.4× 只比 delta**。→ [topic](/topics/defillama-radar.md) [source: logs/2026-11-21#defillama-radar]
- `github-radar` 22:30 · 18 词 · **cron 不注入 `var` → 7d 仅手动 `days:7` 时成立**。11-19 第 30 轮 2008→74→报 27（30d 窗，不可与 7d 轮直比）。**`jeparla` 绕过 `NEG_BY_TERM["jepa"]` 排第一 ⇒ NEG 须逐变体登记**；`data availability` seen/raw=4.7% 仍记饱和 = 误读第二例。→ [topic](/topics/github-radar.md) [source: logs/2026-11-19#github-radar]

## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。判据速查：

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址左补零且全小写。** 买单真伪只认终点余额升高且留住。**门槛先核对分子分母同单位。**[lessons](/topics/lessons.md)
- **行情口径 ①（结算纪律）：** 只用桶结算值，live 不参与 delta；**当日桶隔日复查才可当历史引用**；7d/30d 脚本算；跨 series 按日期对齐。**桶编号须由 ts 换算 UTC 日期**，「倒数第 N 个」差一位会把结论翻反。[lessons](/topics/lessons.md#行情取数形状defillama--coingecko) [source: logs/2026-11-11#defi-overview]
- **行情口径 ②（字段与噪声）：** `change_7d` 实为 `total24h/total7DaysAgo−1`，真 7d 在 `change_7dover7d`；fees `protocols[]` 无 `tvl` 须 join；**F&G 回溯修订**须拉 ≥3 日序列。**`change_1d` 是桶内值非今昨差**。**总 TVL 两套口径（`totalLiquidityUSD` vs `/v2` `tvl`）比值恒 ~2.0，混用造 −50% 假暴跌 —— 比 delta 前先验同源。** [source: logs/2026-11-19#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它，再查它是不是用歧义词假装挡住了** —— `circuit`/`network` 对超导/ML 同样成立 = 无判别力；「零假阴」≠ 规则安全。**漏斗退化成单通道时，0 输出的责任在词表召回**；零幸存来自饱和 ≠ 流量消失。**某桶占比升高 ≠ 杀伤力升高**。**任何「N=0」字段先确认分母没被过滤掉 —— 没进的输入不是零结果**（`cross_windows()` 不量降级词）。→ [lessons](/topics/lessons.md) [source: logs/2026-11-17#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据 `num_turns:1` + 0 tool calls。**失败签名不止一种**，断路器跳闸后重试通道也没了；**probe 偶然跑通 ≠ 修复** → [ops](/topics/ops-plumbing.md) [source: logs/2026-11-12#heartbeat]
- **过程事故两例：** 脚本尾部崩溃 ≠ 本轮没产出（产物在崩溃点前写出，**先看 mtime 再决定重跑**）；**`git reset --hard` 会吃掉已写未提交的内容 —— 取消暂存只能用 `git restore --staged <file>`**（11-11 丢三个 memory 文件）。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-11#defi-overview]
- **「0 新增」≠「废词」** —— 逐词单查 total_count 才分清「饱和」与「查询打不中」；长窗首跑推沉积、次跑归零 = `seen` 吃干；**`seen < raw 5%` 不许记饱和，须归因到具体规则**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫。**整轮没跑成（网关 403）同理**，缺口轮次不计入「连续 N 轮」类序列判据。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-11-17#heartbeat]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) —— 含「watch 重开须先建 `on-chain-state.json`、`last_block` 设当前块，否则重放历史」

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
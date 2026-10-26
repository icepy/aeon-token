# Long-term Memory
*Last consolidated: 2026-10-26*

## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `memory/cron-state.json` 的 `last_dispatch` 和 `logs/`（`scheduler.yml` 用 `cron-due.sh` + `CATCHUP_HOURS=12` 债务模型）。

## Tracked Token
| Token | Contract | Chain |
|---|---|---|
| DEUS | 0x940A319B75861014A220D9c6c144d108552B089B | base |

> `price-alert` 只读本表第一行。地址见 [deus-escrow](/topics/deus-escrow.md)。

## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $20,400，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181e` 240k · 上膛6 `0x3a9039c7` 150k · 上膛5 `0x572bb527` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 先例：带 gas 后 24.4h 才卖）。owner 自持 630,000。见 [note-systems](/topics/tokens/note-systems.md)。
- **⚠️ NOTE 价格与供给：** 上沿 $0.0438 破而复失（10-24 21:01Z，高点 $0.04657 回吐 −8.5%），供给 ~40,000 NOTE/天 ≈ 日量 1.66%（#25+#26+#27）——「持续派发」不是「砸盘」。**盯 ETH 入账，不盯价格。** [source: logs/2026-10-24#onchain-monitor]
- **DEUS 四道 gate 全未触发（10-25 08:09Z，$0.01710812）：** 距 $0.012 −29.86% · $0.025 +46.13% · $0.032 +87.05% · $0.041 +139.65%。**$0.041 要吃掉深池储备 35.4%、实付 $177,880（24h 量的 12.8×）→ 只能靠撤供给、一个块跳过去 = unstake 必须提前 5 天。** 见 [deus-orderflow](/topics/deus-orderflow.md)。 [source: logs/2026-10-25#price-alert]
- **🔴 「CLAIM 日滴 338k = 砸盘压力」是错的（10-25 实测）：** 24h 流出 338,594 中 **97.8% 只流进自家四个导管合约，且导管余额在涨**；真正再派出仅 **145,228**，其中 93,716 走已验证 claim→砸盘 EOA，23,756 进 xDEUS。**净砸市场 ≈ 75,977/天 = 供应 0.0087% ≈ $1,318，够不到 $0.012，不构成 unstake 理由。** [source: logs/2026-10-25#price-alert]

## Active Topics
### DEUS（盘口细节全在 [deus-orderflow](/topics/deus-orderflow.md)）
- **价格 $0.01710812**（10-25 08:09Z 链上 mark），1h +0.13% 全来自 VIRTUAL 引腿。**深度仅约 $1.7k 名义值推动 1%；深池 10-25 多次静默（最长 185.2 分钟）。mark 是停着的，不是被检验过的。** 见 [state](/topics/price-alert-state.json)。
- **🔴 Escrow 29,150,566.777698**，24h +41,905.10 = 5%/日线 **0.029 倍**。**`0xbb0f7533` 仍持 #1396、约 2.9 天未烧 → $0.041 出口的 5 天冷 clock 没启动。**
- **持仓面：** 两巨鲸稳持；派发商 `0x4e3ae00e`（≈56k/天）定节奏。**囤货合约 `0x92325e5a` 持 118,288.59 零转出 —— 转出即 −0.7%~−0.9%，账面最具体的前瞻扳机。** [source: logs/2026-10-25#price-alert]
- **卖盘判据：** 按 `tx.from` 汇总同 tx 全部场所。见 [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md)。
- **🔴 最大单次增发 85,828.91 DEUS（10-25 07:11:49Z）：** 4.5 分钟拆给 **8 个 nonce=1 的 dormant EOA**，**零流出 —— 补给不是抛售，盯第一个转出**。**「净通缩走平」作废**，24h 改 **+73,181.90**。见 [deus-escrow](/topics/deus-escrow.md)。 [source: logs/2026-10-25#price-alert]
- **宏观快照**：[market-context](/topics/market-context.md)。

### NOTE
- 见 [note-systems](/topics/tokens/note-systems.md) —— 解锁-回锁-上膛时间线。

### github-radar（第九轮 · 抽样偏差 3.85×）
- 全文见 [github-radar](/topics/github-radar.md)。**核验永不按 star 分配**（`PER_TERM_CAP=25` 致报告级 20→77）；**报「新增」先与上轮快照求差**；**`pages` 按名字判，别看 size**；**`jepa` star 与 commits 反相关**（新增 65 全 ★0 却占 26 个报告级）。
- **换词前先量两口径的 total_count + 重叠度**：`vla`→全称双赢（污染 22%→1.4%），`jepa`→全称损失 94.6%。分界是术语在生态里怎么写，不是缩写脏不脏。 [source: logs/2026-10-25#github-radar]

## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。这里只留判据速查。

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0**）· **API `h1=null` 当成 0**。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **Solidly Swap 字序 `(a0In, a1In, a0Out, a1Out)`**，按 UniV2 解会把卖读成买 → 用储备差对照符号。**x·y=k：`D>0` 才是净买。**
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d 全 0；单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **`eth_getCode`=`0x` 才是 EOA；`0xef0100…` 是 EIP-7702。** 地址左补零且全小写。**view revert 先怀疑 selector。**
- **门槛数学先核对分子分母同单位**（曾把 DEUS 数量除以美元金额，424 倍 vs 真值 8.2 倍）；**24h 涨跌幅别用 `ohlcv_list[0]`**。
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。
- **「流出」要成为「卖压」须三条全中**：接收方不是自家合约、该方余额在**降**、终点落在池子或最终卖出者。否则是内部搬家。 [source: logs/2026-10-25#price-alert]
- **增量型变量（`totalSupply`/`balanceOf`）反复读到同一数字 ≠ 走平** —— 单块可跳 +85,829。下判断前取 ≥3 个跨度（15m/1h/6h/24h）。 [source: logs/2026-10-25#price-alert]
- **有 seen 基线后「0 新增」≠「废词」** —— 逐词单查 total_count 才分得清「窗口饱和」与「查询打不中」。
- **已合并 ≠ 已生效**：PR 状态 MERGED 后，refactor 仍可能基于旧副本静默覆盖（arxiv-radar PR #8）。**对照文件本体与 commit，别只信 PR 状态。** [source: logs/2026-10-25#arxiv-radar]
- **单个 409 空仓不能触发认证降级** —— 区分「数据为空」与「端点坏了」必须发生在降级逻辑之前。 [source: logs/2026-10-25#github-radar]

## Reference
- [deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [market-context](/topics/market-context.md)
- [world-action-models](/topics/world-action-models.md) · [github-radar](/topics/github-radar.md) — WAM 60 天 **99 仓 / 94 owner**；star≠活跃度（★1107/11 提交 vs ★48/10）。
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.json) · [lessons](/topics/lessons.md)

## 监控清单（memory/on-chain-watches.yml）
5 个：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting `0xfdd9`。已摘 `NOTE` 本体、staging `0x69bb`。**新增 watch 要建 `on-chain-state.json` 条目并把 `last_block` 设为当前块**，否则重放历史。

## 链上取数
- Base 直打 `base.gateway.tenderly.co`（`eth_getLogs` 限 1000 块，长窗 999 分片）；RH 4663 免 key、24k 块窗口。见 [base-rpc-access](/topics/base-rpc-access.md)。
- **DeFiLlama `/v2/chains` 无 `change_1d`**，用 `/v2/historicalChainTvl/{chain}` 自算；**CoinGecko `/global` 的 24h mcap 不可信**，用 `/coins/markets` 加权重算。

## 预警框架（铁律）
- 完整框架见 `memory/alert-framework.md`，做链上预警前先读。用相对量，不用绝对美元阈值。优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。P0 立即、P1 汇总。每条必须带币、数值、命中规则、下一步动作。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文。代币名、合约地址、协议名、代码保留原文。

# Long-term Memory
*Last consolidated: 2026-10-25*

## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `memory/cron-state.json` 的 `last_dispatch` 和 `logs/`。`scheduler.yml` 用精确时隙债务模型（`cron-due.sh` + `CATCHUP_HOURS=12`）。

## Tracked Token
| Token | Contract | Chain |
|---|---|---|
| DEUS | 0x940A319B75861014A220D9c6c144d108552B089B | base |

> `price-alert` 只读本表第一行 —— 一次一个币。当前 DEUS。Escrow / xDEUS 地址见 [deus-escrow](/topics/deus-escrow.md)。

## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $20,400，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181e` 240k · 上膛6 `0x3a9039c7` 150k · 上膛5 `0x572bb527` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 先例：带 gas 后 24.4h 才卖）。owner 自持 630,000。见 [note-systems](/topics/tokens/note-systems.md)。
- **⚠️ NOTE 上沿破而复失（10-24 21:01Z）：** 主池 `0x378b1023` **$0.042599**，liq $410,435，h1 −4.40% / h24 −3.37%，24h 量 $102,753。$0.0438 防守失败回落 −2.7%，高点 $0.04657 回吐 −8.5%。**盯 ETH 入账，不盯价格。**
- **⚠️ NOTE 供给侧斜率变了：** 180,000 进 **schedule #27**（30 天线性）。#25 20k + #26 14k + #27 6k ≈ **40,000 NOTE/天 ≈ $1,704/天 = 日量 1.66%**，无需 owner 决策 ——「持续派发」不是「砸盘」。
- **DEUS 四道 gate 全未触发（10-25 04:01Z）：** $0.012 −30.64% · $0.025 +44.51% · $0.032 +84.97% · $0.041 +136.99%。**$0.041 需净买 6.63M DEUS ≈ $115,027 ≈ 深池 24h 量（$13,952）的 8.2 倍 → 只能靠撤供给到达。这就是 unstake 必须提前 5 天的量化理由。**

## Active Topics
### DEUS（盘口细节全在 [deus-orderflow](/topics/deus-orderflow.md)）
- **价格 $0.01730**（10-25 04:01Z DexScreener 深池 mark；链上储备 mark $0.0173407），1h **−0.28%**（实测），24h **−4.37%**。见 [state](/topics/price-alert-state.json)。
- **🔴 最新一小时（03:57:43Z 起）：全市场 44,807 DEUS 砸向盘口、7 笔 swap 零买入。** 复活第一笔就是卖；资金 100% 来自 CLAIM 回收（`claim → 新 EOA → 30 秒清仓`，TELL 10 第五次复现）。**溢价第四小时收窄至 +0.24% —— 是分母在动，不是套利出力。**
- **🔴 Escrow 连续第八轮逐 wei 闭合：** 29,150,566.777698，24h **+41,905.10** = 5%/日线的 **0.029 倍**。**`0xbb0f7533` 仍持 #1396，连续第九轮未烧 = 下次扳机。** CLAIM 24h 净出 **338,671.85**（38.78% 供应）。总供应 24h **−12,373.69**。
- **存量巨鲸无主动砸盘** —— 四个最大持有者（335,249 / 70,034 / 250,000 / 284,371）逐 wei 未动；卖压来自小仓位、老仓 `0x8cd54fbd` 与批发商 `0x4e3ae00e`（持 8.07M，每天放 ~5 万）。
- **最大买单是合约囤货**：`0x92325e5a` 0→118,288 零转出（同一合约昨天砸 101,983）。**盯它转出 = 下一根 −0.7%~−0.9%。**
- **卖盘判据：** 单池计数会低估单一操作者 —— 归因按 `tx.from` 汇总同 tx 全部场所。对手方见 [deus-buyers](/topics/deus-buyers.md) · 事件线见 [deus-events](/topics/deus-events.md)。
- **🔴 DEUS 7d 净增发 +65,381 已陈旧**；**连续四天净通缩：−19,693 → −38,770 → −38,770 → −38,770**（block-pinned 24.00h）。重测前别再引 +65,381。见 [deus-escrow](/topics/deus-escrow.md)。
- **宏观快照**：[market-context](/topics/market-context.md)。

### NOTE
- 见 [note-systems](/topics/tokens/note-systems.md) —— 解锁-回锁-上膛时间线、per-schedule 量级。

### github-radar（第六轮已收口，详见 [github-radar](/topics/github-radar.md)）
- **🔴「加密侧实测为空」是核验上限造成的假象。** 35 个加密仓 34 个 ★0–2 被 `CHK_CAP=250` 挤掉；补齐后 **18 个 ≥5 提交**，但 **10 个近 7 天零提交**（爆完即停）。
- **判据：30d 提交 ≠ 现在还在写**（机器人侧 ≥10 提交的 51 仓里 20 个 7d=0）；**根目录 `AGENTS.md`/`CLAUDE.md` = 「单人 + agent」指纹**（加密 10/18 vs 机器人 2/21）；**按 star 分配核验预算会饿死低 star 域**。
- **WAM 簇 99 仓 / 94 owner，逐周 6/10/7/9/19/20/7/12/9** —— 换轮次完全复现。见 [world-action-models](/topics/world-action-models.md)。**未修缺陷：单个 409 空仓会把 `GH` 全局置 False**，长窗口下静默把后面全标 unverified。

## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。这里只留判据速查。

- **假零六件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼。**报「平静」前查已知活跃窗口 + `eth_call` 余额。**
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **Solidly Swap 字序 `(a0In, a1In, a0Out, a1Out)`**，按 UniV2 解会把卖读成买 → 用储备差对照符号。**x·y=k：`D>0` 才是净买，负数 = 方向写反。**
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d 全 0；单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **`eth_getCode`=`0x` 才是 EOA；`0xef0100…` 是 EIP-7702。** 地址左补零且全小写。**view revert 先怀疑 selector。**
- **缺 `h1` ≠ 平静** —— 按 0 处理会让 gate 显 QUIET 但实际未测量；state 存 `null`，API 的 `v1h=0` 也拿 Swap log 验。
- **门槛数学先核对分子分母同单位**（曾把 DEUS 数量除以美元金额，424 倍 vs 真值 8.2 倍）；**24h 涨跌幅别用 `ohlcv_list[0]`**（未走完的当日 K）。
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。
- **网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。

## Reference
- [deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [market-context](/topics/market-context.md)
- [world-action-models](/topics/world-action-models.md) · [github-radar](/topics/github-radar.md) — WAM 提法 60 天 **99 仓 / 94 owner**；star≠活跃度（★1107/11 提交 vs ★48/10 vs ★199/2）。
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.json) · [state 契约](/topics/price-alert-state.md)
- [note-systems](/topics/tokens/note-systems.md) · [lessons](/topics/lessons.md)

## 监控清单（memory/on-chain-watches.yml）
5 个：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting `0xfdd9`。Base $200/$250；NOTE $500。timelock 不加 `event_topics`。已摘：`NOTE` 本体、staging `0x69bb`。**新增 watch 必须在 `on-chain-state.json` 建条目并把 `last_block` 设为当前块**，否则重放历史。

## 链上取数
- Infura 免费档只允许 10 块 → 直打公共端点（Base `base.gateway.tenderly.co` 1000 块 / RH `rpc.mainnet.chain.robinhood.com` 24k 块）。见 [base-rpc-access](/topics/base-rpc-access.md)。
- **RH 4663 免 key**，24k 块窗口可扫。**DeFiLlama `/v2/chains` 无 `change_1d`/`change_7d`**，用 `/v2/historicalChainTvl/{chain}` 自算；**CoinGecko `/global` 的 24h mcap 不可信**，用 `/coins/markets` 加权重算。

## 预警框架（铁律）
- 完整框架见 `memory/alert-framework.md`，做链上预警前先读。用相对量，不用绝对美元阈值。
- 优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。P0 立即、P1 汇总。每条必须带币、数值、命中规则、下一步动作。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。

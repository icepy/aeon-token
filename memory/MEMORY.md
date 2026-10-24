# Long-term Memory
*Last consolidated: 2026-10-24T21:10Z*

## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `memory/cron-state.json` 的 `last_dispatch` 和 `logs/`。`scheduler.yml` 用**精确时隙债务模型**（`cron-due.sh` + `CATCHUP_HOURS=12`），晚 12h 内补跑。

## Tracked Token
| Token | Contract | Chain |
|---|---|---|
| DEUS | 0x940A319B75861014A220D9c6c144d108552B089B | base |

> `price-alert` 只读本表第一行 —— 一次一个币。当前 DEUS。
> Escrow / xDEUS 地址见 [DEUS escrow](/topics/deus-escrow.md)。

## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $20,400，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181ed1540a83281ca053df49ac32019e8731` 240k · 上膛6 `0x3a9039c7069382594f779d95db6686007119f35e` 150k · 上膛5 `0x572bb5272603889f5742e8b8ab2f1d4c6851a93e` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 先例：带 gas 后 24.4h 才卖）。owner 自持 630,000。
- **🔴 NOTE 上沿破而复失（10-24 21:01Z）：** 主池 `0x378b1023` **$0.042599**，liq $410,435，h1 −4.40% / h24 −3.37%，24h 量 $102,753。**$0.0438 防守失败，回落 −2.7%；高点 $0.04657 已回吐 −8.5%。** 12:00Z 判的「CONSOLIDATING 非 BREAKOUT」成立。**盯 ETH 入账，不盯价格。**
- **⚠️ NOTE 供给侧斜率变了：** owner 首次动仓，180,000 进 **schedule #27**（30 天线性）。**#25 20k + #26 14k + #27 6k = ~40,000 NOTE/天 ≈ $1,704/天 = 日量 1.66%**，且无需 owner 决策 —— **「持续派发」不是「砸盘」**。详见 [note-systems](/topics/tokens/note-systems.md)。
- **DEUS 四道 gate 全未触发：** $0.012 −31% · $0.025 +44% · $0.032 +84% · $0.041 +135%。**$0.041 需净买 6.6M DEUS ≈ 深池 24h 量的 240 倍 → 只能靠撤供给到达。这就是 unstake 必须提前 5 天的量化理由。**

## Active Topics
- `price-alert` DEUS **$0.017410**（10-24 20:01:47Z 深池 mark；诚实区间 $0.017163–$0.017410，USDC 中位 $0.017181），1h +0.27%，24h −3.05%。**深池连续第二小时溢价（+1.34%）且在扩大，别单引深池一个数当中位价。** 见 [state](/topics/price-alert-state.json)。
- **Escrow 29,150,566.78**（24h **−267,657 = −0.910%**；两笔 stake-in 10,905 + 36,000，零 unstake、零 burn）→ 对 5%/日 线 1.47M 仅 **0.182 倍**，无 unstake 压力。占供应 3.3270%。xDEUS **1728**。供应 24h **−29,152.63**（第九次净通缩）。
- **`0xbb0f7533` 仍持 xDEUS #1396 —— 扳机连续第四轮未响。** 上次 #1492 释放 319,562 DEUS 后 75 分钟全砸。
- **DEPTH 待补：** 深池 `0x3E97c5EC`（Aerodrome classic，token0=VIRTUAL 不是 DEUS）。**池子死/活有效期只有一轮，每轮重测。**
- **买盘分两种：结构性套利 vs 方向性留存 —— 只有后一种是真 bid。** 9 条判据见 [lessons](/topics/lessons.md#price-feeds)。单池「N 买 / 0 卖」常是同秒双池套利的一半；归因必须读 `tx.from`，`topics[1]` 只是路由。
- **新钱 cohort：** `0x3fd51604` 加至 7,735；`0x1184de98` 10-24 10:02 清仓 46,195 换 SLC（轮动非离场）。见 [deus-buyers](/topics/deus-buyers.md)。
- **DEUS 7d 净增发 +65,381 已陈旧**，连续多日净通缩。**再引用前必须重测完整 7d 窗口。** 见 [deus-escrow](/topics/deus-escrow.md)。
- **宏观：** [market-context](/topics/market-context.md)。10-23 chop，F&G 50。

## Lessons Learned（每条一行，详情见 [lessons](/topics/lessons.md)）
- **过滤器丢掉的样本要全量抽检** —— `arxiv-radar` 曾 90 天窗 20 篇真货全丢、噪声全进，症状是「零命中」。同一放宽动作在不同域效果相反。
- **RH 历史 `eth_call` 不可用（只有 `latest`）**，24h 余额差额必须走 log 双向扫描；**Base Tenderly 支持任意历史块**，两链别互推。
- **无 ABI 解 calldata：靠 uint 词位置 + 同 tx 事件 data 对齐**。`0x091e7db9` 在 4byte 无收录。
- **「owner 转账 = 砸盘」是本轮被打掉的最大假设** —— 先看 `tx.to` 是不是自家合约。判信号要算「释放速率 ÷ 日成交量」。
- **钱包型 watch 不能用 `eth_getLogs{address:<EOA>}`** —— EOA 不发事件。要在**代币合约**上做 topic 过滤。
- **Never trust a zero-log window** —— 报「平静」前查已知活跃窗口 + `eth_call` 余额。**假零六件套：RPC 429 返空、`mainnet.base.org` 整批 revert、topic0 只给 4 字节、RH UA 403、`-32602` 被 `||[]` 兜空、地址靠记忆拼。**
- **判「池子安静」前先按地址扫 topic0 直方图** —— 家族不匹配静默出假零（V3 `0xc42079f9` vs Solidly `0xb3e27736`）。
- **计算前先读 `token0()`** —— 深池 token0 是 VIRTUAL，直接 `reserve0/reserve1` 会得出 36.34（真值 0.02795）。
- **`balanceOf` 地址要左补零**，右补零静默返 0；**view 调用 revert 先怀疑 selector**（`isOperationReady`=`0x13bc9f20`）。
- **`eth_getCode` = `0x` 才是 EOA；`0xef0100…` 是 EIP-7702 智能账户**，别当新号。
- **xDEUS is ERC-721** —— `decimals()` reverts，`tokenId` 在 `topics[3]`。
- **上膛钱包的扳机是「第一笔 ETH 入账」**，比 nonce 更早；**claim 制 vesting 看 scheduleId**，同合约不同 schedule 量级差百倍。
- **24h 涨跌幅别用日线首尾收盘价算** —— `ohlcv_list[0]` 是未走完的当日 K 线。
- **缺 `h1` ≠ 平静** —— 按 0 处理会让 gate 显 QUIET 但实际**未测量**；state 存 `null`。
- **网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。

## Reference
- [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [market-context](/topics/market-context.md) · [base-rpc-access](/topics/base-rpc-access.md)
- [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.json) · [note-systems](/topics/tokens/note-systems.md) · [lessons](/topics/lessons.md)

## 监控清单（memory/on-chain-watches.yml）
5 个：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting `0xfdd9`。Base $200/$250；NOTE $500。timelock 不加 `event_topics`。已摘：`NOTE` 本体、staging `0x69bb`。**新增 watch 必须同步在 `on-chain-state.json` 建条目并把 `last_block` 设成当前块**，否则首次运行重放历史。

## 链上取数
- Infura 免费档只允许 10 块 → 直打公共端点（Base `base.gateway.tenderly.co` 1000 块 / RH `rpc.mainnet.chain.robinhood.com` 24k 块）。端点与陷阱见 [base-rpc-access](/topics/base-rpc-access.md)。

## 预警框架（铁律）
- 完整框架见 `memory/alert-framework.md`，做链上预警前先读。用相对量，不用绝对美元阈值。
- 优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。P0 立即、P1 汇总。每条必须带币、数值、命中规则、下一步动作。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。

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
- **🔴 待命 480,000 NOTE ≈ $20,400，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181e` 240k · 上膛6 `0x3a9039c7` 150k · 上膛5 `0x572bb527` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 先例：带 gas 后 24.4h 才卖）。owner 自持 630,000。全串见 [note-systems](/topics/tokens/note-systems.md)。
- **⚠️ NOTE 上沿破而复失（10-24 21:01Z）：** 主池 `0x378b1023` **$0.042599**，liq $410,435，h1 −4.40% / h24 −3.37%，24h 量 $102,753。$0.0438 防守失败回落 −2.7%，高点 $0.04657 回吐 −8.5%。**盯 ETH 入账，不盯价格。**[source: logs/2026-10-24#onchain-monitor]
- **⚠️ NOTE 供给侧斜率变了：** 180,000 进 **schedule #27**（30 天线性）。#25 20k + #26 14k + #27 6k ≈ **40,000 NOTE/天 ≈ $1,704/天 = 日量 1.66%**，无需 owner 决策 —— 「持续派发」不是「砸盘」。见 [note-systems](/topics/tokens/note-systems.md)。[source: logs/2026-10-24#onchain-monitor]
- **DEUS 四道 gate 全未触发：** $0.012 −30.73% · $0.025 +44.30% · $0.032 +84.71% · $0.041 +136.66%。**$0.041 需净买 6.6M DEUS ≈ 深池 24h 量的 238 倍 → 只能靠撤供给到达。这就是 unstake 必须提前 5 天的量化理由。**[source: logs/2026-10-24#price-alert]

## Active Topics
- **DEUS 现价 $0.01732473**（10-24 22:02:51Z 深池 mark；USDC 三池中位 $0.017173），1h −0.24%，24h −3.84%。跌幅第七轮全部来自报价腿（VIRTUAL/USD −4.92%），DEUS 跑赢 VIRTUAL。见 [state](/topics/price-alert-state.json)。
- **盘口连续第三个 <3,000 DEUS 的小时（2,427）。** 溢价第四小时单调收窄 +1.12% → +1.34% → +1.04% → +0.94%，套利量同跌 —— **收敛是分母在动，不是套利出力。两边都没人 = 流动性枯竭，不是抛售。**
- **第四次 claim-and-dump，首次跨两场所拆分：** `0xd1a7ba72`（EIP-7702）100 秒内收 3,529.86 三腿，拆 2,426.78 进深池 + 1,103.08 进 USDC。**归因按 `tx.from` 汇总同 tx 全部场所**，单池计数会低估。见 [deus-events](/topics/deus-events.md)。
- **四个大持有者逐 wei 未动：** 335,249.499443 · 70,034.140337 · 250,000.125225 · 284,371.457830。**无存量主动砸盘。**
- **`0xbb0f7533` 仍持 xDEUS #1396 —— 扳机连续第五轮未响。** 烧 #1492 释放 319,562 DEUS 后 75 分钟全砸。CLAIM 占 38.787% 供应。**$0.012 需净砸 ~3.81M DEUS**。
- **Escrow 29,150,566.78**（24h −267,657.12 = −0.910%，第四次逐 wei 闭合），对 5%/日线 1.47M 仅 **0.182×** —— 无 unstake 压力。xDEUS **1728**。CLAIM 24h 净出 **304,681（记录内最大）**。见 [deus-escrow](/topics/deus-escrow.md)。
- **总供应 876,177,627.81，24h −29,152.63 —— 第十次净通缩。** 7d 净增发 +65,381 已陈旧，**再引用前必须重测完整 7d 窗口**。
- **新钱 cohort：** `0x3fd51604` 加至 7,735；`0x1184de98` 10-24 10:02 清仓 46,195 换 SLC（轮动非离场）。见 [deus-buyers](/topics/deus-buyers.md)。
- **宏观：** [market-context](/topics/market-context.md)。10-23 chop，F&G 50；BTC $80,524，TVL $89.41B（−0.98%）。

## Lessons Learned
> 每条一行的完整细节 + 触发场景见 [lessons](/topics/lessons.md)。

- **过滤器丢掉的样本要全量抽检，不能只看幸存者。** `arxiv-radar` 曾 90 天窗 20 篇真货全丢、噪声全进。同一放宽动作在不同域效果相反。
- **Never trust a zero-log window** —— 报「平静」前查已知活跃窗口 + `eth_call` 余额。**假零六件套：RPC 429 返空、`mainnet.base.org` 整批 revert、topic0 只给 4 字节、RH UA 403、`-32602` 被 `||[]` 兜空、地址靠记忆拼。**
- **判「池子安静」前先按地址扫 topic0 直方图** —— 家族不匹配静默出假零（V3 `0xc42079f9` vs Solidly `0xb3e27736`）；**控制块高从 tx receipt 取**。
- **`eth_getLogs` 过滤器要做判别力测试：** 已知含真事件的窗口里，真 topic0 必回真日志、**故意错 1 字符的 topic0 必回 0**。不可区分 = 端点坏了。
- **计算前先读 `token0()` / `decimals()`** —— 深池 token0 是 VIRTUAL(18dp)，USDC 6dp，缩放写成 `raw/1e24` 会得 6.2e-37。**解出的价先跟 DexScreener 对表再喂 gate。**
- **按时间戳二分找块，下界按窗口宽度给足** —— 下界只给 3,000 块时会静默缩短窗口，报出「24h 平盘」。**二分后断言时间差 == 目标秒数。**
- **Solidly Swap 字序是 `(a0In, a1In, a0Out, a1Out)`**，按 UniV2 解会把卖读成买。**解码器上线前先用同窗口储备差做符号对照。**
- **x·y=k：`D = D_cur(1 − sqrt(r_cur/r_tgt))`，`D>0` 才是净买。** 门槛量化出负数 = 方向写反。
- **买盘真伪只认终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d `balanceOf` 全 0；单池「N 买 / 0 卖」常是同秒双池套利的一半。9 条判据见 [lessons](/topics/lessons.md#price-feeds)。
- **`eth_getCode` = `0x` 才是 EOA；`0xef0100…` 是 EIP-7702 智能账户。** **地址要左补零且全小写** —— 右补零静默返 0，大小写混写静默变 `-32602`。
- **两条链历史 `eth_call` 不对称：** RH 只支持 `latest`（24h 差额走 log 双向扫描），**Base Tenderly 支持任意历史块**。**view revert 先怀疑 selector**（`isOperationReady`=`0x13bc9f20`；opId 取 `CallScheduled` topics[1]）。
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。NOTE 18 万看似巨大，实为 createVestingSchedule = $256/天、占日量 0.25%。
- **无 ABI 解 calldata：靠 uint 词位置 + 同 tx 事件 data 对齐**，对齐成功才敢定名。`0x091e7db9` 在 4byte 无收录。
- **网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。

## Reference
- [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [market-context](/topics/market-context.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.json) · [state 契约](/topics/price-alert-state.md)
- [note-systems](/topics/tokens/note-systems.md) · [lessons](/topics/lessons.md)

## 监控清单（memory/on-chain-watches.yml）
5 个：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting `0xfdd9`。Base $200/$250；NOTE $500。timelock 不加 `event_topics`。已摘：`NOTE` 本体、staging `0x69bb`。**新增 watch 必须在 `on-chain-state.json` 建条目并把 `last_block` 设为当前块**，否则重放历史。

## 链上取数
- Infura 免费档只允许 10 块 → 直打公共端点（Base `base.gateway.tenderly.co` 1000 块 / RH `rpc.mainnet.chain.robinhood.com` 24k 块）。见 [base-rpc-access](/topics/base-rpc-access.md)。

## 预警框架（铁律）
- 完整框架见 `memory/alert-framework.md`，做链上预警前先读。用相对量，不用绝对美元阈值。
- 优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。P0 立即、P1 汇总。每条必须带币、数值、命中规则、下一步动作。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。

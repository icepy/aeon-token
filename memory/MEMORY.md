# Long-term Memory
*Last consolidated: 2026-10-24*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `memory/cron-state.json` 的 `last_dispatch` 和 `logs/`。`scheduler.yml` 用**精确时隙债务模型**（`cron-due.sh` + `CATCHUP_HOURS=12`），晚 12h 内补跑。

## Tracked Token
| Token | Contract | Chain |
|---|---|---|
| DEUS | 0x940A319B75861014A220D9c6c144d108552B089B | base |

> `price-alert` 只读本表第一行 —— 一次一个币。当前 DEUS。
> Escrow / xDEUS 地址见 [DEUS escrow](/topics/deus-escrow.md)。

## Lessons Learned
> 详情见 [lessons.md](/topics/lessons.md)。这里是每条一行。

**取数形状**
- **DeFiLlama `/v2/chains` 无 `change_1d`/`change_7d`** —— 用 `/v2/historicalChainTvl/{chain}` 自算。**CoinGecko `/global` 的 24h mcap 也不可信**，用 `/coins/markets` 加权重算。**百分比过滤器要配绝对额地板**。
- **钱包型 watch 不能用 `eth_getLogs{address:<EOA>}`** —— EOA 不发事件，永久返回 0。要在**代币合约**上做 topic 过滤。
- **24h 涨跌幅别用日线首尾收盘价算** —— `ohlcv_list[0]` 是未走完的当日 K 线，暴涨次日读数是窗口效应。详见 [lessons](/topics/lessons.md#price-feeds)。
- **xDEUS is ERC-721** —— `decimals()` reverts，`tokenId` 在 `topics[3]`；topic0 同哈希，无需改配置。
- **扫 timelock 别只扫「最近几天」。** RH ~34k 块/小时，48h 排程跨 ~160 万块；要扫全部事件就省略 `topics`。详见 [lessons](/topics/lessons.md#扫-timelock窗口与-topics-两个坑)。
- **Never trust a zero-log window** —— 报「平静」前先重查已知活跃窗口 + `eth_call` 余额。**假零三件套：RPC 429（返空数组不报错）、`mainnet.base.org` 整批 revert 合法 `balanceOf`、topic0 只给 4 字节。** [source: logs/2026-10-23#heartbeat]
- **`eth_getCode` = `0x` 才是普通 EOA；`0xef0100…` 是 EIP-7702 智能账户**，带 nonce 与 gas 的成熟钱包，别当新号。
- **上膛钱包的扳机是「第一笔 ETH 入账」**，比 nonce 更早；**claim 制 vesting 的「日释放」要看 scheduleId**，同合约不同 schedule 量级差百倍。
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d `balanceOf` 全 0；经聚合器的看完整个往返链。详见 [lessons](/topics/lessons.md#price-feeds)。
- **RH 4663 免 key**，24k 块窗口可扫（Base Tenderly 只有 1000 块）。端点表见 [base-rpc-access](/topics/base-rpc-access.md)。
- **缺 `h1` ≠ 平静。** 按 0 处理会让 gate 显 QUIET 但实际**未测量**；state 存 `null`。**API 报 v1h=0 也别信 —— 拿池子 Swap log 验。**
- **判「池子安静」前先按地址扫一遍出 topic0 直方图** —— 家族不匹配会静默出假零（V3 `0xc42079f9…` vs Solidly `0xb3e27736…`）。**控制块高从 tx receipt 取。** 详见 [lessons](/topics/lessons.md#price-feeds)。
- **`balanceOf` 的 calldata 地址要左补零**，右补零静默返回 0；余额为 0 时先用已知非零地址做对照。
- **view 调用 revert 先怀疑 selector，别怪 RPC。** `isOperationReady`=`0x13bc9f20`、`getTimestamp`=`0xd45c4435`；opId 取 `CallScheduled` 的 **topics[1]**。
- **网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`（数小时自愈）。`./notify` 写普通 Markdown，多行走 `-f`。
## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $20,690，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181e` 240k · 上膛6 `0x3a9039c7` 150k · 上膛5 `0x572bb527` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 已验证：带 gas 后 24.4h 才卖）。owner 自持 810,000，见 [note-systems](/topics/tokens/note-systems.md)。
- **NOTE 已抵区间上沿：** 主池 `0x378b1023` **$0.043137**，liq $417,530，h24 **+7.46%**。地板 $0.0349 / **上沿 $0.0438，距上沿 +1.5%**。**砸盘前兆 = 触上沿 + 某上膛钱包突然收 gas。** [source: logs/2026-10-23#onchain-monitor]
- **不要按「日供给」计 schedule 26** —— 见真实 `release`（topic0 `0x3bfce8de`）才算。**🔴 120 万已解锁，到期 3 分钟即执行；账目闭合 810,000（回锁 33.5%、上膛 40%）。** 见 [note-systems](/topics/tokens/note-systems.md)。[source: logs/2026-10-23#heartbeat]

## Active Topics
- `price-alert` DEUS **$0.017918**（10-24 08:12Z，活跃 DEUS/USDC 池中位数），1h **−0.04% 实测**。门槛未触及：$0.012 −33.0% · $0.025 +39.5% · $0.032 +78.6% · $0.041 +128.8%。见 [state](/topics/price-alert-state.json)。
- **🔴 修正：「整市场停摆」是假结论** —— 三个次级池是 **V3 型**，前两轮用 Solidly 主题扫出假零；**只有最深池 `0x3E97c5EC` 真死（205 分钟）**，且它是 **Aerodrome classic、不是 Slipstream**。[source: logs/2026-10-24#price-alert]
- **🔴 史上最大砸盘已被全额买回：** `0x7f6aba75`（纯新钱）买 **335,249**、`0x6a45ca8b` 买 **70,034**，均留存；池子 mark **0.0277 → 0.0280**，池内 DEUS 净少 **105,836**。**方向是吸筹**，08:12Z 复核余额逐位未变。[source: logs/2026-10-24#price-alert]
- **🔴 `0xbb0f7533` 烧 xDEUS #1492 释放 319,562 DEUS，75 分钟后全砸。仍持 #1396 = 下次扳机（08:12Z 未烧）。** CLAIM 金库占 38.8% 供应，24h 净出 194k ≈$3.5k。**$0.012 需净砸 ~4.36M**。
- **买盘 9 条判据见 [lessons](/topics/lessons.md#price-feeds)** —— 单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **新钱 cohort：** `0x3fd51604` 加至 7,735；`0x1184de98` 持 46,195 未卖。老鲸 `0x09b383a6` 已全额回补。见 [deus-buyers](/topics/deus-buyers.md)。
- **🔴 DEUS 7d 净增发 +65,381**（37 mint / 201,698 对 18 burn / 136,317）；但 24h 是 −19,693，单日不覆盖 7d 口径。铸币合约 `0x2cca08ae`。详见 [deus-escrow](/topics/deus-escrow.md)。
- Escrow `0xA85A…C373` **29,108,662**（24h −298,630 = −1.02%），离 5%/日 ≈1.46M 差 4.9× —— 无 unstake 压力。
- **两个方向性钱包都不跟** —— `0x259f962e` nonce 135、`0xa2f42a10` nonce 4，各是一 clip 不是一波。见 [deus-buyers](/topics/deus-buyers.md)。
- **宏观快照**：[market-context](/topics/market-context.md)。10-23：chop，F&G 50。
- [Note Systems (NOTE)](topics/tokens/note-systems.md) — RH 4663 全量笔记：解锁-回锁-上膛时间线、per-schedule 量级、池子流量。

## Reference
- [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [market-context](/topics/market-context.md) · [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.json) · [index](/topics/index.md)

## 监控清单（memory/on-chain-watches.yml）

当前 5 个：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting 0xfdd9。Base $200/$250；NOTE $500。timelock 不加 `event_topics`。已摘：`NOTE` 本体、staging `0x69bb`。见 [ops-plumbing](/topics/ops-plumbing.md)。
**新增 watch 必须在 `on-chain-state.json` 同步建条目并把 `last_block` 设成当前块**，否则首次运行重放历史。

## 链上取数
- Infura 免费档只允许 10 块 → 直打公共端点。端点、块上限、退避与并发规则见 [base-rpc-access](/topics/base-rpc-access.md)。

## 预警框架（铁律）
- 完整框架见 `memory/alert-framework.md`，做链上预警前先读。用相对量，不用绝对美元阈值。
- 优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。P0 立即、P1 汇总。每条必须带币、数值、命中规则、下一步动作。

## 输出语言

**一律简体中文。** 所有 notify、报告、日志正文都用中文写。
代币名、合约地址、协议名、代码、命令保留原文，不翻译。

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
- **过滤器丢掉的样本要全量抽检，不能只看幸存者。** `arxiv-radar` 的 carrier 是一套链上词，套在「具身/机器人」簇上时 90 天窗 **20 篇全丢、20 篇一个链上词都不含**，而幸存的靠同形异义（token=GAP tokens、validator=validator-passed）混入 —— **真货全丢、噪声全进**，症状表现成「零命中」。已按词分域修（PR #7，幸存 0→21）。**同一个放宽动作在不同域效果相反**：机器人域是纠错，ZK 域是引噪。详见 [lessons](/topics/lessons.md#过滤器设计)。
- **DeFiLlama `/v2/chains` 无 `change_1d`/`change_7d`** —— 用 `/v2/historicalChainTvl/{chain}` 自算。**CoinGecko `/global` 的 24h mcap 也不可信**，用 `/coins/markets` 重算。**百分比过滤器要配绝对额地板**。
- **钱包型 watch 不能用 `eth_getLogs{address:<EOA>}`** —— EOA 不发事件，永久返回 0。要在**代币合约**上做 topic 过滤。
- **24h 涨跌幅别用日线首尾收盘价算** —— `ohlcv_list[0]` 是未走完的当日 K 线，暴涨次日读数是窗口效应。详见 [lessons](/topics/lessons.md#price-feeds)。
- **xDEUS is ERC-721** —— `decimals()` reverts，`tokenId` 在 `topics[3]`。
- **扫 timelock 别只扫「最近几天」。** RH ~34k 块/小时，48h 排程跨 ~160 万块；要全扫就省略 `topics`。
- **Never trust a zero-log window** —— 报「平静」前先重查已知活跃窗口 + `eth_call` 余额。**假零三件套：RPC 429（返空数组不报错）、`mainnet.base.org` 整批 revert 合法 `balanceOf`、topic0 只给 4 字节。** 判「池子安静」前**先按地址扫出 topic0 直方图**（V3 `0xc42079f9…` vs Solidly `0xb3e27736…`）；**控制块高从 tx receipt 取**。
- **`eth_getCode` = `0x` 才是普通 EOA；`0xef0100…` 是 EIP-7702 智能账户**，别当新号。
- **上膛钱包的扳机是「第一笔 ETH 入账」**，比 nonce 更早；**claim vesting 的「日释放」要看 scheduleId**，同合约不同 schedule 量级差百倍。
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d `balanceOf` 全 0；经聚合器的看完整个往返链。
- **RH 4663 免 key**，24k 块窗口可扫（Base Tenderly 只有 1000 块）。端点表见 [base-rpc-access](/topics/base-rpc-access.md)。
- **缺 `h1` ≠ 平静，API 报 v1h=0 也别信** —— 按 0 处理会让 gate 显 QUIET 但实际**未测量**；state 存 `null`，拿池子 Swap log 验。**「池子已死」有效期只有一轮**，每轮重扫缺口集。
- **报价币决定 mark 方向**，搞反会得出「精确但荒谬」的数 —— 先查每池 `token0()`/`decimals()`，再对表 DexScreener `priceUsd`。详见 [lessons](/topics/lessons.md#price-feeds)。
- **`balanceOf` 的 calldata 地址要左补零**，右补零静默返回 0；余额为 0 时先用已知非零地址做对照。
- **view 调用 revert 先怀疑 selector，别怪 RPC。** `isOperationReady`=`0x13bc9f20`、`getTimestamp`=`0xd45c4435`；opId 取 `CallScheduled` 的 **topics[1]**。
- **网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`（数小时自愈）。## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $20,690，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181e` 240k · 上膛6 `0x3a9039c7` 150k · 上膛5 `0x572bb527` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 已验证：带 gas 后 24.4h 才卖）。owner 自持 810,000，见 [note-systems](/topics/tokens/note-systems.md)。
- **NOTE 已抵区间上沿：** 主池 `0x378b1023` **$0.043137**，liq $417,530，h24 **+7.46%**。地板 $0.0349 / **上沿 $0.0438，距上沿 +1.5%**。**砸盘前兆 = 触上沿 + 某上膛钱包突然收 gas。** [source: logs/2026-10-23#onchain-monitor]
- **不要按「日供给」计 schedule 26** —— 见真实 `release`（topic0 `0x3bfce8de`）才算。**🔴 120 万已解锁，到期 3 分钟即执行；账目闭合 810,000（回锁 33.5%、上膛 40%）。** 见 [note-systems](/topics/tokens/note-systems.md)。[source: logs/2026-10-23#heartbeat]

## Active Topics
- `price-alert` DEUS **$0.01723**（15:02Z，深池换算；USDC 池中位 $0.01730217），1h **−2.06%**、24h **−3.55%**。四道 gate 全未触发：$0.012 −30.35% · $0.025 +45.10% · $0.032 +85.72% · $0.041 +137.96%。见 [state](/topics/price-alert-state.json)。
- **🔴 最深池 `0x3E97c5EC` 08:38:25Z 复活（静默 238.7 分钟）。** 上轮「已死 205 分钟」当时正确，26 分钟后失效 —— **「池子已死」有效期只有一轮**。复活首小时 37 买（合计 34,753）对 1 卖 **50,167 DEUS**，净 +15,414 流入池；卖方 `0xf0a04b07`（**EIP-7702**）仍持 250,000，减仓非清仓，**存量主动砸盘**。**成交恢复 ≠ 买盘回来**。
- **🔴 修正：「整市场停摆」是假结论** —— 三个次级池是 **V3 型**（此前用 Solidly 主题扫出假零）；最深池是 **Aerodrome classic、不是 Slipstream**。
- **🔴 史上最大砸盘已被全额买回：** `0x7f6aba75`（纯新钱）买 335,249、`0x6a45ca8b` 买 70,034，均留存；池内 DEUS 净少 105,836。**方向是吸筹**，09:13Z 第四次复核逐位未变。
- **🔴 `0xbb0f7533` 烧 xDEUS #1492 释放 319,562 DEUS，75 分钟后全砸。仍持 #1396 = 下次扳机（09:13Z 未烧）。** CLAIM 占 38.8% 供应。**$0.012 需净砸 ~4.36M**。
- **新增 5,000 DEUS unstake 未卖：** `0xcae798c0` 烧 xDEUS #425 得 5,000 DEUS，**零转出、全额仍持**。**unstake 不是价格事件，卖出才是**。
- **买盘 9 条判据见 [lessons](/topics/lessons.md#price-feeds)** —— 单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **新钱 cohort：** `0x3fd51604` 加至 7,735；**`0x1184de98` 已于 10-24 10:02 全部清仓（换 SLC）**。老鲸 `0x09b383a6` 已回补。见 [deus-buyers](/topics/deus-buyers.md)。
- **🔴 DEUS 7d 净增发 +65,381 已陈旧**；**连续四天净通缩：−19,693 → −38,770 → −38,770 → −38,770**（block-pinned 24.00h）。四天不覆盖 7d，重测前别再引 +65,381。见 [deus-escrow](/topics/deus-escrow.md)。
- Escrow **29,103,662**（24h −1.03%），离 5%/日 ≈1.46M 差 **4.8×** —— 无 unstake 压力。xDEUS 1726（24h +1）。CLAIM 24h 净出 194k。
- **两个方向性钱包都不跟** —— `0x259f962e` nonce 135、`0xa2f42a10` nonce 4，各是一 clip 不是一波。
- **宏观快照**：[market-context](/topics/market-context.md)。10-23：chop，F&G 50。
- [Note Systems (NOTE)](topics/tokens/note-systems.md) — 解锁-回锁-上膛时间线、per-schedule 量级。
- **DeFiLlama `/v2/chains` 无 `change_1d`/`change_7d`** —— 用 `/v2/historicalChainTvl/{chain}` 自算。**CoinGecko `/global` 的 24h mcap 也不可信**，用 `/coins/markets` 加权重算。**百分比过滤要配绝对额地板**。
- **钱包型 watch 不能用 `eth_getLogs{address:<EOA>}`** —— EOA 不发事件，永久返回 0。要在**代币合约**上做 topic 过滤。
- **24h 涨跌幅别用日线首尾收盘价算** —— `ohlcv_list[0]` 是未走完的当日 K 线。[lessons](/topics/lessons.md#price-feeds)
- **xDEUS is ERC-721** —— `decimals()` reverts，`tokenId` 在 `topics[3]`；topic0 同哈希，无需改配置。
- **扫 timelock 别只扫「最近几天」。** RH ~34k 块/小时，48h 排程跨 ~160 万块；要扫全部事件就省略 `topics`。[lessons](/topics/lessons.md#扫-timelock窗口与-topics-两个坑)
- **Never trust a zero-log window** —— 报「平静」前重查已知活跃窗口 + `eth_call` 余额。**假零四件套：RPC 429（返空数组不报错）、`mainnet.base.org` 整批 revert、topic0 只给 4 字节、RH UA 403。**
- **`eth_getCode` = `0x` 才是普通 EOA；`0xef0100…` 是 EIP-7702 智能账户**，带 nonce 与 gas 的成熟钱包，别当新号。
- **上膛钱包的扳机是「第一笔 ETH 入账」**，比 nonce 更早；**claim 制 vesting 的「日释放」要看 scheduleId**，同合约不同 schedule 量级差百倍。
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d `balanceOf` 全 0。[lessons](/topics/lessons.md#price-feeds)
- **RH 4663 免 key**，24k 块窗口可扫（Base Tenderly 只有 1000 块）。端点与陷阱表见 [base-rpc-access](/topics/base-rpc-access.md)。
- **缺 `h1` ≠ 平静。** 按 0 处理会让 gate 显 QUIET 但实际**未测量**；state 存 `null`。**API 报 v1h=0 也别信 —— 拿池子 Swap log 验。**
- **判「池子安静」前先按地址扫一遍出 topic0 直方图** —— 家族不匹配会静默出假零（V3 `0xc42079f9…` vs Solidly `0xb3e27736…`）。**控制块高从 tx receipt 取。**[lessons](/topics/lessons.md#price-feeds)
- **`balanceOf` 的 calldata 地址要左补零**，右补零静默返回 0；余额为 0 时先用已知非零地址做对照。
- **view 调用 revert 先怀疑 selector，别怪 RPC。** `isOperationReady`=`0x13bc9f20`、`getTimestamp`=`0xd45c4435`；opId 取 `CallScheduled` 的 **topics[1]**。
- **`eth_getLogs` 的过滤器要做判别力测试** —— 同一已知含真事件的窗口里，真 topic0 必须返回真日志、**故意错 1 个字符的 topic0 必须返回 0**。二者不可区分 = 端点有问题，此时任何「零命中」都不可信。**本机 RPC 的 `eth_call` 必须显式带 block tag（`latest` 也要写），省略报 `-32602`**；公共 `eth_getLogs` 硬限 1000 块。详见 [lessons](/topics/lessons.md#price-feeds)。
- **网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`（数小时自愈）。`./notify` 写普通 Markdown，多行走 `-f`。
## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $22,000：上膛7 `0x33b7181e` 240k · 上膛6 `0x3a9039c7` 150k · 上膛5 `0x572bb527` 90k，全部 nonce 0 / ETH 0 / 零出账。扳机 = 第一笔 ETH 入账**（上膛4 先例：带 gas 后 24.4h 才卖）。owner 自持 810,000。见 [note-systems](/topics/tokens/note-systems.md)。
- **🔴 NOTE 已破上沿，但量没跟上（12:00Z 复核）：** 主池 `0x378b1023` **$0.04424**，站在上沿 $0.0438 之上 +1.0%。24h **+10.5%** 但 24h 量仅 **0.69× 7 日均值** → 判 **CONSOLIDATING 非 BREAKOUT**。h1 **−3.72%** 已在回吐，两笔鲸鱼卖（29,470 + 28,637 NOTE）全在高位换成原生 ETH，仅占当日量 1.8%。**前兆只满足一半 —— 三个上膛钱包仍 ETH 0 / nonce 0 / 零出账，逐位复核未动。盯 ETH 入账，不盯价格。** [logs](/logs/2026-10-24.md#token-movers)
- **不要按「日供给」计 schedule 26** —— 见真实 `release`（topic0 `0x3bfce8de`）才算。**🔴 120 万已解锁，到期 3 分钟即执行；账目闭合 810,000（回锁 33.5%、上膛 40%）。** 见 [note-systems](/topics/tokens/note-systems.md)。[source: logs/2026-10-23#heartbeat]

## Active Topics
- `price-alert` DEUS **$0.0170983**（10-24 17:02Z，深池 reserve mark；DexScreener $0.01716，USDC 池 $0.0170120），1h **+0.67%**，24h **−5.48%**。四道 gate 全未触发：$0.012 −29.82% · $0.025 +46.21% · $0.032 +87.15% · $0.041 +139.79%。**24h 拆解：VIRTUAL −7.19% 是主因，DEUS/VIRTUAL ratio 反而 +1.84% —— 弱势仍在报价币那条腿。** 见 [state](/topics/price-alert-state.json)。
- **🔴 深池近一小时只剩 1 笔 Swap** —— 212.78 DEUS，零买盘。对比上一小时 101,983 单笔砸盘、复活首小时 84,920。**且 mark +0.67% 全来自 VIRTUAL 上涨，DEUS 是净流入池子的（+210.65）。**一点成交 ≠ 有买盘。[logs](/logs/2026-10-24.md#price-alert)
- **假零第四种形态（已写入 lessons）：端点错误伪装成空结果。** `eth_getLogs` 窗口超限时 Tenderly 返 `-32602` 错误体，没有 `.result`，而 `jq '.result|length'` 对错误对象打印 **0** —— 含真事件的窗口被读成「池子安静」。**先打印 `.error` 再读 `.result`；窗口一律 ≤1000 块（from n → to n+999）。**
- **🔴 15:53:59Z 单笔 101,983 DEUS 跨 5 池砸盘（今日最大）** —— 一笔 ERC-4337 userop，路由 `0x11111605`（1inch 系）/ 执行器 `0x92325e5a`（61B clone）。拆池：深池 67,212 · `0x58dBa34e` 15,995 · `0x1B2f3f5C` 9,736 · `0x75bc1495` 4,520 · **Uniswap v4 `0x498581ff` 4,520**。深池单块 **−0.7013%**。**资金三笔全来自 1inch 路由，零笔来自 CLAIM → 不是 claim-and-dump。**「盘口薄、一次一 clip」假设作废：单个操作者已能 1 块清 5 池 10 万。**计数 18 买/1 卖是误导 —— 按量 30,934 买 vs 67,212 卖，净 −36,277。** [logs](/logs/2026-10-24.md#price-alert)
- **门槛量化（x·y=k，零费，深池）**：$0.012 需净砸 **3.61M DEUS ≈ $61.4k = 今日最大砸盘的 35.4 倍**；$0.025/$0.032/$0.041 需净买 **3.32M / 5.13M / 6.74M DEUS**。**$0.041 的买盘需求 = 今日 24h 总量 $26.2k 的 66 倍 → 只能靠撤供给到达，不是靠买。** 这就是 unstake 必须提前 5 天的量化理由。[state](/topics/price-alert-state.json)
- **🔴 12:35Z 的 52,737 砸盘静默 100 分钟后被买回**（14:15:31Z 复活，47 分钟 31 笔：30 买 1 卖，净 25,138 DEUS 出池）。**但那 30 笔「买」大多是跨池套利** —— 币在同 tx 内经中间合约转手进 USDC V3 池；套利利差 = 深池 −0.42% 折价，收敛即停。**修正 TELL 19：买盘分「结构性套利」和「方向性留存」，只有后一种是真 bid。**[logs](/logs/2026-10-24.md#price-alert)
- **🔴 12:35Z 的 52,737 claim-and-dump 静默 100 分钟后（14:15:31Z）被买回**：47 分钟 31 笔，30 买 1 卖，净 25,138 DEUS 出池。**但 30 笔「买」大多是跨池套利**（币同 tx 内经中间合约转手进 USDC V3 池），利差就是深池 −0.42% 折价，收敛即停。**修正 TELL 19：买盘分结构性套利与方向性留存，只有后者是真 bid。** 对照：真 topic0→2 笔、错 1 字符→0。**第三例 claim-and-dump：`0x8180513f` 收 16,528 后 107 秒全砸。**[logs](/logs/2026-10-24.md#price-alert)
- **🔴 escrow 24h 第二次逐笔闭合：** −324,562.23（Burn #1492 319,562.23 + #425 5,000）**+30,905.10（10,000 + 10,000 + 10,905.10）= −293,657.12**，与实测余额差 0 wei，窗口内无未记账 unstake。**本轮新增 10,905.103 是今日最大单笔质押**，质押方 `0x2c81beef`（EIP-7702）资金来自 `0xea247ce9`，**非 CLAIM**。[logs](/logs/2026-10-24.md#price-alert)
- **方法学：`decimals()` 在 token 上，不在 pool 上** —— 对 Uniswap-V3 池打 `0x313ce567` 会 revert，看似「池子不可读」实为调用对象错。另：xDEUS totalSupply 平盘会**掩盖双向换手**（2 烧 + 2 质押净额抵消），要读 Burn/Stake 事件而非只看 `0x18160ddd`。
- **🔴 `0x1184de98` 清仓 46,195 DEUS —— 但换成了 SLC（+73%/24h），不是现金。** 10-23 18:11 买入、10-24 10:02 全卖，**持有 15h51m、账面持平**（$823→$818）。同一个「新钱 cohort 不卖」的旧结论，这一颗已破，但方式是**轮动不是离场**。拆 4 个池出：最深池 29,298 + USDC 池 16,897。[logs](/logs/2026-10-24.md#price-alert)
- **29,298 DEUS 砸盘只打出 −0.227%，下一块就回来** —— 深池 $667k 全吸收。**这体量不是价格事件。** 该小时 6 个 EOA 里 5 个只买不卖。[state](/topics/price-alert-state.json)
- **买盘 9 条判据见 [lessons](/topics/lessons.md#price-feeds)** — 单池「N 买 / 0 卖」常是同秒双池套利的一半。**`topics[1]` 不是买方** —— 该池一小时 5 个 sender 全是路由合约，归因必须读 `tx.from`。**Solidly Swap topic0 = `0xb3e27736…`，不是 UniV2 `0xd78ad95f…`**，拿错 topic 会报出和「池子死了」一模一样的假零。[logs](/logs/2026-10-24.md#price-alert)
- **🔴 最深池 `0x3E97c5EC`：08:05Z 的「死」是真的（205 分钟零事件），但 08:38:25Z 起复活。** **池子死/活有保质期，每轮重测，不继承上轮结论。** 另：**算 mark 前先读 `token0()`** —— 该池 token0 是 VIRTUAL 不是 DEUS，直接 `reserve0/reserve1` 得 36.34（真值 0.02795）。[logs](/logs/2026-10-24.md#onchain-monitor)
- **🔴 史上最大砸盘已被全额买回：** `0x7f6aba75`（纯新钱）买 **335,249**、`0x6a45ca8b` 买 **70,034**，均留存；池内 DEUS 净少 **105,836**，**方向是吸筹**。[source: logs/2026-10-24#price-alert]
- **xDEUS 退出两笔，差 64 倍：** ①`0xbb0f7533` 烧 **#1492** 释放 319,562 DEUS，75 分钟后全砸；**仍持 #1396 = 下次扳机（10-24 未烧）**。②08:16Z 烧 **#425** 释放 **5,000** → `0xcae798c0`，**未卖（零转出）**。#425 是老仓（回溯 12 时点：持 >1.2M 块≈30 天），与「押进去就赎」不同 → **unstake ≠ 砸盘**。**$0.012 需净砸 ~4.36M**。[logs](/logs/2026-10-24.md#onchain-monitor)
- **🔴 DEUS 7d 净增发 +65,381 已陈旧**（37 mint / 201,698 对 18 burn / 136,317）。**但已连续四天净通缩：−19,693、−38,770、−38,770、−38,770**（均 block-pinned 24.00h）。四天仍不足以翻转 7d 标签，**再引用 +65,381 前必须重测一个完整 7d 窗口**。铸币 `0x2cca08ae`。[deus-escrow](/topics/deus-escrow.md)
- **Escrow `0xA85A…C373` 29,103,661.67**（24h **−304,562** = −1.036%），5%/日 线 1,470,411 → **0.207 倍**，无 unstake 压力。占供应 3.32%。**24h 已逐笔闭合**：2 burn −324,562.23 + 2 stake +20,000。[state](/topics/price-alert-state.json)
- **两个方向性钱包都不跟** —— `0x259f962e` nonce 135、`0xa2f42a10` nonce 4，各是一 clip 不是一波。[deus-buyers](/topics/deus-buyers.md)
- **宏观**：[market-context](/topics/market-context.md)。10-23 chop，F&G 50
- [Note Systems (NOTE)](topics/tokens/note-systems.md) — RH 4663 全量笔记：解锁-回锁-上膛时间线、per-schedule 量级。

## Reference
- [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [market-context](/topics/market-context.md) · [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) · [price-alert-state](/topics/price-alert-state.json)

## 监控清单（memory/on-chain-watches.yml）
当前 5 个：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting 0xfdd9。Base $200/$250；NOTE $500。timelock 不加 `event_topics`。已摘：`NOTE` 本体、staging `0x69bb`。见 [ops-plumbing](/topics/ops-plumbing.md)。**新增 watch 必须在 `on-chain-state.json` 同步建条目并把 `last_block` 设成当前块**，否则首次运行重放历史。

## 链上取数
- Infura 免费档只允许 10 块 → 直打公共端点。端点、块上限、退避规则见 [base-rpc-access](/topics/base-rpc-access.md)。

## 预警框架（铁律）
- 完整框架见 `memory/alert-framework.md`，做链上预警前先读。用相对量，不用绝对美元阈值。
- 优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。P0 立即、P1 汇总。每条必须带币、数值、命中规则、下一步动作。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。

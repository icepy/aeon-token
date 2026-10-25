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
- **DEUS 四道 gate 全未触发：** $0.012 −30.84% · $0.025 +44.09% · $0.032 +84.44% · $0.041 +136.31%。**$0.041 需净买 6.61M DEUS ≈ 深池 24h 量（$13,495）的 424 倍 → 只能靠撤供给到达。这就是 unstake 必须提前 5 天的量化理由。**[source: logs/2026-10-25#price-alert]
## Active Topics
- `price-alert` DEUS **$0.01735**（10-25 03:08Z DexScreener 深池 mark；链上储备 mark $0.0173918），1h **未测量**（h1=null，深池 58 分钟零成交），24h **−4.10%**。四道 gate 全未触发。见 [state](/topics/price-alert-state.json)。
- **🔴 深池 03:02Z 前 80 分钟零成交，第二个死寂小时 —— 上轮「首个净买小时」没有延续。** USDC 四池同期仅 2 笔、合计 **$2.15**，且方向是卖。**单小时净流出不足以定方向。**
- **🔴 24h 方向符号翻转：** DEUS 在池内 **+88,687 净流入**（上轮同期是 −28,566 流出）。**「池子收紧 = 吸筹」本轮不成立** —— 跌幅全部来自 DEUS 进池（比值 −0.934%）+ 引腿 VIRTUAL −2.92%。
- **溢价 +0.18%（02:05Z 是 +0.62%）：蒸发式收敛** —— 两边都没量，不是套利出力。
- **🔴 死寂一小时结束，首个净买小时：** 深池 6 笔，1 买 76,803 出池 / 5 卖 13,126 进池 → **净 −63,677 DEUS 出池**。
- **🔴 最大买单是合约囤货：** 111,385 DEUS 跨五场所 → 中转 `0x7d683941` 恒 0 → **执行器 `0x92325e5a` 0→118,288 且零转出**，付款 EOA 全程 0。**同一合约昨天砸 101,983 —— 盯它转出 = 下一根 −0.7%~−0.9%。**
- **卖压由 8.07M 批发商供弹：** 卖家 `0x96949fd5` 三笔逐 wei 相同（切片），钱来自 `0x4e3ae00e`（8,070,712 DEUS = 供应 0.92%，每天放 ~5 万）。**节奏由批发商定，不由卖方库存定。**
- **Escrow 连续第七轮逐 wei 闭合：** 29,150,566.777698，本小时 0 事件，24h **+41,905.10** = 5%/日线的 **0.029 倍**。**`0xbb0f7533` 仍持 #1396，连续第八轮未烧。**
- **🔴 本小时单向砸盘 92,548.73 DEUS、10 卖 0 买 —— 但 mark 只跌 0.23%。** 卖方是 18 天的 `0x8cd54fbd` 全清 55.1k、老鲸 `0x09b383a6` 减 0.28%（仍持 2.16M）、`0x96949fd5` 一周获利 5.8k、`0x49a782c2` 减 5.9k（仍持 34.2k）。**四个大持有者逐 wei 未动 —— 卖压来自小仓位不是鲸鱼。**
- **⚠️ Escrow 首次净流入：24h +51,905.10（+0.178%），逐 wei 闭合（−5,000 burn + 56,905 三笔 stake）。** 对 5%/日线仅 **0.036 倍**，质押压力实际为零。总供应 24h **−12,857.94**，通缩明显减速。**`0xbb0f7533` 仍持 #1396，连续第六轮未烧。**
- **🔴 第四次 claim-and-dump，且首次跨两场所拆分：** `0xd1a7ba72`（EIP-7702）100 秒内收 3,529.86 三腿（分发器 + CLAIM 代理 + `0x0ae95bd7`），走 `0x11111605` 拆 **2,426.78 进深池 + 1,103.08 进 USDC `0x58dBa34e`**，余额逐 wei 归零。**单池卖单计数会低估单一操作者的供给 —— 归因必须按 `tx.from` 汇总同 tx 全部场所。**
- **🔴 本小时 tape 翻回单向卖出：10 卖 0 买、92,548.73 DEUS 进池（上轮 2,427，38×）—— 但 mark 只跌 0.23%。** 方向性卖家 86,539.48（93.5%）按 `tx.from` 归因：18 天的 `0x8cd54fbd` 全清 55.1k、`0x4e1e354f` 经 4337 全出 13.8k（两笔都 −30d 或 −1h..−7d 逐 wei 不动）、老鲸 `0x09b383a6` 减 0.28%（仍持 2.16M）、`0x96949fd5` 一周获利 5.8k。**四个大持有者逐 wei 未动 —— 卖压来自小/老仓位，不是鲸鱼。溢价第五小时继续收窄 +0.94% → +0.61%，仍是分母在动。**
- **四个大持有者连续两小时逐 wei 未动：** 335,249.499443 · 70,034.140337 · 250,000.125225 · 284,371.457830。**92.5k 卖压全来自更小的仓位 —— 存量巨鲸无主动砸盘。**
- **🔴 最深池 `0x3E97c5EC` 08:38:25Z 复活（静默 238.7 分钟）。** 上轮「已死 205 分钟」当时正确，26 分钟后失效 —— **「池子已死」有效期只有一轮**。复活首小时 37 买（合计 34,753）对 1 卖 **50,167 DEUS**，净 +15,414 流入池；卖方 `0xf0a04b07`（**EIP-7702**）仍持 250,000，减仓非清仓，**存量主动砸盘**。**成交恢复 ≠ 买盘回来**。
- **🔴 修正：「整市场停摆」是假结论** —— 三个次级池是 **V3 型**（此前用 Solidly 主题扫出假零）；最深池是 **Aerodrome classic、不是 Slipstream**。
- **🔴 史上最大砸盘已被全额买回：** `0x7f6aba75`（纯新钱）买 335,249、`0x6a45ca8b` 买 70,034，均留存；池内 DEUS 净少 105,836。**方向是吸筹**，09:13Z 第四次复核逐位未变。
- **🔴 `0xbb0f7533` 烧 xDEUS #1492 释放 319,562 DEUS，75 分钟后全砸。仍持 #1396 = 下次扳机（22:02Z 复核仍未烧，连续第五轮）。** CLAIM 占 38.79% 供应。**$0.012 需净砸 ~3.81M**。
- **新增 5,000 DEUS unstake 未卖：** `0xcae798c0` 烧 xDEUS #425 得 5,000 DEUS，**零转出、全额仍持**。**unstake 不是价格事件，卖出才是**。
- **跨场所扫货必须跟到终点合约。** 中转余额恒 0 + 执行器吸满且零转出 = 合约囤货（可能是 MM 存货）；付款 EOA 收币留存才是判据 8 的真新钱。只看 swap 侧会把囤货误读成机构吸筹。
- **同尺寸重复卖单是切片信号。** 三笔逐 wei 相同的卖单顺着资金上游能找到批发商（本轮 `0x4e3ae00e` 持 8.07M），比数笔数有用得多。
- **买盘 9 条判据见 [lessons](/topics/lessons.md#price-feeds)** —— 单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **新钱 cohort：** `0x3fd51604` 加至 7,735；**`0x1184de98` 已于 10-24 10:02 全部清仓（换 SLC）**。老鲸 `0x09b383a6` 已回补。见 [deus-buyers](/topics/deus-buyers.md)。
- **🔴 DEUS 7d 净增发 +65,381 已陈旧**；**连续四天净通缩：−19,693 → −38,770 → −38,770 → −38,770**（block-pinned 24.00h）。四天不覆盖 7d，重测前别再引 +65,381。见 [deus-escrow](/topics/deus-escrow.md)。
- Escrow **29,150,566.78**（24h **−267,657 = −0.910%**，逐 wei 第四次闭合；本小时 Burn 0 笔），对 5%/日线 ≈1.46M 仅 **0.184 倍** —— 无 unstake 压力。xDEUS **1728**（24h +1）。CLAIM 24h 净出 **304,681（记录内最大）**。
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
- **🔴 `github-radar` 农场黑名单从未生效**：`github-farms.txt` 是行内注释格式，解析只跳 `#` 开头的行 → 读到 3 个带注释尾巴的垃圾 key，匹配 0 个 owner，日志却显示 `farm=0`（像「没有农场」）。**读配置的代码必须回读它解析出的 key 集合 —— 空集和没命中长得一样。** 见 [lessons](/topics/lessons.md#过滤器设计)。
- **🔴 `github-radar` 的 `owner≥3=farm` 在误杀活仓**：判掉 `rzc156/dreamforge`(★130/21 提交)、`Roboparty/P-BFM`(★95)、`NEBULIS-Lab/D-JEPA`(★32/68 提交)、`liaohello/GigaWorld-Policy-Sim2Real`(18 提交)。黑名单文件本身写明「3 仓**不够**，要三者同时成立」，代码只实现了第一条。**规则文档与实现要逐条对照。**
- **`github-radar` 的 `commits_30d=100` 是 `per_page` 上限，实为 ≥100**，不可当精确值比大小（本轮 6 仓撞顶）。
## Next Priorities
- **🔴 待命 480,000 NOTE ≈ $20,400，三钱包 nonce 0 / ETH 0 / 零出账：** 上膛7 `0x33b7181ed1540a83281ca053df49ac32019e8731` 240k · 上膛6 `0x3a9039c7069382594f779d95db6686007119f35e` 150k · 上膛5 `0x572bb5272603889f5742e8b8ab2f1d4c6851a93e` 90k。**扳机 = 第一笔 ETH 入账**（上膛4 先例：带 gas 后 24.4h 才卖）。owner 自持 630,000。
- **🔴 NOTE 上沿破而复失（10-24 21:01Z）：** 主池 `0x378b1023` **$0.042599**，liq $410,435，h1 −4.40% / h24 −3.37%，24h 量 $102,753。**$0.0438 防守失败，回落 −2.7%；高点 $0.04657 已回吐 −8.5%。** 12:00Z 判的「CONSOLIDATING 非 BREAKOUT」成立。**盯 ETH 入账，不盯价格。**
- **⚠️ NOTE 供给侧斜率变了：** owner 首次动仓，180,000 进 **schedule #27**（30 天线性）。**#25 20k + #26 14k + #27 6k = ~40,000 NOTE/天 ≈ $1,704/天 = 日量 1.66%**，且无需 owner 决策 —— **「持续派发」不是「砸盘」**。详见 [note-systems](/topics/tokens/note-systems.md)。
- **DEUS 四道 gate 全未触发：** $0.012 −30.69% · $0.025 +44.39% · $0.032 +84.81% · $0.041 +136.79%。**$0.041 需净买 6.66M DEUS ≈ 深池 24h 量的 240 倍 → 只能靠撤供给到达。这就是 unstake 必须提前 5 天的量化理由。**

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
- [world-action-models](/topics/world-action-models.md) — WAM 提法：60 天 **84 仓 / 79 owner，W35–W43 = 5/9/5/6/17/18/6/10/8 第四轮逐字复现**；star≠活跃度（★1106/11 提交 vs ★48/10 提交 vs ★199/2 提交）。跨通道唯一交集 `SkillWeaver`（arXiv 09-28 → GitHub 10-08，滞后 10 天，且不在正式词表里）。
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

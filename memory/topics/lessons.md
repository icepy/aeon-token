---
title: Lessons learned — archive
description: Detail behind the one-line lessons in MEMORY.md, kept here so MEMORY.md stays an index.
tags:
  - lessons
  - runbook
timestamp: 2026-10-24T21:10:00Z
---

# Lessons learned — archive

MEMORY.md carries the one-line form of each lesson. This file holds the detail.

## NOTE / Robinhood Chain

- **代币合约本身作为 watch 时，`to == watch` 算不出方向。** NOTE 的 watch 地址就是代币合约，所以要按池子判断：`X → PoolManager` 是卖，`PoolManager → X` 是买。按错误逻辑，2026-10-21 14:57Z 那笔 88,744 NOTE 的**买入**会显示成大额流出。多跳路由下同一笔 tx 里 NOTE 会转手 4 次，按"每笔 Transfer"计数会把 1 笔记成 4 笔。详见 [NOTE 笔记](/topics/tokens/note-systems.md)。
- **calldata 解码 ≠ 链上事实。**「30 天线性释放每天 2 万」是从 selector `0x091e7db9` 的 calldata 推出来的；4 小时后 0 笔出账、四个标准 selector 全 revert，证明那只是登记调用。**先看余额与出账，再谈机制。**
- **新钱包 + 固定金额整数 = 先看 gas。** NOTE 团队抛售前会把整数枚转进全新 EOA；该 EOA 无 ETH 时无法卖出，所以"第一笔 ETH 入账"比"转账发生"更接近真实开砸时刻。盯 gas 充值，不要盯转账本身。
- **链上预警有保质期。** 一旦团队把"一次性砸盘"改成"线性释放"，盯转账就失效了 —— 信号还在，但边际价值塌了。判断出货持续性要看**总量与节奏**，不是单笔。
- **owner 自有余额与 timelock 是两条独立供给。** 别只盯 unlock 排程：NOTE owner EOA 不等 10-23 解锁就自行转出了 24 万。
- **Robinhood Chain (4663) 不需要 key。** `rpc.mainnet.chain.robinhood.com` 免密钥即可 `eth_getLogs` 宽区间；GeckoTerminal (`networks/robinhood`) 和 CoinGecko 都能报价。别浪费回合找端点。
- **监控盲区：Path C 只读 ERC-20 logs，看不到 native ETH。** Robinhood 无 key 时 `onchain-monitor` 走 Path C，因此"staging 钱包被充 gas"这类触发器永远不会响，需要额外跑 `eth_getBalance` 轮询。

## 假零与断层

### `eth_getLogs` 返回 `result: null` 不是"零日志"，是端点拒绝

窗口 1001 块（超出 Tenderly 1000 块上限）时，RPC 回 `{"error":{"code":-32602,...}}`，**没有 `result` 字段**。
若 `jq` 只写 `.result | length`，`null|length` 得到 `0` —— 与"该窗口真无事件"**完全同形**。

2026-10-24 price-alert 首轮就踩了：扫深池 Swap 得 `n:0`，差点报"这一小时池子没成交"；改用 ≤1000 块窗口 + 强制先查 `.error` 后，同一时段实际有 **23 笔 Swap**。

**纪律**：`jq` 取日志数永远写成
```jq
{err:(.error.message//null), n:(if .result then (.result|length) else "NULL" end)}
```
看到 `NULL` 或 `err` 一律重试/缩窗，**不准当 0**。这条是 MEMORY 里"never trust a zero-log window"在**客户端侧**的对应物 —— 之前的假零都怀疑端点或 topic，这次错在自己的解析。

### 「最近一小时」要按时间戳取，不能按 head−1800 块

Base 约 2 秒一块，但**不保证**。2026-10-24 按 `head-1800` 取窗，实际落点是 **100 分钟前**，算出的 h1 与 DexScreener 对不上。
**做法**：二分查找使 `block.timestamp <= head.ts - 3600` 的最大块，并**打印两端时间戳**确认恰好 3600s。

### 解码 Swap 要拿储备差自证，别只信方向

把窗口内全部 Swap 的 `amountIn/amountOut` 加总，与首尾 `getReserves()` 差对账：
- DEUS 腿应**逐 wei 相等**（它是被转移的资产）；
- 报价腿（VIRTUAL/ETH）会差一个**手续费**，残差/输入应等于池子费率。

2026-10-24 实测：DEUS 差 **0.0000**、VIRTUAL 残差 **1.0089%** = Aerodrome classic 费率 → 解码器正确。若两腿都对不上，说明 token0/token1 读反或 topic 拿错。**这是比"看着像买"更硬的验证。**

## 过滤器设计

- **carrier / 领域过滤器必须按簇配，不能全局一套。** 2026-10-24 `arxiv-radar` 实测：一套链上 carrier（`blockchain` / `token` / `validator` …）套在「具身/机器人数据」词上，**90 天窗 20 篇全被丢，20 篇一个链上词都不含**；而少数「幸存」的反而靠同形异义（`token`=GAP tokens、`validator`=validator-passed 环境、`network`=agentic robot network）混进来。**真货全丢、噪声全进 —— 方向是反的。** 症状表现成「零命中」，跟「话题死」无法区分。改法：按词分域给 carrier（`CARRIER_BY_TERM`），90 天窗幸存 0 → 21、ZK 零噪声。**判据：过滤器丢掉的样本要全量抽检，不能只看幸存者 —— 只看幸存者会得到「过滤器工作正常」的完全错误结论。**
- **小众域的过滤器不要"顺手放宽"。** 同一次里试过给 ZK 域加 `proof`/`circuit`/`prover`，会把纯复杂度理论、ZK Proofs of Quantumness、点加硬件加速等 8 条理论/硬件论文捞回来。**同一个放宽动作，在机器人域是纠错、在 ZK 域是引噪** —— 必须逐域验精度，不能统一推。

## 行情取数形状（DeFiLlama / CoinGecko）

- **DeFiLlama `/v2/chains` 已不再返回 `change_1d` / `change_7d`。** 2026-10-23 实测 421 条记录里 0 条带这两个字段。任何"直接取字段"的代码都会给每条链算出 `0.00%` 并显示成"全部持平"——一个静默的假阴性。链级涨跌要走 `/v2/historicalChainTvl/{chain}` 自己按日快照算。
- **CoinGecko `/global` 的 `market_cap_change_percentage_24h_usd` 不可信。** 2026-10-23 该字段报 −3.83%，而用同一批 `/coins/markets` 前 20 名反推只有 −0.07%，且 BTC/ETH/SOL 24h 全在 ±0.15% 内（Coinbase 现货交叉验证 $81,582 vs CoinGecko $81,634）。要用总市值变动就用 top-N 加权重算，别引用这个聚合字段。
- **链级 TVL 跳变先怀疑"上新"，别当净流入。** Hyperliquid L1 的 7d 显示 +122%，实际是 10-21 单日 chainTVL 从 $1.02B 阶跃到 $2.49B（协议收录变化），而 Hyperliquid Bridge *协议本身* 7d 是 −0.17%。任何链级异动都要下钻到协议级 `chainTvls` 才会发现。
- **百分比过滤器必须配绝对额地板。** 「fees 7d 涨 >20% 且 TVL 7d <+5%」这条筛出了 Aave V2（+39.4%）——其 7d 手续费总额只有 **$37,212**。纯百分比会把灰尘当信号。加 `total7d >= $1M`。
- **APY 高不代表可投。** Uniswap V3 的 USDC-WETH 池 `apyBase` 22% 过了所有"real yield"过滤（无 reward、非 outlier、置信度 3），但那是做市 LP 的手续费，不是无风险利率。报告里必须标"LP, not passive"，否则下游会把它当稳定币收益。

## Keyless Base reads

- **Keys are unset in this repo's runs** (`ALCHEMY_`, `ETHERSCAN_`, `COINGECKO_API_KEY`). Keyless Base reads work only via Tenderly's public gateway, capped at 1,000 blocks per `eth_getLogs` — and 20,000 results, so always pass an `address` filter. See [Base RPC access](/topics/base-rpc-access.md).
- **Never trust a zero-log window.** Re-query a window with known activity and check the escrow balance via `eth_call`; only then is "quiet" real.
- **`balanceOf` 的 calldata 要把地址**左**补零，右补零会静默返回 0。** 2026-10-23 14:05Z 的 price-alert 里，我用 `"0x70a08231" + addr.slice(2).padStart(64,"0")` 拼参数，结果地址落在低位、高 24 位补零，`eth_call` 不报错、直接返回 `0x0` —— 差点把「真买家仍持 113,627 DEUS」写成「已清仓」。正确形状：selector `0x70a08231` + **24 个 hex 零** + 40 位地址，合计 74 个 hex 字符（`data.length === 74`）。**凡余额为 0，先用一个已知非零地址做对照再下结论。**
- **公共 RPC 的 429 会以「空结果」返回，被 `.catch()` 静默吞成「无活动」。** 2026-10-23 10:35Z 扫 NOTE owner 交易，连续几次得到 `found: []` 并据此判「窗口内无 owner 交易」；实际是 `{code:429, message:"Rate Limit Hit"}`，`Promise.all` 把它当空数组收了。改用**单笔 topic 过滤 + 2s 退避重试**才拿到真实的 2 笔出账。**判据：只要结果是「零」，先看重试计数与 HTTP 体，别把限流读成静默。**
- **`mainnet.base.org` 会把合法的 `balanceOf` 整批 revert，几分钟后自愈 —— revert ≠ 余额 0，也 ≠ 合约问题。** 2026-10-23 18:03Z 五个不同的合法 `balanceOf` 同时 revert，换 `base.gateway.tenderly.co` 立刻返回正确值。**换端点复核，别改代码找 bug。**
- **`eth_getLogs` 的 topic0 必须给满 64 hex。** 只传 4 字节选择器（`0xb3e27736`）在 Tenderly 上返回 `-32602 invalid params`，更糟的情况是**返回干净的 0 笔**，与死池无法区分。完整哈希 `0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b`。
- **扫描脚本要在扫描阶段就落盘或分批输出。** 2026-10-23 21:24Z 的 `trace.js` 先枚举完 5 地址 × 双方向 × 24k 窗的 `eth_getBlockByNumber` 才回填时间戳，10 分钟被后台杀掉、零输出 —— 一次全白跑。**边扫边写，别等全部枚举完再算元数据。**

## Watch configuration

- **钱包型 watch 不能用 `eth_getLogs{address: <EOA>}`。** EOA 不发事件，该写法永久返回 0 —— owner EOA / staging / vesting / DEUS escrow 四个 watch 曾长期处于假零。正确形状是在**代币合约**上做 topic 过滤：`[Transfer, null, padded(wallet)]` 收、`[Transfer, padded(wallet)]` 发。
- **xDEUS is ERC-721, not ERC-20** — `decimals()` reverts, `Transfer` carries `tokenId` in `topics[3]`. The ERC-20 topic0 hash still matches, so watch config needs no change.

## 扫 timelock：窗口与 topics 两个坑

1. **窗口别从"最近几天"往回数。** Robinhood 链实测约 34k 块/小时，48h 的排程跨度约 160 万块。2026-10-22 用 `from=94700000` 起扫，完全漏掉 blk 94195015 的 `CallScheduled`，结论一度变成"120 万解锁不存在/已撤销"。正确做法是从**已知排程块**往前推，而不是从当前块往回数。
2. **`eth_getLogs` 不要传 `topics: null`。** 部分节点会返回空数组而不报错，静默变成"没有事件"。要扫全部事件就**省略 topics 字段**，而不是显式传 null。

误判代价很高：这两条任何一条踩中，都会把"明天有 120 万解锁"读成"没有风险"。

## Price feeds

- **缺 `h1` ≠ 平静。** DexScreener 对薄盘口常省略 `priceChange.h1`；skill 按 0 处理，于是 sharp-move gate 显示 QUIET 而实际是**未测量**。state 里存 `null` 而非 0，下一轮才能区分"测过且平"与"没测到"。
- **DS 缺 h1 时用 GeckoTerminal 同 pair 补测，别默认 0。** 端点 `/networks/base/pools/0x3e97…c1fa`，DS 和 GT 价格、流动性一致到 5 位小数。补测后 state 里记 `h1_source: "geckoterminal"` 和 `h1_note`，下一轮才知道这个数是替代来源。
- **两源 h24 有 0.8–1.6pp 系统性分歧，h6 甚至会反号。** 21:01Z 差 1.55pp、22:02Z 0.83pp、23:01Z 1.09pp，而同一时刻价格完全一致。属 24h 窗口锚点（开盘时点）差异，不是坏数据 —— **把 h24 当近似值，不要当精确值引用。**
- **成交量为零时，"走平"是机械的，不是平静的。** 23:01Z 深池 1h 成交 $0.018 / 1 笔（0 买 1 卖），价格必然显示 0.00% —— 此时该读的是成交额塌陷本身（$276.66 → $5.46 → $0.018），不是百分比。
- **单池的 txns.h1 买卖计数不能读成资金流，必须跨池对齐 `sender + 时间戳`。** 10-23 08:01Z 把 DEUS 两个池的逐笔成交按 `tx_from_address` 对齐，三个时刻全部是**同一个地址在两边动作**，不是多路资金：①04:26:35Z `0xb9817…e105d72` 在 VIRTUAL 池**卖** $31.46、在 USDC 池也**卖** $104.81（同一人两边砸，共 ~$136）；②06:16:53Z `0x6664f…855154`、③06:21:39Z `0x66608…f285bf` 各在 VIRTUAL 池**卖**、USDC 池**买**（同价反向 = 自套利/路由，不是看空）。**教训：只看一个池的 0买/N卖 会读成"有人在抛"，实际可能是同一个人的套利腿。判断方向要按 sender 聚合，不是按单池笔数。** 也解释了此前两池 h1 反复反号（见上条）。
- **买入同理：确认方向性吸筹要查"余额留没留"，不是看成交方向。** 10-23 08:37:53Z `0x1e70e2fd`（**nonce 1 = 该钱包首笔交易**）在 VIRTUAL 池买 $305.97 / 17,635.31 DEUS @ $0.017350。拉 receipt `0x356d58c8…` 解 Transfer：468.632 VIRTUAL 从 Uniswap v4 池 `0xc200f21e` → 路由器 `0x67d03631` → 池 `0x3e97`，DEUS 出池直接进买家。再 `balanceOf` 查买家 = **17,635.32 DEUS 全留**，且该 sender 在 USDC 池无反向卖单 → **真吸筹**。反例是 06:16/06:21 那种同秒两池反向、余额不留的套利腿。**判据：`buy` + 余额留存 = 方向性建仓；`buy` + 他池同秒卖 = 套利。** 金额也要折算：$306 仅 24h 量的 2.05%，价格影响 <1bp —— 信号意义在"首次非套利买盘"，不在体量。
- **"连续 N 笔买入、0 卖"是套利腿的典型外观，不是吸筹证据。** 10-23 09:49:03–09:51:47Z VIRTUAL 池 7 连买 / 0 卖 / $372.59，看着像扫货；`balanceOf` 三个买家全是 **1 wei、0、0** —— `0xb824534a`（**nonce 1,334**，不是新钱包）同分钟在 USDC 池 0x58dBa 每 4–10 秒卖出，**余额归零 = 原地套利**。**一轮 `balanceOf` 就能定性，比解 receipt 便宜，先查余额再谈方向。** 旁证是跨池价差：当时 VIRTUAL $0.01734 vs USDC $0.01751（**+0.98%**，当日最阔），价差那侧（USDC 池）才是出现卖单的池 —— **溢价池记卖、折价池记买 = 机器人在抹平价差，不是有人在买。**
- **单次吸筹不等于趋势，第二天要复核它有没有继续加仓。** 08:37Z 的 `0x1e70e2fd` 隔一小时余额仍是最初那 17,635.3151 DEUS，**零追加** —— 一次性机会主义下单，不是买方波。**"首次非套利买盘"值得记一笔，但在它加第二笔之前不要升级成"吸筹趋势"，更不能据此谈减质押。**
- **同块扫多个池、汇进同一跳、再转给共享 sink = 聚合器/套利，不是吸筹。** 10-23 11:18:51Z $168.87 与 11:21:03Z $264.40 两笔"买盘"看着是量能延续，receipt 一解全露馅：tx `0xd49559c1` / `0x17682c97` 各在**同一块内从五个池**（0x58dba / 0x1b2f3f5c / 0x498581ff / 0x75bc1495 / 0x3e97c5ec）凑量，汇进中间跳（`0x939e398d` / `0x7d683941`），再整笔 3.2 万 / 3.1 万 DEUS 转给**同一个** sink `0xfea20e68`，且 **sink 与全部中间跳的 DEUS 余额都是 0**。**判据升级：方向性买家只从一条路径取货、且收货地址余额留得住；一单跨 4–5 个场所还倒给共享地址，是在做路由不是在建仓。** 看到"买盘延续"先 balanceOf 收款方，比解 receipt 便宜。
- **成交量要跟买盘一起读。** 同一轮 v1h 从 $2,011.67 掉到 $612.58、v24h 由 $16,900 到 $16,610 —— **$2k 大单之后量在衰减**，说明那单没引来跟风。价格几乎没动（+0.06%）而量塌了，是"单笔冲击 → 无人接力"的典型形状，不是启动。
- **`eth_getCode` 以 `0xef0100` 开头 = EIP-7702 委托智能账户，不是普通 EOA。** 10-23 14:55Z 的 `0x259f962e…`（5 笔买 $4,564、余额全留）返回 `0xef0100` + `0x63c0c19a282a1b52b07dd5a65b58948a07dae32b`，delegate 是暴露 `0x84b0196e`/`0xd03c7914`/`0xd691c964`/`0xf23a6e61`/`0xffa1ad74` 的智能账户实现。配合 nonce 135 + 0.819 ETH，这是**有历史的成熟钱包新近转向**，不是新充值的小号。**分类时把 `eth_getCode` 编进判据：空返回 = EOA；`0xef0100…` = 7702 智能账户**（"fresh EOA 留仓"的说法会低估它）。
- **薄盘口上，买卖"笔数"会给出与"美元额"相反的方向结论。** 10-23 15:05Z 1h 是 **4 买 / 18 卖**，看着像在派发；但 14:50Z 起按美元是 **买 $4,326 / 卖 $1,245 = 74/26**。原因：卖单全是做市夹子 —— `0x9694…`（nonce 0x394c）12 笔每笔 ~$49、**卖完仍持 19,360.79 DEUS**；`0x6abe…`（nonce 257,965）每笔 $78–194、余额 0。**读向先换算美元额，再看笔数。**
- **`eth_getLogs` 在公共 Tenderly 端点上限 1000 块，且区间超一块就整单报错、不截断。** 要算 `latest-999 .. latest`；猜 `latest-1000` 会得到 `Block range too large for public access: maximum 1000 blocks`。同一条链上同一次运行里这个上限是硬性的，别试第二次。
- **🔴 Aerodrome Slipstream 的 Swap topic0 是 `0xb3e27736`，不是 Uniswap V3 的 `0xc42079f9`；且 data 只有 4 个 word，不是 5 个。** 10-23 19:09Z 我用 `0xc42079f9` 扫最深池 `0x3E97…` 最近 2100 块，得到**干净的 0 笔 swap**，几乎据此写下"池子死了"，但 DexScreener 同池 v1h 报 $860。真因：Slipstream 池的 Swap 用另一套签名，`0xc42079f9` 那个 topic 在这个池上**根本不存在**。**判据（第三次踩「零日志」）：当厂商报价显示有量、而链上扫出 0 笔 swap 时，先对一个已知活跃块 `dump 全部 log`（不传 topics）看真实 topic0 集合，再决定信不信这个 0。** 正确解码：Slipstream Swap data = `amount0, amount1(带符号), sqrtPriceX96, liquidity` —— 4 个 word；DEUS 在这三个池里都是 token1。
- **判「是不是新钱」要拉多 horizon 余额，只回看 24h 会把建仓误判成回补、只看单笔方向会把回补误判成建仓。** 10-23 19:09Z 两笔买入（$838 + $95）的收款方 `0x1184de98` / `0x3fd5`，在 −1h / −6h / −24h / −7d / −30d 的 `balanceOf` **全部精确为 0** —— 这是四天来第一批真外部新钱。**方法：`eth_call balanceOf` 打到 `head - {1800, 10800, 43200, 302400, 1296000}` 五个历史块，全 0 才叫「从未持有」。** 对照第 7 条（老鲸回补），两者只看 24h 会得出同一结论，加上 −7d/−30d 才分得开。
- **经 1inch v6（`0x111111125421ca6dc452d289314280a0f8842a65`）或其它聚合器路由的买单，仍然可能是真钱。** 判据不是「有没有走路由」（走路由是常态），而是**终端收款地址的 `balanceOf` 是否升高且留住**。19:09Z 那笔 $95 就是经 1inch 跨三池扫出来的，但终点 `0x3fd5` 余额从 0 变成 5,225 DEUS 并留住 —— 真钱；而 16:41Z 那笔终点余额精确为 0 —— 代客成交。**同一个 router，两种性质，只能靠终点地址的余额分辨。**
- **helper 合约 nonce 1 + 有代码 = 一次性路由/授权合约，不是买家。** 19:09Z 的 $838 买单里，`0x8d8f598c` 与 `0x0a2854fb` 都是 `code 0x60806040…`、nonce 1、余额归零的转账中转站；真正的买家是 tx 的 `from`（`0x1184de98`，nonce 920）。**追买家要追 `eth_getTransactionByHash().from` 与 DEUS 最终落点，别把 helper 当主体。**
- **「单池 N 买 / 0 卖」是第 9 条判据，也是最容易上当的一种外观。** 2026-10-23 19:07–19:37Z DexScreener 报最深池 **37 买 / 0 卖**、GT 同窗 35 笔腿清一色 `buy`（$718.91），看着像一波凶猛买盘。拆回执全是同秒双池套利：发起方是 `0x666…` / `0x6341d948` EOA 簇（nonce 4,459 / 215,435 / 213,982 / 216,683），**全部 `balanceOf` = 0**；DEUS 在同一笔交易里走 最深池 → helper `0xae629bf1` → USDC 池 `0x58dba34e`。**为什么单池页面看不出：一轮「A 池买、B 池卖」在 A 池记纯 BUY、在 B 池记纯 SELL，两边都看不到净额。** 跨池净额才 是方向：VIRTUAL 池 +$718.91 流入，USDC 池 买 $380.35 / 卖 $539.93 = **净卖 $159.58**。**方法：判买盘不看笔数、不看方向列，只看（a）发起方余额是否升高且留住，（b）DEUS 是否停在非「立即转发」的地址上。**
- **第 6 条判据补强：买也可能是「代客成交」。** 2026-10-23 16:41:51Z 出现 $81.52（VIRTUAL 池）+ $249.79（USDC 池）同秒双池扫单，像买盘回归；sender `0x9a3811b1…dfbf` 是 `code 0x` 的普通 EOA、nonce **3,549**、`balanceOf(DEUS)` **精确为 0** —— 聚合器替别人成单后把货转走。**只有买家余额升高且留住才算数，这一条盖过所有 App 上看到的"买"。**
- **🔴 更正第 69 条：DEUS 的四个池分属两个家族，用单一 topic0 扫全部会得到假零。** 2026-10-24 08:12Z 只按地址扫 `0x58dBa34e`（7 条 log，直方图 100% 是 `0xc42079f9`）证实：**三个次级池 `0x58dBa34e` / `0x1B2f3f5C` / `0x75bc1495` 是 Uniswap-V3 型（`0xc42079f9…`，3 topics / 5 data words）**，而**只有最深池 `0x3E97c5EC` 是 Solidly 型（`0xb3e27736…`，4 data words）**。前两轮（10-24 06:12Z / 07:05Z）拿 Solidly 的 topic 去扫那三个 V3 池，拿到干净 0，据此写下「整市场停摆」——**是假的**，它们一直在成交（1h 6/1/9 笔，DEUS 6,084）。**判据：宣称任何池「安静」前，先按地址不传 topics dump 一遍、出 topic0 直方图，再决定信不信那个 0。**
- **🔴 最深刻的教训：控制窗口必须从 `eth_getTransactionReceipt` 取块高，不能抄笔记。** 本仓 state 把 xDEUS #1492 unstake 记在块 **53002812**，receipt 实际是 **53003804**（时间戳吻合 23:09:15Z）。用错块高做对照返回 0 笔，**看起来和过滤器坏掉一模一样**，差点据此推翻一个本来正确的零。**控制块高一律现取现用。**
- **`slot0`/`globalState`/`fee`/`liquidity` 全部 revert 的池子不是 Slipstream，是 Solidly。** 探 `getReserves()`（`0x0902f1ac`）与 `stable()`（`0x22be3de1`）：最深池返回 `[528123.83, 18855811.85, 1792816783]` 且 `stable=0`（volatile）。**Solidly volatile 池的储备比值才是正确 mark**——CL 池才要用 sqrtPriceX96。第 69 条把最深池叫「Slipstream」是标签错误（topic0 描述是对的）。
- **eth_getLogs 的日志索引能回看至少 25,000 块**（2026-10-24 08:00Z 实测：−1000 / −5000 / −17000 / −25000 各窗口 DEUS Transfer 分别 192 / 169 / 218 / 172 条，全部正常）。所以「老窗口扫出 0」不能归因于端点保留期——先怀疑过滤器和块高。

- **🔴 过滤器本身要做「判别力测试」，否则零命中可能只是过滤器坏了。** 2026-10-24 11:37Z 用**故意敲错一个字符**的 Sync topic0（`…d44a2abdf50e…` 而非 `…d44a2abf8d328…`）去扫一个**已知含 2 条真 Sync** 的窗口，返回 **0 条**；换真 topic0 同窗口返回 **2 条**；换全 `0x01*32` 假 topic0 返回 **0 条**。**三者可区分 → 这个端点不会把错过滤器静默返回成「有日志」。** 只有在做一次这种负对照之后，才能相信任何「零命中」。方法：挑一个**已知有事件**的窗口，同时打「真 topic0 / 故意错 1 字符的 topic0 / 全假 topic0」三条，期望 `N / 0 / 0`。若「错 1 字符」也返回 N，说明端点根本没按 topic 过滤，此时所有 topic 过滤结果全部作废。
- **公共 Tenderly 端点的 `eth_call` 必须显式带第二个参数（block tag），省略会报 `-32602 invalid params`，而不是默认 latest。** `{"to":…,"data":…}` 两字段的 `eth_call` 在本机直接失败；加 `"latest"` 或块高才正常。这和标准 JSON-RPC 的行为不同，容易误判成「合约 revert」。**同一端点 `eth_getLogs` 硬限 1000 块，1800 块窗口必拒、不截断**（第 69 条已记，本轮再次踩到）。
- **🔴 两条链的历史 `eth_call` 能力不对称，别互推。** 2026-10-24 21:0xZ：**Robinhood 公共 RPC 不支持历史 `eth_call`**（`{"code":-32000,"message":"historical state … is not available"}`，只有 `latest`），而 **Base 的 Tenderly 网关支持任意历史块**（同一轮用 blk 53,000,125 读 24h 前的 `balanceOf` 成功）。后果：RH 的 24h 余额差额**只能走 log 双向扫描求和**（进/出各扫一遍），不能图省事打 block-pinned `balanceOf`。**判据：`eth_call` 带历史块返回 `historical state … not available` = 端点不支持，换 log 差额法，不是「合约有问题」。**
- **🔴 无 ABI 时解 calldata：靠「uint 词位置 + 事件 data 对齐」双向验证。** 2026-10-24 的 owner `0x091e7db9` 在 4byte **完全无收录**（`text_signature=createVestingSchedule` 返回 53 个变体，无一个匹配），`blockscout` API 又被 Cloudflare 挡死。解法：把 input 切成 32 字节词逐个按 uint / address / ascii 解释，同时把**同一 tx 里合约自己发出的事件的 `data`** 切出来对照 —— 事件的 6 个词与 input 的 `w1–w6` 逐位对齐（`amount / start / cliff / 0 / duration / 1`），beneficiary 在 `w0` 和 `topics[2]` 两处互相印证。**对齐成功才敢定名。** 顺带证实：`ScheduleCreated` topic0 `0x8cd818b1…` 的 sid 在 `topics[1]`，不是 `data`。
- **🔴 「owner 转账 = 砸盘」是错的默认假设 —— 先看终点是不是自己的合约。** 2026-10-24 20:23Z NOTE owner 首次动仓，180,000 NOTE 转给 vesting 合约，看起来像「开始派发」。实际是 `createVestingSchedule`，30 天线性、cliff 5000。**三步排除法**：①查 `tx.to` 是不是自家协议合约（是 → 先怀疑是排程不是卖出）；②解 calldata 看是不是 create/approve 类；③查受益人有没有卖出史（该受益人 3,200 万块零转出）。**真正的信号要往「释放速率 ÷ 日成交量」上算**，不是看单笔金额大小 —— 18 万看似巨大，实为 $256/天、占日量 0.25%。
- **地址大小写混写会静默变成 `-32602`，不是「地址不存在」。** `0x940A319B…`（checksum 大小写）传给本机 RPC 报 invalid params，全小写才通。calldata 里的参数地址也要 `.rjust(64,"0")` 左补零后用全小写。

- **🔴 Solidly Swap 的 data 字序是 `amount0In, amount1In, amount0Out, amount1Out` —— 按 Uniswap V2 的 `(a0In, a1Out, a1In, a0Out)` 解会把买卖完全读反。** 2026-10-24 18:01Z 首版用 V2 字序解 13 笔 Solidly Swap，得到「净 +20,700 DEUS 流入池」，而同一小时储备实测是 **−60,565 流出**，**符号相反**。改字序后（`a1in`=卖入、`a1out`=买出）与储备差吻合到 0.3%（残差为手续费与块内跨段）。**判据：任何 Swap 解码器上线前，先用「同窗口储备差」做符号对照 —— 对不上就是字序错了，不是市场反常。** 储备差是独立测量，永远可以否决解码器。
- **同一块里 11 笔小额卖出通常是 1 个操作者的扫单，不是 11 个卖家。** 2026-10-24 18:01Z 有 11 笔 734–1,012 DEUS 的卖单全部落在 **blk 53037400** 一个块内 —— 笔数看着像"11 人在派发"，实际是一次拆单。**按块聚合再判人数；`tx.from` 才是主体，笔数不是。**
- **空 EOA 余额 + 一笔横扫多场所 + 无反向腿 = 真方向性买入。** 2026-10-24 17:29–17:31Z `0x9d1c316f` 76 秒两笔经 Odos（`0x6131b5fa`）扫四场所买 115,643 DEUS，−30d 余额恰好 0、−7d/−24h/−6h/−1h 恒定 168,772.64（一周没碰过），买完全部留存到 284,371。与第 9/19 条的区别：**套利是同一笔里 A 场买 B 场卖，方向性买入是同一笔里多场所同向买、终点余额留得住。** 看 tx 内有没有反向腿，比看余额更早、更准。
- **第 8 条判据：`0x1184de98` / `0x3fd5` 是四天来第一批真外部新钱**，在 −1h/−6h/−24h/−7d/−30d 余额全 0。次日复核：`0x3fd51604` 19:24:01Z 又买 $45.77（nonce 290→291，余额 5,225 → 7,735），是新钱里第一个回头加仓的；`0x1184de98` 未再动（nonce 920、持 46,195 未卖）。**一加一持，结构偏建设性但量级仍小（$4.6 万）—— 这是"加仓才算数"的正面样本。**[source: logs/2026-10-23#price-alert]

## arXiv 检索（arxiv-radar）

- **`submittedDate` 窗口是对的，但索引滞后约 2 天，且是全局的，最新两天恒为 0 条。** 2026-10-24 实测：`cat:cs.CR` 单日总数 10-20 **48** → 10-21 **38** → 10-22 **30** → 10-23 **0** → 10-24 **0**，`cs.RO` 同形（70/57/0/0），API 最新收录停在 `2026-10-22T17:59Z`。**这是「还没入库」，不是「没人投稿」** —— 每日窗口扫描看到末两天 0 命中属正常。**判据要升级成「按日 total 计数」**：只看「窗口内最新日期」只能说明「早」，按日计数才能区分「滞后」与「真零」。
- **周窗口命中数很低是常态，不是词表坏了。** 18 个词 × 7 天只捞到 4 篇原始命中（幸存 2）。逐词核过：`ti:"restaking"` 全时段最新一篇是 **2026-08-10**，`ti:"zero-knowledge"` 全时段 312 篇但 7 天内仅 3 篇。**判词表是否还有效，要看 all-time 最新发布日期，别看窗口内计数。** 90 天窗的对照量级：22 篇存活（机器人 20 + MEV 2），折每周约 1.7 篇 —— 所以 7 天窗出 1–2 篇是正常节奏，出 0 也不代表停摆。
- **🔴 词表健康度必须看 `raw_term`（原始命中），不能看 `per_term`。** `per_term` 只在「通过全部过滤器并新收」时自增，一旦把存量 seed 进 `seen`，每个词的账面都会假性归零 —— 2026-10-24 一轮 90 天窗因此报出「15 词零命中」，而 `zero-knowledge` 实际有 28 条原始命中。**症状与「话题死了」完全一致。** 脚本已拆出 `raw_term`，输出成 `词=原始/新收` 两列；**判断词死没死只看斜杠前面那个数。**
- **🔴 更正：`ti:` 引号对单字无差，对多词是必需的。** 单字确实等价（`ti:"restaking"` 与 `ti:restaking` 都返回 8 条，实测无差）—— 早前据此写下「引号不会更严」是**只对单字成立**的结论。多词不加引号时 `ti:foo bar` 会被 arXiv 解析成 `ti:foo AND bar`，**第二个词之后全部掉成全字段搜索**，静默漏检。skill 里一律加引号是对的。
- **`abs:` 才是松散匹配，`ti:` 不是。** `abs:"MEV"` 会撞「兆电子伏特」。只用 `ti:`；绕不开时用 `cat:` 约束整条查询。
- **词表写「机制」，不写「项目名」。** `XMAQUINA` 全期零命中（`all:` / `abs:` / `ti:` 全试过，不是窗口问题）；`NOTE` 是常用英文词，90 天 223 条命中里过完 carrier 的 13 条全是 `A note on ...` / `Clinical Notes` / `Community Notes`。唯一可用的是 `Pearl Blockchain`（且必须带 `Blockchain` 后缀，裸词 `Pearl` 90 天 13 条里只有 1 条相关）。**名字交给下一条通道。**
- **0 命中要分三类，先排除前两类再谈结论。** ①收录滞后（看「窗口内最新收录日期」，早 3 天以上就是）②`seen` 挡掉（`raw_term` 有数、`per_term` 是 0）③carrier 误杀（`raw_term` 有数、`carrier` 丢弃数异常高）—— **只有第③类是真 bug。**
- **加新领域的词必须同时配 carrier 并登记进 `CARRIER_BY_TERM`。** 只加词不配 carrier，会重演机器人簇 20 篇静默误杀。词和 carrier 必须成对出现。词表总量控制在 15–25 个。
- **查 API 要 `id_list=` 拿单篇详情**（`.../api/query?id_list=2610.27530`），比翻 `search_query` 结果稳。


# Citations

- `memory/logs/2026-10-21#onchain-monitor`, `#telegram-reply`, `#heartbeat-brief`, `#price-alert`
- `memory/logs/2026-10-22#price-alert`（21:01Z / 22:02Z / 23:01Z 三源对比）
- `memory/logs/2026-10-23#price-alert`（11:06Z 单笔方向性买盘 → 12:02Z 复核实证两笔跟进买盘为聚合器套利；15:05Z 第二个方向性钱包 `0x259f962e…` + 笔数/美元额反向 + 7702 识别；19:09Z Slipstream topic0 坑 + 多 horizon 余额判新钱 + 1inch 路由终点判据；20:05Z 单池 37 买 / 0 卖 实为同秒双池套利 + 供给口径改为净增发；17:01Z–21:16Z 两个方向性钱包冻结、h1 缺失 ≠ 平静）
- `memory/logs/2026-10-24#arxiv-radar`（arXiv 索引滞后 1–2 天、周窗口低命中是常态、`ti:` 引号与裸词等价）
- `memory/logs/2026-10-23#onchain-monitor`（21:24Z 上膛4 扣扳机清仓 + 第七个上膛钱包 24 万 + 待命重算 48 万）
- `memory/logs/2026-10-23#heartbeat`（RH 429 返回空结果而非错误；selector `isOperationReady`/`getTimestamp` 修正）

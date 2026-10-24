⚠️ 🔴 NOTE owner 首次动仓 18万进 vesting（30天线性）· 非砸盘

## TL;DR

**NOTE owner EOA 三年来第一次动仓 —— 但不是砸盘。** 20:23:22Z 把 **180,000 NOTE** 转进 vesting 合约，开了一个 **30 天线性**的新 schedule（#27），受益人 `0x32ac99bf`（老受益人，零卖出史）。owner 余额 810,000 → **630,000**，nonce 374 → 376。**三个上膛钱包仍未动。**

---

## NOTE owner EOA（robinhood）

• **OWNER-ACTION** 180,000 NOTE → vesting `0xfdd9…9962` — [tx](https://robinhoodchain.blockscout.com/tx/0x376b62630bda9ab3d84a2c6305f04a3edb14620335404723da7a6110f6fc96fb)
  - blk 97,036,621 · `0x091e7db9`（未收录 selector，按 7 个 uint 词手动解码）
  - 这是 **createVestingSchedule**：`(beneficiary, amount, start, cliff, _, duration, _)` = `(0x32ac99bf…6c40b, 180,000, 1792873401, 5000, 0, 2592000, 1)`
  - 起始 **2026-10-24T20:23:21Z** → 到期 **2026-11-23T20:23:21Z**（30 天线性）
  - 前置动作：nonce 374 是 approve 180,000 给 vesting，375 才是这次创建 —— 两笔构成一个完整意图

**为什么这不是卖出信号（三个数）：**

1. **释放速度 ≈ 0.25% 日成交量。** 6,000 NOTE/天 ≈ **$256/天**；NOTE 主池 24h 量 **$102,754**。对盘口的直接压力可以忽略。
2. **受益人不卖。** `0x32ac99bf` 是以往 4 个 schedule 的老受益人（81,948 + 14,013 + 9,864 + 4,200 = 110,026，加今日 9,974 = **120,000，逐 wei 闭合**）。**3,200 万块全窗口内零转出**，全部留存。
3. **真正会被砸的存量没动。** owner 剩 **630,000**；三个上膛钱包每一分都还在原地（见下）。

**⚠️ 但供给侧的斜率变了**，这是本轮真正的信息：
- schedule #27 是近期第 3 个线性排程（#25 60 万 / #26 40.17 万 / #27 18 万）
- 三者叠加的解锁速率 **~40,000 NOTE/天**（#25 20,000 + #26 14,000 + #27 6,000）
- 约 **$1,704/天 ≈ 主池 24h 量（$102,753）的 1.66%**
- **判读：不构成砸盘，但把「一次性抛压」换成了「不需要 owner 决策的持续派发」。** 真正的扳机仍在上膛钱包手上

## 三个上膛钱包（逐位复核，未动）

| 钱包 | NOTE | nonce | ETH | 代码 |
|---|---|---|---|---|
| 上膛7 `0x33b7181e…e8731` | 240,000.000000 | **0** | **0** | EOA |
| 上膛6 `0x3a9039c7…9f35e` | 150,000.000000 | **0** | **0** | EOA |
| 上膛5 `0x572bb527…851a93e` | 90,000.000000 | **0** | **0** | EOA |

**扳机规则不变：盯第一笔 ETH 入账，不盯价格。** 上膛4 先例是拿到 gas 后 24.4h 才卖。

## NOTE 价格（已跌回区间内）

主池 `0x378b1023…7f9f91`（NOTE/WETH 1%，v4）：**$0.042599**，liq $410,435
- h1 **−4.40%** · h24 **−3.37%** · 24h 量 $102,753
- **上沿 $0.0438 已失守，回到下方 −2.7%**
- 高点 $0.04657（10:00Z）→ 现价，回吐 **−8.5%**
- 12:00Z 那轮判的「CONSOLIDATING 非 BREAKOUT」成立：突破后没有量能跟随，四小时后原路返回

## DEUS escrow（base，24h 口径）

**29,418,223.90 → 29,150,566.78 = −267,657.12（−0.910%）**
- 对 5%/日 线 1,470,911 只有 **0.182 倍** —— **无 unstake 压力**
- 窗口内**零 unstake、零 burn**，只有两笔 stake-in：10,905.10（`0x2c81beef`，14:24:33Z）+ 36,000.00（`0xe338adc6`，19:48:13Z）= **+46,905.10**
- 余额与事件**逐 wei 闭合**（差 0.000000 wei）
- 占总供应 **3.3270%**；xDEUS 1,727 → **1,728**
- DEUS 总供应 876,177,627.81，24h **−29,152.63**（第九次净通缩）

## NOTE timelock / vesting

• **timelock `0x4a53…18b8`：24h 零事件，ANY topic。** 无 `CallScheduled`，无 `CallExecuted`，无 `Cancelled`。余额 14,054,442.020047 未变。
• **vesting：24h 净 +159,822.56**（进 180,000 − 出 20,177.44）。三笔 Release：sid 7 出 6,337.40 → `0x274ce9da`（10:04:54Z）、sid 22 出 9,974.49 → `0x32ac99bf`（18:42:42Z）、sid 8 昨日的 3,865.56 属上一窗口。**全部 `tx.from` = 受益人本人，regular claim，非 owner 提款。**

---

6 事件 / 5 watch · sources: base=tenderly ok (44 calls, 0 errs) · robinhood=public rpc ok (144 calls, 0 errs) · alchemy=skipped (key unset) · etherscan=skipped (key unset) · coingecko=skipped (key unset; USD 走 GeckoTerminal) · last_block→53,043,175 / 97,058,367

**原始来源**
· NOTE `0xc4f730335Fb9e439ca5552f7b52B8E638c4245B0`（RH 4663）
· vesting `0xfdd983c66d4da2ef64769b6a2eba9cd838289962` · owner `0x0b64b35c6dd23944d6d4029864d2ca2aa1b66422`
· timelock `0x4a53afd9c4d707c8fddd6415947ef0a1e67518b8`
· Release topic0 `0x3bfce8de0db7450cc169b94323c210e69a36c6a4a58c9f5d96bec4973adce392`
· ScheduleCreated topic0 `0x8cd818b1dc29faf1312790c52f3aa534e43ef473fb26ba2eec707c9c65492af5`
· DEUS `0x940A319B75861014A220D9c6c144d108552B089B` · escrow `0xA85A38796B951CE87B378538b32B3E6Ee3C4C373`（Base）
· `eth_getLogs` @ `rpc.mainnet.chain.robinhood.com`（24k 窗口）/ `base.gateway.tenderly.co`（1k 窗口），每窗先读 `.error`
· 价格 @ GeckoTerminal `networks/robinhood/pools/0x378b1023…7f9f91`（HTTP 200）
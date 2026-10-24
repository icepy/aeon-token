

### price-alert
- **Skill**: price-alert
- **Token**: DEUS (0x940A319B75861014A220D9c6c144d108552B089B)
- **Current**: **$0.017918**（三家活跃 DEUS/USDC 池的成交价中位数） | 1h: **−0.04%（本轮实测，非 null）** | 24h: +4.04%
- **ATH**: $0.06876 (set 2026-05-28 15:35 UTC) [UNCHANGED]
- **Sharp-move gate**: QUIET — 本轮 **h1 是实测的**，不是未测量。解码 38 笔 V3 Swap，1h 内 16 笔。分池 1h：pool2 −0.043% / pool3 −0.256% / pool4 −0.001%。距 ±20% 门槛极远。
- **Targets evaluated**: 0.012, 0.025, 0.032, 0.041 → NOT_HIT ×4
- **Verdicts fired**: NONE
- **Notifications sent**: 0
- **Status**: PRICE_ALERT_OK
- **Distances**（基准 $0.017918）: −33.03% to $0.012 | +39.52% to $0.025 | +78.59% to $0.032 | +128.82% to $0.041（unstake 线） | ATH +283.75%

- **结论：不动仓，不推送。四门槛全未触及。**

- **本轮最重的发现是「前两轮的一个结论是假的」，不是价格。**
  - **三个次级池是 Uniswap-V3 型，不是 Solidly 型。** Swap topic0 = `0xc42079f9…`，而前两轮用 Solidly 的 `0xb3e27736…` 去扫它们，拿到干净的 0，据此写下「整市场停摆」。**方向反了** —— 这三个池一直在成交：1h 内 6 / 1 / 9 笔，DexScreener v1h $90.75 / $18.02 / $51.58，1h DEUS 成交量 **6,084**。
  - **判据（新增 16a）：宣称任何池「安静」之前，先只按地址扫一遍、出 topic0 直方图。** 池子家族不匹配会静默产出零，长得和死盘一模一样。
  - **判据（新增 16b）：控制窗口必须对准正确块高。** state 里记的 xDEUS #1492 unstake 块高是 53002812，**tx receipt 实际是 53003804**（时间戳吻合 2026-10-23T23:09:15Z）。用错块高做对照会返回 0，看起来像过滤器坏了。**控制块高一律从 `eth_getTransactionReceipt` 取，不要从笔记里抄。**
  - **判据（新增 16c）：`slot0`/`globalState`/`fee`/`liquidity` 全部 revert 的池子不是 Slipstream。** 要探 `getReserves`(`0x0902f1ac`) 与 `stable()`。最深池 `0x3E97c5EC` 实测 `stable=0`（volatile）、`getReserves` 正常返回 → **Aerodrome classic(Solidly)**，此时储备比值才是正确 mark（CL 池才不是）。旧笔记断言的「Slipstream」是错的。

- **最深池确实死了，且死得更久。** 全量地址扫描 53010000-53019896 只回 **3 条日志，全部来自同一笔 04:39:43Z 的 tx** `0x7b71081f`。到本轮 08:05Z 已 **205 分钟**零事件。对照：00:24Z 砸盘窗口同过滤器仍回 9 笔 → 真死。**但它不是「没有成交」，它是「这个池没人用」** —— 真成交在三个次级池。两池 mark 差 −0.86%（最深 $0.017763 vs 活跃 $0.017918），一致性够用，门槛不受影响。

- **两条前瞻信号连续第三轮没动。**
  - 两个新钱买家一颗没卖：`0x7f6aba75` **335,249.4994426125**、`0x6a45ca8b` **70,034.14033726917**，逐位不变 —— 连活跃盘口都没用来派发。
  - `0xbb0f7533` 的 xDEUS **#1396 仍未烧**（`tokenOfOwnerByIndex = 1396`），4,000 块内 escrow Burn **0 笔**。**下一笔砸盘扳机没扣动。**
  - Escrow **29,108,661.6747**（本轮 Δ 0），24h **−298,630（−1.02%）**，5%/日 线 1,455,433 —— 24h 流出只有它的 **1/4.9**，无 unstake 压力。xDEUS 供应 1727（24h **+2**，质押仍是净增）。CLAIM 金库 **340,081,346.43**，24h 净出 **193,983 DEUS ≈ $3,472/日**（低于 30d 的 283k–350k 区间）。
  - ⚠️ **DEUS 总供应 24h 是 −19,693，与 7d 口径 +65,381 净增发相反。** 不拿单日覆盖 7d 账本，两个都记下，等 7d 窗口重测再定论。

- **原始来源**：最深池 `0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa`（Aerodrome classic，liq $682,345）· 活跃池 `0x58dBa34e` / `0x1B2f3f5C` / `0x75bc1495` · `eth_getLogs` @ `base.gateway.tenderly.co` · DexScreener `api.dexscreener.com/latest/dex/tokens/0x940A…089B` · escrow `0xA85A…C373` · xDEUS `0xe6d5f7439Bc236C40054e2275f765f59343D4431` · CLAIM `0x5cbf5dfa…879a`

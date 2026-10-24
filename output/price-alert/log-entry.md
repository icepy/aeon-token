### price-alert
- **Skill**: price-alert
- **Token**: DEUS (0x940A319B75861014A220D9c6c144d108552B089B)
- **Current**: $0.01761830 | 1h: +0.17% | 24h: +0.13%
- **ATH**: $0.06876（2026-05-28 15:35 UTC）[UNCHANGED — 现价距 ATH 还有 +290.28%]
- **Sharp-move gate**: QUIET（实测 +0.17%，离 ±20% 门槛极远）
- **Targets evaluated**: 0.012, 0.025, 0.032, 0.041 → 全部 no-cross（0.012 −31.89% · 0.025 +41.90% · 0.032 +81.63% · 0.041 +132.71%）
- **Verdicts fired**: NONE
- **Notifications sent**: 0
- **Status**: PRICE_ALERT_OK

**取数（全部链上实测，不采信 API 的 h1）**
- 1h 窗口用时间戳二分钉死：blk 53024389 → 53026189，实际间隔 **恰好 3600s**，2.0 s/块。不是「最近 1800 块」的近似。
- 最深池 `0x3E97c5EC`（Aerodrome classic / Solidly）储备：VIRTUAL 526,949.5383 → 527,320.3462，DEUS 18,897,831.3862 → 18,884,542.5680。比价 **0.02788413 → 0.02792338（+0.141%）**。
- USD 腿：ETH/USD **$2,363.62**（WETH/USDC V3 `0xd0b53D92`，token0=WETH 方向已核）；VIRTUAL = 0.00026694 ETH = **$0.630951**。合成 **$0.01761830**。
- 交叉校验：三个 DEUS/USDC V3 池实测 **$0.01757362 / $0.01751881 / $0.01746856**，中位 **$0.01751881**。最深池 mark 高出中位 **+0.57%**，与历史同量级。DexScreener 印 $0.01766（差 −0.24%）。尘埃池 $0.01851（liq $1.30）已排除。

**四道 gate 全部未触发 —— 本轮不出声**
- **ATH**：存储值 $0.06876 是 CoinGecko 2026-05-28 的真历史高点，非跟踪起点，现价低 74%。不会假触发。
- **Sharp move**：+0.17%，离 20% 差两个数量级。
- **Targets**：四个价位最近的是 $0.012，还差 −31.89%。
- **结论：不发通知。** 按 STRATEGY「只在触发条件成立时推送」。

**🔴 本轮最重要的一条：取数过滤器本身做了判别力测试**
- 上一轮记下的 Sync topic0 `0xcf2aa508…f982149848a` 是真的。本轮**先**做地址级全量扫（不设 topics）出 topic0 直方图，再解码 —— 没有重犯家族混扫。
- **判别力验证（同一窗口 blk 53024572–53025572，已知含 2 条真 Sync）**：真 topic0 → **2 条**；我故意敲错一个字符的 `…d44a2abdf50e…` → **0 条**；全 `0x01*32` 假 topic0 → **0 条**。**三者可区分，说明这个端点不会把错过滤器静默返回成「有日志」或「池子死了」。** 这一步以前没做过，现在有了负对照。

**⚠️ 一次差点误判的坑（值得记）**
- 最新 1000 块窗口内**地址级扫就是 0 条日志**。若只看这一段，会得出「池子已死」。往前翻窗口才发现 10:27:33Z / 10:41:35Z / 10:47:19Z 各有 3 条（Swap+Sync+自定义）。**最近一次事件 10:47:19Z，距本轮 46.1 分钟。** 是**真静音**，不是假零 —— 但只有翻了多个窗口才能确认这一点。TELL 17 再次生效：死/活判定每轮重测，不继承。

**本小时真实成交（2 笔，极其清淡）**
- 买 1 笔 **13,513.23 DEUS** 出池；卖 1 笔 **226.68 DEUS** 入池；**净 −13,286.55（DEUS 流出池）**，即买方占优但量极小（约 $239）。
- 对比 09:13Z 那小时 84,920 DEUS，本轮量缩到 1/50。**价格是被「没人交易」托住的，不是被买盘抬住的** —— mark 的 +0.17% 不构成方向证据。

**前瞻触发（这才是要盯的，不是当前价格）**
- **xDEUS #1396 仍未烧**：`0xbb0f7533` 的 `balanceOf(xDEUS)=1`、`tokenOfOwnerByIndex(owner,0)=1396`，本轮亲测。DEUS 余额仍是 **0.0000**。这是下一次质押仓砸盘的扳机。
- **250k 在位者 `0xf0a04b07`（EIP-7702）** 本轮余额 **250,000.1252，逐位未变** —— 还有 5 倍于上次 print 的存量没出。
- 上次大买的两个地址 `0x7f6aba75`（335,249.4994）/ `0x6a45ca8b`（70,034.1403）**连续第五轮逐位未变**，没在今天这波清淡里出货。
- 过去 6h 全链 escrow Burn 只有 1 笔：`0xcae798c0` 的 #425 放 5,000 DEUS（08:16:23Z），**且仍未卖**。负对照 0 条。

**原始来源**
- 最深池 `0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa` · `getReserves()`=`0x0902f1ac` · `token0()`=`0x0dfe1681` · `token1()`=`0xd21220a7` · Swap topic0 `0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b` · Sync topic0 `0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a`
- USDC V3 池 `0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b` / `0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642` / `0x75bc14950Ab093cBd1f80BbbDf458596939180A3`（`slot0()`=`0x3850c7bd`）
- VIRTUAL/WETH Solidly `0x21594b992F68495dD28d605834b58889d0a727c7` · WETH/USDC V3 `0xd0b53D9277642d899DF5C87A3966A349A798F224` · VIRTUAL `0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b` · WETH `0x4200000000000000000000000000000000000006`
- escrow `0xA85A38796B951CE87B378538b32B3E6Ee3C4C373` · xDEUS `0xe6d5f7439Bc236C40054e2275f765f59343D4431` · Burn topic0 `0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35`
- RPC `base.gateway.tenderly.co` · DexScreener `api.dexscreener.com/latest/dex/tokens/0x940A…089B`（http 200）

### price-alert — under the hood
- 🔧 DexScreener 2 次（均 200）· Tenderly `eth_call` 约 45 次 · `eth_blockNumber`/`eth_getBlockByNumber` 约 20 次 · `eth_getLogs` 分窗约 30 次 · 7 个自建诊断脚本
- ✅ 本轮新增两个负对照：topic0 判别力测试（真 2 / 错 1 字符 0 / 全假 0）、escrow Burn 负对照（0）
- ⚠️ 环境注记：本机 RPC 要求 `eth_call` 显式带 block tag，省略会报 `-32602 invalid params`；`eth_getLogs` 公共端点硬限 1000 块，1800 块窗口必拒。
- 未发通知（四道 gate 均未触发）；state 原子写入 `jq empty` 通过，`.bak` 已滚动。

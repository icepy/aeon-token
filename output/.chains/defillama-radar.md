**defillama-radar** · 2026-11-03 · 可报 3

来源 `https://api.llama.fi/protocols` · 8919 条 · HIT/MISS 两份 id 逐条相同（非缓存假零）

**1. BOND Capital** · 储备货币 · $177,632 · `id 9314` · 登记 11-02 21:55Z
自述"Robinhood Chain 上的机构级储备资产，$BOND 由国债储备背书，带 NAV 下限"。**但 `chains` 写 Arbitrum，`address` 是 `robinhood:0xEB288E3ca1607E7B921BCb47d5831E88331D65ef`，描述又写 Robinhood Chain —— 三处互斥。** 无网站 · 推特 `BondDotCeo` · `audits: 0`

**2. Exceed Finance exBTC** · 收益 · Solana · $652 · `id 9315` · 11-02 21:59Z
以 cbBTC 标称付息，资金来自比特币抵押放贷。`misrepresentedTokens: true`

**3. Exceed Finance exSOL** · 流动性质押 · Solana · $122,068 · `id 9316` · 11-02 21:59Z
以 SOL 标称付息，来源是质押 SOL + SOL 借贷 + 有担保信用。`misrepresentedTokens: true`
站点 `https://www.exceed.finance/` · 同族 `exUSDC`（$595,587）10-28 已入库

## 两条要看背景

- **第 2、3 条按源站口径其实该被丢。** 扫描吃的缓存快照里它们 `parentProtocol` 为空，源站已补成 `parent#exceed-finance`（同族 exUSDC 本来就在这个父下）。**过滤对"登记 <1 小时"的条目系统性失效** —— 下一轮会走 parent 桶自愈，不会重复打扰。
- **BOND Capital 的链到底在哪，DefiLlama 自己没定。** 全量 133 条 `robinhood:` 前缀里，这是唯一一条新登记却报别的链的。**如果它实际在 Robinhood Chain，金额约 $177K，是个新标的；如果链填错了，那 TVL 也不可信。别直接采信。**

漏斗：新增 20（可报 3 / 过滤 17）· parent 7 · category 8 · 空 `chains` 2 · 拉取失败 0 · 非基线轮
空 `chains` 占全量 17.6%（五轮持平）· **近 3 天登记 27 条里 23 条无链（85%）**，继续走高
判据修正：9290–9293（Kraken/Coinbase/Upbit/Bithumb）不是永久空洞，是延迟 3 天批量回填 —— 上轮写的"id 必须 ≥ 历史最大值"校验规则作废
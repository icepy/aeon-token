**defillama-radar** · 第 23 轮 · 可报 2 条

全量 9070 / 新增 14（可报 2 · 过滤 12）

---

**1. Trestly** · Bridge · Ethereum / Binance · TVL $9,267
把 USDT 从 Ethereum 和 BNB Chain 桥到 Kaspa，铸成 1:1 全额抵押的 kUSDT（USDT 锁在自家金库）。
`id 9469` · `listedAt 2026-11-17T19:00:41Z` · 无官网字段 · 无 parent

**2. Polydash** · Launchpad · Robinhood Chain · TVL $21.99
Robinhood Chain 上的生态入口，含 Polypad 发射台 + 代币化基金金库。
`id 9468` · `listedAt 2026-11-17T18:57:39Z` · https://polypad.family · 无 parent

---

**看点**：`Polydash` 是 Robinhood Chain 新冒出来的发射台入口，TVL 只有 $22 -- 名字先到、量还没到，属「基础设施先上」那一类，不是有资金进场。`Trestly` 是纯桥，量集中在 USDT→Kaspa 这条单一路径，$9.3K 同样是小额起步。

**被过滤的 12 条里没有误杀**：8 条 `parentProtocol` 子条目（`EscapeSwap`/`EscapeHub Launchpad`/`Liquidium WTF`/`GrowStreams Spot`/`dreamDEX Perps`/`Buttonwood Cash`/`Kalos V4`/`BTR V2`）+ 4 条空 `chains` 且无 TVL（`Cool Eggs`/`Nyraa`/`Marg`）。唯一「有白名单链但被 parent 挡」的是 `EscapeHub Launchpad`（Robinhood Chain+Solana+Base，$1,510）与 `Buttonwood Cash`（Robinhood Chain，$13）-- 都是母协议铺子条目，符合铁律。

---

**上轮预告兑现**：第 22 轮记的尾部空洞 `9455`/`9456` 本轮**双双出现**，即 `Buttonwood Cash` 与 `Kalos V4`，`listedAt` 分别 11-16T22:59:19Z / 23:03:51Z -- **都早于上轮快照的 23:38Z**。这正面验证了 11-03 修正后的判据：id 分配先于数据入库，「永久空洞」不存在，只有「暂未回填的分配号」。

**CF 校验**：`?_cb=` 源站取数 `cf=MISS`，`etag W/"6afce57d-933178"`、`last-modified Tue, 17 Nov 2026 23:38:37 GMT`、9070 条。两向差集 `only_raw=[]`、`only_seen=['4818']`（连续第十四轮真下架）。

**数据源**：https://api.llama.fi/protocols · 口径 `dl-v1` · `STATUS: DEFILLAMA_RADAR_OK`
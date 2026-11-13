**defillama-radar** · 第 18 轮 · 可报 4 条 · 全量 9026 / 新增 14

## 一、可报（4 条，TVL 合计 $9.28M）

- **Swan DAO**（9415）· Ethereum · TVL **$5.19M** / staking $113.4K · `CDP` · 由 wstETH 背书的 DAO 自有稳定币（swanUSD），主打零息贷款。`audits=2`，全轮唯一带审计的新条目。`url=swanusd.com`、`twitter=MonolithMarket`、`listedAt 11-12T17:52:32Z`
- **Sigma Labs**（9412）· Ethereum · TVL **$3.89M** · `Risk Curators` · 链上风险研究与量化策略实验室，做多链基础设施。`address` 空、`url` 空、`audits=0`、`listedAt 11-11T22:48:59Z`
- **DeltaUSD**（9420）· Base / X Layer / Berachain / Plasma / Binance · TVL **$162.0K** · `Basis Trading` · 收益累积型合成美元，运营方主动管理背书，策略写明 delta 中性资金费/基差/价差。按 `chainTvls` 拆：Base $81.1K、X Layer $59.8K、Berachain $20.4K、Plasma $751.6、Binance $7.1 → **白名单链只占 50.0%**（Base+Binance），另 50% 在非白名单链。`listedAt 11-12T21:38:03Z`
- **NoxFund**（9424）· Binance · TVL **$43.0K** · **`Ponzi`** · BNB Chain 上按日固定 USDT 返利、45 天本金锁仓、七级推荐分成。**类目原样带、不做判断**，但 `category` 已自报为 Ponzi。`listedAt 11-12T22:35:07Z`

## 二、过滤 10 条的真边际（逐条可数）

**`parent` 桶 6 条，真边际 3 条（全部仍被别桶挡）：**

| id | 名称 | 去掉 parent 后 |
|---|---|---|
| 9425 | `wstO Vault` | 仍挡（`parent#o1-exchange` 之外，白名单链链上 TVL 全为 0，量全在 staking $3.97M） |
| 9416/9417/9418 | `Kalos Marketplace` / `Launchpad` / `Trade` | 仍挡（`chains=[]`，三条同父 `parent#kalos`，18:25:14→24Z 相隔 5s/5s） |
| 9421/9422 | `Boxa V1` / `V2` | 仍挡（V2 `chains=[]`；V1 链 `Elysium Kinetiq` 非白名单） |

**空 `chains` / 链白名单桶 4 条：** `Solflare Card`(9413，`Crypto Card Issuer`，`chains=[]`，Solflare 官方自托管 Visa 卡) · `Perpsplexity`(9414，`Sui`，$70.0K) · `Kleos`(9419，`Elysium Kinetiq`，$48.5K) · `Hubble Sonic`(9423，`Sonic`，$3.3K)。

**本轮无一「本可报却被误挡」的条目** -- `parent` 的 3 条真边际全部同时被空链/非白名单链挡掉，去掉 parent 也进不来。

## 三、洞察

### 1. `Elysium Kinetiq` 第三次出现，加链结论仍不变：不加
本轮 3 条新增挂该链：`Kleos` $48.5K、`Boxa V1` $80.9K（被 parent 挡）、`Boxa V2`（空链）。该链存量已 **18 条**（上轮 15 → 本轮 18）。**但本轮加链的净边际 = 1 条 `Kleos` $48.5K** -- `Boxa V1` 有 parent、`Boxa V2` 空链，加链救不了。三轮边际：$514 → $2.6K → $48.5K，**在升但仍然是个位数条数**，代价是删 9026 条 seen 重做基线。**结论不变：不加。**

### 2. `9412`/`9415` 回填 -- 上轮缺席的高号真的回来了
上轮记录「`9412-9415` 虽高于历史最大 id 却缺席，证明高号也可能待回填」。本轮 **`9412`（Sigma Labs）、`9415`（Swan DAO）双双出现**，正落在那段区间里。**「分配号 + 延迟回填」机制第二次实盘复现**（首次 11-02→11-03 的 9290-9293）。`9413`/`9414` 同批出现。仍然缺 `9382`（连续第三轮）、`9391`（连续第二轮）。

### 3. 可报 TVL 和 vs 单条体量：本轮**首次不比了**
前两轮都在记「可报 TVL 和不代表新增体量」（418× / 1279×）。本轮可报合计 **$9.28M**，新增 14 条里最大的被丢弃条目是 `wstO Vault` 的 **staking $3.97M**（`tvl=0`）-- 但它是 `staking` 不是 `tvl`，**不可直接与可报集的 `tvl` 相加比较**。可比的 `tvl` 侧本轮没有单条超过可报最大值。**读数：这是 17 轮来第一次可报集本身就吃到了大体量，因为两条 $M 级（Swan DAO / Sigma Labs）恰好既无 parent、类目不属 EXCL、又挂在 Ethereum。**

### 4. `wstO Vault` 是「`tvl=0` 但 $3.97M 在 staking」的极端例
`chainTvls` 里 `Robinhood Chain=0`、`Base=0`，量全在两条链的 `-staking` 子项（$3.67M / $296.7K）。**这是「`chains` 是部署声明、`chainTvls` 才是实际量」迄今最极端的一例** -- 一条 `chains=['Robinhood Chain','Base']`（都是白名单）的条目，白名单链上的 `tvl` 是 0，全部价值在质押侧。若只看 `tvl` 会误判为空壳。

### 5. `listedAt` 整分秒值本轮 0 条
新增 14 条 `listedAt` **无一为整分 `:00`**（上轮 22 条里 2 条）。全量仍 69/7350 = 0.94%。跨度 **23.91h**（11-11T22:48:59Z → 11-12T22:43:27Z），最小间隔 **4s**（`Boxa V1`→`V2`，同 `parent#boxa`）。同秒 ≥3 条批量指纹新增 **0 组**，最近一组仍是 11-07T14:26:04Z(n=4)。

### 6. `XMAQUINA`(9317) 仍在 `filtered`，无变化
第 9 轮被空链钉成 `filtered` 的清单内协议，本轮复查 `chains` 仍为 `[]`、`tvl=None`。**补链不补报，设计如此，不动 seen。**

## 四、审计与校验

- **CF 校验通过：** 常规 `HIT`、etag `W/"6af64df0-928e7c"`、`last-modified Thu, 12 Nov 2026 23:38:24 GMT`、`cache-control: public, max-age=300`；`?_cb=` + `no-cache` 源站 `MISS`，**etag 与 last-modified 与 HIT 完全相同**，`only_hit=[]` / `only_miss=[]`，9026 条逐条相同；14 条新增 11 字段两份快照**零差异**。`parentProtocol` 翻转连续九轮未复现。
- **漏斗：** 全量 9026 · 新增 14（可报 4 / 过滤 10）· seen 命中 9012 · `parent` 6 · `category` **0（真 0，本轮无 CEX/Chain/Interface 新增）** · 空链/链白名单 4 · 无 id 0 · 拉取失败 0 · 重报 0。
- **`only_seen=['4818']`、`only_raw=[]` 连续第九轮** → 真下架，保持引用。
- **`chains=[]` 全量 1618/9026 = 17.93%**（上轮 17.90%，十轮区间 17.4-17.93）。
- **`max_id=9425`**，`9382`（连续第三轮）/`9391`（连续第二轮）缺席按「待回填」处理，不改求差逻辑。非数字 id 仍只有 **`<5471>`（`OpenTrade`，$237.6M）** 一条，`seen` 里键仍是带尖括号的形式 -- 字符串键未归一化的裂缝依旧存在。
- **单侧读数：** 加密侧 4 / AI 侧 0 -- 本源只有加密，**高命中不是词表变准**。

数据源：`https://api.llama.fi/protocols` · 2026-11-13 第 18 轮 · `dl-v1`
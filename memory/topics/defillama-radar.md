---
title: DefiLlama Radar
description: 第二层（名字）发现通道 —— 用全量 id 求差找白名单链上新登记的协议。机制、四态、判据与已知陷阱（含延迟批量回填使「永久 id 空洞」判据作废、parentProtocol 跨快照翻转、address 前缀不可替代 chains、旁路收益的窄口径）。
tags:
  - crypto
  - discovery
  - defillama
resource: https://api.llama.fi/protocols
timestamp: 2026-11-03T00:30:00Z
---

# DefiLlama Radar

发现层三通道之一（论文 `arxiv-radar` ~4 个月 → 代码 `github-radar` ~1–2 个月 → **部署并拿到 TVL = 本通道 ~0**）。
平行，不是下游。词表与白名单全在 `skills/defillama-radar/scan.py`，本文件不抄一份，只记**机制与判据**。

## 为什么只能靠 id 求差

DefiLlama 的 `listedAt` 覆盖不全且**缺失不随机** —— 缺的是头部大协议（TVL≥$1B 的 68 个里缺 16 个：Lido / LayerZero V2 / Robinhood / SSV Network / WBTC / Sky Lending / Arbitrum Bridge）。所以新度只能靠 `memory/defillama-seen.json` 存全量 id、本轮求差。

**反面**：`listedAt` 在**近期新登记**上覆盖完整（近 30 天有值的逐条都在），可作交叉校验，不能替代。

## `id` 单调递增（2026-10-28 实测，求差正确性的正面证据）

7186 条有 `listedAt` 的样本：

| 检验 | 读数 |
|---|---|
| 按 id 排序，相邻对 `listedAt` 逆序率 | **2.6%**（190/7185） |
| id 最小 200 条 `listedAt` 中位 | 2021-11-04 |
| id 最大 200 条 `listedAt` 中位 | 2026-10-19 |
| 10-20 起连续登记 | 91 条，id 9164–9254，**缺口 0** |

由此得到一条独立校验：**若差集里出现小于历史最大 id 的条目，那不是新登记，是旧条目回流（DefiLlama 会下架再上架）。**

**2026-11-02 曾判「缺口成群存在」，2026-11-03 已被推翻。** 11-02 看到 9289 → 9294 之间 4 个 id（9290–9293）整段缺席，判为「id 是分配号，下架/回收留永久空洞」，并立了校验规则「差集元素 ≥ 历史最大 id 才是新登记」。**11-03 第 8 轮这 4 个 id 全部出现**，是 `Kraken` / `Coinbase` / `Upbit` / `Bithumb` 四条 CEX，`listedAt` 全在 `2026-11-01 20:47–20:48Z` 这 35 秒内。

**真正的机制是延迟批量回填：** DefiLlama 成批导入同类别条目（此处是交易所名称），id 按分配序落到号段里，但数据要几天后才出现在 `/protocols`。所以**「永久空洞」不存在，只有「暂未回填的分配号」**——缺席 ≠ 永远不会出现。

**修正后的求差判据（替换上文的「≥ 历史最大 id」规则）：**

| 差集元素特征 | 判定 |
|---|---|
| id ≥ 历史最大 id | 新登记 |
| id < 历史最大 id，且**同一分钟 ≥3 条** | **批量回填，仍是真新增** |
| id < 历史最大 id，单条 | 旧条目回流嫌疑（下架再上架） |

同秒批量指纹的另一个用途见下文[同秒批量](#同秒批量去重)。**注意：`id` 单调递增的假设仍成立（分配序），失效的只是「分配序 = 出现序」。**

## 陷阱：CDN 快照让差集恒为 0

`api.llama.fi` 走 Cloudflare，`cache-control: max-age=1798`。两轮若落在同一份边缘对象内，**id 集合必然相同，差集恒 0** —— 与「今日无新协议」完全同形。

**2026-10-28 实例**：基线轮 06:22Z 与第 2 轮 06:31Z 同吃 `last-modified 05:39:24Z`、`age 751`、`cf-cache-status: HIT`。加 `?_cb=<ts>` + `Cache-Control: no-cache` 复取源站（`MISS`、`last-modified 06:02:09Z`、etag 变）后：id 集合仍相同，但 **1255/8859 条 `tvl` 已变（全量 TVL −$610M）** → 0 为真。

**2026-11-02（第 7 轮，连续第四轮正面证据）**：常规 `HIT`（`last-modified Sun, 01 Nov 2026 23:38:10 GMT`、`age 382`、etag `W/"6ae7cd62-905a80"`）· `?_cb=` + `no-cache` 取到 `MISS`，**etag 与 last-modified 与 HIT 份完全相同**。两份 8899 个 id 逐条相同，`only_hit` / `only_miss` 均为空集。**本轮 0 可报不是缓存假零。**

## 今天这条判据要推翻：`description` 旁路并不优于 `url`（2026-11-02）

11-01 记过「description 旁路 +38% 优于 url +39%，且桥噪声 23% vs 46%，旁路收益 3 倍」。**本轮按同源数据重算，这个结论站不住。**

同一份 payload、同一套白名单正则，只把窗口对齐后：

| 窗口 | 通过现行漏斗 | 空 `chains` 挡 | url 召回 | url 净（去桥/Foundation） | desc 召回 | desc 净 |
|---|---|---|---|---|---|---|
| 7d | 8 | 15 | 11 | 11 | 10 | 10 |
| 30d | 77 | 76 | **44** | 21 | **31** | 23 |
| 90d | 256 | 139 | 73 | 48 | 56 | 47 |

**三条修正：**

1. **召回量 `url` 反而更高**（30d 44 vs 31，90d 73 vs 56）。11-01 的 +38% vs +39% 是把两个不同分母的结果并排写，不是同一分母的比较。
2. **去噪后两者打平**（30d 净 21 vs 23，90d 净 48 vs 47）。所谓 description 更「干净」的优势，在把桥/Foundation 两类一起削掉后消失。
3. **桥噪声的 46% 是被一个同秒批量污染的单点抬起来的，不是常态。** 30d `url` 分支 44 条里 22 条是桥类，其中 **18 条全部落在 `listedAt = 1791380325`（2026-10-07T13:38:45Z）这一个秒**（`Squid` / `Layerswap` / `Relay` / `Snowbridge` / `Hyperbridge` …）。剔除这一秒后，30d 空挡只剩 55 条，url 26 条（桥 4），desc 28 条（桥 4）—— **两者几乎完全一致**。

**因此正确的结论是：两条旁路是同族的，不是替代关系。** 全量 773 条空 `chains` 组里 url 命中 586、desc 命中 190、交集 132 —— desc 独有的只有 58 条。真正的增量来自**并集**（30d 净 36 vs 单条 21–23），不是选哪一条。

**可执行的方向（下轮改 `scan.py` 时用）**：不要二选一，写成 `chains 为空 → (url 非空 OR description 命中白名单链)` 的并集，且**必须带同秒 `listedAt` 批量去重**（判据：同一 `listedAt` 秒内 ≥3 条即视为批量录入，整批不进拼接结果）—— 否则 10-07 那 22 条会把报告污染成 18 条桥。

**候选集上限（务必先看这个）**：并集净后 30d 只多 36 个名字、90d 78 个。**这不是能改变信噪比的量级**，是「每周多几条可看」的量级。改之前先接受这个上限，别指望它翻转漏斗。

## 被挡桶拆分：改旁路的收益仍大于加链，但两者都在小量级（2026-11-01，11-02 复核）

近 30d 漏斗输入（「通过 + 被挡」，只含带 `listedAt` 的条目）：

| 桶 | n | 占输入 |
|---|---|---|
| 通过现行漏斗 | 77 | 43% |
| **只被空 `chains` 挡** | **76** | **42%** |
| 只被「链不在白名单」挡 | 26 | 15% |

加链的收益上限 ~15%，改旁路的理论上限 ~42% —— 方向仍是压旁路。但按上节去噪后的净增量，**旁路真正的可兑现收益是 30d +36 / 90d +78，不是 +42%**。两个数字都要带着看。

## 口径纪律：两个「空 chains 占比」不可混用（2026-11-01，11-02 复核）

| 口径 | 读数 | 稳定性 |
|---|---|---|
| 全量 `chains=[]` | 1573/8919 = **17.6%** | 10-30 起五轮：17.4 / 17.5 / 17.5 / 17.5 / 17.6 |
| 带 `listedAt` 子集内的滚动窗占比 | 3d 高 · 7d 高 · 30d 约三分之二 | 五轮同形 |

滚动窗只覆盖有 `listedAt` 的条目（空 `chains` 群体里只有约 37% 有 `listedAt`，本身就有选择偏差）。**报「新登记三分之二不带链」时必须标住「带 `listedAt` 子集」这个限定，别与全量 17.6% 混读。**

**近 3 天登记的读数在走高（11-03）**：27 条里 23 条 `chains=[]` = **85%**，上轮（11-02）是 65.5%。**但别据此推「新协议越来越不带链」** —— 见下节：本轮 20 条里 17 条空链，其中 12 条被 `parent` / `category` 桶挡掉，**真正只被空链挡的只有 2 条**。占比升高不等于漏斗杀伤力升高。

## 空 `chains` 群体的真实画像（2026-11-01，11-03 复核）

| 特征 | 读数 |
|---|---|
| 空 `chains` 总数 | 1573（全量 8919 = 17.6%） |
| 其中 `tvl` 非空 | **0 条**（第五轮确认，`chains=[]` ⟺ `tvl` 缺失） |
| 其中带 `parentProtocol` | 619 条 |
| 其中**有 `url`** | 1301 条 = 83.6%（11-01 读数，未重算） |
| 去 parent/EXCL 后 | **773 条**（11-01 读数） |
| 其中 url 命中 | 586（75.8%） |
| 其中 description 命中白名单链 | 190（24.6%） |
| 两分支并集 | **644**（交集 132） |

即这个群体**不是「一无所有」，是「有站点、有描述、无链、无 TVL」** —— 缺的两个字段是同源录入缺口。这正是任何旁路可行的原因：信息在，只是不在 `chains` 里。

**但旁路的可兑现收益要按「只被空链挡」的窄口径算，不是按 42% 的宽口径。** 11-03 实测：本轮 17 条空链条目里，12 条同时被 `parent` / `category` 挡掉（旁路改不动），能救的只有 2 条（`WARs DEX` / `Volt Protocol`）—— 且这两条的 url 与 description **都不命中任何白名单链**，所以并集旁路本轮实际救回 **0 条**。**旁路是实现细节，不是产能开关。**

## `parentProtocol` 会在两份快照间翻转 —— 该过滤对「刚登记」条目系统性失效（2026-11-03）

第 8 轮实测：扫描撞上 25 分钟前的边缘缓存（`HIT`，`last-modified 2026-11-02T23:02:20Z`），其中 `Exceed Finance exBTC`(9315) / `exSOL`(9316) 的 `parentProtocol` 为 `None`，**通过过滤进了报告**。随后 `?_cb=` + `no-cache` 取源站（`MISS`，`last-modified 23:38:44Z`），**这两条的 `parentProtocol` 已变成 `parent#exceed-finance`**（同族 `exUSDC` 本来就在这个父下）。

**两份快照的 id 集合仍然逐条相同（8919 条，`only_hit` / `only_miss` 空集）—— 缓存校验能证明「没有漏条目」，但证明不了「字段值是最新的」。** 这是 CF 校验的一个新边界，与 10-28 那条「差集恒 0」是不同的问题。

**含义：`parentProtocol` 是 DefiLlama 事后补录的字段，录入当时缺失、几分钟内补上。** 所以版本铺开类条目在登记后的一段窗口内会漏过 parent 过滤。该过滤器的真实有效面是**登记 ≥1 小时**的条目。

**自愈路径成立但慢一轮：** 被误放的条目按现行实现记 `notified: None`，下轮拿到新快照后走 parent 桶、记 `filtered`，不会重复打扰。**若要根治，parent 判定须改为「任一份快照有 parent 即丢」** —— 代价是每轮两次取数，与「一轮 1 次请求」的铁律冲突，尚不建议改。

## `address` 前缀不能替代 `chains`（2026-11-03）

`BOND Capital`(9314) 三处互斥：`chains=["Arbitrum"]`、`chainTvls={"Arbitrum": …}`、`address=robinhood:0xEB288E…5ef`、`description` 又说 "onchain central bank on **Robinhood Chain**"。

**「`address` 前缀是更硬的事实」这个想法经检验站不住**：全量可比条目里 `address` 前缀与 `chains` 不一致的占 **6.1%（96/1577）** —— 含桥（`Arbitrum Bridge` 地址在 arbitrum 而 `chains=Ethereum`，语义正确）、多链部署（`Velodrome V3` 地址在 base 只报其他链）、大量老条目。**这个噪声水平使 `address` 进不了过滤器，只能当人工复核线索。**

样本量提醒：133 条 `robinhood:` 前缀里，`chains` 不含 Robinhood Chain **且** TVL 非空的只有 2 条（`BOND Capital` 与老条目 `IXS`），**其余 131 条要么正确、要么空链无 TVL**。这是稀有异常，不是普遍口径偏移，不值得改过滤器。

**同价陷阱排除法**：BOND 的 $177,632 与 `Camelot V4` 的 $177,634 只差 $1.91，看着像 TVL 串号。两条独立检验否定：① 全量 4250 条 TVL≥$1000 里，相邻差 <$5 的对数占 **11.7%（498 对）**，近价不稀有；② 两份快照的位移不同步（+$80.34 vs +$82.93）。**「数值接近」不是串号判据。**（另：`Camelot V4` 与 V2/V3 共用合约地址，但 TVL 只有 V3 的 6.2%，是独立的新池子条目，非幻影。）

## 本轮漏斗口径（11-03，供下轮对照）

新增 id 20（可报 3 / 过滤 17）· `parent` 7 · `category` 8 · 空 `chains` 2 · 无 id 0 · 拉取失败 0 · 重报 0。**`category` 桶首次成为最大丢弃桶**（8 > parent 7），其中 4 条是 `Kraken`/`Coinbase`/`Upbit`/`Bithumb` 的批量回填（见上）、4 条是 Interface。**这是 EXCL_CATEGORY 生效的正面证据，此前七轮该桶读数多为 0–1。**

# Citations

- 实测数据：`https://api.llama.fi/protocols`（2026-11-03 第 8 轮；常规 `HIT` 8919 条、`last-modified 2026-11-02T23:02:20Z`、etag `W/"6ae9167c-9091f1"`；`?_cb=` + `no-cache` `MISS` 8919 条、`last-modified 23:38:44Z`、etag `W/"6ae91f04-909517"`；id 集合逐条相同）
- 实测数据：同上两份快照**字段值不同** —— `parentProtocol` 在 9315/9316 上由 `None` 变 `parent#exceed-finance`，全量 TVL 亦有变动
- 实测数据：`https://api.llama.fi/protocol/bond-capital` 与 `/protocol/camelot-v4`（2026-11-03；BOND `currentChainTvls={"Arbitrum": 177551.75638}`、`address=robinhood:0xEB288E3ca1607E7B921BCb47d5831E88331D65ef`、`audits: 0`、`twitter: BondDotCeo`、无 url）
- 实测数据：`https://api.llama.fi/protocols`（2026-11-01 第 6 轮；两份 payload 各 8892 条，etag `W/"6ae67bf0-903d78"`）
- 实测数据：`https://api.llama.fi/protocols`（2026-10-28 06:31Z 与 06:32Z 两次取数）
- 机制与铁律：[`skills/defillama-radar/SKILL.md`](/skills/defillama-radar/SKILL.md) · 实现 [`scan.py`](/skills/defillama-radar/scan.py)
- 同族判据：[lessons · 假零与断层](/topics/lessons.md#假零与断层)

---
title: DefiLlama Radar
description: 第二层（名字）发现通道 —— 用全量 id 求差找白名单链上新登记的协议。机制、四态、判据与已知陷阱（含延迟批量回填使「永久 id 空洞」判据作废、parentProtocol 跨快照翻转、address 前缀不可替代 chains、旁路收益的窄口径、桶序有损、非数字 id 归一化会让老条目冒充新协议）。
tags:
  - crypto
  - discovery
  - defillama
resource: https://api.llama.fi/protocols
timestamp: 2026-11-12T00:10:00Z
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

## `filtered` 的不可逆性会咬到自己的清单（2026-11-04）

第 9 轮，清单内协议 **`XMAQUINA`**（id 9317，`category=RWA`，`chains=[]`，`tvl` 缺失，`listedAt 2026-11-03T00:45:05Z`）首次进入 `/protocols`，**被空 `chains` 桶挡掉、入库那一刻钉成 `filtered`**，此后永不重报 —— 即使它明天接上 `chains=["Base"]` 也进不来。

这不是回归，是 SKILL.md 明写的设计（「补 `chains` 不补报」「加链不回溯」「扩张不算新」）。但有三点值得记死：

1. **清单不参与任何桶的判定。** `memory/defillama-names.txt` 只决定 `in_names` 标注，不影响 `parent` / `category` / `chain` 任何一条。所以清单内协议被过滤时，**审计里不打星、不进 `out`、不留任何痕迹** —— 事后只能靠翻 `seen` 里 `first == 今天` 的条目人工比对。这不是缺陷，是「只做发现、不做判断」的必然结果。
2. **恢复可见性的正确做法是改 seen，不是删整表。** 只删 `memory/defillama-seen.json` 里 `9317` 这一条即可让它在下一轮重新走漏斗（属修订单条记录，非加链，**不需要重做基线**）。删整表会让 8925 条全部重灌成 `baseline`，代价与收益完全不对等。
3. **不要把这条当成「该加 `Base` 之前先重做基线」的信号。** `Base` 早在 `CHAINS` 里（本轮命中 915）；XMAQUINA 进不来纯粹因为它自己 `chains=[]`，加链救不了它。

## `parent` 首次成为绝对主导桶，且吃掉本轮最大 TVL（11-05 第 10 轮）

18 条新增里 10 条被过滤，其中 **6 条只被 `parentProtocol` 挡**（Privacy Pools V2 · HedgeHood Share Lending · StonkBrokers Books · StonkBrokers Clutch TV · Dexalot OmniVaults · Precept←`parent#templar-protocol`），同轮 `category` 桶为 **0**、空链桶 3。前九轮 `parent` 单轮 0–7，从未同时压过这两桶。

**这是录入潮的形状，不是回归。** 一批新增集中来自「同一母协议铺子协议」（StonkBrokers 两条、Privacy Pools V2、Dexalot OmniVaults、HedgeHood、Precept），正是 SKILL.md「版本号铺开是最大噪声源」要挡的东西。

**由此得一条读数口径：可报集的 TVL 和不代表本轮新增体量。** 本轮 8 条可报合计 TVL 仅 **$102K**（最大 `Axcess` $97.6K），而被丢弃的 `Dexalot OmniVaults`(9337) 单条 **$1.96M** —— 它只被 `parent` 一个桶挡。因为「不设 TVL 地板」是铁律，`out.json` 按定义**不含体量信息**，读「本轮最大的新协议」必须回看 `payload` 的差集全集，不能只读 `out.json`。

## `seen` 多出一条不属于 payload 的 id = 下架痕迹，不是损坏（11-05 首次观测）

本轮反向差集出现 `only_seen=['4818']`、`only_raw=[]`：id 4818（`first 2026-10-28`、`notified=baseline`）仍在 seen 里，但已不在 `/protocols`。seen 总数 8943 = 8924 命中 + 18 新增 + **1 下架残留**。

**判据：`only_seen` 非空而 `only_raw` 为空 ⇒ 条目不在了，不是读坏了。** seen 是只增不删的表（脚本从不移除 id），所以任何「seen 有、payload 无」的 id 都是 DefiLlama 侧下架；若这些 id 日后重新出现，会走 `seen` 命中、`notified != None` 分支，**静默跳过、不会重报** —— 这与 [id 单调递增 / 旧条目回流](#id-单调递增2026-10-28-实测求差正确性的正面证据) 记的「下架再上架」互相印证。**只看 seen 文件大小无法区分「下架残留」和「解析异常」，要看两个方向的差集。**

## 桶序会掩盖读数：`parent` → `category` 是一条有损链（11-07 第 12 轮首次定量）

`scan.py` 的判定顺序是 `seen` → `parent` → `category` → `chain`，每桶 `continue`，所以**一条记录只会记进它撞上的第一个桶**。第 12 轮 6 条新增全部被 `parent` 吃掉（`parent=6` / `category=0` / `空链=0` / 链白名单=0），审计读起来像「parent 是唯一问题」，实际不是：

| id | 名称 | category | 被 parent 挡后，去掉 parent 会怎样 |
|---|---|---|---|
| 9348–9351 | `Sparkling *` 四条 | **Interface** | 仍被 `category` 挡 |
| 9352 | `pump.fun Perps` | **Interface** | 仍被 `category` 挡 |
| 9353 | `Vesper V2` | Yield Aggregator | 空链也挡不住（`chains=['Ethereum']`）→ **唯一真边际** |

**`parent` 对本案的边际贡献只有 1/6。** 另外 5 条是双帽，`category` 桶**真实读了 5 条、显示 0**。

全量口径的重叠率（同一份 payload 实测）：

| 窗口 | `listedAt` 有值 | 带 parent | 其中 category∈EXCL |
|---|---|---|---|
| 7d | 63 | 24 | 11（46%） |
| 30d | 420 | 225 | **137（61%）** |
| 90d | 916 | 384 | 142（37%） |
| 全时段 | — | 2668 | 247（9.3%） |

**读法：`category=0` 不等于 `EXCL_CATEGORY` 没生效，只等于「没有不带 parent 的 EXCL 条目」。** 近 30d 里 EXCL 类目共 178 条，其中 137 条带 parent、只有 41 条不带 —— 即该桶在 30d 尺度上的可观测面只有 23%。反过来 `parent` 也同理：它吞掉了 61% 的本该记给 `category` 的条目，所以**「parent 占比升高」可能只是「Interface 类铺子协议变多」的同一个事实换了个名字**。

**不改代码。** 想让两个桶都可读需要改成「多标签计数」（一桶丢弃后继续判定其余桶），这与「只做发现」无关、只是审计口径，但会让 `drop` 各桶之和 > 新增数，破坏现有「新增 = 通过 + 过滤」的闭合式。真要改，须同步改审计行语义。**当前纪律：任何单桶「占比」读数必须注明桶序，且不能与其他桶读数做减法。**

## `id` 不是整数：`<5471>` 这种带尖括号的 id 存在，且它救了一轮（11-08 第 13 轮）

第 13 轮求差时按 `int(id)` 排序做 id 连续性校验，**直接崩在 `<5471>`（`OpenTrade`，RWA，TVL $245.6M，`chains=['Avalanche','Ethereum','Plume Mainnet']`，`parentProtocol=None`，`listedAt=2024-12-06T14:40:42Z`）**。这不是脏数据：该 id 自基线轮（10-28）就在 `seen` 里，`notified=baseline`，尖括号是 DefiLlama 侧原始格式。

**判据：`scan.py` 全程用 `str(p.get("id"))` 做键，这一点是对的 —— 任何「把 id 当整数处理」的校验脚本都会在这里翻车，且是崩在本地校验而不是扫描本身。** 好处也是实的：本轮 `<5471>` 与 `5471` 在 `seen` 里只有前者存在，说明字符串键没有归一化，所以**一个 `id` 从 `<N>` 变成 `N`（或反之）会被当成新协议重报一次**。本轮未发生，但这是 `seen` 键空间的一条已知裂缝，判「本轮新增」时若出现巨型老协议（本例 TVL $245.6M）要先查是不是 id 写法变了。

数字 id 侧：最大 **9362**，9340–9362 **连续无缺口**，连续五轮无「暂未回填的分配号」。

## 链白名单桶首次真正咬到输入，但 2 条里 0 条是「链不在白名单」（11-08 第 13 轮）

前十二轮 `链白名单` 桶读数多为 0（仅 11-05 有 1 条 `Lubics`）。本轮审计报 **`链白名单=2`**，看起来像白名单终于开始做功，实际不是：

| id | 名称 | chains | 真实原因 |
|---|---|---|---|
| 9354 | `BNQ` | `['Hemi']` | 链不在白名单（$538，`Hemi`） |
| 9362 | `Yellow Onchain` | `[]` | **空 `chains`**，不是链不匹配 |

`scan.py` 里 `if not hit` 一个条件同时吞掉「空 `chains`」和「链不在白名单」两种情况，审计只打一个 `chain` 桶。**所以 `链白名单=2` 里只有 1 条真属于「非白名单链」，另 1 条是空链。** 与上文 `parent → category` 的有损链同源：桶名比桶语义窄。

## `parent` 的真边际首次可以逐条数清：7 条里 2 条（11-08 第 13 轮）

本轮 7 条带 `parentProtocol`，逐条拆开：

| id | 名称 | parent | EXCL | 空链 | 判定 |
|---|---|---|---|---|---|
| 9355 | `Rocketswap Anubis V3` | ✓ | ✗ | ✓ | parent 与空链**双帽** |
| 9356 | `PeddleSwap V2` | ✓ | ✗ | ✗ | **parent 唯一** |
| 9357 | `PeddleSwap V3` | ✓ | ✗ | ✗ | **parent 唯一** |
| 9358–9361 | `Jupiter *` 四条 | ✓ | ✗ | ✓ | parent 与空链**双帽** |

**`parent` 真边际 = 2/7**，且只有 `PeddleSwap V2/V3` 这两条是「有白名单链（`Robinhood Chain`+`Base`）、只被 parent 挡」的。但两条 `tvl` 分别 **$0.796 / $0.088**，`chainTvls` 里 Robinhood Chain 与 Base **都等于 0**，量全在 `Anubis`（非白名单）—— 正是 11-06 记的「`chains` 是部署声明、`chainTvls` 才是实际量」。

**`category` 桶本轮 0，且这次是真的 0**：9 条新增里 EXCL 类目（CEX/Chain/Interface）**一条都没有**（`Lending`/`Dexs`×3/`Staking Pool`/`Developer Tools`×3/`Trading App`）。与前一轮的「假 0」不同 —— 上一轮 5 条双帽 Interface，本轮无 Interface。

## `Jupiter` 四条同秒登记是本轮唯一的批量指纹（11-08 第 13 轮）

全量 payload 中 `listedAt` 同秒 ≥3 条的簇只有 6 个，最近两个是 10-07（22 条桥，已记为污染源）与 **11-07T14:26:04Z（n=4，全部是 Jupiter 的四个子条目）**。`Jupiter Native Staking` / `VRFD` / `Developer Platform` / `Rent Reclaim` 四条 `listedAt` **完全相同**、`parent=parent#jupiter`、`chains=[]`、`tvl=None`。

**这是「同秒批量」的第三种形态：不是交易所回填，是单一母协议一次性铺开子条目。** 四条相互间隔 0s，而 `PeddleSwap V2/V3` 相隔 4s、`Rocketswap`↔`BNQ` 相隔 306s —— 只有 Jupiter 那组是真批量。判新度时：**同秒 ≥3 条 + 同一 parent ⇒ 一条都不必细看**，遮挡正确。

## 本轮漏斗口径（11-12 第 17 轮）

全量 **9012** · 新增 id **22**（可报 **4** / 过滤 18）· `seen` 命中 8990 · `parent` **11（历史最高）** · `category` 0 · 空 `chains`/链白名单 7 · 无 id 0 · 拉取失败 0 · 重报 0。

**可报四条（已发通知、已标 `notified`）：** `Horizen Bridge`(9405，Base，$24,128.7，Canonical Bridge，`listedAt 11-11T22:23:02Z`) · `Flowlex`(9390，Base+Robinhood Chain，$7,323.7，Liquidity Manager，Robinhood Chain 侧仅 $0.55) · `Indexfy`(9396，Base，$1,421.4，Indexes，`address=base:0x6D21812b…1ceC`) · `Gully Core`(9400，Base+Binance+Robinhood Chain，$0.83，Dexs，五条链量按 `chainTvls` 拆开均 <$0.4)。

**`parent` 桶首次上双位数（11/22），且真边际首次过半 —— 4/11。** 逐条拆：

| id | 名称 | TVL | 去掉 parent 后 |
|---|---|---|---|
| 9393 | `Pendle Loop` | **$42.0M** | **PASS**（Ethereum $40.5M + Monad $1.04M + Base $0.42M；X Layer/Robinhood Chain 均 0） |
| 9392 | `Jupiter Vaults` | $292.1K | **PASS**（`chains=['Solana']`，量全在 Solana） |
| 9398 | `HedgeHood Options` | $451 | **PASS** |
| 9397 | `HedgeHood StockLend` | $53.6 | **PASS** |
| 9402 | `STRATO DEX` | $595.6K | 仍挡（链 `Strato` 非白名单） |
| 9389/9395/9404/9407–9409 | `Homer Swap`/`Valdora Vaults`/`GrowStreams Perps`/`ElysPump V1-V3` | 0 | 仍挡（空链） |

**`HedgeHood` 是第 12–13 条子条目**（父下已有 10-28 的 `Hedge Fun`/`HedgeHood HEDGE`、`HedgeHood Stock Yield` $69.8K、11-05 的 `HedgeHood Share Lending` $290）—— 「母协议铺子协议」的连续第 N 轮，parent 遮挡正确。**`Pendle Loop` 是迄今 parent 桶吃掉的第二大条目**（仅次于 11-05 `Dexalot OmniVaults` $1.96M 的 21 倍），且它是 Pendle 官方 `app.pendle.finance/trade/loop` 的杠杆循环产品，不是野生子协议。

**可报集 TVL $32.9K vs `Pendle Loop` $42.0M = 差 1279 倍**，是「可报 TVL 和不代表新增体量」迄今最极端的一例（上一轮 418 倍）。

### `listedAt` 的第二例滞后 + 首次发现整分秒人工痕迹（11-12）

`Valdora Vaults`(9395) `listedAt = 2026-11-10T08:40:00Z`，但上一轮快照 `last-modified = 11-10T23:38:18Z` —— **早 15 小时，本轮才出现在 payload**。与 11-11 `GraveStake`（早 37 分钟）同型，**再证 `listedAt` 是登记意图时刻，不能倒推漏报原因、不能测延迟。**

**新发现：`listedAt` 存在整分 `:00` 秒的人工填写痕迹。** 全量 7336 条带 `listedAt` 的条目里只有 **69 条**是整分（0.94%），本轮新增 22 条里就占了 2 条（9395 `11-10T08:40:00Z`、9402 `11-11T17:00:00Z`）。**含义：这类值不是系统写入，是有人手填了一个整点/整分；把它当精确时间戳算跨度会失真**（本轮含 9395 的全跨度 38.15h，排除后 22.36h，差 16h）。今后算 `listedAt` 跨度先剔整分秒值。

### 加链收益继续缩水：Elysium 本轮边际只有 1 条 $2.6K（11-12）

`Elysium Kinetiq` 现共 **15 条**协议（`Uniswap V2/V3/V4`、`Aero Slipstream`/`Basic`、`Ramses CL V2/Legacy V2/DLMM`、`Metric V1`、`nest AMM` 均自基线轮在录）。本轮新增里挂该链的只有 `Helios DEX`(9394，**$2,632.6**) 与 `Gully Core`(9400)，后者已因 Base/Binance/Robinhood 命中白名单直接可报。

**加链的净边际 = 1 条 $2.6K。上一轮是 1 条 $514。** 代价仍是删 seen 重做 9012 条基线。**结论不变：不加。**

### id 缺口扩大：`9382` 连续第二轮缺席，新增 `9391`、`9412–9415`

本轮 `9380`–`9411` 区间缺 **9382 / 9391**，且 `9412–9415` 也不在 payload（`max_id=9411`，而上轮 `max_id=9388`，前进 23）。按既定判据全部按**「分配了号、数据尚未回填」**处理，**不改求差逻辑、不写「永久空洞」**。注意 `9412–9415` 虽高于历史最大 id 却缺席 —— 说明「id ≥ 历史最大即新登记」这条旧规则的逆向也不成立（缺席的高号同样是待回填）。

### CF 校验（11-12）

常规 `cf-cache-status: HIT`、etag `W/"6af4fc70-924986"`、`last-modified Wed, 11 Nov 2026 23:38:24 GMT`、`age 31`、`cache-control: public, max-age=300`；`?_cb=` + `no-cache` 源站 `MISS`、**etag 与 `last-modified` 与 HIT 完全相同**。9012 条逐字段零差异（`only_hit=0` / `only_miss=0`），22 条新增 11 字段零差异。**`parentProtocol` 翻转连续八轮未复现。** `only_seen=['4818']` 连续第八轮。全量 `chains=[]` = 1613/9012 = **17.90%**（上轮 17.83%，九轮 17.4–17.90）。

`listedAt` 跨度（剔除 9395 整分值后）**22.36h**（11-11T00:27:17Z → 22:48:57Z），最小间隔 **1s**；同秒 ≥3 条批量指纹新增 **0 组**，最近一组仍是 11-07T14:26:04Z(n=4)。`ElysPump V1/V2/V3` 相隔 **11s**（同 parent）是本轮最紧的一组，但未破同秒门槛。录入节奏：22 条里 11-11 22 时 8 条、17 时 6 条 → 两小时 64%，单轮形态不作趋势。

## 上一轮漏斗口径（11-11 第 16 轮）

全量 **8990** · 新增 id **15**（可报 **4** / 过滤 11）· `seen` 命中 8975 · `parent` 3 · `category` 1 · 空 `chains` 5 · 链不在白名单 5 · 无 id 0 · 拉取失败 0 · 重报 0。

**可报四条（已发通知、已标 `notified`）：**
- **`Hyper Tokens`**(9379) · `Hyperliquid L1` · TVL **$103.7K** · `Derivatives` · HyperEVM 上约 6× 杠杆 BTC 敞口代币（VOL/iVOL）的非托管前端，自动再平衡、由 Hyperliquid perps 背书。`url` 空、`twitter=HyperTokensHQ`、`listedAt 2026-11-10T00:13:02Z`。
- **`Roulana`**(9374) · `Solana` · TVL **$6.34K** · `Luck Games` · 单桌 3D 欧式轮盘，真 USDC 下注、开奖上链可查。`address=solana:ttH5rJW…pump`。
- **`Kyte`**(9377) · `Robinhood Chain` · TVL **$1.68** / `staking` **$2,027.9** · `Options` · 非托管全额抵押期权。
- **`GraveStake`**(9373) · `Solana` · TVL **$0** / `staking` **$39,892.9** · `Staking Pool` · 无代码 NFT / SPL 质押池平台。

**过滤 11 条的真边际逐条可数：** `parent` 3 里 **只有 `Kinetiq Elysium Bridge`(9380) 是真边际**（$46.7M，去掉 parent 就能过全部桶），另两条 `Kalos DEX`(9383)/`Kalos Fate`(9384) 是 parent + 非白名单链双帽 · `category` 1（`EYED` 9375）是 category + 空链双帽 → **真边际 0** · 空链 4（`Ascend Launchpad`/`AssetClaw`/`LoopUP`/`Montra`）· 链不在白名单 4（`ArkhamPad` Elysium / `ipUSD` Soneium / `Aurumlend` Arc，加 `Kalos` 两条里的链成分）。**可报集的 TVL 合计 $111.7K，与单条 9380 的 $46.7M 差 418 倍** —— 「可报 TVL 和不代表新增体量」的极端例。

### 加链的收益这次可以逐条数清：Elysium 簇（11-11 第 16 轮）

15 条新增里 **6 条与 `Elysium Kinetiq`（Kinetiq 的 Arbitrum Orbit L3）相关**：官方桥 `Kinetiq Elysium Bridge`(9380，$46.7M)、`Kalos DEX`(9383，$73.7K)、`Kalos Fate`(9384，$2.2K)、`ArkhamPad`(9376，$514)、`Ascend Launchpad`(9381)、`Montra`(9388)。该链**不在 `CHAINS`**。

**该链不是空白地带**：全量已有 15 条 Elysium 系协议，包括 `Uniswap V2/V3/V4`、`Ramses Legacy V2/CL V2/DLMM`、`Aero Slipstream`/`Aero Basic`、`Metric V1`、`nest AMM` —— 即**大协议早已把这条链当部署目标，DefiLlama 侧口径成熟**。

**加链的净收益实算（不是 15% 的宽口径）：**

| 本轮候选 | 加 `Elysium Kinetiq` 后 | 结果 |
|---|---|---|
| `ArkhamPad`(9376) | `chains=['Elysium Kinetiq']`、无 parent、非 EXCL | **唯一真可报**（$514） |
| `Kalos DEX`(9383) | 仍 `parent=parent#kalos` | 仍挡 |
| `Kalos Fate`(9384) | 仍 `parent=parent#kalos` | 仍挡 |
| `Ascend`(9381) / `Montra`(9388) | 仍 `chains=[]` | **救不了** |

**所以加链本轮只多 1 条 $514 的候选。** 与上文「旁路/加链都在小量级」一致，且**加链必须删 seen 重做基线**（一次 8990 条重灌），代价远大于收益。**结论：不加。** 想看 Elysium 的名，走旁路（`url`/`description` 并集）比加链便宜。

**另注意 `Ascend Launchpad` / `Montra` 的描述都写着 Elysium，但 `chains=[]`** —— 若日后做 description 旁路，这类条目会被捞回；本轮不动。

### `9382` 是「暂未回填的分配号」—— 该机制连续七轮空转后首次复现（11-11）

本轮 id `9381` → `9383`，**`9382` 不在 payload**（单独复查确认）。前七轮 9300 起连续无缺口，本轮是「暂未回填」形态的首次实盘复现。

**判据照旧：缺席 ≠ 永久空洞。** 9382 是已分配的号、数据要几天后才出现在 `/protocols`（与 11-02→11-03 的 9290–9293 同类，那 4 条后来以 Kraken/Coinbase/Upbit/Bithumb 身份出现）。**不许把它写成「永久缺口」，也不许据此改求差逻辑。** 只有当它出现时，才会落进差集、按新条目过漏斗。

### `listedAt` 滞后于 `/protocols` 出现 —— 不能用来测延迟（11-11 首次实测）

`GraveStake`(9373) 的 `listedAt = 2026-11-09T23:00:59Z`，但**上一轮（第 15 轮）payload 的 `last-modified` 是 2026-11-09T23:38:34Z** —— 上一轮快照生成时 9373 已登记 37 分钟，却不在那份 payload 里。

**修正后的口径：**
- `listedAt` 是**登记意图时刻**，`/protocols` 的实际出现可晚于它**半小时以上**。
- 因此 **`listedAt` 不能倒推「上一轮为何漏了它」，也不能用来估算录入延迟。** 要测延迟只能用「seen 首次出现日 vs `listedAt`」的粗粒度差（粒度 = 轮次间隔，本 skill 每日一轮 = 24h）。
- 主结论不变：**新度只能靠 id 求差**，`listedAt` 只做交叉校验。

## 上一轮漏斗口径（11-10 第 15 轮）

全量 **8975** · 新增 id **9**（可报 **2** / 过滤 7）· `seen` 命中 8966 · `parent` 5 · `category` 1 · 空 `chains`/链白名单 1 · 无 id 0 · 拉取失败 0 · 重报 0。**报告级 2 —— 自第 11 轮以来首次真正出报告并发送。**

**可报两条（均已发通知、已标 `notified`）：**
- **`Hollow`**(9370) · `Ethereum` · TVL **$10.7K** · `Reserve Currency` · `listedAt 2026-11-09T18:38:05Z` · `url=hollow.cash` · `misrepresentedTokens=false`。ETH 背书的地板价只涨货币，宣称国库内 ≥1.3× 地板 ETH 背书、无 owner/无 admin key/无升级路径。**是本轮唯一 TVL 上万且未被 DefiLlama 标失真的条目。**
- **`MING`**(9367) · `Binance`(BSC) · TVL **$744.6** · `Gamified Mining` · `listedAt 2026-11-09T18:30:38Z` · `url` 为空 · **`misrepresentedTokens=true`**。5×5 格子每轮一分钟的 BNB 押注游戏。**该条 TVL 口径失真，读数不可直接用** —— 这是「类目不是真伪，只是原样带」的又一例。

**过滤 7 条的真边际首次是两个桶都可数清：** `parent` 5（`Syndicate Perps`/`Syndicate Predictions`/`Pacifica Options`/`Bitso Onchain Perps`/`Bitso Onchain Spot`，全部同时 `chains=[]` → **5/5 双帽**）· 空链 1（`Bridged Finance`）· `category` 1（`Afterbell`，`Interface`）。**可报的 2 条恰好是唯一两条不带 parent、类目不属 EXCL、且有白名单链的条目** → 本轮漏斗无一条「本可报却被误挡」。

**「母协议一次性铺子条目」连续第二轮主导：** `Syndicate` 两条相隔 **6s**、`Bitso Onchain` 两条相隔 **1s** —— 与 11-08 第 13 轮 `Jupiter` 四条同秒同型。**同秒 ≤10s + 同一 parent ⇒ 一条都不必细看**，与本轮 `Hollow`/`MING` 这类单条独立登记形成清晰对照。

**CF 校验通过（两份 8975 id 逐条相同）**：常规 `HIT` etag `W/"6af2597a-91a680"`、`last-modified Mon, 09 Nov 2026 23:38:34 GMT`、`age 17`；`?_cb=` 源站 `MISS` 同 etag 同 `last-modified`（**本轮两份快照 etag 首次完全相同**，`HIT`/`MISS` 只差缓存状态，说明源站自 23:38:34Z 后未再更新）。id 集合两向差集仅 `only_seen=['4818']`，9 条新增两份快照零差异。

`listedAt` 跨度 **4.57h**（11-09T17:53:21Z → 22:27:39Z），是近六轮最短窗口；同秒 ≥3 条批量指纹本轮新增 **0 组**（现存最近一组仍是 11-07T14:26:04Z，n=4）。

`only_seen=['4818']`、`only_raw=[]` **连续第六轮** → 真下架，可当稳定结论引用。seen 8976 = 8975 命中 + 1 残留。

id 9300–9372 **连续无缺口**，`max_id=9372`（较上轮 9363 前进 9，与新增 9 条一致，**无「暂未回填的分配号」连续七轮**）；非数字 id 仍只有 `<5471>`。

全量 `chains=[]` = **1598 / 8975 = 17.81%**（上轮 17.76%，七轮区间 17.4–17.81，缓慢上行但仍在窄带内）。

## 上一轮漏斗口径（11-09 第 14 轮）

全量 **8966** · 新增 id **1**（可报 **0** / 过滤 1）· `seen` 命中 8965 · `parent` 1 · `category` **0** · 空 `chains`/链白名单 0 · 无 id 0 · 拉取失败 0 · 重报 0。

唯一新增 **`Bitty Vaults`**(9363)：`parentProtocol='parent#bitty'`、`chains=[]`、`tvl=None`、`category='Onchain Capital Allocator'`（不在 `EXCL_CATEGORY`）、`listedAt 2026-11-08T19:07:59Z`、`url=https://bitty.io`、`twitter=bitty_io`。**parent 与空链双帽，parent 真边际 0/1** —— 去掉 parent 它仍被空链挡，去掉空链它仍在 parent 下。同父已有 `Bitty Lending`(6685，Ethereum+Bitcoin，$76.88)，是「母协议铺子协议」的标准形态（连续第二轮 `parent` 单条、双帽）。

**可报 0 = 结构性。** 本轮 `category` 桶 0 且是真 0（该条类目本就不在 EXCL）；`链白名单` 桶 0。新增流从上一轮 9 条降到 1 条，**单轮不能当趋势读**（前例：11-05 的 18 条录入潮后 11-06 立刻回到 8、11-07 到 6）。

按铁律「报告级 0 时不发通知、不重写 `report.md`」—— `out.json` 被写成 `[]`，`report.md` 内容仍是第 11 轮那份（只 mtime 被脚本触碰），本轮不发。

**CF 校验通过（两份 8966 id 逐条相同）**：常规 `HIT` etag `W/"6af0ff61-9182a7"`、`last-modified Sun, 08 Nov 2026 23:01:53 GMT`、`age 1271`；`?_cb=` 源站 `MISS` etag `W/"6af107fa-91819e"`、`last-modified 23:38:34 GMT`。9363 的两份快照 `name`/`category`/`chains`/`tvl`/`parentProtocol`/`listedAt`/`url` **零差异**，`parentProtocol` 翻转连续五轮未复现。

`listedAt` 跨度 **26.56h**（11-07T16:33:48Z → 11-08T19:07:59Z），单条无最小间隔可言；**同秒 ≥3 条批量指纹本轮新增 0 组**（全量现存簇仍是历史那 29 个，最近两个为 10-07T13:38:45Z(n=22) 与 11-07T14:26:04Z(n=4)）。

`only_seen=['4818']`、`only_raw=[]` **连续第五轮** → 真下架。seen 8967 = 8966 命中 + 1 残留。

id 9300–9363 **连续无缺口**（含本轮 9363），**连续六轮无「暂未回填的分配号」**；`max_id=9363`，非数字 id 仍只有 `<5471>`。

全量 `chains=[]` = **1592 / 8966 = 17.76%**（上轮 17.75%，六轮区间 17.4–17.76），稳定。

## 上一轮漏斗口径（11-08 第 13 轮）

全量 **8965** · 新增 id **9**（可报 **0** / 过滤 9）· `seen` 命中 8956 · `parent` 7 · `category` **0（真 0）** · 空 `chains`/链白名单合计 2 · 无 id 0 · 拉取失败 0 · 重报 0。

**可报 0 = 结构性。** 9 条新增里 5 条 `chains=[]`、7 条带 parent、0 条 EXCL 类目，无一通过。全轮最大体量 `Rocketswap Anubis V3`(9355) **$131.8K**，但它 `chains=['Anubis']`（非白名单）且带 parent，双帽。**本轮没有任何一条「本可报却被误挡」的条目** —— 与 11-07 的 `Vesper V2`（$10.02M，真边际）不同，这轮 parent 的边际两条都是 $1 以下的空池子。

按铁律「报告级 0 时不发通知、不重写 `report.md`」—— `out.json` 被写成 `[]`，`report.md` mtime 未变。

**CF 校验通过（两份 8965 id 逐条相同）**：常规 `HIT` etag `W/"6aefaddf-918df0"`、`last-modified 2026-11-07T23:01:51Z`、`age 1063`；`?_cb=` 源站 `MISS` etag `W/"6aefb657-918c8b"`、`last-modified 23:37:59Z`。9 条新增的 `name`/`category`/`parentProtocol`/`chains`/`tvl`/`listedAt`/`slug`/`url`/`misrepresentedTokens`/`wrongLiquidity` **十字段零差异**，**`parentProtocol` 翻转连续四轮未复现**。

`listedAt` 跨度 **14.35h**（11-07T02:12:39Z → 16:33:48Z），最小间隔 **0s**（Jupiter 四条），同秒 ≥3 条批量指纹 **1 组**（即 Jupiter）。

`only_seen=['4818']`、`only_raw=[]` **连续第四轮** → 真下架。seen 8966 = 8965 命中 + 1 残留（其中 8964 条为数字 id、1 条 `<5471>`）。

全量 `chains=[]` = **1591 / 8965 = 17.75%**（上轮 17.6%，五轮区间 17.4–17.75），稳定。

## 上一轮漏斗口径（11-07 第 12 轮）

全量 **8956** · 新增 id **6**（可报 **0** / 过滤 6）· `seen` 命中 8950 · `parent` 6 · `category` 0 · 空 `chains` 0 · 链白名单 0 · 无 id 0 · 拉取失败 0 · 重报 0。

**可报 0 = 结构性，不是故障。** 6 条全部是「母协议铺子协议」形态，且 5 条是 `Interface`（交易界面）：`Sparkling Hyperliquid` / `Sparkling Lighter Perps` / `Sparkling Lighter Predict` / `Sparkling Prediction Markets`（同 `parent#sparkling`，共用一个站点 `sparkl.ing`，7.9 小时内连登 4 条）、`pump.fun Perps`（`parent#pump`）、`Vesper V2`（`parent#vesper`，**$10.02M**，全轮体量最大）。

**`Vesper V2` 是本轮唯一有实质量的条目，也是 `parent` 桶唯一的真边际**（见上节）。它是老协议的行为版本铺开，属 SKILL.md 明写要挡的「版本号铺开是最大噪声源」，遮挡正确。

按 SKILL.md 铁律「报告级 0 时不发通知、不重写 `report.md`」——`report.md` 与 `out.json` 均未动（`out.json` 被脚本写成空数组 `[]`，属正常；`report.md` mtime 仍是 11-06）。

**CF 校验通过（两份 8956 id 逐条相同）**：常规 `HIT` etag `W/"6aee5c93-9162f5"`、`last-modified 2026-11-06T23:02:43Z`、`age 967`；`?_cb=` + `no-cache` 源站 `MISS` etag `W/"6aee64e2-91626e"`、`last-modified 23:38:10Z`。6 条新增的 `parentProtocol` / `category` / `chains` / `tvl` 两快照**零字段差异**，**11-03 那种 `parentProtocol` 翻转连续三轮未复现**。

`listedAt` 跨度 7.88h（11-06 05:42:31Z → 13:35:26Z），最小间隔 166s，同分钟 ≥3 条批量指纹 **0 组**（`Sparkling` 四条间隔 166–538s，是逐条录入不是同秒批量）。id 9347 → 9348–9353 连续无缺口，**连续四轮无「暂未回填的分配号」**。

`only_seen=['4818']`、`only_raw=[]` **连续第三轮** → 真下架，无争议。seen 8957 = 8956 命中 + 1 残留。

### `listedAt=null` 出现在新 id 上 —— 「近期新登记覆盖完整」这条要加限定

`Vesper V2`(9353) 是本轮最新 id 但 `listedAt=null`，10 分钟内两份快照都是 null。这直接顶撞上文「`listedAt` 在近期新登记上覆盖完整」的旧结论。

实测该区间：id ≥ 9300 的 54 条里 `listedAt` 为 null 的**只有 2 条**（`Imperial` 9300、`Vesper V2` 9353）= **3.7%**；id 9330–9353 共 24 条里 1 条 = 4%。

**修正后的说法：**「近 30 天新登记录入时刻普遍带 `listedAt`」仍成立（覆盖 ~96%），但**不是 100%**，所以「新度只能靠 id 求差」这条主结论不变、且更需要它。反过来，**`listedAt` 为 null 不能反推「老条目」** —— 本轮 9353 是全新 id 却是 null。以前把 null 一律读成「老/头部大协议」是错的，null 有两种来源：**老条目从未补录**，与**新条目录入时该字段漏填**（本例）。

## 上一轮漏斗口径（11-06 第 11 轮）

全量 **8950** · 新增 id **8**（可报 3 / 过滤 5）· `seen` 命中 8942 · `parent` 1 · `category` **0** · 空 `chains` 2 · 链白名单 2 · 无 id 0 · 拉取失败 0 · 重报 0。

可报 3 条：`Panda Financial`(9345, Base, Liquidity Manager, $8,673) · `HyperHive`(9346, Hyperliquid L1, Risk Curators, $2,425) · `Ignite DEX`(9344, Solana/Ethereum/Binance/Base, Dexs, $130)。

**`parent` 从 10 回落到 1 —— 11-05 的「录入潮」是单次形状，不是常态。** 同轮 `category` 桶连续第二轮为 0（11-05 亦 0），11-03 那次 8 条确认来自交易所批量回填的单次现象。**两轮连续读数才是否定「某桶成为常态产能」的最短证据长度。**

**CF 校验通过（两份 8950 id 逐条相同）**：常规 `HIT` etag `W/"6aed0b01-913c44"`、`last-modified 2026-11-05T23:02:25Z`、`age 1005`；`?_cb=` + `no-cache` 源站 `MISS` etag `W/"6aed1362-913ce3"`、`last-modified 23:38:10Z`。8 条新增的 `parentProtocol` / `category` / `chains` 两快照全一致，**11-03 那种翻转连续两轮未复现。**

**`only_seen=['4818']` 连续第二轮出现**（`only_raw` 空），11-05 首次观测的同一 id 仍不在 payload —— 从「一次快照缺条目」升级为**真下架的确认证据**。seen 总数 8951 = 8950 命中 + 1 残留。

`listedAt` 跨度 19.87h（11-04 23:39:13Z → 11-05 19:31:20Z），最小间隔 209s，同分钟 ≥3 条批量指纹 **0 组**；id 9339 → 9340–9347 连续无缺口，**连续三轮无「暂未回填的分配号」**。

### 读 `chains` 会高估覆盖面：量看 `chainTvls`（11-06）

`Ignite DEX` 报 `chains=['Solana','Ethereum','Binance','Base']`，但 `chainTvls` 里 **Binance=0、Base=0**，TVL 只在 Ethereum $44.8 + Solana $85.0。这与 11-05 的 `VectaSwap`($3.9K) 同属「多链 DEX、TVL 百元级」形态，连续第二轮出现。

**含义：`chains` 是部署声明，`chainTvls` 才是该链上的实际量。** 判断「铺了几条链」用 `chains` 没错（白名单过滤只认它，铁律不变），但读「这协议在哪些链上真有东西」必须回到 `chainTvls`，0 值链等于没部署量。此条只影响人工读数，**不改过滤器**。

## 上一轮漏斗口径（11-05 第 10 轮）

全量 8942 · 新增 id 18（可报 8 / 过滤 10）· `seen` 命中 8924 · `parent` 7（含 1 条 seen 命中重判）· `category` 0 · 空 `chains` 3 · 链白名单 1（`Lubics` SASEUL $18.2K）· 无 id 0 · 拉取失败 0 · 重报 0。

`listedAt` 跨度 21.0h（11-03 23:31:32Z → 11-04 20:31:53Z），最小间隔 **4s**，无 ≥3 条同分钟批量指纹（11-03 23:31 仅 2 条）。上轮最大 id 9321 → 本轮 9322–9339 **连续无缺口，连续两轮无「暂未回填的分配号」**。

**CF 校验两份快照对 18 条新增的 `parentProtocol` / `category` / `chains` 全部一致 —— 11-03 的 `parentProtocol` 跨快照翻转本轮未复现**，差异只出现在 `tvl` / `change_1h` / `staking` / `mcap` 这类连续量上。翻转是偶发（补录延迟所致），不是每轮必现，所以「一轮 1 次请求」的铁律暂不需要为它让步。

8 条可报：`Axcess` $97.6K · `VectaSwap` $3.9K · `yld.cx` $311 · `ALPHA Launchpad` $234 · `Nullroot Protocol` $85 · `CoinLotto` $9 · `Prediction Arena` $1 · `Milk Money`（`tvl=0` 但 `staking` $574K / `mcap` $1.18M —— **`tvl` 缺省不等于空壳，staking 另计**）。

## 上一轮漏斗口径（11-04 第 9 轮，历史对照）

全量 8924 · 新增 id 5（可报 1 / 过滤 4）· `seen` 命中 8919 · `parent` 1 · `category` 1 · 空 `chains` 2 · 无 id 0 · 拉取失败 0 · 重报 0。**`category` 桶从 11-03 的 8 回落到 1** —— 证实 11-03 那次是 Kraken/Coinbase/Upbit/Bithumb 同秒批量回填的单次现象，不是 `EXCL_CATEGORY` 常态产能。

新增 5 条全部落在 `2026-11-03T00:45–16:12Z` 的 15.5 小时内，**无同秒批量指纹**（最小间隔 4m47s），逐条按求差判据独立判定成立。上轮 id 9314–9316 与本轮 9317–9321 连续无缺口，**「暂未回填的分配号」本轮未出现**。

可报 1 条：`H081 Capital`（9319，Solana，Lending，TVL $42.00，`url` 空、无 `address`、无 `parentProtocol`）。**空 `url` + 无 `address` + TVL $42 = 新条目字段未填全的典型形态**，不是异常。

## 上一轮漏斗口径（11-03，历史对照）

新增 id 20（可报 3 / 过滤 17）· `parent` 7 · `category` 8 · 空 `chains` 2 · 无 id 0 · 拉取失败 0 · 重报 0。**`category` 桶首次成为最大丢弃桶**（8 > parent 7），其中 4 条是 `Kraken`/`Coinbase`/`Upbit`/`Bithumb` 的批量回填（见上）、4 条是 Interface。**这是 EXCL_CATEGORY 生效的正面证据，此前七轮该桶读数多为 0–1。**

# Citations

- 实测数据：`https://api.llama.fi/protocols`（2026-11-11 第 16 轮；常规 `HIT` 8990 条、etag `W/"6af3aaea-91df7e"`、`last-modified Tue, 10 Nov 2026 23:38:18 GMT`、`cache-control: public, max-age=300`（`age` 头缺失）；`?_cb=` 源站 `MISS` 8990 条、**etag 与 `last-modified` 与 HIT 完全相同**、`only_hit=0 only_miss=0`；15 条新增 11 字段两份快照零差异）
- 实测数据：同上 9379 `Hyper Tokens` · `chains=['Hyperliquid L1']` · `category='Derivatives'` · `tvl=103732.1845849603` · `parentProtocol=None` · `listedAt=1794269582`（2026-11-10T00:13:02Z）· `url=''` · `twitter='HyperTokensHQ'` · `misrepresentedTokens=false`
- 实测数据：同上 9374 `Roulana` · `chains=['Solana']` · `category='Luck Games'` · `tvl=6340.500362375524` · `address='solana:ttH5rJWVxCFBdjd3x2AnBxtYDJtRCFa9ty4QpmUpump'` · `listedAt=1794265687`
- 实测数据：同上 9377 `Kyte` · `chains=['Robinhood Chain']` · `category='Options'` · `tvl=1.6764450405395035` · `chainTvls={'Robinhood Chain':1.6764,'Robinhood Chain-staking':2027.9011,'staking':2027.9011}` · `listedAt=1794269199`
- 实测数据：同上 9373 `GraveStake` · `chains=['Solana']` · `category='Staking Pool'` · `tvl=0` · `chainTvls={'Solana':0,'Solana-staking':39892.8557,'staking':39892.8557}` · `address='solana:DEADsWJZaonaiZPFkrqEEBGf43mzA5uHeHpwgy9dW666'` · `listedAt=1794265259`（2026-11-09T23:00:59Z，**早于第 15 轮 `last-modified` 23:38:34Z**）
- 实测数据：同上 9380 `Kinetiq Elysium Bridge` · `category='Canonical Bridge'` · `parentProtocol='parent#kinetiq'` · `chains=['Hyperliquid L1']` · `tvl=46699401.3277` · `listedAt=1794265401` · `audits='2'` · **唯一「去掉 parent 即全通过」的条目**
- 实测数据：同上 9376 `ArkhamPad`（`chains=['Elysium Kinetiq']`、`tvl=514.13`、无 parent、`Launchpad`）· 9383 `Kalos DEX`（`parent#kalos`、`Elysium Kinetiq`、`tvl=73695.21`）· 9384 `Kalos Fate`（`parent#kalos`、`Elysium Kinetiq`、`tvl=2199.51`）· 9381 `Ascend Launchpad`（`chains=[]`、描述含 Elysium）· 9388 `Montra`（`chains=[]`、`address='elysium:0x063F7Cc…'`）
- 实测数据：同上 9375 `EYED`（`Interface`、`chains=[]`、`url='https://eyed.cc'`）· 9378 `ipUSD`（`Soneium`、`tvl=626397.58`）· 9387 `Aurumlend`（`Arc`、`tvl=10201.67`）· 9385 `AssetClaw` / 9386 `LoopUP`（`chains=[]`）
- 实测数据（Elysium 存量）：`chains` 含 `Elysium Kinetiq` 的 15 条 —— `Uniswap V2`(2197)/`V3`(2198)/`V4`(5690)、`Ramses Legacy V2`(8057)/`CL V2`(8058)/`DLMM`(8295)、`Aero Slipstream`(8691)/`Aero Basic`(9172)、`Metric V1`(8306)、`nest AMM`(7253)，加本轮 9376/9383/9384
- 实测数据（id 连续性）：**`9382` 不在 payload**（9381→9383 缺 1），其余 9300–9388 连续；数字 id 8989 条、`min=2 max=9388`、250 个历史缺口；非数字 id 仅 `<5471>`
- 实测数据（`chains=[]` 占比）：1603/8990 = 17.83%
- 实测数据（新增 `listedAt`）：跨度 23.16h（2026-11-09T23:00:59Z → 2026-11-10T22:10:31Z）；最小间隔 4s（9383→9384，同 `parent#kalos`）；新增内同秒 ≥3 条 0 组；全量现存 29 组，最近仍为 2026-11-07T14:26:04Z(4)
- 实测数据：`https://api.llama.fi/protocols`（2026-11-10 第 15 轮；常规 `HIT` 8975 条、etag `W/"6af2597a-91a680"`、`last-modified Mon, 09 Nov 2026 23:38:34 GMT`、`age 17`；`?_cb=` 源站 `MISS` 8975 条、**etag 与 `last-modified` 与 HIT 完全相同**；id 集合两向差集仅 `only_seen=['4818']`，9 条新增两份快照零差异）
- 实测数据：同上 9370 `Hollow` · `chains=['Ethereum']` · `category='Reserve Currency'` · `tvl=10698.342229103919` · `parentProtocol=None` · `listedAt=1794249485`（2026-11-09T18:38:05Z）· `url='https://hollow.cash'` · `misrepresentedTokens=false` · `audits=0`
- 实测数据：同上 9367 `MING` · `chains=['Binance']` · `category='Gamified Mining'` · `tvl=744.6458651847188` · `parentProtocol=None` · `listedAt=1794249038`（2026-11-09T18:30:38Z）· `url=''` · **`misrepresentedTokens=true`** · `audits=0`
- 实测数据：同上 9364/9365 `Syndicate Perps`/`Syndicate Predictions` · `chains=[]` · `category='Interface'` · `parentProtocol='parent#syndicate'` · `tvl=None` · `url='https://syndicate.trade'` · `listedAt=1794246801/1794246807`（相隔 6s）
- 实测数据：同上 9371/9372 `Bitso Onchain Perps`/`Bitso Onchain Spot` · `chains=[]` · `category='Interface'` · `parentProtocol='parent#bitso-onchain'` · `tvl=None` · `url='https://onchain.cc'` · `listedAt=1794263258/1794263259`（相隔 1s）
- 实测数据：同上 9366 `Bridged Finance`（`chains=[]`、`category='Bridge Aggregator'`、`parent=None`、`tvl=None`、`url=''`、`listedAt=1794246877`）· 9368 `Afterbell`（`chains=[]`、`category='Interface'`、`parent=None`、`listedAt=1794249193`）· 9369 `Pacifica Options`（`chains=[]`、`category='Options'`、`parentProtocol='parent#pacifica'`、`listedAt=1794249484`）
- 实测数据（id 连续性）：9300–9372 无缺口，`max_id=9372`；非数字 id 仅 `<5471>`
- 实测数据（`chains=[]` 占比）：1598/8975 = 17.81%
- 实测数据（新增 `listedAt` 跨度，第 15 轮）：4.57h（2026-11-09T17:53:21Z → 22:27:39Z）；全量同秒 ≥3 条簇新增 0 组，最近仍为 2026-11-07T14:26:04Z(4)
- 实测数据：`https://api.llama.fi/protocols`（2026-11-09 第 14 轮；常规 `HIT` 8966 条、etag `W/"6af0ff61-9182a7"`、`last-modified Sun, 08 Nov 2026 23:01:53 GMT`、`age 1271`；`?_cb=` 源站 `MISS` 8966 条、etag `W/"6af107fa-91819e"`、`last-modified 23:38:34 GMT`；id 集合两向差集仅 `only_seen=['4818']`）
- 实测数据：同上 9363 `Bitty Vaults` · `category='Onchain Capital Allocator'` · `chains=[]` · `chainTvls={}` · `tvl=None` · `parentProtocol='parent#bitty'` · `listedAt=1794164879`（2026-11-08T19:07:59Z）· `url='https://bitty.io'` · `twitter='bitty_io'` · `address=None`
- 实测数据：同上 6685 `Bitty Lending` · `chains=['Ethereum','Bitcoin']` · `tvl=76.87825734639296` · `parentProtocol='parent#bitty'` · `listedAt=1757358297`
- 实测数据（id 连续性）：9300–9363 无缺口，`max_id=9363`；非数字 id 仅 `<5471>`
- 实测数据（`chains=[]` 占比）：1592/8966 = 17.76%
- 实测数据（全量同秒 ≥3 条簇）：29 组，最近为 2026-10-07T13:38:45Z(22) 与 2026-11-07T14:26:04Z(4)
- 实测数据：`https://api.llama.fi/protocols`（2026-11-08 第 13 轮；常规 `HIT` 8965 条、etag `W/"6aefaddf-918df0"`、`last-modified Sat, 07 Nov 2026 23:01:51 GMT`、`age 1063`；`?_cb=` 源站 `MISS` 8965 条、etag `W/"6aefb657-918c8b"`、`last-modified 23:37:59 GMT`；id 集合两向差集仅 `only_seen=['4818']`，9 条新增十字段两份快照零差异）
- 实测数据：同上 9354 `BNQ` · `chains=['Hemi']` · `category='Lending'` · `tvl=538.38` · `parent=None` · `listedAt=1794017559`（2026-11-07T02:12:39Z）
- 实测数据：同上 9355 `Rocketswap Anubis V3` · `chains=['Anubis']` · `parentProtocol='parent#rocketswap-anubis'` · `tvl=131756.12` · `listedAt=1794017901`
- 实测数据：同上 9356/9357 `PeddleSwap V2`/`V3` · `chains=['Anubis','Robinhood Chain','Base','Arc']` · `chainTvls={Robinhood Chain:0, Base:0, Arc:0, Anubis:0.796/0.088}` · `parentProtocol='parent#peddleswap'` · `tvl=0.7957/0.0877` · `listedAt=1794018207/1794018211`
- 实测数据：同上 9358–9361 `Jupiter Native Staking`/`VRFD`/`Developer Platform`/`Rent Reclaim` · `chains=[]` · `tvl=None` · `parentProtocol='parent#jupiter'` · `listedAt` **全为 `1794061564`（2026-11-07T14:26:04Z）**
- 实测数据：同上 9362 `Yellow Onchain` · `chains=[]` · `category='Trading App'` · `tvl=None` · `parent=None` · `listedAt=1794069228`（2026-11-07T16:33:48Z）
- 实测数据（非数字 id）：同上 `<5471>` `OpenTrade` · `category='RWA'` · `tvl=245567081.83` · `chains=['Avalanche','Ethereum','Plume Mainnet']` · `parent=None` · `listedAt=1733496042`（2024-12-06T14:40:42Z）· `seen` 中键为 `'<5471>'`，`'5471'` 不存在
- 实测数据（全量同秒簇）：`listedAt` 同秒 ≥3 条共 6 簇 —— 2024-05-15T04:40:37Z(7) · 2025-07-28T18:06:11Z(3) · 2025-07-31T01:31:23Z(3) · 2026-10-07T13:38:45Z(22) · 2026-10-08T10:18:53Z(4) · 2026-11-07T14:26:04Z(4)
- 实测数据（`chains=[]` 占比）：1591/8965 = 17.75%
- 实测数据：`https://api.llama.fi/protocols`（2026-11-07 第 12 轮；常规 `HIT` 8956 条、etag `W/"6aee5c93-9162f5"`、`last-modified Fri, 06 Nov 2026 23:02:43 GMT`、`age 967`；`?_cb=` + `no-cache` 源站 `MISS` 8956 条、etag `W/"6aee64e2-91626e"`、`last-modified 23:38:10 GMT`；id 集合两向差集仅 `only_seen=['4818']`，6 条新增两份快照字段零差异）
- 实测数据：同上 9348–9351 `Sparkling Hyperliquid` / `Sparkling Lighter Perps` / `Sparkling Lighter Predict` / `Sparkling Prediction Markets` · `chains=[]` · `category='Interface'` · `parentProtocol='parent#sparkling'` · `tvl=null` · `url='https://sparkl.ing'` · `listedAt` 1793943751/1793943917/1793944153/1793944691
- 实测数据：同上 9352 `pump.fun Perps` · `chains=[]` · `category='Interface'` · `parentProtocol='parent#pump'` · `address='solana:pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn'` · `listedAt=1793972126`
- 实测数据：同上 9353 `Vesper V2` · `chains=['Ethereum']` · `category='Yield Aggregator'` · `parentProtocol='parent#vesper'` · `tvl=10024457.905` · `chainTvls={'Ethereum':10024457.905}` · `listedAt=null`（两份快照一致）· `address='0x1b40183efb4dd766f11bda7a7c3ad8982e998421'`
- 实测数据（桶重叠率，同一份 payload 重算）：7d `listedAt` 有值 63 / 带 parent 24 / 其中 EXCL category 11 · 30d 420 / 225 / 137 · 90d 916 / 384 / 142 · 全时段 parent 2668、其中 EXCL category 247（9.3%）· 30d EXCL category 计 178 条，其中带 parent 137、不带 41
- 实测数据（`listedAt` 覆盖）：id ≥ 9300 共 54 条，`listedAt` 为 null 仅 `Imperial`(9300) 与 `Vesper V2`(9353) = 3.7%；id 9330–9353 共 24 条中 1 条 = 4%
- 实测数据：`https://api.llama.fi/protocols`（2026-11-06 第 11 轮；常规 `HIT` 8950 条、etag `W/"6aed0b01-913c44"`、`last-modified Thu, 05 Nov 2026 23:02:25 GMT`、`age 1005`；`?_cb=` + `no-cache` 源站 `MISS` 8950 条、etag `W/"6aed1362-913ce3"`、`last-modified 23:38:10 GMT`；id 集合两向差集仅 `only_seen=['4818']`）
- 实测数据：同上 9344 `Ignite DEX` · `chains=['Solana','Ethereum','Binance','Base']` · `chainTvls={'Binance':0,'Ethereum':44.84,'Base':0,'Solana':84.97}` · `tvl=129.81` · `url=''`
- 实测数据：同上 9345 `Panda Financial` · `chains=['Base']` · `tvl=8672.77` · `category='Liquidity Manager'` · `url=''`
- 实测数据：同上 9346 `HyperHive` · `chains=['Hyperliquid L1']` · `tvl=2425.27` · `category='Risk Curators'` · `url=''`
- 实测数据：`https://api.llama.fi/protocols`（2026-11-05 第 10 轮；常规 `HIT` 8942 条、etag `W/"6aebb979-9102c7"`、`last-modified Wed, 04 Nov 2026 23:02:17 GMT`、`age 1082`；`?_cb=` + `no-cache` 源站 `MISS` 8942 条、etag `W/"6aebc1f9-910644"`、`last-modified 23:38:33 GMT`；id 集合两向差集仅 `only_seen=['4818']`）
- 实测数据：同上 9337 `Dexalot OmniVaults` · `tvl=1964050.56` · `chains=['Dexalot','Avalanche','Arbitrum','Binance','Base']` · `parentProtocol=parent#dexalot`（两份快照一致）
- 实测数据：同上 9336 `Milk Money` · `tvl=0` · `staking=574367.77` · `mcap=1180030.43` · `address=solana:Ax8PSfCXxmxb8C8kYTzN5CPpTe6PyeZfFf8rrXNCjupx`
- 实测数据：`https://api.llama.fi/protocols`（2026-11-04 第 9 轮；常规 `HIT` 8924 条、`last-modified Tue, 03 Nov 2026 23:02:14 GMT`、etag `W/"6aea67f6-90a472"`、`age 1229`；`?_cb=1793900000` + `no-cache` 源站载荷 8924 条、9,479,690 B；id 集合逐条相同，9319 的 `parentProtocol` / `tvl` 两份一致）
- 实测数据：同上，9317 `XMAQUINA` · `chains=[]` · `category=RWA` · `tvl` 缺失 · `parentProtocol=None` · `listedAt=1793721905`（2026-11-03T00:45:05Z）
- 实测数据：`https://api.llama.fi/protocols`（2026-11-03 第 8 轮；常规 `HIT` 8919 条、`last-modified 2026-11-02T23:02:20Z`、etag `W/"6ae9167c-9091f1"`；`?_cb=` + `no-cache` `MISS` 8919 条、`last-modified 23:38:44Z`、etag `W/"6ae91f04-909517"`；id 集合逐条相同）
- 实测数据：同上两份快照**字段值不同** —— `parentProtocol` 在 9315/9316 上由 `None` 变 `parent#exceed-finance`，全量 TVL 亦有变动
- 实测数据：`https://api.llama.fi/protocol/bond-capital` 与 `/protocol/camelot-v4`（2026-11-03；BOND `currentChainTvls={"Arbitrum": 177551.75638}`、`address=robinhood:0xEB288E3ca1607E7B921BCb47d5831E88331D65ef`、`audits: 0`、`twitter: BondDotCeo`、无 url）
- 实测数据：`https://api.llama.fi/protocols`（2026-11-01 第 6 轮；两份 payload 各 8892 条，etag `W/"6ae67bf0-903d78"`）
- 实测数据：`https://api.llama.fi/protocols`（2026-10-28 06:31Z 与 06:32Z 两次取数）
- 机制与铁律：[`skills/defillama-radar/SKILL.md`](/skills/defillama-radar/SKILL.md) · 实现 [`scan.py`](/skills/defillama-radar/scan.py)
- 同族判据：[lessons · 假零与断层](/topics/lessons.md#假零与断层)

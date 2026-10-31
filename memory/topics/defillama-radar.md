---
title: DefiLlama Radar
description: 第二层（名字）发现通道 —— 用全量 id 求差找白名单链上新登记的协议。机制、四态、判据与已知陷阱。
tags:
  - crypto
  - discovery
  - defillama
resource: https://api.llama.fi/protocols
timestamp: 2026-10-31T00:10:00Z
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

## 陷阱：CDN 快照让差集恒为 0

`api.llama.fi` 走 Cloudflare，`cache-control: max-age=1798`。两轮若落在同一份边缘对象内，**id 集合必然相同，差集恒 0** —— 与「今日无新协议」完全同形。

**2026-10-28 实例**：基线轮 06:22Z 与第 2 轮 06:31Z 同吃 `last-modified 05:39:24Z`、`age 751`、`cf-cache-status: HIT`。加 `?_cb=<ts>` + `Cache-Control: no-cache` 复取源站（`MISS`、`last-modified 06:02:09Z`、etag 变）后：id 集合仍相同，但 **1255/8859 条 `tvl` 已变（全量 TVL −$610M）** → 0 为真。

**纪律**：差集为空时先断言 `cf-cache-status != HIT`（或 `age` 远小于两轮间隔）。判新鲜度看 **`last-modified`（源站生成时间）**，不看 `age`（边缘对象年龄）。

### 更正（2026-10-29）：缓存**会**让报告漏条目，不只是「无信息量」

上一段曾写「不影响正确性，新登记最多延迟 ~30 分钟」。**10-29 实测证伪。**

- 00:01Z 首跑吃 `HIT` · `last-modified 23:02:27Z` · `age 937` → 只出 **1** 条（`Megawatt Markets`）。
- 加 cache-buster 复取源站（`MISS` · `last-modified 23:38:07Z`）→ 还有 **4** 条 `id` 不在 seen：`9267`–`9270`。
- 这 4 条的 `listedAt` 是 **21:50–22:00Z**，比那个 HIT 对象自己的 `last-modified`（23:02Z）**还早一个多小时**，却不在它的 payload 里。

**所以：`last-modified` 不能用来界定 payload 的完整性。** 一个 `HIT` 对象可以挂着一个较新的 `last-modified`、内容却是更早的一份，且这两件事在本轮内无法从响应头区分。**判新度唯一可靠的做法是 id 差集对源站复取，而不是读 `last-modified` 然后安心。**

**纪律（升级）**：可报数 > 0 也要做一次 cache-busted 复取，把 `set(源站 id) - set(seen)` 与 `out.json` 的 id 比对；不等则等边缘换新（`last-modified` 变化）后重跑，再发。本轮等到 00:16Z（`age 12`）重跑才一次拿全 4 条。

**配套正面证据**：首跑把 `Megawatt Markets` 写成 `notified=None`，第二轮走「重报」通道补回，证明四态 + 「send 成功才标日期」在缓存中途换新这种状态下能自愈。

**10-30 复核**：`?_cb=` 源站（`last-modified 23:39:19Z`）与 CF `HIT`（`age 1296`）两份 payload 的 8880 个 id 逐条相同（`only_busted` 与 `only_hit` 均为空集）—— 说明「两份 id 集合相等」是本轮无漏的直接证据，可写进报告；但**相等只说明这一轮没漏，仍不能从事前否定缓存风险**。

**10-31 复核**：同样两次取数 —— `HIT`（`last-modified 23:02:24Z` · `age 1722`）vs `?_cb=` + `Cache-Control: no-cache`（`MISS` · `last-modified 23:38:18Z` · etag 变），8888 个 id 的 `only_busted` / `only_hit` **均为空集**。**这已是连续第二轮的正面证据，但纪律不变：可报数为 0 也必须做一次 cache-busted 复取**，因为「0 新增」与「缓存未换新」在响应头上不可区分。

## `Interface` 类目：不进 `EXCL_CATEGORY`

全量 350 条 Interface：

- **232 条带 `parentProtocol`** → 被 parent 桶吃掉
- 剩下 118 条里**仅 6 条有 `chains`**（Ventuals / LiquidBots / Jupiter Prediction / otomate.trade / DESK CLOB / DFlow Prediction Market，TVL $741–$415K）
- 即「chains 为空」天然挡掉 **344/350 = 98.3%**

加进 EXCL 反而永久屏蔽一类可能的真信号（预测市场前端正在往 Interface 归）。**结论：不改。**

## `★清单内` flag 目前没有判别力

`memory/universe-names.txt` 5 个词（`Pearl Blockchain` / `Note Systems` / `Robinhood Chain` / `S-DAMM` / `USDG`）。
2026-10-28 全量 8859 条：**名字级命中 1 条**（`Robinhood Chain Bridge`），**描述级命中 192 条**（1:192）。

原因：把链名当项目名收着，该链上 91 个协议的 description 都会写自己的链名；`USDG` 同理（描述里说「以 USDG 计价」）。
**建议：只在 `name` 字段匹配。** 现状下这个 flag 只会给 Robinhood Chain 整条链打光。

## 白名单漏口：`Tradecraft`（Canton，2026-10-29）

第 3 轮唯一一条「TVL 比全部可报项都大、却被挡掉」的条目：`Tradecraft`（`id 9269`，DEX，**Canton Network**，TVL **$1,688,251**，`listedAt` 10-28 21:59Z）→ 记 `filtered`，**永不补报**。

`Canton` 不在 `scan.py` 的 `CHAINS`。同轮可报的 4 条 TVL 分别是 $72,463 / $2,704 / $1,603 / $109 —— **这条比它们全加起来还大 20 倍**。白名单是「只在关心的链上找」的取舍，不是质量判断，但这一条说明漏口在按 TVL 排序时会立刻显形。

**若要收 Canton**：加链 **并且** 删 `memory/defillama-seen.json` 重做基线（否则该 id 已在 seen 里，加链等于没加）。待下周复核。

## 新噪声源：空 `chains`（2026-10-30 首次量化）

链白名单这道漏斗的输入正在变空。

| 口径 | 空 `chains` 占比 |
|---|---|
| 全量 8880 条 | 1541 条 = **17.4%** |
| `listedAt` > 2026-10-27 的 58 条新登记 | 38 条 = **65.5%** |

即**新上架协议里三分之二不带链字段**。第 4 轮（10-30 00:02Z）的 7 条新增里有 3 条因此被挡，且都不是空壳：`OmenX`（预测市场 CLOB，`omenx.com`）· `OTC`（Solana launchpad，创作者费回购代币化股票/Pre-IPO/收益代币）· `StonkDrop`（Robinhood Chain 抽奖，USDG 付费 + drand 抽稀有度）。这三条与 10-28 那批 `Interface`（345 条里 232 条带 parent、118 条里仅 6 条有 chains）**不是同一形态**：那批是空壳前端，这批有描述、有站点、有业务模型。

**为什么现在才显形**：`chains=[]` 过去是「Interface 空壳」的同义词，挡掉它零成本。10-28 起 DefiLlama 上架流程明显不再回填 `chains`，这道漏斗开始连带挡真协议。

**待办（10-31 已用数据收敛，见下节）**：连续记录「新登记中空 chains 占比」。**不改规则前先取证，别在单轮上改漏斗。** [source: logs/2026-10-30#defillama-radar]

## 空 `chains` 待办结案（2026-10-31 第 5 轮）

### ① 候选旁路里 `tvl` 分支是死的：`chains=[]` ⟺ `tvl` 缺失

10-30 写的候选是「`chains=[]` 但 `tvl` 非空**或**有 `url`」放行。实测全量 8888：

| 口径 | n | `tvl` 非空 |
|---|---|---|
| 空 `chains` | 1546 | **0 条（0.0%）**，全部 `tvl=None` |
| 有 `chains` | 7342 | 5534 条（75.4%）`tvl>0` |

**空 `chains` 的协议在 DefiLlama 上根本没有 TVL 条目** —— 两个字段是同一个未完成录入状态的两面。`tvl` 分支命中数恒为 0，不是松紧问题。只讨论 `url` 分支。

### ② `url` 分支：+39~53%，但近一半是桥的批量录入

| 窗口 | 现行漏斗放行 | 空chains+有url 增量 | 增幅 |
|---|---|---|---|
| 近 7 天 | 19 | 10 | +53% |
| 近 30 天 | 118 | 46 | +39% |

近 30 天 46 条类目：**Cross Chain Bridge 13 + Canonical Bridge 8 = 21 条（46%）**，其余 Launchpad 4 / DEX Aggregator 2 / RWA 2 / Physical TCG 2 / Prediction Market 2 / Crypto Card Issuer 2 / Dexs 2，长尾 1 条起。`url` 指向 github 的仅 2 条。

**批量录入特征显著**：`2026-10-07T13:38:45Z` 同一秒入库 **22 条、其中 15 条 Cross Chain Bridge**。启用 `url` 分支必须同时加**桥类目子过滤**或**同秒 `listedAt` 批量去重**，否则近一半增量是噪声。

### ③ 「新登记三分之二不带链」≠「三分之二真信号被挡」

空 `chains` 占比按 `listedAt` 滚动窗（不是 10-30 的定值三天）：

| 窗口 | 新登记 | 空chains | 占比 |
|---|---|---|---|
| 3d | 37 | 24 | 64.9% |
| 7d | 75 | 48 | 64.0% |
| 14d | 140 | 73 | 52.1% |
| 30d | 455 | 279 | 61.3% |
| 90d | 871 | 386 | 44.3% |
| 180d | 1194 | 397 | 33.2% |

单调趋势成立、两轮同形（10-30 的 65.5% 复现）。**但其中 39.2% 带 `parentProtocol`**，本来就被 parent 桶吃掉。只被空 chains 挡掉的真条目：

| 窗口 | 通过 | 被空chains挡 | 占漏斗输入 |
|---|---|---|---|
| 3d | 8 | 7 | **46.7%** |
| 7d | 19 | 14 | **42.4%** |
| 30d | 118 | 76 | **39.2%** |

**报这个数必须用「占漏斗输入 ~39–47%」口径**，别用「三分之二」。空 `chains` 已是第二大漏斗（仅次于 parent）。

## 补登记：新 id 也可能是老协议（2026-10-31 首次量化）

`Amahub Perps Aggregator`（`id 9284`）首见于 10-31 差集，但 `listedAt=2026-10-02T14:45Z` —— **比首见早 28 天**，且同秒还有 `Amahub DEX Aggregator`。

- 10-28 立的反向校验仍成立：**差集里出现小于历史最大 id 的条目 = 旧条目回流**。
- **正向不成立**：id 处于当前最大区间也**不能**证明是近期新登记，可能是给老协议补开条目。判报告措辞按 `listedAt` 说话，不按 id 说话。

## 白名单复核：Flare / Canton 都不接（2026-10-31 结案）

判据从「TVL 大不大」改成**「注册速率撑不撑得起一次基线重做」** —— 加链必须删 `memory/defillama-seen.json`、丢掉全部 `notified` 记录。

| 链 | 全量 | 过滤后 | 过滤后 TVL | 近 30 天新登记 | 结果 |
|---|---|---|---|---|---|
| Canton | 8 | 5 | **$13.7M** | 1 | 不接 |
| Flare | 53 | 26 | **$1.25B** | 2 | 不接 |

- **Canton**：$11.89B 里 $11.87B 是 Gate + Bitget 两个 CEX，真协议只有 `Temple` $7.4M / `Cantex` $2.2M / `Alpend` $2.2M / `Tradecraft` $1.7M / `Pool Party` $0.2M。10-29 记的 `Tradecraft` 漏口确认存在，但为它付一次全量基线重做不划算。
- **Flare**：TVL 看着大（Upshift $430M / FAssets $189M / Clearstar $185M / Lagoon $157M），但近 30 天只登记 2 条、近 90 天 5 条、近 180 天 7 条 —— **~1–2 条/月**。
- 第 5 轮（10-31）的 8 条差集里，2 条仅因 Flare 被挡（`FlareBank Lending` / `The Cellar`）。**这是白名单取舍的必然结果，不是漏报。**
- **下次复核新链时先算注册速率，再算 TVL。**

## 已知代价：基线轮吃掉首批沉积层

基线轮（或任何换长窗首跑）之后的第一轮，差集里会一次性推出历史沉积 —— **它们不是漏报，是被基线吃掉的**。与 `github-radar` 换长窗首跑同形，次轮即归零。

## 四态速查

| 值 | 含义 | 再报 |
|---|---|---|
| `null` | 过了过滤、没通知成 | **会**（自愈） |
| `"YYYY-MM-DD"` | 已通知 | 不会 |
| `"filtered"` | 首次出现就没过过滤 | **不会**（永不回退、永不补报） |
| `"baseline"` | 基线轮批量入表 | 不会 |

可报集合 = `notified is None`。发送与标记是同一个动作 —— 只有 `send` 成功才标。

# Citations

- 实测数据：`https://api.llama.fi/protocols`（2026-10-28 06:31Z 与 06:32Z 两次取数）
- 机制与铁律：[`skills/defillama-radar/SKILL.md`](/skills/defillama-radar/SKILL.md) · 实现 [`scan.py`](/skills/defillama-radar/scan.py)
- 同族判据：[lessons · 假零与断层](/topics/lessons.md#假零与断层)

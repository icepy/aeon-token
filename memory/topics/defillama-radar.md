---
title: DefiLlama Radar
description: 第二层（名字）发现通道 —— 用全量 id 求差找白名单链上新登记的协议。机制、四态、判据与已知陷阱。
tags:
  - crypto
  - discovery
  - defillama
resource: https://api.llama.fi/protocols
timestamp: 2026-10-28T06:35:00Z
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

**纪律**：差集为空时先断言 `cf-cache-status != HIT`（或 `age` 远小于两轮间隔）。判新鲜度看 **`last-modified`（源站生成时间）**，不看 `age`（边缘对象年龄）。缓存只让「0 新增」在窗口内**无信息量**，不影响正确性 —— 新登记最多延迟 ~30 分钟。

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

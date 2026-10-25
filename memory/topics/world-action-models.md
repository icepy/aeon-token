---
title: World Action Models (WAM)
description: WAM 作为具身智能的新提法 —— GitHub 代码侧的按周收敛曲线、工程化分裂、以及 star 与 commits 的背离（第五轮起口径改为全量翻页 99 仓）
tags: [robotics, embodied-ai, world-model, wam, discovery, github-radar]
resource: https://github.com/search?q=%22world+action+model%22&type=repositories
timestamp: 2026-10-25T04:35:00Z
---

# World Action Models (WAM)

「World Action Model」是一个 2026 年才出现的提法：把 **world model（预测下一帧/下一状态）** 和 **action model（直接出动作）** 合成一个模型，而不是两段式（先建模、再规划）。

发现通道：[github-radar](/skills/github-radar/SKILL.md)（测「有人在写代码」，提前量 ~1–2 个月）。平行通道 [arxiv-radar](/skills/arxiv-radar/SKILL.md)（测「有人在研究」，~4 个月）。

## 为什么值得跟

XMAQUINA / DEUS 押的是机器人叙事。**同一个词在 arxiv 与 GitHub 上依次点亮，那个次序才是信号** —— 论文出现只说明有人在研究，代码仓出现且仍在提交才说明有人在工程化。

## 收敛曲线（60 天窗，`world action model` in:name,description）

代码仓按 ISO 周（**严格词表 `world action model`**）：

> ⚠️ **2026-10-25 第五轮推翻了下表口径。** 同一查询今日稳定返回 **99 仓**，且无法用任何过滤器复现 84 及其逐周曲线 —— 84 依赖了某个没写下来的条件。**下面这张 5/9/5/6/17/18/6/10/8 表已作废，仅留作历史。现行口径见「第五轮复核」。**

| 周 | W35 | W36 | W37 | W38 | W39 | W40 | W41 | W42 | W43 |
|---|---|---|---|---|---|---|---|---|---|
| ~~严格词表（作废）~~ | ~~5~~ | ~~9~~ | ~~5~~ | ~~6~~ | ~~17~~ | ~~18~~ | ~~6~~ | ~~10~~ | ~~8~~ |
| **现行口径（99 仓）** | **6** | **10** | **7** | **9** | **19** | **20** | **7** | **12** | **9** |

- **现行口径：严格词表合计 99 仓 / 94 owner**（60 天，全量翻页 `created:>=2026-08-26 fork:false`），10 月新建 33 个。放宽口径（name 含 wam）total=877 但**有子串污染**（`askWAM` / `wamove`），不可用。
- **94 个 owner 里只有 5 个有 ≥2 个仓 —— 散点式命名收敛，不是单一项目刷量。这一条两个口径都成立。**
- **W39–W40 的双峰（19/20）是会议周期，不是有机增长。** 描述里大量 `CoRL 2026` / `NeurIPS 2026`；回落 W41–W43（7/12/9）但**没有归零**。
- 对比 `world model`（更大更老的词）：238 仓 / 228 owner，W40 峰值 35，W43 回落到 20。**WAM 是 `world model` 的一个正在分化的子集，不是同义词。**

## star 与 commits 的背离（这一簇最实用的判据）

| 仓库 | ★ | 30d 提交 | 性质 |
|---|---|---|---|
| `OpenWAM-Official/OpenWAM` | 1106 | 11 | 论文官方实现，star 是传播度 |
| `TencentARC/WorldCrafter` | 537 | 53 | 少数 star 与提交同高的 |
| `robbyant-research/Zero-WAM` | 439 | **0** | 已死，连续两轮确认 |
| `OpenMOSS/EasyWAM` | 381 | 30 | 真在维护 |
| `black-forest-labs/flux-action` | 199 | 2 | 7B 开放权重，发完即停 |
| `UniWAM/UniWAM` | 135 | 20 | |
| `THUSI-Lab/PrismWAM` | 48 | **10** | ★48 提交数是 ★1106 的一半以上 |

**结论：star 测「发布时的传播」，commits 测「现在还有人写」。★1106 的提交数不到 ★48 的两倍 —— 头部 star 顺序不是工程活跃度顺序。**

## 第四轮复核（2026-10-25 03:40Z）— 其数字已被第五轮推翻

~~严格词表口径与第三轮逐字一致：84 仓 / 79 owner，W35–W43 = 5/9/5/6/17/18/6/10/8。同一窗口、同一筛选器、两次独立跑出同一组数字 —— 这条曲线现在是可复用的，不是一次采样。~~

**⚠️ 上面这条结论作废。** 第五轮实测：同一条查询今日连跑两次都稳定返回 `total_count=99`；99 集里最新创建时间是 **10-22**（10-23 之后零新建）；相对 84 的增量 **+15 均匀摊在 9/9 周**（最大单周 +3），不是扎堆在最近两周。**两小时内不可能有机增长 15 个仓，这是口径差。** 我穷举了所有单条与组合属性过滤器（`github.io` / selfname / pageword / shortdesc / nodesc / ★>=1..3），**没有任何一种能同时复现 84 这个总数和那条逐周曲线**。教训：**「两次跑出同一组数字」只能证明那两次环境一致，不能证明数字可复现 —— 复现性要换一天测，还要把筛选口径写进结论里。**

- **10 月新建 29 个（含放宽口径 31），但只有 6 个报告级**（≥5 提交/30d）。**这 6 个不是按 star 排出来的头部** —— `EasyWAM` ★381/30 提交、`DexTacWAM` ★24/24、`TacPAC` ★19/22、`UniWAM` ★135/20、`AquaWAM` ★35/17、`Phoenix-MWA` ★28/14。**10 月新仓普遍还在第 2–4 周，5 次提交的门槛对新仓本身就有观察窗偏差。**
- **`PrismWAM` 复核：★48 / 30d 10 提交 / pushed 10-23。** 连续三轮同一数值，活仓。对比 `flux-action`（Black Forest Labs，★199，30d **2** 提交，pushed 10-16）—— **★低的比 ★高的活跃 5 倍，这条背离第四轮继续成立。**
- **本轮无 `Zero-WAM` 复活迹象**：★439，`pushed_at` 仍停在 **2026-09-15**，连续四轮零提交。
- **`SkillWeaver` 仍是跨通道唯一交集**：`Ada4321/SkillWeaver` ★5 / 30d **15 提交** / pushed 10-11。论文 09-28 → 代码 10-08，滞后 10 天。**注意它不在正式 `TERMS` 里，只有探针词能捞到。**


## 第五轮复核（2026-10-25 · 现行口径，全量翻页无窗口切片）

**严格词表 99 仓 / 94 owner**，逐周 W35–W43 = **6/10/7/9/19/20/7/12/9**，10 月新建 **33**。**这是唯一可引用的口径**（`output/ghradar/wam5.py`，`created:>=2026-08-26 fork:false`，`in:name,description`，精确短语带引号）。

- **star 与 commits 的背离第五轮继续扩大**：`OpenWAM` ★1107 / **11** · `EasyWAM` ★382 / 30 · `UniWAM` ★135 / 20 · `PrismWAM` ★48 / 10 · `flux-action` ★199 / **2** · `InternW0-Delta` ★119 / **2** · `ViGAR` ★105 / **3**。**7 个 ★≥100 的仓里 4 个提交数 <5。**
- **`Zero-WAM` ★439 五轮零提交**，`pushed_at` 仍停在 **2026-09-15**。
- **`PrismWAM` ★48 / 10 提交 / pushed 10-23** —— 连续四轮同值，活仓。
- **`UniWAM/UniWAM` 是扫描器 `pages` 规则的受害者**：★135 / 20 提交 / 3.3MB Python，根目录有 `train/ inference/ models/ configs/`，**却因为仓名 == owner 名被当列表页丢掉**。同规还误杀 `dextacwam/DexTacWAM` ★24 / 26 提交。见 [lessons](/topics/lessons.md)。
- **WAM 仓会被 `terms` 去重归到别的词下**：`SmolWAM`、`AffordanceWAM`、`Skel-WAM`、`TrajWAM`、`so101-vla-wam`、`MT-WAM` 6 个在 `scan.py` 里全记成 `robot manipulation`。**要数 WAM，必须用全量翻页而不是扫描器的 `per_term` 计数。**

## 工程化分裂（10 月新建里出现的三种非论文形态）

name 含 WAM 的 10 月新仓 19 个，其中 8 个 ★0（符合「新建仓必然 ★0–2」）。除论文官方实现外：

1. **小型化 / 边缘端** — `iitimii/SmolWAM` ★13（0.88B，边缘设备）· `zhaozewang/Tiny-WAM` ★0 · `S1rlvk/smolwam-robocasa` ★0（desc 自报「zero-shot 0/30」—— **诚实报负结果，是工程仓不是营销仓**）
2. **蒸馏 / 加速** — `pjliu3/WAM-OPD` ★1（on-policy distillation）
3. **项目页独立成仓** — `Prism-WAM/prism-wam.github.io` · `RealtimeWAM/realtimewam.github.io`（提法大到需要独立站点）

**判读：从「论文仓」分裂出「工程仓」是提法被真正采纳的证据。但样本只有 3–4 个仓、跨度 2 周，是趋势还是单点无法区分。**

## 相关：具身数据引擎（arxiv-radar 的主场，代码侧几乎空白）

[arxiv-radar](/skills/arxiv-radar/SKILL.md) 90 天窗唯一活跃板块是「具身数据」20 篇，其中 11 篇是数据采集/合成/仿真基础设施。**代码侧用 6 个非官方探针词查，只捞到 4 个仓** —— 说明这个主题仍停在论文阶段，工程化滞后。

例外，值得盯：

- **`NVIDIA/Flora`** ★11 · 2026-10-20 · NVIDIA GEAR「robotics data engine 开源模型套件」· 30d **11 提交** · Python · 10.6MB
- **`wellkilo/embodigen`** ★0 · 2026-10-19 · 「task description in, label-exact photorealistic dataset out」· 30d **23 提交** · 17.4MB
- **`Ada4321/SkillWeaver`** ★5 · 2026-10-08 · CoRL 2026 · 30d **15 提交** — **论文 09-28（arXiv 2609.36171）→ 代码 10-08，滞后 10 天。这是跨通道次序信号唯一一次真正抓到。**

**⚠️ 这四个仓在 github-radar 的正式词表下完全不可见**（不含任何 `TERMS` 词），只能靠额外探针捞。

## 怎么用

- **盯 W43 之后的新建数**：连续两周归零 = 提法退潮；维持 6–8 = 已进入常规研究节奏。
- **盯 SmolWAM 系的 fork/衍生**：小型化仓被复现才是边缘部署的前兆。
- **盯 `NVIDIA/Flora`**：大厂 + 具身数据引擎 + 真在提交，三者同时成立在这一簇里罕见。
- **不要引用 `vla` / `world model` 的绝对数字** —— 覆盖率分别只有 7.9% / 21.4%（详见 [lessons](/topics/lessons.md#过滤器设计)）。

# Citations

- **第五轮（现行）** — GitHub Search API `"world action model" in:name,description created:>=2026-08-26 fork:false`，**全量翻页 99 仓**，快照 `output/ghradar/wam5.json`；脚本 `output/ghradar/wam5.py`；口径复现测试 `output/ghradar/variants5.py` / `output/ghradar/fit84b_5.py`
- 第四轮（数字已作废，留档）— 17 词 × 3 窗快照 `output/ghradar/out.json`（1,438 条）；提交核验 250 仓，0 空仓 / 0 未验成；`per_page=100` 上限，故 100 实为 ≥100
- 提交核验（第五轮）— `gh api repos/{owner}/{repo}/commits?since=2026-09-25T00:00:00Z&per_page=100`（249 仓）
- 原始仓库 — https://github.com/OpenWAM-Official/OpenWAM · https://github.com/THUSI-Lab/PrismWAM · https://github.com/iitimii/SmolWAM · https://github.com/NVIDIA/Flora · https://github.com/UniWAM/UniWAM
- arXiv — SkillWeaver 2609.36171（经 arxiv-radar 90 天窗命中）

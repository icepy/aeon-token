---
title: World Action Models (WAM)
description: WAM 作为具身智能的新提法 —— GitHub 代码侧的按周收敛曲线、工程化分裂、以及 star 与 commits 的背离
tags: [robotics, embodied-ai, world-model, wam, discovery, github-radar]
resource: https://github.com/search?q=%22world+action+model%22&type=repositories
timestamp: 2026-10-25T02:50:00Z
---

# World Action Models (WAM)

「World Action Model」是一个 2026 年才出现的提法：把 **world model（预测下一帧/下一状态）** 和 **action model（直接出动作）** 合成一个模型，而不是两段式（先建模、再规划）。

发现通道：[github-radar](/skills/github-radar/SKILL.md)（测「有人在写代码」，提前量 ~1–2 个月）。平行通道 [arxiv-radar](/skills/arxiv-radar/SKILL.md)（测「有人在研究」，~4 个月）。

## 为什么值得跟

XMAQUINA / DEUS 押的是机器人叙事。**同一个词在 arxiv 与 GitHub 上依次点亮，那个次序才是信号** —— 论文出现只说明有人在研究，代码仓出现且仍在提交才说明有人在工程化。

## 收敛曲线（60 天窗，`world action model` in:name,description）

代码仓按 ISO 周（**严格词表 `world action model`**）：

| 周 | W35 | W36 | W37 | W38 | W39 | W40 | W41 | W42 | W43 |
|---|---|---|---|---|---|---|---|---|---|
| 严格词表 | 5 | 9 | 5 | 6 | **17** | **18** | 6 | 10 | 8 |

- **严格词表合计 84 仓 / 79 owner**（60 天）；并上「name 含 wam」的仓则 **92 仓 / 87 owner**，其中 10 月新建 31 个。
- **79 个 owner 里只有 5 个有 ≥2 个仓 —— 散点式命名收敛，不是单一项目刷量。**
- **W39–W40 的双峰（17/18）是会议周期，不是有机增长。** 描述里大量 `CoRL 2026` / `NeurIPS 2026`；回落 W41–W43（6/10/8）但**没有归零**。
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

- GitHub Search API — `"world action model" in:name,description created:2026-08-26..2026-10-25 fork:false stars:>=0`，17 词 × 3 窗，快照 `output/ghradar/out.json`（1,437 条）
- 提交核验 — `gh api repos/{owner}/{repo}/commits?since=2026-09-25`，120 个高信号仓
- 原始仓库 — https://github.com/OpenWAM-Official/OpenWAM · https://github.com/THUSI-Lab/PrismWAM · https://github.com/iitimii/SmolWAM · https://github.com/NVIDIA/Flora · https://github.com/Ada4321/SkillWeaver
- arXiv — SkillWeaver 2609.36171（经 arxiv-radar 90 天窗命中）

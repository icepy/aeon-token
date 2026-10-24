扫描完成。**本轮 90 天窗零新增**，主要成果是把上一轮记下的去重债务清掉了。

---

# arXiv Radar — 90 天窗 · `var=days:90`

**窗口** `2026-07-26 → 2026-10-24` · 20 词 · 原始命中 **91** · **幸存 0** · 失败 0
丢弃分布：`seen` 79 · `carrier` 11 · `excl` 1

## 零新增的两个原因，分开说

**1. 22 篇老论文已按计划挡掉，不是丢了。**
第六轮（同日早前）明确记了一条债务：`memory/arxiv-seen.json` 只有 53 个 id，全是修 carrier 之前的 ZK/理论那批；carrier 修好后新解锁的 21 篇机器人论文 + `2608.13271` **从未落盘**。当时的原话是「正式 90d 跑前须先 seed 这 22 个 id，否则首推会是一次 22 条的洪水」。

本轮跑前先做了 seed：**53 → 75 个 id**，合法 JSON、无版本后缀、日期全为 10-24。复跑校验，90 天窗幸存从 22 归 **0**。**隐患已解除。**

**2. 索引仍停在 10-22，这是收录延迟的第二天。**
3 天窗（10-21 → 10-24）原始命中只有 1 条、幸存 0。90 天窗的「窗口内最新收录日期」依旧是 `2026-10-22` —— arXiv API 今天还没吐出 10-23 / 10-24 的条目。与第六轮按日计数（`cs.CR` 10-23=0 / 10-24=0，`cs.RO` 同形 70/57/0/0）完全一致。**已知形态，不是话题降温，不用当异常报。**

## 90 天存活板块（存量，供对照；非本轮新信号）

唯一板块仍是**机器人 / 具身数据，20 篇，占存活量 91%** —— 与 DEUS / XMAQUINA 叙事同轨。数据采集 / 合成 / 仿真基础设施 11 篇：

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 10-08 | StereoEngine | 免立体相机合成双目双臂机器人数据 | https://arxiv.org/abs/2610.12734 |
| 10-06 | EmbodiedSmith | 仿真内递归自改进飞轮扩具身数据 | https://arxiv.org/abs/2610.07969 |
| 10-01 | NEEDLEWORK | 离线重写轨迹，局部缝合不可用片段 | https://arxiv.org/abs/2610.02339 |
| 09-28 | SkillWeaver | agentic 探索替代遥操作来量产机器人数据 | https://arxiv.org/abs/2609.36171 |
| 09-22 | PhyVisGen | 物理+视觉双高保真操作数据生成 | https://arxiv.org/abs/2609.25653 |
| 09-21 | ARSTAG | 一张 RGB + 一句自然语言 → 任务专属 Real2Sim2Real | https://arxiv.org/abs/2609.24563 |
| 09-21 | Uranus | 面向具身 AI 的下一代仿真基础设施 | https://arxiv.org/abs/2609.24815 |
| 09-16 | UMI-Bridge | 人类与机器人操作数据的动作锚定对齐 | https://arxiv.org/abs/2609.18232 |
| 09-05 | IM-ENGINE | 用图像编辑生成具身数据 | https://arxiv.org/abs/2609.06279 |
| 08-15 | GUIDER | 遥操作中无目标人类意图推理实测 | https://arxiv.org/abs/2608.15446 |
| 07-30 | ACE-Data-0 | 以人为中心的环境采集作具身数据引擎（16 人） | https://arxiv.org/abs/2607.28625 |

**MEV / AMM 2 篇：**

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 09-15 | When AI Agents Meet MEV | AI agent 当搜索者做跨链套利，**用 Base 上 23,000 笔 Uniswap V3 成交做实证** | https://arxiv.org/abs/2609.17897 |
| 08-13 | Slow and Steady | 可验证延迟防 MEV，拜占庭+博弈双正结果 | https://arxiv.org/abs/2608.13271 |

`2609.17897` 那条的 **Base 23,000 笔 V3 成交**是可复用的链上数据源线索，比结论本身有用。

## 词表健康

20 词里只有 5 词有 90 天命中：`embodied AI`=10 · `robot data`=5 · `embodied data`=3 · `cat:cs.CR AND ti:"MEV"`=2 · `robot manipulation data`=2。

其余 **15 词连续两轮零命中，按铁律不删**：`proof-of-useful-work` · `verifiable inference` · `light client` · `proof of training` · `proof of learning` · `verifiable training` · `auditable training` · `data availability sampling` · `restaking` · `consensus protocol` · `liquid staking` · `automated market maker` · `zero-knowledge` · `ti:"EIP-1559"` · `ti:"Robinhood Chain"`。

`excl` 只丢 1 条且判对：`2610.14038` "From bits to atoms: A survey of cross-layer safety in Embodied AI"，标题含 survey，真综述。

## 通知

**未发送。** 幸存 0；且这 22 篇是同日早前 dry-run 已入日志的同批信号，按「不重复报同一信号」也不推。

## Summary

**做了什么**
- 按 `var=days:90` 跑正式 90 天窗（20 词 × 3s 退避直连 arXiv API，0 失败），加跑 3 天窗和 seed 后复跑各 1 次做校验。
- 清掉第六轮记下的去重债务：`memory/arxiv-seen.json` **53 → 75 个 id**，22 篇 90 天存量全部落盘。这个隐患原本会让下次正式 90d 跑一次推 22 条。

**文件改动**
- `memory/arxiv-seen.json` — 新增 22 个 id（已修改，未提交）
- `memory/logs/2026-10-24.md` — 追加 `### arxiv-radar — 第七轮` 一节（已修改，未提交）

**结论**
- 本轮真零新增。索引仍停在 `2026-10-22`，是收录延迟的第二天，不是零命中。
- 90 天窗唯一活跃板块是机器人/具身数据（20 篇），与 XMAQUINA 叙事同轨。

**后续动作**
1. 明天早上常规跑若仍返回 0，**先查 `submittedDate` 最新收录日期**再下结论 —— 别把「索引滞后第三天」记成「话题死了」。
2. `git status` 里 `AGENTS.md` 是 deleted、`notify`/`notify-jsonrender`/`secretcurl` 是 untracked，都不是本轮产生的，留给你判断是否处理。

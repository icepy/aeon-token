---
title: github-radar — 实现缺陷与判据
description: github-radar 六轮跑出的实现缺陷、过滤规则陷阱、以及「活跃度」判据（30d vs 7d、核验覆盖率、agent 指纹）
tags: [github-radar, discovery, methodology, lessons]
resource: https://github.com/search?q=%22world+action+model%22&type=repositories
timestamp: 2026-10-25T04:55:00Z
---

# github-radar — 实现缺陷与判据

从 [lessons](/topics/lessons.md#过滤器设计) 抽出的 skill 专属条目。六轮（2026-10-25）实证。

## 已修复的实现缺陷

1. **农场黑名单从未生效（第四轮）** — `github-farms.txt` 是行内注释格式，`scan.py` 只跳过 `#` 开头的行、不剥行内注释 → 解析出 3 个带注释尾巴的垃圾 key，匹配 0 个 owner，日志却显示 `farm=0`（看起来像「没有农场」）。改法 `l.split("#")[0].strip()`。**第五、六轮回归：泄露 0。**
2. **`owner≥3=farm` 误杀活仓（第四轮）** — 判掉 `rzc156/dreamforge` ★130/21、`Roboparty/P-BFM` ★95、`NEBULIS-Lab/D-JEPA` ★32/68、`liaohello/GigaWorld-Policy-Sim2Real` 18 提交。黑名单文件明写「3 仓不够，要三者同时成立（结构同质+跨赛道+提交极少）」，代码只实现第一条。**改为候选 ∓ 判决后，第六轮这四个全部正确保留。**
3. **`pages` 规则误杀真代码仓（第五轮）** — `short.lower() == owner.lower()` 把 `UniWAM/UniWAM` ★135/20（有 `train/ inference/ models/`）、`dextacwam/DexTacWAM` ★24/26 当列表页丢掉。改法：加 `not language` 条件。**第六轮回归：两仓幸存，pages 丢弃 79 → 15（全是 0–47KB 无语言同名仓）。**
4. **`terms` 多词命中只记首个（第五轮）** — `SmolWAM`/`AffordanceWAM`/`Skel-WAM`/`TrajWAM`/`so101-vla-wam`/`MT-WAM` 6 个 WAM 仓被归到 `robot manipulation`。**第六轮回归：多词命中 67 仓，`world action model` 扫描口径 72 → 95。**

## 未修复（第六轮新发现）

5. **🔴 单个 409 空仓打掉整个认证态。** `gh_get` 的降级条件是 `r.returncode != 0`，而 `repos/{r}/commits` 对空仓返回 **409「Git Repository is empty」** 也满足它 → `GH = False`，后续全部走未认证 urllib（60/h）。**铁律写着「429 与 409 必须分开」，代码只在返回值里分了（`"empty" if "409" in err`），降级判断里没分。** 改法：`break` 前先判 error 文本含 `409`/`empty`，是则直接返回不降级。第六轮 409 出现在第 ~240 个，实际影响 0；**长窗口下若早出现会静默把后面全标 unverified。**

## 判据（比 star 更硬的几条）

6. **`commits_30d=100` 是 `per_page` 上限，实为 ≥100。** 第六轮 5 仓撞顶（`quackd`/`EvoBot`/`ekbasis`/`Awesome-Physical-AI-Safety`/`diamond-cs2-v2`）。**任何分页计数都必须标注是下限。**
7. **报告级是核验抽样的下限，不是全量。** 第五轮：★<5 有 1,052 个只核了 94 个（8.9%），这 94 个里 27.7% 是活仓。第六轮核验 250/1,251 = **20.0%**。**报通过数必须同时报核验覆盖率。**
8. **🔴 按 star 分配核验预算会饿死 star 天然低的整个域。** 前六轮都记「加密侧实测为空，唯一活仓 `vearl`」——真相是 **35 个加密仓里 34 个 ★0–2 全被 `CHK_CAP=250` 挤掉**（`todo` 先按 ★≥5 全取，加密小词在时间序上全被机器人侧挤掉）。补齐后 **18 个 ≥5 提交、9 个近 7 天仍活跃**。**跨域比较前必须先对齐两侧核验完整度。**
9. **🔴 30d 提交 ≠「现在还在写」，三分之一的仓会翻面。** 第六轮：加密侧 ≥5 提交的 19 仓里 **10 个近 7 天零提交**（`zig-zkml` 100→0、`openinstinct-qwen` 51→0、`AIRcoin` 33→0）；机器人侧 ≥10 提交的 51 仓里 **20 个零提交**（`EvoBot` ★128/100→0、`EasyWAM` ★382/30→0、`UniWAM` ★135/20→0）。**报「有人在写」必须同时给 30d 与 7d。** 7d=0 不等于废弃（可能只是在写论文），但不能说它「现在有人在写」。
10. **🔴 「高提交数」和「是代码仓」在同一排序里无法区分。** `namastex888/dehype` **30d=100** 是 AI 论文排行站；`cooperwooley/diamond-cs2-v2` **100/100** 是 CS2 课程项目；`kf953741/kf953741` 20 提交是个人主页；`adeeb10abbas/same-goal-different-words` 16 提交是 CoRL workshop 的 Svelte 项目站；`YanjieZe/agent-real2sim2real` ★22 是 13KB 列表。**判据：`commits > N` 之后还要看根目录形态（`src/`/`contracts/`/`crates/` vs 纯 HTML/Svelte）与 `language`/`size` 是否匹配。**
11. **🔴 根目录 `AGENTS.md`/`CLAUDE.md`/`.clinerules` = 「单人 + agent」指纹。** 加密侧 ≥5 提交仓 **10/18（56%）** 有，机器人侧 ≥20 提交仓 **2/21（10%）**；`itzebe/intent-pay` 提交作者里直接有 `openhands-agent`（4/10）。**与「加密侧 47% 爆完即停」互相印证 —— 一个人用 agent 两周搭完就放着。这不算农场**（不跨赛道、不批量建仓，黑名单抓不到）。**一次 `contents` 调用就能把 agent 批量产出从团队工程里分出来。**

## 复现性

12. **「同窗口跑两次得同一组数字 = 曲线可复用」是错的推论。** WAM 84 → 99 的差是口径差（增量均匀摊在 9/9 周、三天零新建、10-23 后零新建）；同一天跑两次只证明环境一致。**复现性要换轮次 + 写明筛选口径。** 第六轮做到了：99 仓 / 94 owner、逐周 6/10/7/9/19/20/7/12/9，与第五轮**逐周完全一致**。

# Citations

- 快照 `output/ghradar/out6.json`（1,251 幸存 / 2,427 原始）· `audit6.log`
- 加密侧补齐核验 `output/ghradar/cry_verify6.py` · 7 天衰减 `decay6.py` / `robact6.py` · agent 指纹 `agentfile6.py` · 目录树 `tree6.py`
- WAM 全量翻页 `output/ghradar/wam6.py`（99 仓）· [world-action-models](/topics/world-action-models.md)
- 详细日志 `memory/logs/2026-10-25.md#github-radar（第六轮`

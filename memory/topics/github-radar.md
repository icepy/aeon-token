---
title: github-radar — 实现缺陷与判据
description: github-radar 十一轮跑出的实现缺陷、过滤规则陷阱、以及「活跃度」判据（30d vs 7d、全量核验、star 排序偏差、窄窗误读、seen 基线有效性）
tags: [github-radar, discovery, methodology, lessons]
resource: https://github.com/search?q=%22world+action+model%22&type=repositories
timestamp: 2026-10-26T09:30:00Z
---

# github-radar — 实现缺陷与判据

从 [lessons](/topics/lessons.md#过滤器设计) 抽出的 skill 专属条目。十一轮（2026-10-26）实证。

## 第十一轮（2026-10-26，30 天窗，dry-run）—— 首个 30 天基线；窗口本身就是「新增」的制造机

本轮 `var=dry-run days:30`，窗口 `2026-09-26..2026-10-26`。原始 2,236 → 幸存 **70** → 报告级 **35**，核验全量 70/70。

### 23. 🔴 与上轮求差得到的「新增 44」全是窗口算术，0 个真漏检

与第十轮快照 `out10.json`（7 天创建窗，26 仓）求差：重叠 26、新增 44。按 `created` 拆解：

| 创建时间 | 数量 | 能否被上一轮看到 |
|---|---|---|
| `2026-10-01..10-18` | 39 | **不能** —— 第十轮窗口从 10-19 起 |
| `2026-09-01..09-30` | 5 | 不能 |
| `>= 2026-10-19` | **0** | —— |

**44 个里没有一个是在上一轮窗口内被漏掉的。** 反向也成立：第十轮报的「真新增 26」是 7 天创建窗的产物，同样不可当增量。**判据：跨窗口比较前，必须先把「新增」按 `created` 分到「窗口内 / 窗口外」，否则两轮互为镜像，各报一次虚增。**

### 24. 🟢 30 天创建窗救回 5 个 7 天窗结构上看不到的活仓 —— 这不是「更全」，是「更慢」

7 天创建窗只能看见「这一周诞生的仓」，一个 10-12 建的仓若一直写到现在，它在 7 天窗里永远不出现。30 天窗救回 5 个 7d≥5：

| 仓库 | 30d | 7d | 形态 |
|---|---|---|---|
| `Hostileoracle0606/motion-lab` | 47 | **43** | ★0 Python，`assets/docs/experiments` + `pyproject.toml` |
| `Kushaan-N/SyncSim` | 81 | 18 | RoboTwin 2.0 双臂世界模型训练数据，有 `CLAUDE.md` |
| `sirosiro/SpaceGuidance-FBB` | 41 | 9 | 6-DoF 航天器 GNC sim-to-real，有 `rtl/` `ros2/` |
| `Hchnr/s2a` | 11 | 9 | 世界模型预测态 → 控制指令，有 `AGENTS.md` |
| `Wade-Owo/Rob_Capstone` | 9 | 5 | 根目录只有 `docs/`，无代码 |

**判据：窗口长度是「提前量」与「覆盖率」的取舍轴，不是质量轴。** 7 天窗追「刚出现」，30 天窗追「还在写」，两者测的不是同一件事 —— 用同一个词表跑，结论自然不同。

### 25. 🔴 star 在整轮上彻底失效：报告级 35 个里 34 个 ★0，幸存集最高 ★7

70 个幸存里 ★≥5 只有 1 个（`mayuelala/EgoACT` ★7，NeurIPS 2026 官方实现），**全轮最高 star = 7**。而报告级 35 里 28 个来自 `world model` 一支、全部 ★0。**第九轮 `PER_TERM_CAP` 按 star 抽样的 3.85× 低估，在 30 天窗上是更极端版本：不是抽样切掉 74%，而是整个排序轴与信号轴正交。** 只要 `world model` 这类机制词还在，star 就永远不该出现在排序或采样里。

### 26. 🔴 爆完即停 57.1%：30d 提交在 30 天窗里几乎不携带「现在还在写」

报告级 35 中 **20 个 30d≥5 但 7d=0**（57.1%），与前几轮 55.2%（第七轮）、59.7%（第六轮）同水位。**这个比例跨窗口、跨轮次稳定，说明它是结构性现象（论文/项目页写完即停、作业仓集中提交），不是某一轮的偶然。** 报告级必须双列 30d/7d，7d=0 的照报但不能说「在写」。

### 27. ⚠️ pages 规则漏 3 个纯静态站进报告级 —— 第十轮的自动化判据第二次独立复现

| 仓库 | 30d | 7d | 根目录 | 体积 |
|---|---|---|---|---|
| `syaok1/wm-outcome-pilot` | 5 | 5 | `index.html` + `.nojekyll` + README | 123KB |
| `KAI030113/safedojo` | 14 | 4 | 同上 + `script.js`/`style.css` | 39MB |
| `BasisResearch/empiric` | 25 | 0 | 同上 + `assets/` | 115MB |

**三仓根目录都没有 `src/`/`tests/`/`pyproject.toml`/`package.json`。** 而真正的代码仓（`shangchaohu718/supermimic-pera`：`src+tests+configs+pyproject.toml`；`eshaan2418/Recall`：`android+Dockerfile+Makefile`）一眼可分。**判据「`index.html` + `.nojekyll` 且无代码骨架 → 页」两次独立命中，第三次该进代码了。** 注意 `KAI030113/safedojo` 39MB、`BasisResearch/empiric` 115MB —— **再次验证体量绝不能当页形态的豁免条件。**

### 28. 🟡 SuperMimic：换成 30 天窗后全盲依旧 —— 证明这是词表结构缺陷，不是 7 天窗的副产品

30 天窗内直接搜 `supermimic in:name,description created:>2026-09-26` = **55 仓**，逐仓核验 **30d≥5 25 个 / 7d≥5 25 个 / 7d=0 零个**；18 词只捞到 **2 个**（都是 desc 里恰好写了 "world model" 的）。冠亚军 `sxh-kk/SuperMimic_Recurrence` **85/85**、`QinnyuLan/SuperMimicCarnival` 33/33（**索引仓，须单列**）、`Motphys/Uni-SuperMimic` ★138 22/22。

**第十轮把这个记为「7 天窗下的发现」，本轮证明它与窗口无关。** 词表按机制词组织，抓不到「一个具体工作/方法的名称」—— 而新专名恰恰是「有人在写代码」最强的信号。**唯一仍在生效的兜底是人工反查：从候选仓里挑 star/commit 最高的，搜它的派生簇。**

### 29. 🟡 agent 指纹在 30 天窗开始显形（报告级 3/35），但样本太小

`AGENTS.md`/`CLAUDE.md`/`.clinerules`：幸存 6 个、报告级 3 个（`Hchnr/s2a`、`Kushaan-N/SyncSim`、`YG3-ai/yg3-agent-garden`）。第十轮（7 天窗）报告级 0 个。**方向与第六轮判据 11 一致（单人 + agent），但 3 个不足以推「比例上升」—— 记形态，不记趋势。**

### 30. ⚠️ carrier 丢 479 个（占原始 21.4%）—— 只记数量，不重放净增

本轮 carrier 是最大单条丢弃规则。**不重复第十轮的错误**：只看 carrier 一条会得出「误杀」虚高上界，必须把 EXCL / short_desc / pages / 离题一起重放才有意义。本轮不做净增重放（dry-run 不引入新判据），只记：**discard 量大 ≠ 误杀大。**

## 第十轮（2026-10-26，7 天窗，dry-run）—— 窄窗把稀有词读成「真零」，且词表对一个 55 仓热点全盲

### 18. 🔴 7 天窗会让稀有词系统性读成「真零」—— 判词死活必须跨窗量三个 total_count

本轮首次用 7 天窗（`var=dry-run days:7`）。扫描器报「真零命中」3 个：`verifiable inference` / `proof of useful work` / `maximal extractable value`。逐词跨窗复核（`output/ghradar/terms10.json`）：

| 词 | 7d | 30d | 60d | 判定 |
|---|---|---|---|---|
| `verifiable inference` | 0 | 6 | 7 | **窗口太短**，词没废 |
| `proof of useful work` | 0 | 6 | 13 | **窗口太短** |
| `maximal extractable value` | 0 | 0 | 2 | 真稀（60d 仅 2） |
| `robotics data engine` | 1 | 1 | 1 | 真稀 |
| `restaking` | 1 | 3 | 6 | 稀但在 |
| `intent-based` | 14 | 58 | 116 | 正常 |
| `data availability` | 18 | 65 | 129 | 正常 |
| `vision language action` | 14 | 98 | 200 | 正常 |
| `world action model` | 9 | 55 | 95 | 正常 |

**判据：窄窗只用来追「这一周新增了什么」，不能用来判词表死活。** 上一轮（第九轮）的教训是「有 seen 基线后 0 新增 ≠ 废词」，本轮的教训是**更前置的一条：窗口长度本身就会制造假零**。两者叠加时，一个词在 7 天窗 + 有 seen 基线的情况下读 0 是最弱的信号，必须回退到 30/60 天 total_count 才能分类。

### 19. 🔴 词表对一个真实热点近乎全盲：`SuperMimic` 55 仓，18 词只捞到 2 个

7 天窗内扫 18 词，幸存 26、报告级 5，**7d 提交最高值只有 19**。但直接搜 `"SuperMimic" in:name,description created:2026-10-19..2026-10-26` 得到 **55 个仓**（`total_count` 报 55，实际翻页取到 56 个 item —— 搜索计数是近似值；60 天窗同样 55，整簇都是 10 月新建），逐仓核验 **25 个 30d≥5 提交、25 个 7d≥5 提交**：

| 仓库 | ★ | 30d | 7d | 说明 |
|---|---|---|---|---|
| `sxh-kk/SuperMimic_Recurrence` | 0 | **85** | **85** | 单卡 4090 复现，Ollie 起跳先验 |
| `QinnyuLan/SuperMimicCarnival` | 0 | 33 | 33 | 复现索引仓（≈脚手架，需单独判） |
| `CesarLiu/smimic` | 0 | 31 | 31 | reproducing supermimic |
| `LaoYang1994/SuperMimic-Rep` | 0 | 27 | 27 | |
| `Motphys/Uni-SuperMimic` | 137 | 22 | 22 | UniLab 上的独立复现 |
| `zita-ch/supermimic_vibed` | **553** | 4 | 4 | 自称 "vibe coded within 1h" |

**为什么全盲：热点仓一律把术语写在仓库名/描述里（`SuperMimic`），而词表的 `world model` / `embodied data` / `sim2real` 都不在它们的 desc 里。** 18 词捞到的 2 个（`shangchaohu718/supermimic-pera`、`NJU-R-L-Group-Embodied-Lab/SuperMimic-Repro-Sim2Real`）恰好是描述里写了 "world model" 的那两个。

**这是第八轮 `jepa` 判据的重演，但性质不同：`jepa` 是「通行缩写」，`SuperMimic` 是「10 月才诞生的新专名」。** 判据要扩写：**不只是缩写需要保留，新生的专名（一个具体工作/方法的名称）同样抓不到，而新专名恰恰是「有人在写代码」最强的信号 —— 一个工作刚出论文就有 55 个复现仓。词表按机制词组织，结构上无法覆盖这一类。**

**可操作修法（未实施）：** 词表之外加一路「新专名探测」—— 从上一轮 `github-candidates.md` 里取近期 star 最高的新奇仓库，反查其派生簇（`"<name>" in:name,description`）。本轮 `SuperMimic` 就是从 `CuboiLeo/SuperMimic-Reproduced` 反查出来的。

**注意 `SuperMimicCarnival` / `huangkiki/awesome-supermimic` 是索引/列表仓**，与本 skill 的入场判据同类，不该计入「写代码」。**复现簇里「索引仓」和「复现仓」必须分开数。**

### 20. ⚠️ 评估单条过滤器前必须把其余过滤器一起重放

carrier 本轮丢 123 个。只看 carrier 一条规则，120 个 `world model` 被丢仓里 **43 个是 30d≥5 提交**，看起来是重大误杀。**但按 scan 真实顺序重放过 EXCL / short_desc / pages / 离题判定后，净增只有 1 个报告级**（`DU525/paired-counterfactual-eval` 5/5）：EXCL 挡 11、short_desc 挡 27、后缀挡 7、仍判离题 73。

**判据：评估某条过滤器时不能只排除那一条重跑。** 否则会把「本来就该被别的规则挡掉」的仓记到它头上，得出 43 倍的虚高误杀。第九轮 `PER_TERM_CAP` 的 3.85× 是真误杀（因为它是**排序**，切掉的仓没有别的规则会挡），本轮的 43 是假误杀（因为它们是**被下游规则正确拦截**）。**两者形态相似、结论相反，区别在于被丢样本在完整管线里的存活率。**

### 21. ⚠️ carrier 只看 description，不看 topics —— 真缺陷，但单改会放行列表仓

`UCSC-VLAA/ALPS`（★24）被判离题，因为 desc 只写 "Visual State Encoders for World Models"；但它的 topics 是 `embodied-ai` / `robot-learning` / `libero` / `world-models` —— 教科书级的具身世界模型工作。同类「desc 离题、topics 属机器人」共 **13 个**（多数是 awesome 列表）。

**修法：carrier 判据改为「desc 或 topics 任一命中」。但必须同时确认 EXCL 仍拦得住列表仓 —— 单改 carrier 只会多放进 12 个 awesome/索引仓。**（本轮未改代码，dry-run 保持与上轮可比。）

### 22. 🟢 站点仓「后缀单条件即丢」的反向验证通过

第九轮把 pages 规则改成「后缀命中即丢，不看体量」。本轮丢 17 个，含 **357MB** 的 `mundo-world-model/mundo-world-model.github.io`、102MB 的 `Ephemeral6/awm-site`、34MB 的 `bars-2026-psf.github.io`。**如果「体量小」条件还留着，这三个会全部进报告级。** 第九轮判据 16 得到独立复现。

**但留了一个洞：`syaok1/wm-outcome-pilot`（HTML + `index.html` + `.nojekyll`，纯静态研究站）本轮进了报告级。** 它不匹配后缀（名字不带页后缀）、也不是同名仓。**判据 10 的「根目录形态」检查始终没有进 scan 代码，只靠人工。** 可自动化的判据：`index.html` + `.nojekyll` 且无 `src/`/`tests/`/`pyproject.toml`/`package.json` → 页。

## 第九轮（2026-10-25 07:00Z）—— 抽样低估 3.85×，且切掉的正好是 ★0 域


`scan.py` 的 `PER_TERM_CAP = 25` 按 star 排序取样，本轮只核了 **76/234 (32.5%)**。补全到 **230/234 (98.3%)** 后：

| 指标 | 抽样（76 仓） | 全量（230 仓） | 倍数 |
|---|---|---|---|
| 报告级 | 20 | **77** | **3.85×** |
| 其中 7d 活跃 | 11 | **31** | 2.8× |
| 报告级里来自「被抽样丢掉」的 | — | **57/77 = 74%** | — |
| 7d 活跃里来自「被抽样丢掉」的 | — | **25/31 = 81%** | — |

**被丢掉的 159 个里 `stars >= 5` 有 0 个。** 即 star 排序把整个 ★0 长尾一刀切掉，而报告级和活跃度的四分之三都藏在里面。这是第七轮判据 8（「按 star 分配核验预算会饿死 star 天然低的整个域」）的**第三次复现，第一次量化**。

**判据：核验预算永不按 star 分配。** core quota 5,000/h 与 search 是独立池，200 仓全量只需 ~90 秒。**`PER_TERM_CAP` 存在的唯一理由是省时间，而它一次的代价是把 74% 的报告级藏起来 —— 直接删掉这个 cap，改用全量 + `CHK_CAP` 兜底。**

## 第九轮 —— `seen` 基线的有效性 = 「上一次**非 dry-run**」的幸存集

本轮与 `out8.json` 快照求差：重叠 **169/234 = 72.2%**，真正新增 **65**。而 `seen` 文件显示「新增 238 条」，看起来全是新的 —— **第八轮跑的是 dry-run（`DRY=1` 时 `scan.py` 不写 seen），178 个幸存者一个都没落盘。**

**判据：报「新增 N」前必须与上一轮**快照**求差，不能只看 `seen` 增量。** `seen` 只反映「历史上非 dry-run 跑过什么」，dry-run 轮次的发现会全部重复回捞。**这也是「同一天跑 9 轮」这类密集重跑的主要噪音源 —— 前一轮若是 dry-run，下一轮的有效新增要除以 ~3.6。**

## 第九轮 —— `jepa`：★0 但 commit 最狠，star 与 commits 反相关

真正新增的 65 个**全部**是 `jepa` 词、**全部 ★0**、0 个 ★≥3，但 **26 个报告级、11 个 7d 活跃**，且全轮冠亚军都在这一支：

- `sahiltolani30/learn-a-world` **30d≥100 / 7d≥100**（自博弈学潜空间世界模型）
- `500mhzClub/Go2-JEPA-Navigation` **30d≥100 / 7d=52**（Go2 上 JEPA 表征是否真能导航）

**第八轮的「jepa 换全称损失 94.6%，缩写才是生态写法」成立；但由此推出「jepa 只剩噪音」不成立。** 恰恰相反：它是本轮 commit 密度最高的一支。**star 在这支上完全失效 —— 要跟 JEPA 线只能按 commits 排，按 star 会全部漏掉。** 补充第八轮的结论：`jepa` 该留，但应与 `vision language action` 分开排序/展示，因为它靠 star 永远浮不上来。

## 第九轮 —— `pages` 规则「体量小」条件在巨型静态站上反向失效

第八轮判据 16 定为「名字像页 **+** 体量小」，本轮 19 个页形态幸存、**9 个进报告级**，最大 **304,228KB**：

`le-wam/le-wam.github.io` **297MB** · `liujiting123/morphact-website` 99MB · `DILL-VLA/dill-vla.github.io` 74MB · `PhyLatent/phylatent.github.io` 27MB · `4AxiomRobotics/Axiom0-page` 19MB · `rkdrn79/AnisoWM-page` 11MB。

**「体量小」在静态站上是反向的 —— 论文项目页往往带大图和视频，越大越是页。** 正确判据：**名字/后缀像页 → 单条件成立即丢**（`PAGE_SUFFIX` 已覆盖 `.github.io`/`-page`/`-site`/`-website`），或改用「根目录无 `src/`/`contracts/`/`crates/` 且 `language ∈ {HTML,CSS,JavaScript,TypeScript}`」。**别再用 size 做页形态的正向判据。**

## 第八轮（2026-10-25 06:45Z）—— 词表改全称，vla 成功 / jepa 惨败

第七轮把「缩写必须换全称」列为下一次必改项。本轮执行，结果**不对称**：

| 词 | 口径 | 60d total | 幸存 | 污染 | 报告级 |
|---|---|---|---|---|---|
| `vla` | 缩写 | 3,696 | — | **22.0%** | — |
| `vision language action` | 全称 | 205 | **138** | **1.4%** | **47** |
| `jepa` | 缩写 | 654 | — | 14.5% | — |
| `joint embedding predictive` | 全称 | 35 | **1** | 0% | 1 |

**🟢 `vla` → 全称是净胜，而且两个口径几乎不重叠（138/205 是 `vla` 从没抓到过的）。**
原因：仓库名普遍是 `smolvla` / `InfraVLA` / `TernaVLA` / `Q-VLA-Forge` 这类**合成词**，GitHub 搜索按词切分，独立的 `vla` token 打不中它们；而描述里通常写全称。**换全称 = 同时解决污染和漏检，是罕见的双赢。**

**🔴 `jepa` → 全称是灾难，损失 94.6%（654 → 35）。** JEPA 是 LeCun 家族的**固定缩写**，仓库名一律 `jepa-*`，几乎没人把全称写进 name/description。**规则要分类：术语本身就是通行缩写的（JEPA、VLA 作为模型类别名）必须保留缩写 + NEG 兜底；只有「缩写是习惯简写、全称才是描述主流」的才该换。** 差的不是污染，是**术语在生态里实际怎么被书写**。

**判据：换词前先量两个口径的 total_count 与重叠度。** 只看污染率会误判 —— `vla` 污染 22% 但基数 3,696；`jepa` 换全称污染降到 0，代价是赛道没了。

## 第八轮 —— 共享脚手架簇：黑名单结构上抓不到的一种农场

`seen` 饱和后本轮幸存 178 里，**同一个仓库名 `jepa-world-model-from-scratch` 出现 8 个不同 owner**（`AdrienBarrau` / `yassinzayed` / `amitabhswain` / `Mohan-afk` / `tanghaibao` / `vtnguyen04` / `jsaumil` / `avikds`），**description 逐字相同、根目录相同（`README.md,docs,model.py,scaffold.py`）、commit message 逐字相同（`Step 38: jepa_world_model_experiment`）**。这是教程/课程的共享脚手架，不是 8 个研究组。

**`github-farms.txt` 的黑名单按 owner 匹配，对这种「一 owner 一仓、同名不同人」的结构完全失效**（每个 owner 都只有 1 个仓，`owner≥3` 也命中不了）。**毕业作业簇污染了本轮报告级顶部 —— 7d 排名第一的 `AdrienBarrau`（30d=46 / 7d=30）就是它。**

**可审计的判据（新增，需进 scan）：** 同 repo 名跨 owner ≥3 **且** description 前 80 字符相同 → 判脚手架。三个条件都能一次搜索拿到，不需要额外 API。

## 第八轮 —— EXCL 只查 description，不查仓库名

`scan.py` 的 `if any(x in desc.lower() for x in EXCL)` 只看 description。**名字里带 `awesome` / `website` / `page` 但 desc 不带的直接漏网**，本轮 4 个（`ishandutta2007/Awesome-Vision-Language-Action-Models` 30d=10 甚至进了报告级、`WenhowYu/awesome-embodied-ai-daily`、`kaicheng001/Awesome-Action-Tokenizer`、`irom-princeton/awesome-robotics-video-world-model-papers`）。**判据：EXCL 必须同时查 `repo.split("/")[-1]` 和 description。** 另有 `*-website` / `*-page` / `*-showcase` 三种后缀同理，本轮 7 个页面形态进了报告级。

## 已修复的实现缺陷

1. **农场黑名单从未生效（第四轮）** — `github-farms.txt` 是行内注释格式，`scan.py` 只跳过 `#` 开头的行、不剥行内注释 → 解析出 3 个带注释尾巴的垃圾 key，匹配 0 个 owner，日志却显示 `farm=0`（看起来像「没有农场」）。改法 `l.split("#")[0].strip()`。**第五、六轮回归：泄露 0。**
2. **`owner≥3=farm` 误杀活仓（第四轮）** — 判掉 `rzc156/dreamforge` ★130/21、`Roboparty/P-BFM` ★95、`NEBULIS-Lab/D-JEPA` ★32/68、`liaohello/GigaWorld-Policy-Sim2Real` 18 提交。黑名单文件明写「3 仓不够，要三者同时成立（结构同质+跨赛道+提交极少）」，代码只实现第一条。**改为候选 ∓ 判决后，第六轮这四个全部正确保留。**
3. **`pages` 规则误杀真代码仓（第五轮）** — `short.lower() == owner.lower()` 把 `UniWAM/UniWAM` ★135/20（有 `train/ inference/ models/`）、`dextacwam/DexTacWAM` ★24/26 当列表页丢掉。改法：加 `not language` 条件。**第六轮回归：两仓幸存，pages 丢弃 79 → 15（全是 0–47KB 无语言同名仓）。**
4. **`terms` 多词命中只记首个（第五轮）** — `SmolWAM`/`AffordanceWAM`/`Skel-WAM`/`TrajWAM`/`so101-vla-wam`/`MT-WAM` 6 个 WAM 仓被归到 `robot manipulation`。**第六轮回归：多词命中 67 仓，`world action model` 扫描口径 72 → 95。**

## 未修复（第六轮新发现，第七轮已修）

5. **✅ 已修：单个 409 空仓打掉整个认证态。** `gh_get` 的降级条件是 `r.returncode != 0`，而 `repos/{r}/commits` 对空仓返回 **409「Git Repository is empty」** 也满足它 → `GH = False`，后续全部走未认证 urllib（60/h）。**铁律写着「429 与 409 必须分开」，代码只在返回值里分了，降级判断里没分。** 第七轮改法：`break` 前先判 error 文本含 `409`/`empty`，是则直接返回不降级。**回归通过：本轮 27 个 409 空仓全部正确分类为 `empty`，`GH` 全程未降级，核验 0 失败。**

## 第七轮新发现（2026-10-25 05:55Z）

### 13. 🔴 报告级 89 是 4.5× 低估 —— 全量核验后是 402

连续六轮都写「报告级 89（250 仓抽样下的下限）」。**第七轮用 core quota（5,000/h，与 search 独立池）全量核验 1,251 仓，119 秒完成**：

| 指标 | 抽样（250 仓） | 全量（1,231 仓） |
|---|---|---|
| ≥5 提交/30d | 89 | **402 (32.7%)** |
| ≥1 提交/7d | 未测 | **318 (25.8%)** |
| 30d 零提交 | 45 | **420 (34.1%)** |
| 爆完即停 | 20/51 | **222/402 (55.2%)** |

**抽样偏差量化：第六轮已验的 281 个里 38.4% ≥5 提交；未验的 950 个里 30.9%。** 偏差真实但不巨大 —— 上轮担心的「新仓天然更活跃导致外推失真」被证伪。**教训：当 core quota 有 5,000/h 而幸存集只有 ~1,600 时，「抽样」没有任何理由，直接全量。**

### 14. 🔴 「真零命中」把「全已见」误判成废词 —— 会直接误导删词

`per_term[term]` 只数**新幸存者**。有 seen 基线后，命中的仓若全部已见 → `per_term=0` → 审计打「⚠️ 真零命中」。**第七轮报了 12 个「真零」词，逐词单查 60 天 total_count 后全部非空**：`data availability` **126**、`intent-based` **116**、`egocentric` **141**、`sim-to-real` **166**、`world action model` **99**、`robot dataset` 41、`embodied data` 18、`proof of useful work` 13、`verifiable inference` 7、`restaking` 6、`maximal extractable value` 2、`robotics data engine` 1。

**分类必须四类：A 查询失败 / B 真零命中（total=0）/ C 全已见（total>0 但新=0）/ 有新增。** 「本轮无新增」= **窗口已采尽**，不代表词废。**这推翻前六轮反复出现的「这 4 个加密词该删或换 topic 路由」—— 它们是饱和，不是查不到。**

### 15. 🔴 缩写词子串污染 —— 铁律写着「缩写必然脏」，但词表里就有 `vla` / `jepa`

加深到第 2 页后长尾污染全浮出（第七轮新增集）：

- **`vla` 撞 VLAN（网络工程）与 Vlad（斯拉夫名）：污染 20/91 = 22.0%。** 典型：`valdissor1990-ui/vladossVPN`（★0 但 **30d=100 / 7d=100**，纯 Android VPN 客户端 —— 单仓就能霸榜）、`vedangkolte238-pixel/VLAN-InterVLAN-Routing`、`ondra-jakub/VlakoveCedule`（捷克语列车时刻表）。存量集 21/145 = 14.5%。
- **`jepa` 撞印尼语 `jepang`（日本）与城市 `Jepara`：污染 16/110 = 14.5%。** 典型：`Agung-laksono/centra-cargo-jepara`（30d=28/7d=28，家具货运站）、`kharinsaflaura/kuis-kotoba-jepang-{1,2,3,4}`（日语测验，**同一 owner 7 仓**）。存量集 13/120 = 10.8%。
- **剔污染后合并报告级 515 → 495**，其中 7d 活跃 **216**。
- **判据：缩写词必须配 carrier（像 `world model` 那样）或改用全称。`vla` 用 `"vision language action"`，`jepa` 用 `"joint embedding predictive"`。** 本轮未改词表（保持与前六轮可比），但这是下一次必改项。

### 16. ⚠️ `pages` 规则在两侧都判错：先漏放静态站，后误杀代码仓

第六轮修法是「`short==owner` 且 `size<300KB` 且 **无 language** 才丢」，于是 `*.github.io` 里 **<300KB 但有 language** 的仓被放行（GitHub 会把静态站标成 HTML/JS/CSS），两批共 **6 个漏网**（`vladimirsk1234.github.io` 0KB HTML、`focal-vla.github.io` 0KB HTML 等）。**第九轮反向验证了这个修法错得更深**：`pages` 只丢 <300KB 后，**19 个页形态幸存、9 个进报告级，最大 304,228KB**（`le-wam/le-wam.github.io` **297MB**、`liujiting123/morphact-website` 99MB、`dill-vla.github.io` 74MB、`phylatent.github.io` 27MB、`Axiom0-page` 19MB）。**「体量小」这个条件在巨型静态站上是反向的 —— 304MB 的 `.github.io` 仍然是页。**
**最终判据：改用「名字像页 / 后缀像页」单条件成立即丢；或「根目录无 `src/`/`contracts/`/`crates/` 且 language ∈ {HTML,CSS,JS,TypeScript}」。`size` 与 `language` 都不能单独当豁免 —— 研究组的官方实现仓经常就叫 `Owner/Project`，也可能叫 `Owner/Project.github.io`（后者塞了 594MB CSS/JS 资源）。**

### 16b. 🟢 第八、九轮补上的一课：`jepa` 不是噪音，是「★0 但代码写得最狠」

第八轮按污染率把 `jepa` 判为「换全称损失 94.6% → 缩写才是生态写法」，据此又推出「jepa 只剩噪音」，**后半句是错的**。第九轮真正新增的 65 个仓**全部是 `jepa`、全部 ★0、0 个 ★≥3**，但其中 **26 个报告级、11 个 7d 活跃**，且全轮前两名都在这里：`sahiltolani30/learn-a-world` **30d≥100 / 7d≥100**、`500mhzClub/Go2-JEPA-Navigation` **30d≥100 / 7d=52**。**star 与 commits 在这支上反相关 —— 追随 JEPA 线只能按 commits 排，按 star 会全部漏掉。`jepa` 该留，但应与 `vision language action` 分开排序。**

### 16c. 🔴 第九轮：`PER_TERM_CAP=25` 是抽样低估 3.85× 的直接原因

`scan.py` 的 `PER_TERM_CAP=25` 按 star 排序取样，本轮只核了 **76/234**。补全后：

| 指标 | scan 抽样（76 仓） | 全量（230 仓） | 倍数 |
|---|---|---|---|
| 报告级 | 20 | **77** | **3.85×** |
| 其中 7d 活跃 | 11 | **31** | 2.8× |
| 来自「抽样丢弃」部分的报告级 | — | **57/77 = 74%** | — |
| 来自「抽样丢弃」部分的 7d 活跃 | — | **25/31 = 81%** | — |

**未核验的 159 个里 `stars>=5` 有 0 个** —— star 排序把整个 ★0 长尾整条切掉，而报告级和活跃度的四分之三都藏在里面。**这是「按 star 分配核验预算会饿死 star 天然低的整个域」的第三次复现，第一次量化到「75% 的报告级被切掉」。core quota 5,000/h 足够全量，`PER_TERM_CAP` 存在的唯一理由是省时间，代价是把绝大多数信号藏起来 —— 直接删掉。**

### 17. 🟢 加密侧「空」第三次被推翻，这次是全量

33 个加密幸存仓**全部核验**：≥5 提交 **19 个（57.6%）**、clean 且 7d 活跃 **9 个（27.3%）**。**加密侧的提交率（57.6%）反而高于机器人侧（32.6%）** —— 但其中 10 个是「爆完即停」。`vearl-verified-compute/vearl` ★22 Rust **七轮连续**仍在写（7d=25）。

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

- 第十一轮快照 `output/ghradar/out.json`（70 幸存 / 2,236 原始，窗口 `2026-09-26..2026-10-26`）· `audit.log` · `report.md` · `scan.py` **未改** · 窗口拆解 `diff11.py` · 根目录 `tree11full.py` → `tree11full.json`（70/70）· 词分布 `agg11.py` · SuperMimic 簇 `cluster11.py` → `cluster11.json`（55 仓全量核验）+ `probe11b.py` → `probe11b.json` · 形态抽查 `shape11.py` · agent 指纹 `fp11.py` → `fp11.json` · `logs/2026-10-26#github-radar（第十一轮`
- 第十轮快照 `output/ghradar/out10.json`（26 幸存 / 592 原始，窗口 `2026-10-19..2026-10-26`）· `audit10.log` · 扫描 `scan10.py` · 跨窗词表 `terms10.py` → `terms10.json` · 簇探测 `cluster10.py` → `cluster10.json`（SuperMimic 55 仓全量核验）· carrier 审计 `carrier10.py` → `carrier10.json` / `carrier10_commits.py` / `carrier10_net.py` → `carrier10_net.json` / `carrier10_topics.py` → `carrier10_topics.json` · 根目录 `tree10.py` → `tree10.json` · `logs/2026-10-26#github-radar（第十轮`
- 第九轮快照 `output/ghradar/out9full.json`（234 幸存 / 3,461 原始）· `audit.log` · 全量核验 `full9.py`（230/234）· 候选重建 `cards9.py` · 对照第八轮 `out8.json`（178 幸存，dry-run 未落 seen）· 词表口径 `terms9.py` → `terms9.json`
- 第八轮：`output/ghradar/out8.json`（178 幸存 / 2,817 原始）· 全量核验 `verify8.py`（174/178）· 词表口径 `terms8.json` · 目录树 `tree8.py` · 加密复核 `cry8.json` · `logs/2026-10-25#github-radar`
- 第七轮：`output/ghradar/full7.py` → `full7.json`（1,251 仓）+ `full7b.py` → `full7b.json`（332 仓）· 污染量化 `contam7.py` · 词表饱和 `terms7.py`
- 第六轮：`output/ghradar/cry_verify6.py` · `decay6.py` · `robact6.py` · `agentfile6.py` · `wam6.py`
- 第八轮快照 `output/ghradar/out8.json`（178 幸存 / 2,817 原始）· `audit8.log` · 全量核验 `verify8.py`（174/178 = 97.8%）· 词表口径 `terms8.json` · 分析 `an8.py` / `deep8.py` / `tree8.py` · 加密侧复核 `cry8.py` → `cry8.json`
- 第七轮快照 `output/ghradar/out7.json`（332 新增 / 3,441 原始）· `audit7.log` · 全量核验 `full7.json`（1,251）+ `full7b.json`（332）· 污染量化 `contam7.py` · 词表饱和 `terms7.py` → `terms7.json` · 汇总 `all7.py` / `an7.py` / `final7.py`
- 第六轮快照 `output/ghradar/out6.json`（1,251 幸存 / 2,427 原始）· `audit6.log`
- 加密侧补齐核验 `output/ghradar/cry_verify6.py` · 7 天衰减 `decay6.py` / `robact6.py` · agent 指纹 `agentfile6.py` · 目录树 `tree6.py`
- WAM 全量翻页 `output/ghradar/wam6.py`（99 仓）· [world-action-models](/topics/world-action-models.md)
- 详细日志 `memory/logs/2026-10-25.md#github-radar（第八轮` · 第七轮 `#github-radar（第七轮`

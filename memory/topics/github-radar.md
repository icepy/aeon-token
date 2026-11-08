---
title: github-radar — 实现缺陷与判据
description: github-radar 三十三轮跑出的实现缺陷、过滤规则陷阱、以及「活跃度」判据（30d vs 7d、30d==7d 即当周新建、全量核验、star 排序偏差、窄窗误读、MAXPAGE 撞顶、seen 基线有效性、probe token 泛化、**carrier 误杀率九轮同向（35–36% vs 94–100%）但仅在长窗可读（7d 恒 100%）**、**窗口会改变报告级分布而不只是流量**、**「jepa+world model 双通道退化」判据第 32 轮被否（单轮回摆）→ 占比类判据须两条件同时成立**、**报告级可全落单一侧**、**入口词会换代须看「谁在贡献报告级」—— teleoperation 第 32/33 轮连两轮居首但质量最差**、**raw=1/seen=0 连三轮 = 靶子稳定，不等于词表无效**、**静态站逃逸：SITE_SUFFIX 只覆盖后缀，不覆盖「名字本身是 website」**、**7 天窗下 `30天=`≡`7天=`（12/12）→ 两栏退化为「仓龄」，测「爆完即停」须看首末提交日间隔；且 7d 下报告级全 ★0，star 只能 `min:0`**）
tags: [github-radar, discovery, methodology, lessons]
resource: https://github.com/search?q=%22world+action+model%22&type=repositories
timestamp: 2026-11-07T22:36:00Z
---

# github-radar — 实现缺陷与判据

从 [lessons](/topics/lessons.md#过滤器设计) 抽出的 skill 专属条目。三十三轮（2026-11-06）+ 第二十轮 7 天窗（11-07）实证。

## 第二十轮（2026-11-07，**7 天窗首次真正生效**，非 dry-run）—— `30天=` 与 `7天=` 退化同值；报告级 12/12 ★0；`jepa` 独占 5/12

漏斗：`gh-v3` · var=`days:7` · 18 词 · 2019 调用（搜索 20：单窗 17 / 需拆窗 1 / 二分 0）· 耗时 72s。原始 **452** → 幸存 **35** → 报告级 **12**。丢弃 seen=187 · excl=28 · archived=0 · short_desc=85 · carrier=86 · neg=14 · pages=17 · pages_root=0 · scaffold=0 · farm=0 · fail=0。核验 35/35 = 100%，黑名单 3 owner。`probe` 跳过（戳 11-03，4 天 < 7 天），`clusters.json` 未重写。

### 96. 🔴 7 天窗下 `commits_30d` 与 `commits_7d` 逐条相等（12/12）—— 两栏退化成「仓龄」

**这不是数据错，是窗口的数学后果**：报告级最老仓仅 15 天，7 天窗内的候选几乎全是新建仓，`30天=` 与 `7天=` 必然同值。所以第 21 轮立的铁律「30 天提交高 ≠ 现在在写」**在 7 天窗下无法用这两个数分辨**。要测「爆完即停」必须比**首提交日与末次提交日的间隔**，而不是两个计数。**判据级：窗口变短不只改流量分布，还会改判据的可观测性 —— 换窗前要重列哪些判据仍然可读。** [source: logs/2026-11-07#github-radar（第 20 轮）]

### 97. 🟢 报告级 12/12 全 ★0 → 7 天窗下 star 排序必须 `min:0`

与第十一轮「★≥5 只有 1 个」同向且更彻底。**7 天窗里没有任何报告级仓拿到星，任何 star 地板都会把整份名单清零。** star 只能作展示字段，不能作筛选或排序主轴。 [source: logs/2026-11-07#github-radar（第 20 轮）]

### 98. ⚠️ `jepa` 单架构词吃掉 5/12（42%），且多为复现/练手仓

`prh-jepa`（明写 replication）· `kuanjepa` · `SpatialCell-JEPA`（NeurIPS workshop 代码）· `nakka1/World-Models-JEPA`（量子硬件误差缓解，与机器人无关）· `prasad-yashdeep/jepa-world-model-from-scratch`。**这是「一个学术名词在衍生复现仓」，不是多方向扩散**；5 条里只有 2 条属本方向。与第三十一轮「`jepa`+`world model` 双通道退化」判据不同 —— 那轮被证伪是总量口径，这轮是**单词语义质量**，两者不可混为一谈。 [source: logs/2026-11-07#github-radar（第 20 轮）]

### 99. 🔴 加密侧第五连轮近零：报告级 0 条

唯一主动通道 `intent-based` raw=12 / 新=1，但未进报告级；`restaking` raw=1 全饱和；`maximal extractable value` **连两轮 raw=0**；`data availability` raw=15 但新=1。**加密侧在本通道召回连续五轮接近零，与 arxiv-radar 侧同向 —— 两条通道同时空，已成结构性而非轮次波动。** [source: logs/2026-11-07#github-radar（第 20 轮）]

### 100. ⚠️ digest 的「核验 35/35（100%）」与「未核验 1」并列，读起来自相矛盾

两个数都对但量的不是一件事：「100%」是**尝试率**，「未核验 1（`Wang-qishen/PredMind`）」是**没拿到 commits**（限速/空仓）。**修法：拆成 `尝试 X/Y` + `成功 X/Y` 两栏。** 属显示层缺陷，不改脚本（不改脚本铁律）。 [source: logs/2026-11-07#github-radar（第 20 轮）]

## 第三十三轮（2026-11-06，**30 天窗**，非 dry-run）—— 静态站逃逸首现；`teleoperation` 由单轮升为连续两轮；加密侧第四连轮近零

漏斗：原始 **2066** → 幸存 **30** → 报告级 **14**，核验 **30/30 = 100%**（全量）。丢弃 seen=971 · excl=133 · archived=0 · short_desc=361 · **carrier=438** · neg=64 · pages=66 · pages_root=0 · scaffold=0 · farm=3 · fail=0。二分至一页：单窗 13 / 需拆窗 5、二分 4 次、搜索调用 45。耗时 166s（搜索 128s / 核验 4s）。`var` 仍未注入（实吃 30d）。`probe` 跳过（戳 2026-11-03，3 天 < 7 天），`clusters.json` 未重写 —— **digest 里那 14 行是 11-03 旧结果，不能当本轮读**。

### 90. 🔴 静态站逃逸两例：`pages` 后缀规则与 `EXCL` 同时漏

`EGalahad/website`（desc 自述 "Static documentation hub for sim2real and Bolt Runtime"，30d=5 / 7d=5）与 `henrikagreat/soarm101challenge`（desc "Static website for the teleoperation challenge..."）双双被当报告级放行。**根因：`SITE_SUFFIX` 只收 `-website` / `.github.io` 这类后缀形态，`EXCL` 里也没有 `website` / `docs` / `hub` → 覆盖的是「后缀」，不覆盖「名字本身是 website / 站名」的形态。** 这推翻了「站点仓按后缀无条件丢」的覆盖假设。候选修法：desc 侧窄判据（desc 含 `static website` / `documentation hub` / `project page` 且无 `language` → 丢），但**须先量误杀再改**。 [source: logs/2026-11-06#github-radar]

### 91. 🟢 `teleoperation` 连续第二轮是最大报告级入口（6/14），但也是质量最差的口径

11 条新收 → 报告级 6：`Moad-byte/PhantomArm`(9/9) · `PMETGAIC/Pancrazio`(14/8) · `henrikagreat/soarm101challenge`(7/7) · `Bkrakshith/hospital-sim-ros2`(7/4) · `unitreerobotics/R1-7A`(16/2) · `Bkrakshith/g1-webcam-teleop`(5/2)。#87「入口词会换代」**由单轮升为连续两轮**。但 6 条里 1 条静态站、2 条同一 owner（`Bkrakshith`）的 Unitree G1 配套仓、`Pancrazio` 是框架壳 —— **真信号只有 `unitreerobotics/R1-7A`（本体厂官方账号，单/双臂遥操作 + 多相机录制回放），且 30d=16 / 7d=2 → 上月铺完、本周停，按 commits 读不是在做。** 判据：入口词的报告级条数 ≠ 信号量，必须逐条看 owner 与 30d/7d 双读数。 [source: logs/2026-11-06#github-radar]

### 92. 加密侧第四连轮近乎零；唯一幸存是「双满但疑似农场」

唯一加密侧报告级 `VibeHash/vibehash`（★2，30d=≥100 / 7d=≥100，`proof of useful work`，矿工训 AI 模型的 PoUW 测试网）—— **本轮唯一 30d 与 7d 双满且 ★≥2 的仓，但 `commits=100` 是 `per_page` 上限（记 ≥100），农场/镜像形态高危，下轮单独看根目录。** 其余 6 个加密词（`data availability` / `intent-based` / `restaking` / `maximal extractable value` / `verifiable inference` / `world action model`）新收全 0 —— 与 arxiv-radar 加密侧第 38 轮同样零产出**同向**，两条通道同时空，记一次、不作判据。 [source: logs/2026-11-06#github-radar]

### 93. 🟢 carrier 口径第九次同向 → 候选结案

丢弃侧仓名自带词表词 169 个（owner 去重 168），核 146 → 近 7 天存活 **51/146 = 35%**；放行幸存者对照 **29/29 = 100%**。连续九轮同向（35–36% vs 94–100%），**carrier 判别力结论不再每轮重开**；改表仍须走 PR 且改前抽检两行。 [source: logs/2026-11-06#github-radar]

### 94. 词表四分类 8 饱和 / 10 有新增，1 个饱和其实是过滤损耗

查询失败 **0** / 真零 **0** / 全已见 **8** / 有新增 **10**。饱和 7 个真被 seen 吸收（`embodied data` raw12/seen4 · `world action model` 40/33 · `robotics data engine` 1/1 · `verifiable inference` 5/4 · `data availability` 56/2 · `restaking` 4/3 · `intent-based` 55/1），**第 8 个 `maximal extractable value` raw=1 / seen=0 连续第三轮同一读数 → 靶子稳定，延 #85，不判饱和。词表动作：本轮不动**（无真零、无失败格）。 [source: logs/2026-11-06#github-radar]

### 95. ⚠️ 异常形态：无 `language` 3 个、空仓 1 个、farm 黑名单 3 个

无 `language`：`DillanImans/haptic-needle-teleoperation` · `ccfdfvapour/SynthSoM-Twin` · `chrisjcc/cohomology`（后两个 desc 与方向词语义弱相关）。空仓（409）：`Louis-24000614/Dual_Nero_Vla`。`farm` 黑名单命中 3 owner。**`farm` 计数连续两轮为 3，与 #89 的「爆完即停降至 2 个」同属「新仓潮退潮后的长尾」形态。** [source: logs/2026-11-06#github-radar]

## 第三十二轮（2026-11-05，**30 天窗**，非 dry-run）—— 双通道退化判据未成立；加密侧第三连轮零产出

漏斗：原始 **2093** → 幸存 **36** → 报告级 **17**，核验 36/36（全量），黑名单 3 owner。丢弃 seen=977 · excl=132 · archived=0 · short_desc=370 · **carrier=448** · neg=61 · pages=64 · pages_root=2 · scaffold=0 · farm=3 · fail=0。二分至一页：单窗 13 / 需拆窗 5、二分 3 次、搜索调用 43、min:0。耗时 152s（搜索 124s / 核验 8s）。`var` 仍未注入（第 10 连跑）。

### 84. 🟢 #79 的「双通道退化」判据**未成立** —— 两个条件同时反向，结案为单轮回摆

第 31 轮立的标尺是「`jepa` 新收仍 ≥10 而其余 17 词合计 ≤10 → 退化」。本轮 **`jepa` 新收 13 → 7**、其余 17 词合计 **21 → 29**，两个条件都反向；幸存占比也从 40% 回落到 **11/36 = 31%**。**判据：#79 是一次单轮回摆，不是趋势。词表仍在多通道产出，不加词、不裁词。教训是「单轮占比定阈值」本身不够稳 —— 占比类判据至少要两个条件同时成立才可下结论，与本轮 defillama-radar「两轮连续读数才是最短证据」同型。** [source: logs/2026-11-05#github-radar]

### 85. 🔴 `maximal extractable value` 连两轮 raw=1 / seen=0 —— 是「同一个被过滤的仓」而非饱和

第 31 轮记它 raw=1 seen=0 判为过滤损耗；本轮**完全复现同一读数**。含义：它每次都捞到同一个已被过滤的仓，不是新仓在进来。**这条同时修正 #80 的动作建议 —— 过滤损耗不一定等于「词表无效」，也可能是「词有效但靶子稳定」。按三级动作先「换写法」（`ti:"MEV"` 式改写或配 carrier），删词留到换写法后再量一轮。** [source: logs/2026-11-05#github-radar]

### 86. 词表四分类（分开记）：查询失败 0 · 真零 0 · 饱和 9 · 有新增 9

饱和 9 中 8 个确被 seen 吸收且**别删**（`embodied data` 11/5 · `robot dataset` 19/19 · `robotics data engine` 1/1 · `verifiable inference` 6/5 · `proof of useful work` 9/9 · `data availability` 57/2 · `restaking` 4/3 · `intent-based` 57/2）；剩 1 个 `maximal extractable value` 见 #85。**加密侧 4 词 + MEV 全部 0 新收（第三连轮）。** 逐词返回/新收/已见：`world model` 771/4/175 · `jepa` 352/7/159 · `teleoperation` 235/7/170 · `robot manipulation` 159/5/122 · `sim-to-real` 104/2/83 · `vision language action` 94/4/75 · `egocentric` 91/4/73 · `sim2real` 81/2/43 · `world action model` 41/3/31。[source: logs/2026-11-05#github-radar]

### 87. 🟢 `teleoperation` 首次成为单轮最大报告级入口 —— 入口词确实会换代

报告级 17 条词分布：`teleoperation` 4 · `jepa` 3 · `world model` 3 · `egocentric` 2 · 其余各 1。**`teleoperation` 上轮仅 7 新收、报告级 0，本轮报告级 4 条居首。** 验证了「入口词会换代」：判断词表健康要看**谁在贡献报告级**，不能只看 raw 返回量。**注意其 raw 235 只排第三、`world model` 771 是它三倍多 —— 返回量与报告级产出不成比例，答辩/教程类长尾多。** [source: logs/2026-11-05#github-radar]

### 88. 🟢 carrier 误杀第八次同向：丢弃侧 36% vs 放行侧 94%（长窗可读）

丢弃里仓名自带词表词的 174 / owner 去重 172 / 本轮核 146 → 近 7 天存活 **53/146 = 36%**；幸存者对照 **33/35 = 94%**。差 2.6 倍，与 #83（35% vs 94%）逐位吻合。**carrier 判据未证伪，不动；改表仍须走 PR 且改前抽检两行。** [source: logs/2026-11-05#github-radar]

### 89. ⚠️ 「爆完即停」降到 2 个且无大仓；无 language 3 个、空仓 1 个

30d 有量 / 7d 归零 2 个：`cookies060809/mwm-resumption`（30d=49）· `cgznb/breast-mri-jepa-versions`（未进报告级）。上轮 3 个含唯一 ★89，本轮**无大仓** —— 但仍须并排看 30d/7d，star 与单看 30d 都不够（#81 判据不变）。无 `language` 3 个：`linker-bot/SDK`（**进报告级，desc 明写 SDK 目录 → 可能是聚合仓而非页**）· `Zizizi-hao/NegWAM` · `xiaopengyou0000/AERIS`。空仓（409）1 个：`zzzyzh/ReOPD`。**新仓潮第五次，仍按 commits 读。** [source: logs/2026-11-05#github-radar]

## 第三十一轮（2026-11-04，**30 天窗**，非 dry-run）—— 词表疑似退化为双通道；加密侧零新增要拆两种成因

漏斗：原始 **2090** → 幸存 **53** → 报告级 **25**，核验 53/53（全量），黑名单 3 owner。丢弃 seen=964 · excl=129 · archived=0 · short_desc=370 · **carrier=444** · neg=58 · pages=59 · farm=13 · fail=0。二分至一页：单窗 13 / 需拆窗 5、二分 2 次、搜索调用 41、min:0。耗时 141s（搜索 118s / 核验 8s）。

### 79. 🔴 `jepa` + `world model` 贡献 21/53 = 40% 幸存者 —— 集中度首次触及「双通道」阈值

两词合计 raw **1117** = 全轮 2090 的 **53%**。逐词返回/新收/已见：`world model` 769/8/172 · `jepa` 348/13/152 —— 新增也集中在这两个（13 + 8 = 21）。其余 16 词里最高的 `teleoperation` 只有 7。

**判据：若下一轮 `jepa` 新收仍 ≥10 而其余 17 词合计 ≤10，说明词表实际已退化为双通道，需按 arxiv-radar 的「出口分散度」口径复核（几个词在贡献），而不是继续加词。** 这与 #67「`jepa` 是在扩散的写法」同向，但这次量到了幸存集的占比，不只是单词语义。 [source: logs/2026-11-04#github-radar]

### 80. 🔴 加密侧第二连轮零新增，但「饱和」与「过滤损耗」必须分开判 —— 只有后者是删词候选

四个加密词本轮 0 新增，成因不同：

- `restaking` raw=4 / seen=3 · `intent-based` raw=55 / seen=2 · `data availability` raw=57 / seen=2 → **seen 饱和**，话题活着但都见过，**删词会丢覆盖**。
- `maximal extractable value` raw=1 / seen=0 → **被过滤规则整条吃掉**，这才是词表无效候选。

**判据（承 #74 的四分类）：看到「0 新增」先分 `seen` 与 raw 的差值 —— `seen≈raw` 是饱和，`seen≈0 且 raw>0` 是过滤损耗。下轮若要动加密侧，只动 MEV 一个词，且先跨窗量 `total_count`。** [source: logs/2026-11-04#github-radar]

### 81. ⚠️ 「爆完即停」本轮吃掉了全部重点仓，含唯一的 ★89 大仓

30d 有量 / 7d 归零 3 个：`Benjamindaoson/WorldDynamics`（30d=19）· **`NVlabs/Flora`（★89，30d=11）** · `backblaze-b2-samples/aistore-b2-gr00t-robotics-training`（30d=9）。

报告级 25 条里 ★≤3 占 22/25、近 7 天仍在写 22/25，其中 **7d == 30d 的 15 个**（新仓潮第四次）。**判据（承 #68 / #76）：star 与 30d 提交数都不足以判「现在还在写」；唯一可信的是把 30d 与 7d 并排看，7d=0 而 30d 高的就是本轮的「重点仓」，正好也是最该扣分的。** [source: logs/2026-11-04#github-radar]

### 82. ⚠️ 「无 language 字段」的批量出现不等于非代码仓 —— 要看同 owner 形态

本轮 8 个无 `language`：`Kushaldatta17/so101-pick-and-place` · `jutrasd/CPE-595-Project---VLA-Robustness-Under-Environmental-Noise` · `Overdamp/g1_study_101` · `Overdamp/g1_study` · `Milkywayna/RLP-from-goals-to-actions` · `sejmoonwei/ForesightFlow` · `LKVexa/KerJEPA-...` · `ZovdaHub/dm0010-egocentric-physical-interaction-samples`。另有空仓 409 一个：`yadong-cruz/VISTA`。

**注意 `Overdamp` 同 owner 两仓同义名（`g1_study` / `g1_study_101`）—— 正是 gh-v4 要求的「同 owner 多仓」形态，但两仓皆无 language，更像课程/笔记作业而非脚手架，本轮不判正样本。** 这说明 #78 的新判据（同 owner 多仓）单独用也不够，还要叠「是代码仓」这一层。 [source: logs/2026-11-04#github-radar]

### 83. 🟢 carrier 误杀对照在长窗维持：丢弃侧 35% vs 放行侧 94%（第七次同向）

丢弃里仓名自带词表词的 171 个 / owner 去重 167 / 本轮核验 146 → 近 7 天存活 **51/146 = 35%**；幸存者对照 **49/52 = 94%**。两线差 2.7 倍，与第 13 轮的 34/97 同向。**本轮是长窗，指标可读**（7d 窗下两侧恒 100% = 测不到，见 #77）。**判据：#77 的「窄窗测不到」与 #73 的「长窗稳定复现」是一体两面 —— carrier 判据未被证伪，改表仍须走 PR 且改前抽检两行。** [source: logs/2026-11-04#github-radar]

## 第三十轮（2026-11-03，**7 天窗**，非 dry-run）—— 首次真正跑窄窗：窗口改变报告级分布；carrier 指标在窄窗失效

漏斗：原始 **439** → 幸存 **35** → 报告级 **7**，核验 35/35（全量）。丢弃 seen=171 · excl=22 · short_desc=84 · **carrier=96** · neg=13 · pages=16 · pages_root=2 · farm=0 · fail=0。四分类：查询失败 0 · 真零 1（`robotics data engine`）· 全已见 6 · 有新增 11。

### 75. 🔴 7 天窗比 30 天窗**幸存更多、报告级更少** —— 窗口不只是成本旋钮

同一词表下，第 15 轮 30d = 33 幸存 / 9 报告级；本轮 7d = **35 幸存 / 7 报告级**。窗口收窄把长尾老仓挡在外面，报告级集中度反而上升。**与 SKILL「有 seen 后 7d 与 30d 稳态产出相同」不一致，差异来源是 `seen` 尚未覆盖 7 天窗外的新增。判据：窗口既是成本旋钮，也在改变报告级分布 —— 跨窗口的「幸存数/报告级数」不可直接相减。** 与 #43「窗口是流量旋钮不是语义轴」同族，但这次量到的是**报告级分布**，不只是流量。

### 76. 🔴 `commits_7d == commits_30d` 第三次成立，且形式更硬

7 个报告级里 **7/7 满星为零、7/7 两窗数字完全相同** —— 等于仓库全部建在 7 天内。前两轮是 11/12 与 8/9「相等」，本轮是**全部相等**。**新仓潮判据（#68）在窄窗下反而更干净：窄窗本身已筛掉老仓，「相等」只剩一种解释。**

### 77. 🔴 carrier 误杀对照在 7 天窗下恒等于 100%/100% —— 该指标只在长窗可读

丢弃堆里仓名自带词表词 **31/31 = 100%**（近 7 天存活），放行侧 **31/31 = 100%**。与第六次 36% vs 97% 完全反向，但**不是 carrier 变好了**：7 天窗下丢弃堆几乎全是近 7 天新建仓，天然「活跃」→ 指标失去分辨力，与 #52 的「两侧都满格时对照无分辨力」同一机制。**判据：carrier 误杀率只能与 30/60d 长窗的读数比，7 天窗的 100% 是分母效应。** 这条给 #54「跨窗口比必得假信号」补了反方向的例子 —— **窄窗不是「没有误杀」，是「测不到误杀」。**

### 78. 🔴 `supermimic` 从正样本退为「异质撞名」—— gh-v4 的正样本判据要改

probe 种子 65 → 候选 token 108 → 反查 28 · 热仓核验 203（未达门槛 73）→ **0 簇过三条件**。`supermimic` total=**132** 但 owners=**99** —— 短名在通用语境里扩散，不是单一项目簇。**判据：`gh-v4` 的正样本不能只看短名聚合量，要改成「同 owner 多仓」** —— 一 owner 一仓 = 撞名（与 #47 同一结论，这次是从「正样本」侧推翻）。`teleop` 本轮 owners=99 / 平均每 owner 5.8 仓，正是「共享脚手架 owner 黑名单抓不到」的形态，维持撞名嫌疑、不作候选词。

## 第二十九轮（2026-11-02，**30 天窗**，非 dry-run）—— 判据全部维持；`teleoperation` 成新入口

漏斗：原始 **2039** → 幸存 **33** → 报告级 **9**，核验 33/33。丢弃 seen=955 · excl=130 · short_desc=360 · **carrier=431** · neg=56 · pages=60 · pages_root=1 · scaffold=0 · farm=13 · fail=0。

### 70. 🟢 第 14/15 轮连续同形：报告级仍 100% 落机器人侧，加密侧 0

9 个报告级全在机器人/具身侧，与上一轮 12/12 同向。**这是「加密侧在代码通道上稀薄」的第三个连续样本**，但边界不变 —— 只能说明这个 18 词表 + carrier 组合测不到。

### 71. 🟢 入口在换代：`teleoperation` 新收 14 = 最大入口，报告级占 4/9

上一轮的最大入口是 `jepa`（4/12），本轮 `teleoperation` 新收 **14**、报告级 **4/9**；`egocentric` 新收 4、报告级 2。**判据：看「哪个词在贡献报告级」而不是「哪个词返回量最大」** —— 与 #67 的「新收/返回比值」同源。

### 72. 🔴 `commits_7d == commits_30d` 第二轮复现：9 个报告级里 8 个相等

唯一例外 `sdua078/TeleoPro`（★106，30d=7 / 7d=5）。**新仓潮判据（#68）从单轮变两轮连续成立。** 量最大的两个仍是新仓：`Embodied-Scout-PuppyPi`（★0，71/71）、`egoumi`（★1，28/28）。

### 73. 🔴 carrier 误杀第六次：36% vs 97%

丢弃侧近 7 天存活 **52/146 = 36%**，放行侧 **29/30 = 97%**。六轮序列 36/97 → 35/96 → 36/96 → 34/97 → 32/97 → **36/97**。**32–36% vs 96–97%，六轮无一次反向 —— 放宽是唯一还没做的动作。**

### 74. ⚠️ 三个词表分类要分开记（避免「饱和」吞掉过滤损耗）

查询失败 **0** · 真零 **0** · 全已见(饱和) **9** · 有新增 **9**。饱和 9 里 8 个真被 seen 吸收，1 个（`maximal extractable value`，raw=1 / seen=0）是**过滤损耗不是饱和** —— 按 #58 的 `seen < raw 5%` 规则必须单独归因，不能并进饱和。

## 第二十八轮（2026-11-01，**30 天窗**，非 dry-run）—— 加密侧在报告级归零；新仓潮 vs 持续工程

`scan.py ""` → **第 14 轮「日跑 7 天」仍未生效**（`var` 不注入，`scan.py:184` 吃 30d）。

漏斗：原始 **2046** → 幸存 **31** → 报告级 **12**。丢弃 seen=962 · excl=136 · short_desc=363 · **carrier=428** · neg=55 · pages=57 · pages_root=1 · scaffold=0 · farm=13 · fail=0。18 词 × 二分至一页（单窗 13 / 需拆窗 5 · 二分 3 次 · 搜索 43）· 核验 **31/31 = 100%** · 119s。

### 66. 🔴 报告级首次 100% 落在机器人/具身侧，加密侧零 —— 从「顺带」变「零」

12 个报告级全部落在 `manipulation` / `teleoperation` / `sim-to-real` / `JEPA` / `world model`。上一轮 10 个里还有 1 个旁落，本轮 12/12 全在机器人侧；`restaking` 有 1 条新收但没过报告级。**连续两轮同向 ⇒ 「加密侧在代码通道上确实稀薄」不再是单轮噪声，但仍不能推向「加密没有工程量」—— 只是这个 18 词表 + carrier 组合下测不到。**

### 67. 🟢 `jepa` 是在扩散的写法，`world model` 已饱和

`jepa` 单词贡献 **4/12** 报告级（beeJEPA / ijepa-decoder / jepa-mean-collapse / CT_PhysProb_JEPA），7 天新收 7 条（两轮 5 → 7 上行），返回量第二（340）。**反向对照：`world model` 返回 754 却只新收 5** —— 同一赛道上，老词的返回量被历史 `seen` 吃干，新写法还在扩散。**判据：判断一个方向是否还在长，看「新收/返回」比值，不看返回量。** 这与 [第八轮](#第八轮2026-10-25-0645z--词表改全称vla-成功--jepa-惨败) 的「`jepa` 缩写是主流」一致：全称化会杀掉它，缩写保留才对。

### 68. 🔴 `commits_7d == commits_30d` 在报告级 11/12 上成立 —— 那是新仓潮，不是持续工程

十二个里 11 个两列逐位相同（beeJEPA 36/36、Sim-to-Hand 29/29、lifth-pai 23/23、lunar-trn 19/19、ijepa-decoder 17/17、jepa-mean-collapse 9/9、CT_PhysProb_JEPA 9/9、robolink 6/6、X-model 6/6、wildcat 5/5、acwm 5/5）；只有 H1V3 是 19/3（★4，唯一有 star 的，老仓放缓）。**含义：这批仓全部在最近 7 天内建仓或一次性推完。判活跃度必须同时看两列；单看 30d 会把新仓潮读成「在写」，单看 7d 又会把老仓的周期性提交读成死。** 与第十轮判据（7d=0 而 30d 高 = 爆完即停）互为镜像，两条一起才构成完整判据。

### 69. 🔴 carrier 误杀第五次同窗口复现：32% vs 97%

丢弃侧仓名自带词表词 **160 仓 / 157 owner**，核 146，近 7 天存活 **47/146 = 32%**；放行幸存者核 31，存活 **30/31 = 97%**。五轮序列 **36/97 → 35/96 → 36/96 → 34/97 → 32/97**，全部 32–36% vs 96–97%。**放宽已具备动手条件（本轮仍未改脚本）。**

**载噪点（只记不判）**：`animeshdubey6472/RoboFlow-VLA` 爆完即停；无 language 6 个。


## 第十七轮（2026-10-26，60 天窗，probe，dry-run）—— carrier 误杀率首次有同口径对照组：50% vs 50%，无差异

本轮 `var=dry-run days:60 probe`，窗口 `2026-08-27..2026-10-26`，18 词 × **窗自适应（整窗 17 / 拆 3 子窗 1）**。原始 **3818** → 幸存 **51** → 报告级 **11**。核验全量 51/51，耗时 302s。

### 36. 🟢 carrier 误杀率有对照组后归零 —— 第十六轮的「误杀率偏高」作废

脚本首次同时打出两侧：**丢弃侧**仓名自带词表词 346 个（owner 去重 327），核 149 个 → 近 7 天存活 **74/149 = 50%**；**放行侧**幸存者核 24 → **12/24 = 50%**。

**同一比例。** 第十六轮按 12 个样本粗估的「误杀率一半到四分之三、明显偏高」站不住 —— 那个估法没有对照，而「活着」在这个池子里本来就是 50% 的基线。**结论：carrier 不构成对活仓的额外误杀，不放宽。** 这是「抽样前先算分母、量误杀率必须有对照组」这条判据第一次真正执行完。

### 37. 🔴 新回归：自适应开窗省了 2/3 搜索调用，代价是覆盖率跌破 95%

开窗从 `18 × 3 子窗` 改为「整窗 17 / 拆窗 1」（`WIN_SPLIT_TOTAL=1000`，`scan.py:366`）。**`sim2real` 52.7%、`restaking` 83.3% 首次跌破 95%。**

手工复量排除封顶：`sim2real`（`created:>2026-08-27`）`total_count=163`，第 1 页 100 条 + 第 2 页 63 条，**两页零重叠、并集正好 163** —— GitHub 侧完全可分页取尽，52.7% 不是仓库封顶。差额来自整窗单次查询的 `total_count`（169）与实际 `items`（89）不一致。

**口径升级：撞顶 66.5% 不可引用（第十四轮），查询侧 total/items 不一致造成的 52.7% 同样不可引用。** 单轮一个样本，先记不改代码。

### 38. ✅ probe 第三判据（`thematic`）首轮全额生效 —— 3 个假阳性全部拦下

`uniview`(19/18) 仍 `cohesive=true` 但 `thematic=false`（主题词 `hikvision`×5 / `dahua`×4）→ 被词表语义挡掉；`senku` / `pouw` / `eidolon` / `physguard` 本轮全 `cohesive=false`（`pouw` 主题词不再取到 `content`，GLUE 剔除生效）。第十六轮 3 个假阳性回归通过，本轮 **0 个同主题真簇**。

## 第十六轮（2026-10-26，60 天窗，probe，dry-run）—— carrier 丢弃名单上线；同窗口复跑 = 完全重复

本轮 `var=dry-run days:60 probe`。原始 **4004** → 幸存 **49** → 报告级 **10**，与第十五轮（4001 / 49 / 10）逐项几乎相同。

### 39. ✅ 第十五轮记的「carrier 是唯一不落名单的规则」已进代码 —— 审计完整性 3/5 → 5/5

`output/ghradar/dropped.json` = `{carrier: [886 个 repo], short_desc: [744 个]}`。**「每条丢弃规则都要能被审计」这条铁律第一次全量兑现。**

### 40. ⚠️ 拿到 `dropped.json` 第一件事是算分母，不是抽样

我这次先抽了 12 个才去数 190/886 的总量 —— **顺序反了，抽样比例是在不知道总体规模的情况下定的**，直接导致第十六轮的粗估被第十七轮推翻。**新数据集到手：先报总量与分母，再定抽样。**

### 41. 🟡 `cohesive` 不充分 —— probe 判据的第三次修正

`cohesive=true` 只量「簇内自洽」，不量「是否是我们这个词」。本轮 3 个 cohesive 候选全假：`senku` 主题词只有 `with`×11（**连接词不在 `STOPWORDS`**）、`uniview` 是海康大华 NVR、`pouw` 撞荷兰语「货运」。→ **`total` 小是必要、`cohesive` 也不充分，还需第三条：主题词落在我们词表语义内。**

### 42. 🟢 第十五轮留的 `PhysGuard` 悬念关闭：不是占名，是同名死仓

`Data-Driven-Computational-Geotechnics/PhysGuard` created 10-25、pushed 10-26、Python（活着）；`ZhouChaunge/PhysGuard` created 04-30、**pushed 2026-05-05，停摆 5 个多月**。「提前占名 / 搬运」假设不成立。

## 第十五轮（2026-10-26，60 天窗，probe，dry-run）—— 翻页修好，幸存 4→49；下一处同型缺陷是 carrier 的措辞假设

本轮 `var=dry-run days:60 probe`，窗口 `2026-08-27..2026-10-26`。原始 **4001** → 幸存 **49** → 报告级 **10**。核验全量 49/49，耗时 388s。

### 35. ✅ `MAXPAGE` 撞顶已修，且逐仓可验 —— 第十四轮判据当场兑现

`MAXPAGE=3` 降级为「曾撞顶」探测器，实际页数 = `min(MAXPAGE_HARD=10, ceil(total/100))`（`scan.py:303`）。审计自报三个撞顶子窗（`world model` 513 / 497 / 416）并自动加页。

**硬证据（本轮新测）：** 第三子窗 `2026-08-27..2026-09-16`（total=416）star 排序下，`SunCCNY/Embodied-AI` 在**第 4 页** —— 旧 `MAXPAGE=3` 永远取不到，新逻辑取到并进报告级（★0、30d=54、7d=9）。`world model` 覆盖率 66.5% → **≥95%**。**「60 天窗比 30 天窗覆盖率低」作废，60 天窗现在更可用。**

### 36. 🔴 下一处同型缺陷：carrier 假设「desc/topics 里得有机器人词」

carrier 已从 desc 改为 `desc ∪ topics`（`scan.py:336`），本轮 **886 个**被 carrier 丢（22.1%，最大单条规则），其中 **16 个靠 topics 放行**，含报告级第一 `latent-horizon/pytorch-world`（★2、30d=85、7d=47）。

**但两个字段都没有 carrier 词的活仓仍整条丢。标本 `colorHur/world-model-lab`：** ★1、Python、`pushed_at` 距开跑 5 小时、不在 `seen`、7d 满。topics 是 `latent-dynamics / model-based-reinforcement-learning / reliable-horizon / reproducible-research / rollout / world-model`，desc 全句无 `embodied/robot/vla/manipulation/sim2real/teleop/egocentric/action/policy/rlbench/lerobot`。**离线 exec `scan.py` 常量重放确认 DROP，且实测它在子窗第 1 页就被取回 —— 单因 carrier，不是翻页。**

**判据：carrier 的语义是「这个词得配机器人语境才算数」，而世界模型正在往「可复现的 rollout 评测」这类纯 ML 措辞漂移 —— 这是词表级问题，不是参数级。别盲改**（参照 `jepa`→全称 654→35 的灾难，缺「命中率 / 误杀率」双向度量前不动）。

### 37. ⚠️ 可审计性缺口：carrier 与 short_desc 是唯一不落名单的两条丢弃规则

`seen / excl / neg / pages / scaffold` 全打印具体仓名；`carrier` 只累加计数（`drop["carrier"] += 1`），**丢掉谁无从查**。铁律「每条丢弃规则都要能被审计」在代码里只兑现 3/5。**下一轮要量 carrier 误杀率，必须先补 `carrier_dropped` 列表 —— 否则每次都得离线重放并重算全套过滤器。**

**本条对应的自查纠错（防重犯）：** 我曾按「不在 `audit.log` 里 = 不在 carrier 丢弃堆」推了一版，是错的 —— 脚本只打印 carrier 的**放行**名单（`scan.py:575`）。**「审计里没有」≠「没被丢弃」，必须用 total_count 实测页位次才能定论。**

### 38. probe token 泛化仍未修，且这次最像真簇的也是假的

`eidolon` total=98 / owners=74，热仓第一 `Sallyn0225/eidolon-sc`（★242、30d/7d 都满、57MB Python）—— profile 确认是**《偶像大师 闪耀色彩》AI 角色对话分身**，与 world model / embodied 零关系。`senku`（54/40）第一是分子对接实验室工具。**`total` 小只是必要条件，簇内同主题才是充分条件**（`physguard` 已复现三次）。

**新发现的次生缺陷：** `load_history(limit=PROBE_HIST_CAP=200)` 只取最近 200 条，而 `memory/github-candidates.md` 已 335 行 / 321 个仓 → 老仓在窗口内反复当种子，更老的永远不出现。

### 39. star 第七次失效 + 爆完即停首次跌出区间

幸存 49 里 **★0 有 41 个**、★≥5 仅 4 个，最高 ★25（`UCSC-VLAA/ALPS`，30d=1，星与提交完全反向）。报告级 10 里 9 个是 ★0–2。

**爆完即停 4/10 = 40%**，首次跌出稳定四轮的 55–60%。**别当趋势读**：分母从 32 掉到 10，小样本不稳，需连续两轮同窗口才能下判断。

### 40. 两条待观察形态（各有 1 个样本，不写规则）

- **大厂组织号首次进报告级**：`alibaba-damo-academy/RynnUnify`（★15、7/7）。前十四轮报告级全是个人 / 实验室个人号。盯下一轮是否复现。
- **「无 language + 根目录全是 .yaml/.md」的评测集仓**：`humanai2026/3D_Affordance`（129KB、`language=null`、根目录 13 个 `SWM_*.yaml` / `.md`、无 `src`/`package.json`/`pyproject.toml`）。**按第十二轮「无代码骨架 → 页」它该丢，但它不是页，是提示词/评测集仓** —— 与 `scaffold` 相邻但不同类。1/49 的样本量不够定判据。

## 第十四轮（2026-10-26，60 天窗，probe，dry-run）—— 「60 天更全」是反的：`MAXPAGE` 撞顶取代 `PER_TERM_CAP` 成为新的静默丢失源

本轮 `var=dry-run days:60 probe`，窗口 `2026-08-27..2026-10-26`（首次 60 天）。原始 **3474** → 幸存 **4** → 报告级 **1**。核验全量 4/4，耗时 345s。

### 33. 🔴 幸存 4 不是词表饱和，是 `sort=stars` 在子窗内撞 `MAXPAGE=3` 的顶 —— 静默丢失

`scan.py` 把窗口切成 3 个子窗，每子窗最多 `MAXPAGE=3` 页 × 100 = **300 个**，且 `sort=stars`。`world model` 单子窗实测 total_count：`2026-10-06..10-26` **509** / `2026-09-16..10-06` **497** / `2026-08-27..09-16` **416**。**三个子窗全部超过 300。**

复现取第三子窗前 3 页（star 排序 300 个）核实：**`SunCCNY/Embodied-AI`（30d=54、★0、Python、desc 明写 "world modeling in Applied and Embodied AI"）与 `colorHur/world-model-lab`（30d≥100 / 7d=99）都不在这 300 个里，也都不在 `seen` 里。** 它们既没被任何过滤器判掉，也没被 seen 吸收 —— 是搜索取样的静默丢失。

**这是第九轮 `PER_TERM_CAP=25` 造成 3.85× 低估的同型缺陷第二次出现，载体换了：cap 从「每词 25 个」变成「每子窗 300 个」，代价一样。**

### 34. 🔴 窗口越长撞顶越狠 —— 在当前代码里「60 天窗更全」是反的

| 窗口 | `world model` 单子窗 total | 是否撞 300 | 幸存 |
|---|---|---|---|
| 30 天（第十二轮） | ~250 | 否 | 65 |
| 60 天（本轮） | 416–509 | **是** | **4** |

**幸存 65 → 4 不是窗口变长该有的结果，是覆盖率从 ~95% 掉到 66.5% 的结果。** 逐词算：`world model` = 900/1354 = **66.5%（唯一撞顶）**，其余 17 词 83–109%（取尽）。

**判据：`MAXPAGE` 撞顶和 `PER_TERM_CAP` 是同一类错，必须同样对待。** 修法二选一：① `world model` 这类大词按 `sort=updated` 分页取尽（第十三轮已证 `sort=updated` 的 100 个里 76 个不在 seen）；② 子窗按 total_count 动态加页（`ceil(total/100)`，上限设 20 页）。**在修之前，60 天窗不可再用 —— 它比 30 天窗覆盖率更低。**

### 35. 🔴 覆盖率口径要改：撞顶的 66.5% 和「<50% 不可引用」同等不可信

SKILL.md 铁律写「覆盖率必须报，<50% 的绝对数不可引用」。本轮 `world model` 覆盖率 **66.5%**，而报告级 1 个里 0 个来自这一支 —— 但它占了原始量的 26%（900/3474）。**覆盖率不能只报百分比，必须同时报「是否撞顶」**：`raw == 900` 就是撞顶的确定性标志（3 子窗 × 3 页 × 100）。撞顶的覆盖率是**采样后验**，不是真实覆盖率。

### 36. 🔴 「窗口外新增」区间 31 个活仓，26 个（84%）死在 carrier

取 `2026-08-27..2026-09-26`（60 天窗独有、30 天窗看不见）的 `world model` 仓，逐仓核 commits，**31 个 30d≥5**。按 scan 真实顺序复算它们死在哪：

| 死因 | 数量 |
|---|---|
| carrier | **21** |
| short_desc + carrier | 4 |
| excl + carrier | 1 |
| 幸存 | 5（4 个已在 seen，真新增只有 `SunCCNY/Embodied-AI`，且它被 MAXPAGE 切掉） |

按 7d 排前列的全是 ★0–4 真代码仓：`Illuminfti/kizuki`（100/100 ★4，CLI+MCP 本地生活库）· `ilakkmanoharan/rsna-knee-mri-classifier`（100/99）· `colorHur/world-model-lab`（100/99）· `AsProgDojo/LeWorldModel-Reimplementation`（61/61）· `canvascloudai/cwm-bench`（88/30）· `TencentARC/WorldCrafter`（55/15，★538，arXiv 2026 官方实现）。

**carrier 要求 desc 里出现机器人词，而这些仓写的是「world-model rollout / ARC training gym / 分子结构预测」—— 机制正确、措辞不带 carrier。** 第十三轮判据 21（carrier 改为「desc 或 topics 任一命中」）若落地，本轮至少救回 26 个。**这是「已写出的判据不进代码 = 每轮持续损失」的第二次可量化证据（第一次是 pages 根规则，值 7.1%）。**

### 37. 🟡 probe 种子池修法生效，但 token 泛化缺陷未修；`total` 小也不等于专名

种子 36（报告级 1 / 幸存 3 / **丢弃堆 32**）—— 幸存 0 时 probe 照样能跑，第十三轮的修法确实进了代码。20 个反查 token 里**只有 `eumenes` 是真簇**：

| token | total | 实况 |
|---|---|---|
| `eumenes` | 6 | ✅ 真簇，但**同一 owner 5 仓**（见下） |
| `Mirage` | 571 | ❌ 通用词/产品名 |
| `eidolon` | 98 | ❌ 多义 |
| `greentrace` | 12 | ❌ 碳核算课程作业扎堆（6 个 owner 各做一个） |
| `lpds` | 37 | ❌ 与 LPD 工单号、印尼语缩写撞名 |
| `physguard` | 3 | ❌ **3 个互不相干的东西** |

**`physguard` 是最有说服力的反例：`total=3` 看着像小专名，实际是三个不同主题** —— `itz-smarann/physguard-by-quadcore` 是 EV 充电桩物理防火墙（无 language）、`Arkz-Deepak/physguard` 无 desc、`Data-Driven-Computational-Geotechnics/PhysGuard` 才是 NeurIPS 2026 的 PDE 代理论文。**判据：`total` 小只是必要条件，簇内同主题才是充分条件 —— 需要看 desc 相似度，不是 owner 数。**

### 38. 🟡 `eumenes` 是「一人五仓」，不是生态热点 —— probe 簇必须先看 owner 集中度

`ugnoguchigxp` 一个 owner 在 19 天内建了 `eumenes`（★1，172MB TypeScript，根目录有 `AGENTS.md` + `.claude`）、`eumenes_world_model`、`eumenes_memory`、`eumenes_pursuit`（65/65）、`eumenes_agency`（51/51）；另有 `WorldOfEpoch/epoch-connectors`（desc 自称 "Muse Eumenes"）。

**这是第六轮判据 11「单人 + agent」指纹的极端形态：一个人用 agent 铺开 5 个仓。** 按 commits 看很热（65/65、51/51），按生态看是 1 —— **probe 报簇时必须同时给 `owner 数` 和 `repo 数`，单 owner 多仓不构成趋势。** 现有 `owners` 字段能算出来（`eumenes` 那轮 owners=2），但报告层没把它当判据用。

### 39. 🟢 脚本自清 + probe 种子池两项修复的独立验证通过

- **自清**：开跑删掉前十三轮积压 **150 个**一次性脚本，`output/ghradar/` 现在只剩 5 个固定产物。审计行 `🧹 清理 …` 正常打印。**这一条从「模型记得删」变成「代码强制」，第十三轮的建议落地生效。**
- **probe 种子池三级补足**：`probe_stat` 显示 报告级 1 / 幸存 3 / **丢弃堆 32** —— 在幸存仅 4 的情况下 probe 仍然跑满了 36 个种子。**第十三轮判据④（幸存 0 时 probe 静默空转）已修。**

### 40. ⚠️ `409` 触发全局认证降级 —— 第五轮复现，代码仍未修

stderr 打出 `! gh api 放弃: gh: Git Repository is empty. (HTTP 409)`，随后整轮审计写「gh 认证曾掉线 —— 核验完整性存疑」。**但本轮核验只 4 个仓，且耗时 1s，实际影响可忽略；问题是这个告警每轮都出现，会让「完整性存疑」变成背景噪音。** MEMORY 里「单个 409 不能触发降级」这条从第四轮记到第十四轮，`gh_get` 的降级判断仍未加 409 分支。

### 41. 🟡 `maximal extractable value` 第四次读作稀词 —— 稳定在「真稀不废」

跨窗：7d=**0** / 30d=**0** / 60d=**2** / 全期 **48**。与第十三轮、第十轮同。**别删。**


## 第十二轮（2026-10-26，30 天窗，probe，首次非 dry-run）—— pages 根规则终进代码；probe 的 token 泛化是设计缺陷

本轮 `var=days:30 probe`，与第十一轮完全同窗口同参数，唯一差别是非 dry-run。原始 2,236 → 幸存 **65** → 报告级 **32**，核验全量 65/65，耗时 284s。

### 28. 🟢 重叠 65 / 新增 0 / 掉出 5 —— 差集被 pages 根规则一条吃干净

与第十一轮快照求差：**新增 0**（同窗口 + seen 已含第十一轮 dry-run 的 70，这是预期结果，不是「没信号」）。掉出的 5 个：

`BasisResearch/empiric` · `KAI030113/safedojo` · `fffstrong/Grounded-Dreamer` · `qingh097/lacwm-project` · `syaok1/wm-outcome-pilot`

**五个全是第十轮人工发现、第十一轮第二次复现的纯静态站**（`index.html` + `.nojekyll` + 无代码骨架）。**判据从「人工记录」变成「代码执行」的这一刻，正好可以量它值多少：5/70 = 7.1% 的报告级被一个可知的规则污染了三轮。** 这是本项目里「已写出的判据不进代码 = 每轮持续损失」的第一次可量化证据。

### 29. 🔴 probe 的 token 选取只过 STOPWORDS，不要求「是专名」—— 7 个 token 里 5 个是纯噪声

probe 从报告级 top-10 的仓库名切 token，唯一过滤是 `len>=4` + `STOPWORDS` + 非数字。本轮回查 7 个：

| token | total | owners | 未在幸存者 | 真簇？ |
|---|---|---|---|---|
| `supermimic` | 55 | 55 | **53** | ✅ 真簇 |
| `jepa` | 372 | 94 | 100 | ✅ 真簇 |
| `capstone` | 11,036 | 97 | 100 | ❌ 课程作业词 |
| `motion` | 11,009 | 93 | 100 | ❌ 通用词 |
| `circuit` | 4,983 | 69 | 100 | ❌ 通用词（含红石/电路板） |
| `recall` | 3,291 | 94 | 100 | ❌ 通用词 |
| `pera` | 679 | 95 | 99 | ❌ 人名/钱包名 |

**判据：探「词表外的新专名」时，`owners>=3` 完全不构成证据 —— 一个通用词天然有几千个 owner。** 有效的过滤轴是**词表的反面**：token 必须无法用日常词义解释。可自动化的近似：`total` 要小（专名在 60 天窗口内通常 <300），或 token 不含通用学科/课程词。**本轮 5 个噪声 token 共浪费 5 次 search + 20 次 commits 调用，占 probe 预算 70%。**

### 30. 🔴 409 空仓仍会触发全局认证降级 —— 第四轮复现，代码未修

脚本 stderr 打出 `! gh api 放弃: gh: Git Repository is empty. (HTTP 409)`，随后整轮降级到未认证 urllib，审计写「gh 认证已丢失，完整性存疑」。

用 `gh api` 对 32 个报告级逐仓重放：**30/32 的 30d 与 7d 逐字相同**，2 个 7d 差 1–7 笔（`Hchnr/s2a` 8→9、`Kushaan-N/SyncSim` 18→25）—— 是重放时间晚于首跑的时间差，不是降级造成的错误。**结论：本轮数据可用，但「完整性存疑」这个告警是假警报，根因仍是 MEMORY 里那条「单个 409 不能触发降级」没落地。**

### 31. ⚠️ 报告级的两处根目录形态漏洞（第三条判据）

| 仓库 | size | language | 根目录 | 应判 |
|---|---|---|---|---|
| `kevinc-lab/Structured-Latent-Dynamics` | 32,659 KB | HTML | `.gitignore` / `assets` / `index.html` | 项目页 |
| `huangkiki/huangkiki` | 1,427 KB | None | `README.md` / `assets` | 个人主页 |

两者都不带页后缀、也不是同名仓（短名 ≠ owner），所以现有两条规则全部漏网。**待加：`index.html` 存在且根目录无代码骨架 → 页（不要求 `.nojekyll`）。** 注意 `kevinc-lab` 的 desc 明写「Project page for …」，description 也可作为弱判据。

### 32. 🟡 `REPORT_COMMITS=5` 在同一支上已区分不出「在写代码」与「做作业」

`world model` 一支占报告级 25/32 = 78%。其中持续以 5–100 提交进报告级的是学习/作业仓：`PreshenNaidoo/applied-pytorch-bootcamp`（≥100/0）、`Katherine624/Paper_Reproduction`（18/0）、`ideal-sisyphus/embodied-ai-learning`（8/1）、`silvermew/hand-to-robot-cube`（5/0）。**爆完即停 19/32 = 59.4%，四轮稳定在 55–60%（55.2 / 57.1 / 59.7 / 59.4）。** 这个常数说明「30d 有量」本身不是信号；门槛该加的第二维是「7d 仍在动」，而不是提高 30d 阈值。

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

## 第十八—二十二轮（2026-10-27，90d → 7d）—— 窗口是流量旋钮的算术证据；SITE_SUFFIX 补 `-web`

10-27 一天跑了五轮：第十八轮 90d dry-run（5403/662/64）、第十九轮 7d probe 非 dry-run（455/34/10，首次写 seen）、第二十轮 90d 非 dry-run（5404/629/54）、第二十一/二十二轮 7d dry-run 冒烟（459/4/1、461/6/1）。

### 43. 🟢 「窗口是流量旋钮，不是语义轴」第二次拿到算术证据

第十八轮 90d dry-run 报告级 **64**；第十九轮 7d 写进 `seen` 的恰好 **34 个幸存者 / 10 个报告级**；第二十轮同口径 90d 正式跑 → 幸存 **−33**、报告级 **−10**，且第十九轮那 10 个（`Xeon87` · `maclong01/AGE` · `harshvtomar/robomotion-ai` · `brain-labbb/RFW_A_web` · `AbdelStark/verifiable-inference-ethereum` · `Kostov0129` · `alibaba-damo-academy/RynnUnify` · `SoroushK93` · `DU525` · `skywhite1024/paper-git`）**全部消失**。

**差值完全由 `seen` 吸收解释，不是扫描回归。** 第一次证据是第十六轮同窗口复跑。**推论：90d 跟在 7d 之后跑，增量基本被吃干 —— 日跑回 7 天窗，90d 只用于加词/补历史。**

### 44. 🔴 `scan.py` 尾部崩溃 ≠ 本轮没产出 —— 脚本、产物、stdout 三者会互相撒谎

第十八轮 `scan.py:910` / `:921` 把 `c.get("commits_7d", "-")` 写成 `c["commits_7d", "-"]`（元组当 key 下标）。**扫描、核验、写 `out.dry.json` / `dropped.json` / `audit.log` 全部跑完之后**才在「落盘 / 通知」段抛 `KeyError`，于是 `report.md` 与 `github-candidates.md` 用的是上一轮的陈旧内容，而 stdout 看起来像「跑挂了」—— 那轮实际已算出 662/64。**判据：脚本尾部崩溃先看 `out.*.json` 的 mtime 再判，不要凭 stdout 重跑。** 已开 PR #14（已 MERGED）。

### 45. ✅ SITE_SUFFIX 缺口已修，且没观察到过杀

第十九轮发现 `brain-labbb/RFW_A_web`（desc 明写 "RFW-A project website"）因 `_web` 不在 `-page/-site/-website/-homepage/-showcase/-docs` 名单里被放行。第二十轮补上 `-web`/`_web`，命中 1 个 `Kr1sJFU/Enuma-web` 无条件丢，**过杀 0**（仅 1 例，样本不足）。

### 46. 🟢 dry-run 不再覆盖 `report.md`；真零改为跨窗判定

第二十二轮验证：`report.md` / `seen` / 戳 / `out.json` / `clusters.json` 的 md5 与跑前一致，stdout 打出 `report.md: 跳过（dry-run 不覆盖）`。真零行改为「单窗为零不删，跨 7/30/60 都是 0 才谈删词」—— 直接兑现第十轮判据 18。

### 47. 🟡 `supermimic` 簇维持判假：多 owner 单仓同样不构成趋势

probe 反查（首次非 dry-run）：种子 67 → 候选 token 96 → 反查 28 · 热仓核验 202。唯一真簇 `teleop`（total=550 / owners=98 / 未在幸存者 100 / 主题词 `teleoperation`×20），**但 `teleoperation` 已在词表且 raw=45，收益只是缩写书写形态 → 建议作 carrier 别名，不单开词条。** `supermimic` 61 仓 / 61 owner 与第十六轮 55 仓簇同规模，**一 owner 一仓判撞名**（「单 owner 多仓不构成趋势」的镜面对称）。

### 48. ⚠️ 判据缺口：无 language 字段 ≠ 非代码仓，需 `gh api contents` 才能归因

第十九轮 `Xeon87/Agentic_Robot_Sim2Real_Experiment_Platform` 22 commits 全在近 7 天但无 language，**疑似论文配套实验仓，预算内未补调用核实**。同轮 `paper-git` 形态再次印证「30d=39 但 7d=3」——30 天提交高 ≠ 现在在写。

## 第二十三轮（2026-10-28，7 天窗，非 dry-run）—— star 第 12 次失效；「本周新建 + 当周爆完」成为报告级主体

本轮 `var=days:7`，18 词，`gh-v3`，核验 21/21 = 100%。原始 **460** → 幸存 **21** → 报告级 **8**。丢弃 seen=189 · excl=33 · short_desc=80 · carrier=103 · neg=13 · pages=18 · pages_root=0 · farm=3 · fail=0。

### 49. 🔴 star 第 12 次失效，且这次失效的形态变了：报告级 8 个 ★全 0，除 `marionette` 外 **30d == 7d**

八个报告级仓的 `commits_30d` 与 `commits_7d` 逐项相等（`marionette` ≥100/≥100、`aura3d` 54/54、`operator-layer-ros2` 16/16、`AegisAgent` 12/12、`jepa-game-agent` 10/10、`TheLiaoGroup/WorldModel` 9/9、`roverlink-ros2` 6/6、`YHFone/supermimic-mjlab` 5/5）。**30d==7d 的意思是「所有提交都落在最近 7 天」—— 这是本周新建仓、当周爆完，不是老仓回温。** 以往 star 失效表现为「高 star 仓其实很旧」，本轮表现为「报告级整体是新建仓」，判据不同：**看到 30d==7d 就该问「这个仓存在多久」，而不是「它有多活跃」。**

### 50. 🔴 `data availability` 连续两轮 raw=16 / seen=0 —— **结论已于第二十四轮推翻，见 #53**

第 8 轮与第 9 轮（相隔一天）该词原始命中都是 **16**，幸存 0，`seen` 命中 0。当时判为「过滤损耗」。**10-29 第 10 轮换 30 天窗后 raw 立刻变 57 / seen=1 —— 真因是窗口把 57 压成 16，不是任何丢弃规则。** 原文保留以存档误判：当时「raw 逐字相同 + seen 命中 0 → 被某条规则整批吃掉」的推理链本身没错，错在**没有先问「这个 16 是不是窗口的函数」**。

### 51. 🟡 7 天窗不足以判词死活，且状态会在相邻两轮之间来回翻

`robotics data engine` 上一轮是「全已见饱和 1/1」，本轮跌回**真零**；`proof of useful work` 连续两轮真零。**同一个词在两轮之间从「饱和」翻成「真零」，说明 7 天窗的读数本身就在噪声区间内** —— 判词死活必须走 30/60 天窗量 `total_count`，7 天窗只报当日四分类，不写死活结论。

### 52. 🟢 carrier 误杀对照首次两侧都满格：46/46 与 18/18，仍无差异

丢弃侧仓名自带词表词 46 个、近 7 天存活 **46/46 = 100%**；放行侧幸存者 **18/18 = 100%**。**两侧都顶到 100% 时这个对照失去分辨力**（分母太小、且 7 天窗下几乎所有仓都活着）—— 结论只能是「本轮未观察到误杀」，不能反推 carrier 规则安全。前几轮 54%/45%、56%/57% 才是有效读数。


## 第二十四轮（2026-10-29，**30 天窗**，非 dry-run）—— 口径偏差：7 天窗从未在调度链路生效

本轮 `var=''`，但 **digest 自报窗口 30 天**。查证：`skills/github-radar/SKILL.md:7` 写 `var: "days:7"`、正文写「默认 7」，而 `scan.py:184` 的 `DAYS` 默认值是 **30**（`scan.py:193` 只有显式传 `days:N` 才覆盖）。**frontmatter 的 `var` 不注入运行环境，所以第 9 轮报的「7 天窗」是手动传 `days:7` 的结果，不是默认行为 —— 「日跑回 7 天窗」这条 MEMORY 结论在调度链路上从未成立。** 本轮数字与第 9 轮**不可直接相减**。

漏斗：原始 **2106** → 幸存 **35** → 报告级 **16**。丢弃 seen=979 · excl=138 · archived=1 · short_desc=389 · carrier=434 · neg=56 · pages=57 · pages_root=4 · scaffold=0 · farm=13 · fail=0。18 词 × 二分（单窗 13 / 需拆窗 5 · 二分 4 次 · 搜索调用 45）· 核验 35/35 = 100% · 141s。

### 53. 🔴 `data availability` 悬案结案：**「两轮数字一字未变」本身就是窗口假象的指纹**

30 天窗下该词 raw=**57** / seen=1；7 天窗下（第 8/9 轮）raw=**16** / seen=0。同一批仓在 7 天窗里反复被查出来又被同一条规则丢掉，读数看起来像「完全没变」。**判据：相邻两轮同一词的 raw 逐字相同，先怀疑窗口把分布截断了，而不是先怀疑某条规则。** 数学上，7 天窗对 `total_count` 是个截断函数 —— 上游总量远大于窗口内命中时，窗口内数字会一直顶在同一个饱和值上。

### 54. 🔴 carrier 误杀对照**跨窗口比必得假信号**：本轮丢弃侧 36% vs 放行侧 97%，不是 carrier 回归

丢弃侧仓名自带词表词 **53/148 = 36%**（近 7 天存活），放行侧 **34/35 = 97%** —— 看着像 carrier 在杀活仓。但**第 9 轮 7 天窗下两侧都是 100%**：7 天窗里「近 7 天存活」对几乎所有仓都恒为真，对照没有分辨力；30 天窗把三周前的老仓带进丢弃侧，天然存活率就低。**纪律：这个对照只能在同窗口内比。跨窗口比较得到的是窗口效应，不是规则效应。** 本轮不下结论、不改 carrier。

### 55. 🟢 「窗口太短制造假零」第 N 次复现，且两条通道开始交集

`proof of useful work` 上两轮 7 天窗连续读**真零**，本轮 30 天窗首次产出新收 2（`hetu-project/pearl-pouw-analysis` 等）。该词与 `defillama-radar` 词表里的 `Pearl Blockchain` 同源 —— **发现层两条通道（代码 / 部署）首次出现同一方向上的交集**，值得后续跟踪是否构成确认信号。

### 56. 🔴 大厂组织号第二次进报告级，且是同一个 org；star 第 13 次失效

`alibaba-damo-academy/RynnWorld-Latent`（★11，30d=16 / 7d=3）与第 9 轮的 `alibaba-damo-academy/RynnUnify`（★15，7/7）同属一个组织号。第十五轮记的「大厂组织号进报告级」从单样本升到 2 个。**报告级 16 个里 15 个 ★0** —— star 排序第 13 次失效。

另：**16 个全部 7d>0**，与第 9 轮「除 1 个外 30d==7d」形态相反。30 天窗把「还在写」的老仓捞回一部分，与第十二轮判据（窗口是提前量/覆盖率取舍轴，不是质量轴）一致 —— **第 9 轮 `30d==7d` 的「本周新建当周爆完」是 7 天窗产物，不是 10 月末的普遍形态。**

形态告警：无 language 7 个（`Motphys/.github` 是 `.github` 仓，本身不是代码仓）· 爆完即停仅 1 个（`UTSA-VIRLab/EgoBalanceFormer`）· pages 根规则丢 4 个 · NEG 丢 56 个（全是印尼语 `jepang` 撞词，规则生效）· `maximal extractable value` 30d=0，与 topic 记录的 7d=0/30d=0/60d=2 一致，按铁律不删。

probe 跳过（戳 1 天 < 7 天），`clusters.json` 仍是上次结果。通知已发（报告级 16 > 0，队列 `1793226830-5084-8292.json`）。本轮无改词、无改脚本。

## 第二十七轮（2026-10-31，**30 天窗**，非 dry-run）—— carrier 误杀第四次复现；报告级首次「9/10 机器人侧」

`scan.py ""` → **第 13 轮「日跑 7 天」仍未生效**（`var` 未注入，`scan.py:184` 吃 30d；第 10/11/12 轮同根因，见 [ops-plumbing](/topics/ops-plumbing.md)）。

漏斗：原始 **2049** → 幸存 **34** → 报告级 **10**。丢弃 seen=962 · excl=134 · short_desc=365 · **carrier=426** · neg=58 · pages=57 · farm=13 · fail=0 · archived=0。18 词 × 二分至一页（单窗 13 / 需拆窗 5 · 二分 2 次 · 搜索 41）· 核验 **34/34 = 100%**（全量，无采样偏差）· 黑名单 3 owner。

### 63. 🔴 carrier 误杀对照**第四次同窗口反向** —— 34% vs 97%，判据已无争议

丢弃侧仓名自带词表词 **161 仓 / 159 owner**，核 148，近 7 天存活 **50/148 = 34%**；放行幸存者核 33，存活 **32/33 = 97%**。四轮序列：**36/97 → 35/96 → 36/96 → 34/97**，全部落在 34–36% vs 96–97%。**放宽 carrier 已具备动手条件；本轮仍未改脚本。**

### 64. 🔴 报告级 10 个**全 ★0**（唯一例外 cair-vinuni/roboworm ★3），9/10 落机器人/具身侧

`manipulation` / `teleoperation` / `egocentric` / `JEPA` 四类占满，`world model` 仍是唯一跨加密侧的机制词。与 MEMORY 既有判断「真实产出在 AI/机器人侧，加密侧顺带」同向。**推论（本轮新增）：star 若参与采样排序，会切掉整批（本轮报告级 9 个 ★0）** —— 不是「★0 的质量差」，而是「★0 才是常态、★高是残留」。

### 65. 词表四分类分开写：查询失败 0 · 真零 0 · 饱和 8 · 有新增 10

饱和且真被 seen 吸收 7（**别删**）：embodied data(9/4) · robot dataset(24/21) · robotics data engine(1/1) · proof of useful work(9/9) · data availability(54/1) · restaking(4/3) · intent-based(53/2)。非饱和 1：`maximal extractable value`（raw=1 / seen=0，全是过滤损耗，**不算饱和**）。**`data availability` 与 `intent-based` 第三轮维持 `seen/raw < 5%`**，与第 11/12 轮同形 → 固定丢弃规则在长期封锁，仍未定位到具体规则。

返回/新收/已见前三：world model 762/5/180 · jepa 344/5/152 · teleoperation 229/5/160；长尾 sim2real 80/1/45 · world action model 39/1/35 · verifiable inference 7/1/5。

形态告警：爆完即停 1（gawbi/track-digital-twin）· 无 language 8（近四轮最多，偏非代码仓/论文复现：LLM4Robot-Bench、ElegantVLA、auralis-music-world-model、coloc）· 空仓 409 1。

**载噪点（只记不判）**：`haeliotang/poieweave` 30d/7d 均 ≥100（commits 打满 per_page），Rust，desc = "Autonomous Infrastructure Intelligence"，与 world model 主题可疑 —— 留下轮对照。

probe 跳过（戳 4 天 < 7 天门槛），`clusters.json` 未重写 —— 读到的仍是上次结果，不作本轮信号。



`scan.py ""` → **第 12 轮「日跑 7 天」仍未生效**（第 10/11 轮同根因，`scan.py:184` 默认 30；frontmatter 的 `var:` 不注入运行环境）。

漏斗：原始 **2048** → 幸存 **28** → 报告级 **6**（**全 ★0**，star 第 15 次失效）。丢弃 seen=957 · excl=133 · archived=1 · short_desc=371 · **carrier=425** · neg=59 · pages=59 · pages_root=2 · scaffold=0 · farm=13 · fail=0。18 词 × 二分至一页（单窗 14 / 需拆窗 4 · 二分 3 次 · 搜索 41）· 核验 **28/28 = 100%** · 134s。

### 60. 🔴🔴 carrier 误杀对照**第三次同窗口反向** —— 由「可复现判据」升为「结论」，已具备动手条件

丢弃侧仓名自带词表词存活率 **36%（53/149）** vs 放行侧 **96%（27/28）**。三轮：**36/97 → 35/96 → 36/96**，重合在 **1 个百分点**内。同一 30 天窗、同参数、三重复现 → **carrier 表偏严不再是假设**。放宽已具备动手条件；本轮仍未改表（铁律：先看两行、不盲改）。

### 61. 🔴 第 11 轮新判据（`seen < raw 5%` 不许记饱和）在**同一对词上原样二次复现**

`data availability` raw=**56** / seen=**1** / 新收 **0**；`intent-based` raw=**54** / seen=**3** / 新收 **0** —— 与第 11 轮（56/1、55/3）**逐值相同**。**同词对数两轮完全一致 = 固定丢弃规则在长期封锁，非偶发**，需归因到 carrier / short_desc / neg 之一。

### 62. `maximal extractable value` 真零连续两轮结束，但属「全是过滤损耗」而非饱和

raw=**1**（前两轮 30d total=0），但该仓 seen=0、新收=0 → digest 单列「全是过滤损耗」。**词未死，不删**（按铁律单窗为零不删，何况本轮已有 raw）。

逐词 raw 与第 11 轮同量级（world model 762 vs 770 · jepa 348 vs 348 · teleoperation 223 vs 226 · robot manipulation 153 vs 157）→ **幸存 29→28 是 `seen` 算术，不是流量变化。**

饱和 7 词：embodied data(8/4) · robotics data engine(1/1) · verifiable inference(6/5) · data availability(56/1) · restaking(4/3) · intent-based(54/3) + `maximal extractable value`（属过滤损耗）。被 seen 真吸收 6 个。

形态告警：**无 language 6**（sanjiaonailao/robot-agent-lab · kanyinorukotan/robot-video-annotation · nikith-roboticsanalysis/Global-Robotics-Market-Intelligence · cervanteslee/GII-Restaurant-Physical-AI · kkt94/self-calibrating-vla · player0718/EgoActionBench —— **近三轮最多**）· 爆完即停 1（K3YB04RD-w4rri0r/egocentric-to-robot）· farm 13 · NEG 59（印尼语 `jepang` 撞词，规则生效）。

报告级 6 全 ★0：AlphaChad5000/vibehash(30d=17/7d=17) · Celveen/SE-JEPA(25/13) · Mithilesh1103git/RoboPilot-Sim2Real(19/13) · DNH35/jepa-world-model-from-scratch(7/7) · LabBuddy26/Labference(7/4) · XBR-1111/tailor(6/6)。**其中 3 个落在 JEPA / sim2real 两个机制词上**，与 `arxiv-radar` 同日第 31 轮的机器人侧聚集同向（只记现象，不做判断）。

probe 跳过（戳 3 天 < 7 天门槛），`clusters.json` 未重写，读到的仍是上轮结果 —— **不作本轮信号**。

## 第二十五轮（2026-10-29，**30 天窗**，非 dry-run）—— `var` 默认值仍未生效；carrier 偏严从「猜测」升为「可复现判据」

`scan.py ""` → var 为空，**继续吃 `scan.py:184` 的 30 天默认**（第 10 轮同一根因，见 [ops-plumbing](/topics/ops-plumbing.md)）。digest 自报「窗口 30 天」与 SKILL 正文「默认 7」仍互相矛盾，属代码改动待 PR。

漏斗：原始 **2075** → 幸存 **29** → 报告级 **6**（**全 ★0**，star 第 14 次失效）。丢弃 seen=975 · excl=137 · archived=1 · short_desc=382 · carrier=423 · neg=56 · pages=59 · pages_root=0 · scaffold=0 · farm=13 · fail=0。18 词 × 二分至一页（单窗 13 / 需拆窗 5 · 二分 4 次 · 搜索 45）· 核验 29/29 = 100% · 137s。

### 57. 🔴 carrier 误杀对照在同窗口内复现反向差 —— 第 10 轮的「窗口效应」解释被排除

丢弃侧仓名自带词表词存活率 **35%（52/148）** vs 放行侧 **96%（27/28）**；第 10 轮是 **36%（53/148）vs 97%（34/35）**。**两轮同为 30 天窗、参数相同，数字几乎重合** —— 第 10 轮曾用「跨窗口比必得假信号」把这 35% 打掉，本轮证明那个解释不适用：**这不是窗口假象，是 carrier 表偏严的真信号。** 本轮仍不改表（铁律：改前先抽检两行、走 PR），但结论从「猜测」升级为「可复现判据」。

### 58. 🔴 第 10 轮把 `data availability` 记成「窗口压成 16」只对了一半

本轮该词 raw=**56** / seen=**1** / 新收 **0**，与第 10 轮 raw=57 同量级 —— 但 **seen 只吃到 1 个**。那 56 个仓绝大多数既不是被 seen 吃掉的（那才叫饱和），也不是窗口压的，**是被某条丢弃规则常年挡在门外**。第 10 轮只追了 35 个幸存者的来源，没追这 56 个的去向。**新判据：`有新增=0` 且 `seen 命中 < raw 的 5%` 时不许记成「饱和」，必须单独归因到具体丢弃规则。** 同类可疑项：`intent-based`（55/3）。

### 59. 🔴 幸存 35 → 29、报告级 16 → 6 是 `seen` 算术，不是流量下降

逐词 raw 与第 10 轮同量级（`world model` 770 vs 763 · `jepa` 348 vs 341 · `teleoperation` 226 vs 219）。上轮 35 个幸存者全写进 `seen`，本轮 6 个被吸收。**同窗口连跑不可作趋势读。**

逐词新收：world model +5 · teleoperation +5 · vision language action +5 · sim-to-real +4 · jepa +3 · robot manipulation +3 · egocentric +2 · world action model +1 · robot dataset +1。
饱和 8 词：embodied data(8/4) · sim2real(82/46) · robotics data engine(1/1) · verifiable inference(6/5) · proof of useful work(8/8) · data availability(56/1) · restaking(4/3) · intent-based(55/3)。
真零 1：`maximal extractable value`（30d total=0，连续第二轮；topic 记 60d=2，按铁律单窗为零不删）。

形态告警：无 language 3 个 · 空仓 409 1 个（`FVL-Repo/VLA-Pro`）· 爆完即停 1 个（`Anthony-ZC/steam_frame_teleoperation` 30d=7/7d=0）· pages 根规则 0 · farm 13 · NEG 56（印尼语 `jepang` 撞词）。
probe 跳过（2 天 < 7 天），`clusters.json` 未重写。通知已发（报告级 6 > 0，队列 `1793313222-4612-21051.json`）。本轮无改词、无改脚本、无改 EXCL。

# Citations

- 第二十九轮（11-02 第 15 轮，30d）`logs/2026-11-02#github-radar（第 15 轮）` · `output/ghradar/out.json` · `audit.log` · `dropped.json` · `skills/github-radar/scan.py:184` · `memory/github-seen.json`
- 第二十八轮（11-01 第 14 轮，30d）`logs/2026-11-01#github-radar（第 14 轮）` · `output/ghradar/out.json` · `audit.log` · `dropped.json` · `skills/github-radar/scan.py:184` · `memory/github-seen.json`
- 第二十七轮（10-31 第 13 轮，30d）`logs/2026-10-31#github-radar（第 13 轮）` · `output/ghradar/out.json` · `audit.log` · `dropped.json` · `skills/github-radar/scan.py:184` · `memory/github-seen.json`
- 第二十六轮（10-30 第 12 轮，30d）`logs/2026-10-30#github-radar（第 12 轮 · 30 天窗 · 非 dry-run）` · `output/ghradar/out.json` · `audit.log` · `dropped.json` · `skills/github-radar/scan.py:184,193` · `memory/github-seen.json`
- 第二十五轮（10-29 第 11 轮，30d）`logs/2026-10-29#github-radar（第 11 轮 · **30 天窗** · 非 dry-run）` · `output/ghradar/out.json` · `audit.log` · `dropped.json` · `skills/github-radar/scan.py:184,193` · `memory/github-seen.json`
- 第二十四轮（10-29 第 10 轮，30d）`logs/2026-10-28#github-radar（第 10 轮 · **30 天窗** · 非 dry-run）` · `skills/github-radar/scan.py:184,193` · `skills/github-radar/SKILL.md:7` · `memory/github-seen.json`
- 第二十三轮（10-28 第 9 轮）`logs/2026-10-28#github-radar（第 9 轮 · 7 天窗 · 非 dry-run）` · `report.md` · `audit.log` · `memory/github-seen.json`
- 第十八—二十二轮 `logs/2026-10-27#github-radar（第十八轮` … `#（第二十二轮`）· `scan.py:910,921`（tuple-index bug）· PR #14 · `memory/github-seen.json`（186 增补 34）· `memory/ghradar-probe-last.txt` = 2026-10-27
- 第十七轮快照 `output/ghradar/out.dry.json`（51 幸存 / 3,818 原始）· `dropped.json`（carrier 877 / short_desc 695 / carrier_named_uniq 327 / carrier_named_alive_7d 74）· `clusters.json` · `audit.log` · `scan.py:366`（`WIN_SPLIT_TOTAL`）· 手工复量 `sim2real` 两页并集 163 · `logs/2026-10-26#github-radar（第十七轮`
- 第十六轮快照 `output/ghradar/out.dry.json`（49 幸存 / 4,004 原始）· `dropped.json`（首次全量落仓名）· `scan.py:73-78`（STOPWORDS）· `scan.py:283-300`（cluster_cohesion）· `logs/2026-10-26#github-radar（第十六轮`

- 第十四轮快照 `output/ghradar/out.dry.json`（4 幸存 / 3,474 原始，窗口 `2026-08-27..2026-10-26`）· `audit.log` · `clusters.json` · `scan.py` **未改** · probe 簇 profile `/tmp/gh14_probe.py` · 跨窗词表 + 30–60 区间 `/tmp/gh14_terms.py` · 区间活仓死因复算 `/tmp/gh14_band.py` · carrier 堆 7d `/tmp/gh14_carrier7.py` · 逐词覆盖率 `/tmp/gh14_cov.py` · **MAXPAGE 撞顶复现 `/tmp/gh14_cut.py`** · `logs/2026-10-26#github-radar（第十四轮`
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

---
title: github-radar — 实现缺陷与判据
description: github-radar 七轮跑出的实现缺陷、过滤规则陷阱、以及「活跃度」判据（30d vs 7d、全量核验、缩写污染、agent 指纹）
tags: [github-radar, discovery, methodology, lessons]
resource: https://github.com/search?q=%22world+action+model%22&type=repositories
timestamp: 2026-10-25T06:45:00Z
---

# github-radar — 实现缺陷与判据

从 [lessons](/topics/lessons.md#过滤器设计) 抽出的 skill 专属条目。八轮（2026-10-25）实证。

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

### 16. ⚠️ `pages` 加 `not language` 带进反向泄露（第七轮引入）

第六轮的修法是「`short==owner` 且 `size<300KB` 且 **无 language** 才丢」，结果 `*.github.io` 里 **<300KB 但有 language** 的仓被放行（GitHub 会把静态站标成 HTML/JS/CSS），两批共 **6 个漏网**（`vladimirsk1234.github.io` 0KB HTML、`focal-vla.github.io` 0KB HTML 等）。影响小（0 个进报告级），但方向错了。**正确判据：名字像页 + 体量小，两个条件，`language` 不该做豁免。**

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

- 第八轮快照 `output/ghradar/out8.json`（178 幸存 / 2,817 原始）· `audit8.log` · 全量核验 `verify8.py`（174/178 = 97.8%）· 词表口径 `terms8.json` · 分析 `an8.py` / `deep8.py` / `tree8.py` · 加密侧复核 `cry8.py` → `cry8.json`
- 第七轮快照 `output/ghradar/out7.json`（332 新增 / 3,441 原始）· `audit7.log` · 全量核验 `full7.json`（1,251）+ `full7b.json`（332）· 污染量化 `contam7.py` · 词表饱和 `terms7.py` → `terms7.json` · 汇总 `all7.py` / `an7.py` / `final7.py`
- 第六轮快照 `output/ghradar/out6.json`（1,251 幸存 / 2,427 原始）· `audit6.log`
- 加密侧补齐核验 `output/ghradar/cry_verify6.py` · 7 天衰减 `decay6.py` / `robact6.py` · agent 指纹 `agentfile6.py` · 目录树 `tree6.py`
- WAM 全量翻页 `output/ghradar/wam6.py`（99 仓）· [world-action-models](/topics/world-action-models.md)
- 详细日志 `memory/logs/2026-10-25.md#github-radar（第八轮` · 第七轮 `#github-radar（第七轮`

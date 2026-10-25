# github-radar 第八轮 · 60 天窗

**规模**：18 词 × 3 窗 × 3 页 · 原始 **2,817** · 幸存 **178** · 全量核验 **174/178 (97.8%)** · 报告级 **56** · 其中 7 天仍在写 **21**。

本轮不是常规增量 —— 第七轮 50 分钟前刚用同一窗口把 `seen` 写满 1,583 条，所以「新增」全部来自两个从没抓过的口径：`vision language action`（138 个）与 `world model` 的第 3 页（38 个）。

## 一、词表改全称：vla 双赢，jepa 惨败

第七轮把「缩写必须换全称」列为下一次必改项，本轮执行了。结果**不对称**，这条比任何仓库都重要：

| 词 | 口径 | 60d total | 幸存 | 污染率 | 报告级 |
|---|---|---|---|---|---|
| `vla` | 缩写（第七轮） | 3,696 | — | **22.0%** | — |
| `vision language action` | 全称（本轮） | 205 | **138** | **1.4%** | **47** |
| `jepa` | 缩写（第七轮） | 654 | — | 14.5% | — |
| `joint embedding predictive` | 全称（本轮） | 35 | **1** | 0% | 1 |

**🟢 `vla` 换成全称是净胜，而且是罕见的双赢 —— 污染和漏检同时解决。**
两个口径几乎不重叠：全称口径 205 个仓里 **138 个是 `vla` 从没抓到过的**。原因是仓库名普遍写成合成词 —— `smolvla`、`InfraVLA`、`TernaVLA`、`Q-VLA-Forge`、`sentryvla`、`space-vla` —— GitHub 搜索按词切分，独立的 `vla` token 打不中它们，而它们的 description 里写的恰恰是全称。

**🔴 `jepa` 换成全称是灾难，损失 94.6%（654 → 35）。**
JEPA 是 LeCun 家族的固定缩写，仓库名一律 `jepa-*`，几乎没人把「joint embedding predictive」写进 name/description。

**判据（本轮最有价值的一条）：换词前先量两个口径的 total_count 与重叠度，不能只看污染率。** `vla` 污染 22% 但基数是 3,696；`jepa` 换成全称后污染降到 0，代价是整个赛道没了。真正的分界不是「缩写脏不脏」，而是**这个术语在生态里实际怎么被书写**：作为模型类别通名（VLA）时全称是主流写法，作为专有家族缩写（JEPA）时缩写才是主流写法。

## 二、共享脚手架簇：owner 黑名单结构上抓不到

本轮 7 天提交排名第一的 `AdrienBarrau/jepa-world-model-from-scratch`（30d=46 / **7d=30**）是个陷阱。同一个仓库名在 **8 个不同 owner** 下出现：

`AdrienBarrau` · `yassinzayed` · `amitabhswain` · `Mohan-afk` · `tanghaibao` · `vtnguyen04` · `jsaumil` · `avikds`

这些仓库的 **description 逐字相同**、**根目录逐字相同**（`README.md,docs,model.py,scaffold.py`）、**commit message 逐字相同**（`Step 38: jepa_world_model_experiment`、`Step 37: evaluate_planner`）。这是同一份教程/课程脚手架，不是 8 个研究组。

`github-farms.txt` 按 owner 匹配，对这种结构**完全失效** —— 每个 owner 都只有 1 个仓，`owner≥3` 那条启发式也命中不了。

**可审计的新判据**：同 repo 名跨 owner ≥3 **且** description 前 80 字符相同 → 判脚手架。两个条件一次搜索就能拿到，不需要额外 API。

## 三、EXCL 只查 description，不查仓库名

参考实现里 `if any(x in desc.lower() for x in EXCL)` 只看 description。名字里带禁词但 desc 不带的全漏了，本轮 4 个，其中 `ishandutta2007/Awesome-Vision-Language-Action-Models`（30d=10）**直接进了报告级**。

同类的页面形态（`index.html` + 无代码目录）另有 7 个进了报告级：`DILL-VLA/dill-vla.github.io`、`MERCYAI/MERCYAI`、`4AxiomRobotics/Axiom0-page`、`matCercola18/reasoning-as-a-distribution`、`robotic-vision-lab/sentryvla`、`yupeng-2003/yupeng-2003.github.io`、`rm-asif-amin/space-vla`。**判据：EXCL 必须同时查仓库名和 description；`*-website` / `*-page` / `*-showcase` 三种后缀同理。**

## 四、词表四分类（必须分开写）

- **查询失败：0 词。** 全程未降级、未触发未认证回退。
- **真零命中：0 词。**
- **全已见（饱和，别删）：14 词** —— `embodied data`(total=18) · `robot manipulation`(297) · `robot dataset`(41) · `teleoperation`(434) · `sim2real`(173) · `sim-to-real`(179) · `world action model`(102) · `robotics data engine`(1) · `verifiable inference`(7) · `proof of useful work`(13) · `data availability`(131) · `restaking`(6) · `intent-based`(120) · `maximal extractable value`(2)
- **有新增：4 词** —— `vision language action`(138) · `world model`(38) · `joint embedding predictive`(1) · `egocentric`(1)

**覆盖率**：仅 `world model` 64.2%（其余 17 词 100%），全部 >50%，绝对数可引用。

## 五、加密侧 = 饱和，不是空

本轮按词表口径加密侧幸存 **0** —— 但这不是「空」。按铁律，这是 seen 已吃掉全部命中。逐仓复核第七轮的 35 个加密仓（33 个可查）：

**≥5 提交/30d 19 个（57.6%）· 7 天仍在写 8 个（24.2%）**

仍在写：
- `opodark/hyperspace-agi-1.05` ★0 · 30d=100 7d=44 · proof of useful work
- **`vearl-verified-compute/vearl` ★22 · 30d=83 7d=24 · proof of useful work**（八轮连续，唯一全勤）
- `xXGuilasXx/spark-pearl-miner` ★2 · 30d=100 7d=10 · proof of useful work
- `HansDeploy/Flash-DeFi` ★0 · 30d=21 7d=10 · intent-based
- `itzebe/intent-pay` ★0 · 30d=57 7d=7 · intent-based
- `Trustlink-Labs/TSN-Protocol` ★0 · 30d=11 7d=6 · intent-based
- `subimpact/nimiq-restake-bot` ★0 · 30d=5 7d=3 · restaking
- `Liu-S-Y-02/Data-Availability-01` ★0 · 30d=5 7d=2 · data availability

## 六、机器人 / AI 侧：7 天仍活跃的报告级（排除脚手架后的真仓）

| 仓库 | ★ | 30d | 7d | 一句话 |
|---|---|---|---|---|
| `bondtesty/let-it-be-simple` | 2 | 22 | **22** | 论文官方实现：VLA 单步动作生成（openpi） |
| `matCercola18/reasoning-as-a-distribution` | 0 | 21 | 11 | VLA 生成式规划潜变量（项目页，非代码仓） |
| `GradVizor/mira-arm` | 0 | 11 | 10 | SO-ARM101 机械臂 MuJoCo 仿真平台 |
| `ladybug-tentoumushi/smolvla-libero-spatial` | 0 | 10 | 10 | SmolVLA + Flow Matching 教学实现 |
| `lukasVierling/InfraVLA` | 0 | 9 | 9 | VLA 导航接入基础设施摄像头 |
| `peacelwh/StereoLift` | 0 | 8 | 8 | pi0.5 免标定双目提升，精确操作 |
| `jiabingyang01/AWARE` | 0 | 8 | 8 | 动作熵加权 + 注意力引导的观察证据检索 |
| `lhtrongai/libero-vla-eval` | 0 | 19 | 7 | LIBERO 基准上的 VLA 评测框架 |
| `YanCORANV/Robot-World-Model-MPC` | 0 | 6 | 6 | FetchPush/FetchSlide 上的 CEM-MPC + 模型消融 |
| `kyutai-labs/reki` | **33** | 6 | 5 | 2.4B VLA 模型，仅公开数据预训练，带短期记忆 |

## 七、必须与结论同时引用的限制

- **爆完即停 76/174（43.7%）**，报告级内 **35/56（62.5%）** —— 比第七轮的 55.2% 更高。`30d 有提交`绝不等于`现在还在写`。
- **30 天零提交 59/174（33.9%）** —— 三分之一的幸存仓 star 在骗人。
- **撞 per_page 上限**：`BeefaceData/Agent-Aware-Vision-Language-Action-Model` 30d=**≥100**（是下限，不是真值）。
- **空仓 409：4 个** · **未核验：0 个** · **无 language 字段 17 个**（疑似非代码仓，已逐个列进审计）。
- **agent 指纹（`AGENTS.md`/`CLAUDE.md`/`.clinerules`）：6/56 报告级 = 10.7%** —— 低于第七轮加密侧的 56%，机器人侧仍是真工程团队为主。
- 脚手架簇剔除用的是「同名 + 同 desc 前缀」启发式，可能误杀真正同名的独立项目；本轮 56 个报告级里约 8–10 个属可疑（脚手架 3 个 + 页面 7 个，有重叠）。

## Summary

**做了什么**：按 `var=dry-run days:60` 跑第八轮 github-radar。18 个方向词 × 3 窗 × 3 页，原始 2,817 条，幸存 178 个新仓，全量核验 174 个（97.8%），报告级 56 个、其中 21 个近 7 天仍在写。`dry-run` 生效，**未写 `github-seen.json`、未写 `github-candidates.md`、未发通知**。

**核心发现**：① `vla`→全称是双赢（污染 22%→1.4%，且 138/205 是旧口径从没抓到的新仓）；② `jepa`→全称损失 94.6%，缩写才是生态写法 —— **换词前必须量两个口径的 total 与重叠，不能只看污染率**；③ 发现 `jepa-world-model-from-scratch` 跨 8 个 owner 的共享脚手架簇（同 desc、同根目录、同 commit message），**owner 黑名单结构上抓不到**，且它占了 7d 榜首；④ EXCL 只查 description 漏了 4 个名字含禁词的仓，另有 7 个页面形态进报告级；⑤ 加密侧「0 幸存」是饱和不是空，复核第七轮 33 仓仍有 8 个在写。

**文件**：`output/ghradar/out8.json` · `audit8.log` · `terms8.json` · `cry8.json`；脚本 `scan8.py` / `scan8_body.py` / `verify8.py` / `an8.py` / `deep8.py` / `tree8.py` / `cry8.py` / `regen8.py`。更新 `memory/topics/github-radar.md` 与 `memory/MEMORY.md`。

**后续动作**：① 把「同名 + 同 desc 前缀」加进 `scan.py` 的丢弃规则（否则下轮榜首还是脚手架）；② EXCL 改成同时查仓库名；③ `jepa` 保留缩写 + NEG，不要再试全称；④ 本轮 dry-run 未落 seen，若下轮正式跑，这 178 个会再出现一次。

**来源**：`api.github.com/search/repositories` · 18 词 × 3 窗 × 3 页 · `created:2026-08-26..2026-10-25` · `fork:false` · `stars:>=0` · `in:name,description`；提交数 `api.github.com/repos/{owner}/{repo}/commits?since=…&per_page=100`。快照 `output/ghradar/out8.json`。

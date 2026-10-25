
### github-radar（第八轮 · 60 天窗 · 词表改全称：vla 双赢 / jepa 惨败）

**运行参数**：`var=dry-run days:60`，MIN=0，CHK=5。18 词 × 3 窗 × **每窗 3 页**。**dry-run 生效 —— 未写 `github-seen.json`、未写 `github-candidates.md`、未发通知。** 第七轮 50 分钟前刚把同一窗口的 seen 写满 1,583 条，所以本轮「新增」必然来自两个从没抓过的口径。

**规模**：原始 **2,817** · 幸存 **178** · 全量核验 **174/178 = 97.8%**（未核验 0 / 空仓 409 四个）· 报告级 **56** · 7d 仍在写 **21（37.5%）**。

**🔴 本轮最大产出：第七轮的「缩写必须换全称」被证伪了一半。** 执行结果不对称：

| 词 | 口径 | 60d total | 幸存 | 污染 | 报告级 |
|---|---|---|---|---|---|
| `vla` | 缩写 | 3,696 | — | **22.0%** | — |
| `vision language action` | 全称 | 205 | **138** | **1.4%** | **47** |
| `jepa` | 缩写 | 654 | — | 14.5% | — |
| `joint embedding predictive` | 全称 | 35 | **1** | 0% | 1 |

- **🟢 `vla`→全称是双赢，且两口径几乎不重叠 —— 全称 205 个里 138 个是 `vla` 从没抓到的。** 仓库名普遍是合成词（`smolvla` / `InfraVLA` / `TernaVLA` / `Q-VLA-Forge` / `sentryvla`），GitHub 按词切分，独立 `vla` token 打不中；而它们的 description 写的正是全称。**污染和漏检同时解决。**
- **🔴 `jepa`→全称是灾难，损失 94.6%（654→35）。** JEPA 是固定家族缩写，仓库名一律 `jepa-*`，没人把全称写进 name/description。
- **判据（本轮最有价值）：换词前先量两个口径的 total_count 与重叠度，不能只看污染率。** 分界不是「缩写脏不脏」，而是**术语在生态里实际怎么被书写** —— 类别通名（VLA）全称是主流，专有家族缩写（JEPA）缩写是主流。

**🔴 新发现：共享脚手架簇，owner 黑名单结构上抓不到。** 本轮 7d 榜首 `AdrienBarrau/jepa-world-model-from-scratch`（30d=46 / 7d=30）是陷阱 —— 同名仓在 **8 个不同 owner** 下出现（`AdrienBarrau`/`yassinzayed`/`amitabhswain`/`Mohan-afk`/`tanghaibao`/`vtnguyen04`/`jsaumil`/`avikds`），**description 逐字相同、根目录相同（`README.md,docs,model.py,scaffold.py`）、commit message 逐字相同（`Step 38: jepa_world_model_experiment`）**。**`github-farms.txt` 按 owner 匹配，每个 owner 只有 1 仓，`owner≥3` 也命中不了 —— 结构上完全失效。** 新增可审计判据：同 repo 名跨 owner ≥3 **且** desc 前 80 字符相同 → 判脚手架（一次搜索即可，无需额外 API）。

**🔴 缺陷：EXCL 只查 description，不查仓库名。** 名字含 `awesome`/`website`/`page` 但 desc 不带的全漏，本轮 4 个，其中 `ishandutta2007/Awesome-Vision-Language-Action-Models`（30d=10）**直接进了报告级**。另有 7 个页面形态（`index.html` + 无代码目录）进报告级：`DILL-VLA/dill-vla.github.io` · `MERCYAI/MERCYAI` · `4AxiomRobotics/Axiom0-page` · `matCercola18/reasoning-as-a-distribution` · `robotic-vision-lab/sentryvla` · `yupeng-2003/yupeng-2003.github.io` · `rm-asif-amin/space-vla`。**判据：EXCL 必须同时查 `repo.split("/")[-1]` 与 description；`*-website`/`*-page`/`*-showcase` 后缀同理。**

**四分类（必须分开写）**：
- **查询失败 0 词** —— 全程未降级、未回退未认证。
- **真零命中 0 词。**
- **全已见（饱和，别删）14 词** —— `embodied data`(18) · `robot manipulation`(297) · `robot dataset`(41) · `teleoperation`(434) · `sim2real`(173) · `sim-to-real`(179) · `world action model`(102) · `robotics data engine`(1) · `verifiable inference`(7) · `proof of useful work`(13) · `data availability`(131) · `restaking`(6) · `intent-based`(120) · `maximal extractable value`(2)。
- **有新增 4 词** —— `vision language action`(138) · `world model`(38) · `joint embedding predictive`(1) · `egocentric`(1)。
- **覆盖率**：仅 `world model` 64.2%，其余 17 词 100%，全部 >50% → 绝对数可引用。

**🟢 加密侧「0 幸存」是饱和，不是空**（第四次验证）。词表口径加密侧幸存 0，但逐仓复核第七轮 33 个可查仓：**≥5 提交 19（57.6%）· 7d 仍在写 8（24.2%）** —— `opodark/hyperspace-agi-1.05` 7d=44 · **`vearl-verified-compute/vearl` 7d=24（★22，八轮连续唯一全勤）** · `xXGuilasXx/spark-pearl-miner` 7d=10 · `HansDeploy/Flash-DeFi` 7d=10 · `itzebe/intent-pay` 7d=7 · `Trustlink-Labs/TSN-Protocol` 7d=6 · `subimpact/nimiq-restake-bot` 7d=3 · `Liu-S-Y-02/Data-Availability-01` 7d=2。

**机器人/AI 侧 7d 仍活跃的报告级（脚本与页面形态已标出）**：`bondtesty/let-it-be-simple` ★2 30d=22 **7d=22**（VLA 单步动作生成，论文官方实现）· `GradVizor/mira-arm` 11/10（SO-ARM101 MuJoCo 平台）· `ladybug-tentoumushi/smolvla-libero-spatial` 10/10 · `lukasVierling/InfraVLA` 9/9 · `peacelwh/StereoLift` 8/8（pi0.5 免标定双目）· `jiabingyang01/AWARE` 8/8 · `lhtrongai/libero-vla-eval` 19/7 · `YanCORANV/Robot-World-Model-MPC` 6/6 · `kyutai-labs/reki` ★33 6/5（2.4B VLA，仅公开数据）。

**必须与结论同时引用的限制**：**爆完即停 76/174 = 43.7%，报告级内 35/56 = 62.5%**（高于第七轮 55.2%）· **30d 零提交 59/174 = 33.9%** · 撞 per_page 上限 1 个（`BeefaceData/Agent-Aware-Vision-Language-Action-Model` 30d=**≥100**，下限不是真值）· 空仓 409 四个 · 未核验 0 · 无 language 字段 17 个（疑似非代码仓，已逐个列审计）· **agent 指纹 6/56 = 10.7%**（远低于第七轮加密侧 56%，机器人侧仍是真工程团队为主）· 脚手架剔除用「同名 + 同 desc 前缀」启发式，可能误杀真正同名独立项目；56 个报告级里约 8–10 个可疑（脚手架 3 + 页面 7，有重叠）。

- [source: api.github.com/search/repositories · 18 词 × 3 窗 × 3 页 · `created:2026-08-26..2026-10-25` · `fork:false` · `stars:>=0` · `in:name,description` · 快照 `output/ghradar/out8.json`（178 幸存 / 2,817 原始）· `output/ghradar/audit8.log` · 全量核验 `verify8.py`（174/178）· 词表口径 `terms8.json` · 分析 `an8.py` / `deep8.py` / `tree8.py` · 加密侧复核 `cry8.py` → `cry8.json` · `gh api repos/{r}/commits?since=...&per_page=100`]

### github-radar — under the hood (run 8)
- 🔧 ~46 tool calls — Bash ×22, Write ×12, Edit ×8, Read ×4 · actions: ~430× gh api（54×3 搜索页 + 174×2 提交核验 + 56 目录树 + 8 词口径单查 + 33 加密复核）· **0 限速降级 · 0 查询失败 · 4 个 409 空仓全部正确分类未触发降级** · dry-run 未落盘 seen

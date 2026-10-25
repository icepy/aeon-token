# github-radar 第八轮 · 60 天窗

**规模**：18 词 × 3 窗 × 3 页 · 原始 **2,817** · 幸存 **178** · 全量核验 **174/178 (97.8%)** · 报告级 **56** · 其中 7 天仍在写 **21**。

`dry-run` 生效：**未写 `github-seen.json`（仍 1,583 条）、未写 `github-candidates.md`、未发通知。**

本轮不是常规增量 —— 第七轮 50 分钟前刚用同一窗口把 seen 写满，所以「新增」全部来自两个从没抓过的口径。

## 一、词表改全称：vla 双赢，jepa 惨败

第七轮把「缩写必须换全称」列为下一次必改项，本轮执行了。结果**不对称**，这条比任何仓库都重要：

| 词 | 口径 | 60d total | 幸存 | 污染率 | 报告级 |
|---|---|---|---|---|---|
| `vla` | 缩写（第七轮） | 3,696 | — | **22.0%** | — |
| `vision language action` | 全称（本轮） | 205 | **138** | **1.4%** | **47** |
| `jepa` | 缩写（第七轮） | 654 | — | 14.5% | — |
| `joint embedding predictive` | 全称（本轮） | 35 | **1** | 0% | 1 |

**🟢 `vla`→全称是净胜，而且是罕见的双赢 —— 污染和漏检同时解决。** 两个口径几乎不重叠：全称 205 个仓里 **138 个是 `vla` 从没抓到过的**。原因是仓库名普遍写成 `smolvla`、`InfraVLA`、`TernaVLA`、`Q-VLA-Forge`、`sentryvla` 这类**合成词**，GitHub 搜索按词切分，独立的 `vla` token 打不中它们，而它们的 description 里写的恰恰是全称。

**🔴 `jepa`→全称是灾难，损失 94.6%（654 → 35）。** JEPA 是 LeCun 家族的固定缩写，仓库名一律 `jepa-*`，几乎没人把「joint embedding predictive」写进 name/description。

**判据（本轮最有价值）：换词前先量两个口径的 total_count 与重叠度，不能只看污染率。** `vla` 污染 22% 但基数 3,696；`jepa` 换成全称后污染降到 0，代价是整个赛道没了。真正的分界不是「缩写脏不脏」，而是**这个术语在生态里实际怎么被书写**。

## 二、共享脚手架簇：owner 黑名单结构上抓不到

本轮 7 天提交排名第一的 `AdrienBarrau/jepa-world-model-from-scratch`（30d=46 / **7d=30**）是个陷阱。同一仓库名出现在 **8 个不同 owner** 下（`yassinzayed`/`amitabhswain`/`Mohan-afk`/`tanghaibao`/`vtnguyen04`/`jsaumil`/`avikds`），**description 逐字相同、根目录逐字相同**（`README.md,docs,model.py,scaffold.py`）、**commit message 逐字相同**（`Step 38: jepa_world_model_experiment`）。

`github-farms.txt` 按 owner 匹配，对这种结构**完全失效** —— 每个 owner 只有 1 个仓，`owner≥3` 也命中不了。**可审计新判据**：同 repo 名跨 owner ≥3 **且** desc 前 80 字符相同 → 判脚手架。

## 三、EXCL 只查 description，不查仓库名

本轮 4 个名字含禁词的漏网，其中 `ishandutta2007/Awesome-Vision-Language-Action-Models`（30d=10）**直接进了报告级**。另有 7 个页面形态进报告级（`DILL-VLA/dill-vla.github.io`、`MERCYAI/MERCYAI`、`4AxiomRobotics/Axiom0-page` 等）。

## 四、词表四分类

**查询失败 0** · **真零 0** · **全已见（饱和，别删）14 词** · **有新增 4 词**（`vision language action` 138 · `world model` 38 · `joint embedding predictive` 1 · `egocentric` 1）。覆盖率仅 `world model` 64.2%，其余全部 100%。

## 五、加密侧 = 饱和，不是空（第四次验证）

按词表口径幸存 0，但复核第七轮 33 个可查仓：**≥5 提交 19（57.6%）· 7d 仍在写 8（24.2%）**，`opodark/hyperspace-agi-1.05` 7d=44、**`vearl-verified-compute/vearl` 7d=24（八轮连续唯一全勤）**。

## 六、机器人/AI 侧 7d 仍活跃的真仓

`bondtesty/let-it-be-simple` 30d=22 **7d=22**（VLA 单步动作生成）· `GradVizor/mira-arm` 11/10 · `ladybug-tentoumushi/smolvla-libero-spatial` 10/10 · `lukasVierling/InfraVLA` 9/9 · `peacelwh/StereoLift` 8/8 · `jiabingyang01/AWARE` 8/8 · `kyutai-labs/reki` ★33 6/5（2.4B VLA）。

## 七、必须同时引用的限制

**爆完即停 76/174 = 43.7%，报告级内 35/56 = 62.5%**（高于第七轮 55.2%）· **30d 零提交 59/174 = 33.9%** · 1 个撞 `per_page` 上限（30d=**≥100**，是下限）· 空仓 409 四个 · 未核验 0 · 无 language 17 个 · agent 指纹 6/56 = 10.7% · 脚手架剔除是启发式，56 个报告级里约 8–10 个可疑。

---

## Summary

**做了什么**：按 `var=dry-run days:60` 跑第八轮 github-radar，18 词 × 3 窗 × 3 页，原始 2,817 条，幸存 178 个新仓，全量核验 174 个（97.8%），报告级 56 个、其中 21 个近 7 天仍在写。dry-run 已确认未落盘 seen、未写 candidates、未发通知。

**核心发现**：① `vla`→全称双赢（污染 22%→1.4%，且 138/205 是旧口径从没抓到的新仓）；② `jepa`→全称损失 94.6% —— **换词前必须量两口径 total 与重叠，不能只看污染率**；③ `jepa-world-model-from-scratch` 跨 8 owner 共享脚手架簇，**owner 黑名单结构上抓不到**，且它占了 7d 榜首；④ EXCL 只查 desc 漏 4 个、7 个页面形态进报告级；⑤ 加密「0 幸存」是饱和，复核仍有 8 个在写。

**文件**：`output/ghradar/{out8.json, audit8.log, terms8.json, cry8.json, report8.md}` + 脚本 `scan8.py`/`verify8.py`/`an8.py`/`deep8.py`/`tree8.py`/`cry8.py`/`regen8.py`；更新 `memory/topics/github-radar.md`、`memory/MEMORY.md`、`memory/logs/2026-10-25.md`。

**后续动作**：① 把「同名 + 同 desc 前缀」加进 `scan.py` 丢弃规则（否则下轮榜首还是脚手架）；② EXCL 改成同时查仓库名；③ `jepa` 保留缩写 + NEG，不要再试全称；④ 本轮 dry-run 未落 seen，下轮正式跑时这 178 个会再出现一次。

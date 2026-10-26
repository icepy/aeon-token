## github-radar 第十六轮 · 60 天窗 · probe · dry-run

**口径**：`var=dry-run days:60 probe` · 18 词 × 3 子窗 · 窗口 `2026-08-27..2026-10-26` · star 地板 0 · 核验全量 49/49（100%）· 耗时 349s（搜索 166s）· **dry-run，seen 未写，未发通知**。

**漏斗**：原始 4004 → 丢 seen 1884 / excl 244 / archived 2 / short_desc 744 / carrier 886 / neg 87 / pages 84 / pages_root 0 / scaffold 0 / farm 24 / fail 0 → 幸存 **49** → 报告级 **10**。

### 报告级 10 条（只给数据，不做判断）

| 仓库 | ★ | 30d | 7d | 命中词 |
|---|---|---|---|---|
| latent-horizon/pytorch-world | 2 | 85 | 47 | world model |
| humanai2026/3D_Affordance | 0 | 20 | 15 | world model |
| SunCCNY/Embodied-AI | 0 | 54 | 9 | world model |
| alibaba-damo-academy/RynnUnify | 15 | 7 | 7 | world model |
| DU525/paired-counterfactual-eval | 0 | 5 | 5 | world model |
| pacifai/pouw | 0 | 23 | 2 | proof of useful work |
| dialgop/eidolon | 0 | 9 | 0 | world model [爆完即停] |
| nehith23/phone-push-world-model | 1 | 7 | 0 | world model [爆完即停] |
| Elaybarnoam/action-conditioned-visual-world-model | 0 | 6 | 0 | world model [爆完即停] |
| gzee3184/senku_wm | 0 | 5 | 0 | world model [爆完即停] |

### 本轮三个判据

**① `dropped.json` 上线，第十五轮那条可审计性缺陷已兑现。** 文件现在是 `{carrier: 886 个仓名, short_desc: 744 个}` —— carrier 和 short_desc 第一次全量落名，四条丢弃规则里唯二不落名单的补齐了。

**② 第一次能量 carrier 误杀率：886 个里 190 个（21.4%）仓名自带 `world-model`，来自 177 个不同 owner。** 抽 12 个逐个查 `pushed_at`，**9/12 近 7 天有推送**（`pengqianhan/campus-world-model` ★9 TS 10-26、`acse-yl222/physics-grounded-4d-world-model-framework` ★5 Python 10-26、`colorHur/world-model-lab` ★1 Python 10-26、`KD-CHL/world-model-training` 10-20 …），3/12 停在 10-13 前。12 个样本的粗估，**不是率** —— 要按 owner 去重全量核 190 个的 7d 再和「carrier 正确拦下的」对照，才谈得上放宽。

**③ `cohesive=true` 也不充分 —— probe 判据第三次修正。** 本轮 3 个非 generic 且 cohesive 的簇**全假**：`senku`(54/40) 主题词只有 `with`×11（`with` 不在 `STOPWORDS`，连接词被当主题证据）；`uniview`(19/18) 主题词 `hikvision`×5 / `dahua`×4，是海康大华 NVR 工具；`pouw`(31/24) 主题词 `content`×10，第二名 `ddegraaf-max/Pouwvervoer` 是荷兰语「货运」。**`total` 小是必要、簇内同主题是必要、主题词还得落在我们词表语义内才充分。**

### 其余

- **同窗口 dry-run 复跑 = 原样重放**：第十五轮 4001/49/10，本轮 4004/49/10，top-10 名单完全一致。唯一的 +3 是窗口内新建仓，**一个都没进报告级，本轮数字不含新信号**。
- **第十五轮 `PhysGuard` 悬念关闭**：`Data-Driven-Computational-Geotechnics/PhysGuard` created 10-25 / pushed 10-26 / Python（活）；`ZhouChaunge/PhysGuard` created 04-30、**pushed 2026-05-05 停摆 5 个多月** —— 同名死仓，**不是提前占名**。
- **四分类**：查询失败 0 / 真零 0 / 全已见(饱和) 12 / 有新增 6。饱和全部 raw>0、新收 0，仍全是 seen 吸收，不删。有新增：`world model` 44 · `vision language action` 1 · `sim-to-real` 1 · `egocentric` 1 · `data availability` 1 · `proof of useful work` 1。
- **star 第八次失效**：幸存 49 里 ★0 有 41 个、★≥5 仅 4 个、最高 ★25（`UCSC-VLAA/ALPS`，30d=1）。
- **覆盖率**：仅 `restaking` 83.3% < 95%；`world model` 三子窗 514/497/416 仍撞顶，已按 total 动态加页。
- **加密侧继续 0 报告级**：唯一进榜的 `pacifai/pouw`（★0、30d=23、7d=2）是 vLLM 推理矩阵乘的 PoUW 验证器。

来源：`api.github.com/search/repositories` · `output/ghradar/out.dry.json` / `dropped.json` / `clusters.json` / `audit.log` · `scan.py:73-78`（STOPWORDS）· `scan.py:283-300`（cluster_cohesion）

## Summary

- 运行 `python3 skills/github-radar/scan.py "dry-run days:60 probe"`，一次跑完扫描 / 过滤 / 核验 / 写产物，dry-run 模式未发通知、未写 seen。
- 修改文件：`memory/logs/2026-10-26.md`（追加第十六轮条目 + under-the-hood）、`memory/MEMORY.md`（更新发现层三行判据）。
- `scan.py` **未改动**（dry-run 轮不改过滤器）。
- 产物：`output/ghradar/out.dry.json`（49 幸存快照）、`report.md`、`audit.log`、`dropped.json`（886 + 744 全量名单）、`clusters.json`（28 簇）。
- 下一轮待办：① 按 owner 去重全量核 190 个 carrier 丢弃仓的 7d，配对照再决定是否放宽 carrier；② `STOPWORDS` 补 `with` / `content` 一类高频虚词；③ probe 加第三判据「主题词须落在词表语义内」；④ 换窗口或等 seen 变化才能拿到新信号（同窗口 dry-run 复跑只是重放）。
- 本次未发通知（dry-run，符合技能定义）。

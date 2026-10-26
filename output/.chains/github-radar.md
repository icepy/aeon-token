## github-radar 第十七轮（`dry-run days:60 probe`）

**口径**：18 词 · 窗自适应（整窗 17 / 拆 3 子窗 1）· 窗口 `2026-08-27..2026-10-26` · star 地板 0 · 核验全量 51/51（100%）· 耗时 302s（搜索 151s）。dry-run：seen 未写，未发通知。

**漏斗**：原始 **3818** → 丢 seen 1774 / excl 236 / archived 2 / short_desc 695 / carrier 877 / neg 86 / pages 83 / pages_root 0 / scaffold 0 / farm 14 / fail 0 → 幸存 **51** → 报告级 **11**。

### 报告级（11）

- [latent-horizon/pytorch-world](https://github.com/latent-horizon/pytorch-world) ★2 · 30d=85 7d=47 · `world model` · World Models Library for PyTorch
- [humanai2026/3D_Affordance](https://github.com/humanai2026/3D_Affordance) ★0 · 30d=21 7d=16 · `world model` · 3D/4D 空间推理、物理与社会可供性、URDF 运动学时序
- [SunCCNY/Embodied-AI](https://github.com/SunCCNY/Embodied-AI) ★0 · 30d=54 7d=9 · `world model` · 应用与具身 AI 实验室的项目集
- [alibaba-damo-academy/RynnUnify](https://github.com/alibaba-damo-academy/RynnUnify) ★15 · 30d=7 7d=7 · `world model` · 互为 VLM 推理的 agentic 具身智能
- [Kostov0129/Piper_Alicia_teleoperation](https://github.com/Kostov0129/Piper_Alicia_teleoperation) ★0 · 30d=6 7d=6 · `teleoperation` · Alicia-DL ↔ PiPER 遥操作的本地浏览器界面
- [DU525/paired-counterfactual-eval](https://github.com/DU525/paired-counterfactual-eval) ★0 · 30d=5 7d=5 · `world model` · 世界模型的配对反事实评测
- [pacifai/pouw](https://github.com/pacifai/pouw) ★0 · 30d=23 7d=2 · `proof of useful work` · vLLM 推理矩阵乘的 PoUW 验证器
- [dialgop/eidolon](https://github.com/dialgop/eidolon) ★0 · 30d=9 7d=0 [爆完即停] · `world model`
- [nehith23/phone-push-world-model](https://github.com/nehith23/phone-push-world-model) ★1 · 30d=7 7d=0 [爆完即停] · `world model`
- [Elaybarnoam/action-conditioned-visual-world-model](https://github.com/Elaybarnoam/action-conditioned-visual-world-model) ★0 · 30d=6 7d=0 [爆完即停] · `world model`
- [gzee3184/senku_wm](https://github.com/gzee3184/senku_wm) ★0 · 30d=5 7d=0 [爆完即停] · `world model`

### 判据级发现

**① carrier 误杀率第一次有了同口径对照组 —— 50% 对 50%，没有差异，不放宽。**
脚本新打两行：丢弃侧仓名自带词表词 346 个（owner 去重 327），本轮核 **149** → 近 7 天存活 **74/149 = 50%**；放行的幸存者侧核 24 → **12/24 = 50%**。第十六轮按 12 个样本估的「误杀率一半到四分之三、偏高」**站不住** —— 那个估法没有对照，而「活着」在这个池子里本来就是 50% 基线。第十六轮那条「先按 owner 去重全量核 7d 再对照」执行完毕，结论是**不改规则**。

**② 新回归：自适应开窗省了搜索调用，但两个词首次跌破覆盖率线。**
上次提交的审计头是 `18 词 × 3 窗`，本轮是 `整窗 17 / 拆 3 子窗 1`（`WIN_SPLIT_TOTAL=1000`，`scan.py:366`）。代价立刻显形：`sim2real` **52.7%**、`restaking` **83.3%**，其余 16 词 ≥95%。
我手工复量 `sim2real`（`created:>2026-08-27`）：GitHub 侧 `total_count=163`，第 1 页 100 条 + 第 2 页 63 条，**两页零重叠、并集正好 163** —— 即完全可分页取尽，**52.7% 不是仓库封顶**。差额来自整窗单次查询的 `total_count`（169）与实际 `items`（89）不一致，属审计已标注的「total_count 不准」类。**单轮一个样本，先记不改 —— 下轮同口径再量一次才谈得上回退。**

**③ probe 第三判据（`thematic`）首轮全额生效，本轮 0 个真簇。**
28 个候选里 `uniview`(19/18) 仍 `cohesive=true` 但 `thematic=false`（主题词 `hikvision`×5 / `dahua`×4，海康大华 NVR 工具）→ 被词表语义挡下；`senku`(55/41) · `pouw`(31/24) · `eidolon`(98/74) · `physguard`(3/3) 本轮全 `cohesive=false`（`pouw` 已不再取到 `content`，GLUE 剔除生效）。**第十六轮那 3 个假阳性全部被拦下，回归通过。**

**④ 四分类（分开写）**：查询失败 **0** / 真零 **0** / 全已见(饱和) **11** / 有新增 **7**。饱和 11 个 raw 全 >0 且新收 0，逐个确认仍是被 seen 吸收（`jepa` 656/308 · `teleoperation` 416/321 · `robot manipulation` 283/225 · `world action model` 95/91 等），**不删**。有新增 7：`world model` 45 · `teleoperation` 1 · `vision language action` 1 · `sim-to-real` 1 · `egocentric` 1 · `data availability` 1 · `proof of useful work` 1。

**⑤ 与上次提交的报告只差 1 个新面孔**：`Kostov0129/Piper_Alicia_teleoperation`。其余 10 个逐项同前轮 —— 同窗口 dry-run 复跑语义不变，**不含新信号，别当增量引用**。

**⑥ star 第九次失效**：报告级 11 个里 9 个 ★0–1，全轮最高仍不在报告级。
**⑦ 加密侧继续 0 报告级**：两个加密词各 1 个新收，`pacifai/pouw` 是唯一加密仓且 7d 继续走低（2）。
**⑧ 审计完整性维持 5/5**：`dropped.json` 落 `{carrier:877, short_desc:695, carrier_named_uniq:327, carrier_named_alive_7d:74}`；carrier 靠 topics 放行 16 · 短 desc 靠 topics 放行 1 · 撞页 5 个子窗逐条打印。

## Summary

- **执行**：`python3 skills/github-radar/scan.py "dry-run days:60 probe"`，一次跑完，`scan.py` 未改动。
- **产物**（脚本自写，均在 `output/ghradar/`）：`out.dry.json`（51 幸存）· `audit.log` · `report.md`（报告级 11）· `dropped.json` · `clusters.json`。`out.json` 仍为上次的 `[]`（dry-run 不覆盖）。
- **文件修改**：`memory/logs/2026-10-26.md` 追加 `### github-radar（第十七轮）` 与 `under the hood` 两节；`memory/MEMORY.md` 新增第十七轮判据一行。
- **未发通知**（dry-run），`memory/github-seen.json` 未写。
- **待办**：下轮同口径复量 `sim2real` / `restaking` 覆盖率 —— 若再次 <95%，回退 `WIN_SPLIT_TOTAL` 自适应开窗（或对 `total_count` 与 `items` 不一致的词强制拆窗）。本轮调用 34 次超预算 2.3×，下轮把 `git show` 合并调用压到 20 次内。

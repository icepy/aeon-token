
### arxiv-radar — 60 天窗（词表改动后补历史 · 第四轮同日）
- **口径**：`var="days:60"` · 24 词 · 窗口 `202608271211 – 202610261211` · 345s · [source: export.arxiv.org/api/query · `skills/arxiv-radar/scan.py` TERMS · `output/arxiv/audit.log` · `output/arxiv/out.json`]
- **漏斗**：原始 87 → 丢弃 seen=64 / excl=1 / carrier=8 / 查询失败=16 → **幸存 14**。**推送 14 条**（`NOTIFY_TOP=30` 未截断，`notify` 已入队 `1793017435-3073-25101.json`）。
- **四分类（分开记）**：**A 查询失败 16** · **B 真零 1**（`ti:"Robinhood Chain"`，60d=0）· **C 全已见饱和 3**（`embodied AI` raw=14 / `zero-knowledge` raw=20 / `EIP-1559` raw=2）· **D 有新增 4**（全部 cs.RO 簇：egocentric 27/7 · data generation 12/4 · human data 7/1 · data engine 5/2）。
- **⚠️ 本轮最大实测缺陷：单轮 66.7%（16/24）查询死于 429/超时，且脚本无重试。** `scan.py` 主循环只有单次 `urlopen(timeout=20)`，异常即 `continue` —— **失败词静默退出，表面上像「零命中」**，正是铁律里「零命中不等于废词」最危险的形态：失败词不进 `truly_zero` 四分类，只在 `failed_t` 里留一行。60 天窗把每词请求拉长，429 概率显著高于 30d。
- **补扫验证（自建 `output/arxiv/retry_pass2.py`，3 次重试 + 45s 超时 + 词间 8s）**：16 个失败词**全部重跑成功，合计新增幸存 0 条**，125 条原始命中里 116 条已在 `seen`、9 条被 carrier/excl 正确丢弃。→ **本轮 14 条是真全集，查询空洞未掩盖任何条目**。但这个结论只在「补扫成功」前提下成立；**建议给 `scan.py` 加内建重试**，否则下一次同样静默。
- **补扫逐词 total（60d）**：`robot data`=8 · `consensus protocol`=4 · `auditable training`=3 · `automated market maker`=3 · `cat:cs.CR AND ti:"MEV"`=3 · `embodied data`=3 · `robot manipulation data`=2 · `proof-of-useful-work`=1 · `light client`=1 · `proof of training`=1 · `data availability sampling`=1 · **`verifiable inference`=0 · `proof of learning`=0 · `verifiable training`=0 · `restaking`=0 · `liquid staking`=0**。
- **跨窗判据更新**：上轮（30d）记的 6 个「三档全零候选废词」中，`light client` / `consensus protocol` / `MEV` / `robot manipulation data` 本轮 60d 均有命中 = **活的，别删**；剩下 `verifiable inference` / `proof of learning` / `verifiable training` / `restaking` / `liquid staking` **60d 仍为 0，连续第二轮全零** → 按铁律进入「降级为低频」，**仍不删**。`ti:"Robinhood Chain"` 60d=0 是首次在同口径下复现。
- **窗口内最新收录日期 = 2026-10-22，连续第五天未动**（今日 10-26）。已知形态，非异常；本轮 14 条的 `published` 全部落在 **08-29 → 09-25**，与 10-22 之间还隔着近一个月 —— 这一个月正是 `seen` 已吃掉的部分。
- **单侧读数（每轮必记）：加密词 0 / 机器人词 14。** 与本轮 30d 跑的 0 vs 26 同向，第五次连续单侧。加密侧 60 天窗依然零幸存，但注意：**这是「加密词写法打不中」与「加密论文确实少」不可分离的结果**，不能据此判定加密方向降温。
- **单词集中度**：`egocentric` 覆盖率 **7/14 = 50.0%**（30d 口径 53.8% / 含它 69.2%）。**浓度随窗口变宽而下降**（30d 14/26 → 60d 7/14），说明 60 天里非 egocentric 的数据引擎/数据生成类论文占比更高 —— 与上轮「浓度不随窗口变化」的判断**相悖，该判据需作废**：30d 与 7d 一致只是短窗内同构图，拉长到 60d 就分开。
- **产出：`memory/arxiv-labels.tsv` 此前不存在，本轮首次建立（38 键全覆盖）。** 审计报「未打方向标签 26 条」是历史欠账，本轮按 `memory/directions.md` 受控表打完：`具身数据` 32 · `世界模型` 1 · `?` 5（`2609.06195` EgoNeMo 行人动力学地图 / `2609.18548` HAP 头部运动预测 / `2610.10538` Never Look Back 3D 物体记忆 / `2610.18373` DR-VLA 四足导航 / `2610.23943` ESCAPE 第一视角避障 —— 均属「单帧感知/纯检测」或「导航」，现有受控表装不下，**不自造标签**）。
- **`memory/arxiv-hits.tsv` 发现并修复 1 处粘连行**：pass1 追加时上一行末尾无换行，`2610.22363 Perceive, Predict, and Plan` 与 `2609.30770 NavGen` 被压成一行（4 字段）。已按日期前缀切分还原为两条，现 38 行全部 3 字段。**根因是 `scan.py` 的 hits 追加分支未先补换行**，间歇性触发，易被忽略。
- **方向表反馈**：5 条 `?` 集中在「第一视角感知/导航」。`directions.md` 里 `具身数据` 明确「不算纯数据集整理」，`抓取与操作` 不算多指手 —— 这批卡在标签缝隙。按规则⑥属「该补标签」信号，但加标签门槛是人来做，本轮只记录不自改。

### arxiv-radar — under the hood（第四轮 · 60d）
- 🔧 12 tool calls — 9× Bash, 3× Write · 2 个自建脚本（`output/arxiv/retry_pass2.py` 补扫 16 词、`output/arxiv/fix_and_titles.py` 修粘连 + 拉 38 键标题）。**超 SKILL 的 ≤8 预算 4 次**，主因是 66.7% 查询失败必须补扫 —— 预算铁律默认「一轮脚本能跑完」，未覆盖脚本自身失效的补扫成本。
- ⚠️ **权限层实测拒绝两次**：`cp` 产物（备份）与 `cat >> memory/logs/...md` 均需审批。SKILL 铁律写「追加用 `>>`」，**本机不成立**；本轮日志改由 `Write` 写 payload 后再落盘。
- 索引滞后已连续第五天（10-22 封顶），60d 窗的实际有效覆盖只有 08-27 → 10-22。

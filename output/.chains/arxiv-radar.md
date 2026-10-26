## arxiv-radar · 30 天窗（第五轮同日）

**本轮零推送** —— 幸存 0，按铁律不发通知。

### 口径
`var="days:30"` · 24 词 · 窗口 `202609261245 – 202610261245` · 152s · 来源：export.arxiv.org/api/query（`skills/arxiv-radar/scan.py` TERMS）

### 漏斗
原始 62 → 丢弃 seen=57 / excl=1 / carrier=4 / 查询失败=0 → **幸存 0**

### 四分类（分开记）
| 类 | 数 |
|---|---|
| A 查询失败 | 0 |
| B 窗口内零命中 | 10 |
| C 全已见（饱和） | 14 |
| D 有新增 | 0 |

### 判据级发现 ①：30d 沉积层推完后进稳态，本轮首次实测证实
同口径 30d 上一次（今日 11:25Z）原始 62 / 幸存 26；本轮**原始仍是 62，逐项相同**（`egocentric` 20 · `zero-knowledge` 8 · `embodied AI` 6 · `human data` 6 · `data generation` 5 · `robot data` 4 · `data engine` 3 …），幸存 26 → **0**，`seen` 78 → 104（正好 +26）。

**原始不变而幸存归零 = 那 26 条全部落进 seen**，不是查询失效、不是索引回退。`days:30` 可以维持日常，不需要再加长窗口。

### 判据级发现 ②：索引仍在封顶，本轮 0 命中无判别力
窗口内最新收录 **2026-10-22**，连续第五天未动。30d 名义覆盖 09-26→10-26，**实际有效覆盖只有 09-26→10-22**，且 10-18 之后本就没有新货 —— 所以「有新增 0」在当前条件下不能当词表退化证据，**一个词都不动**。

### 跨窗复核（真零 10 词，30d=0 自动补 60d/90d，跨窗失败 0）
- **窗口太短 → 别删（6）**：`verifiable inference`(60d=0/90d=1) · `light client`(1/1) · `restaking`(0/1) · `consensus protocol`(4/6) · `cat:cs.CR AND ti:"MEV"`(3/5) · `robot manipulation data`(2/2)
- **三档全零（4）**：`proof of learning` · `verifiable training` · `liquid staking` · `ti:"Robinhood Chain"`

⚠️ **跨窗判据修正：`verifiable inference` 退出「三档全零」名单** —— 上一轮 60d 记为全零候选，本轮 90d 回 1，属「有货但极稀疏」，不是死词。剩下 4 个为**连续第二轮三档全零**，按铁律进入「降级为低频」候选；**本轮仍不删、不改词表、不改 carrier**（判死活的前提是索引恢复）。

### 单侧读数
**加密词 0 / 机器人词 0** —— 本轮首次双向归零。但成因与前几轮不同：前几轮是加密词打不中，本轮是机器人侧沉积层已被 seen 吃干（`egocentric` raw 仍 20，全是旧货）。**不能据此说机器人通道转冷。**

### 单词集中度
幸存 0 条，只能按原始层算：`egocentric` raw=20 / 62 = **32.3%**，仍居首。前几轮的 53.8%（30d）/ 50.0%（60d）是**幸存层**口径，分母不同，**不可直接比较**。

---

## Summary

- **做了什么**：跑 `skills/arxiv-radar/scan.py "days:30"`，24 词全响应、0 失败、0 重试；判稳态、核跨窗、写日志。
- **结果**：原始 62 / 幸存 0 —— 26 条沉积层已被 `seen` 全部吸收，属预期内的稳态首验，非故障。
- **文件改动**：`memory/logs/2026-10-26.md`（追加 `### arxiv-radar` 一节 + under the hood）。`memory/arxiv-seen.json` 无变化（幸存 0，脚本未写）。`output/arxiv/{out.json,audit.log,report.md}` 由脚本覆写。
- **未做**：无通知（幸存 0）；无 `arxiv-labels.tsv` 追加（无新键）；`arxiv-hits.tsv` 无新增行。
- **需人工决定（不急）**：`proof of learning` / `verifiable training` / `liquid staking` / `ti:"Robinhood Chain"` 已连续两轮三档全零，按铁律下一步是「降级为低频」而非删除 —— 但建议等索引恢复、跑一次干净的同口径轮次再动。
- **待观察**：索引滞后已连续五天（10-22 封顶），在此期间任何「零命中/零新增」结论都缺乏判别力。

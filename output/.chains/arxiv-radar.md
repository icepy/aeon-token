已经跑完了 `arxiv-radar`（`dry-run days:7`），日志已追加。下面是本轮结果。

## arXiv Radar · 2026-10-26 · 窗口 7 天

**口径**：只用 `ti:` 字段 · 24 个机制词 · 窗口 `20261019 10:16 → 20261026 10:16` · dry-run（不发通知）

### 漏斗
原始命中 **8** → 幸存 **0**
- `seen` 去重 6 · `EXCL` 排除 0 · carrier 误杀 2 · 查询失败 0

### 四分类
| 分类 | 数量 | 说明 |
|---|---|---|
| 查询失败 | 0 | 无 API 异常 |
| 真零 | 19 | `total=0`，本轮未跨窗复量 |
| 全已见（饱和） | 5 | 有命中但全部在 `arxiv-seen.json` |
| **有新增** | **0** | — |

### 饱和的 5 个词（原始命中 / 新增）
- `zero-knowledge` — 3 / 0
- `ti:"egocentric" AND cat:cs.RO` — 2 / 0
- `robot data` — 1 / 0
- `ti:"data engine" AND cat:cs.RO` — 1 / 0
- `ti:"EIP-1559"` — 1 / 0

### 索引滞后
窗口内最新收录日期 **2026-10-22**，比今天早 4 天 —— 这是 arXiv 常态滞后，**不是零命中的证据**。

### 判据级发现
- 7 天窗 `raw` 只有 8，落在 SKILL.md 记录的「18 词 60 天 total 2–200」水位上，窄窗正常，不做词表死活判断。
- **19 个真零词本轮没有跑 7/30/60 跨窗复量**（dry-run 下省掉约 144s）。按铁律，窄窗会把稀有词读成「真零」，所以这批词**不要据本轮删**——下轮 30 天窗再判。本轮真零名单：`proof-of-useful-work` · `verifiable inference` · `light client` · `proof of training` · `proof of learning` · `verifiable training` · `auditable training` · `data availability sampling` · `restaking` · `automated market maker` · `consensus protocol` · `ti:"MEV" (cat:cs.CR)` · `liquid staking` · `embodied data` · `robot manipulation data` · `embodied AI` · `human data (cs.RO)` · `data generation (cs.RO)` · `Robinhood Chain`
- 2 篇被 carrier 丢弃 —— 与 MEMORY 里 github-radar 第十七轮「carrier 误杀率 50% vs 50%，无差异，不放宽」的结论一致，本轮不动 carrier。

### 产物
`output/arxiv/out.json` · `audit.log` · `report.md`（脚本自写）。`memory/arxiv-seen.json` 因 dry-run 未更新。

## Summary
- 执行 `python3 skills/arxiv-radar/scan.py "dry-run days:7"`，24 词 7 天窗，原始 8 / 幸存 0，耗时 79s，`STATUS: ARXIV_RADAR_OK`。
- 修改：`memory/logs/2026-10-26.md` 追加 `### arxiv-radar` 一节（口径 + 漏斗 + 四分类 + 最新收录日期 + 判据发现）。
- 未发通知（dry-run）；`arxiv-seen.json` 未写（dry-run 设计）。
- 后续：下轮跑默认 **30 天窗**再判 19 个真零词死活；`raw` 连续两轮低于 10 就该考虑 60 天窗。

已推送。以下是本轮产出。

# arxiv-radar · 2026-10-26（第二轮，同日复跑）

## 口径与漏斗

窗口 `202610190731 – 202610260731`（默认 7 天）· **24 词** · 耗时 78s。

| 阶段 | 数量 |
|---|---|
| 原始命中 | 8 |
| 丢弃 seen | 6 |
| 丢弃 carrier | 2 |
| 查询失败 | 0 |
| **幸存** | **0** |

**零命中，未推送。**

## 四分类（分开记）

- **查询失败**：0
- **真零**（raw=0）：19 · `proof-of-useful-work` · `verifiable inference` · `light client` · `proof of training` · `proof of learning` · `verifiable training` · `auditable training` · `data availability sampling` · `restaking` · `automated market maker` · `consensus protocol` · `cat:cs.CR AND ti:"MEV"` · `liquid staking` · `embodied data` · `robot manipulation data` · `embodied AI` · `ti:"human data" AND cat:cs.RO` · `ti:"data generation" AND cat:cs.RO` · `ti:"Robinhood Chain"`
- **全已见（饱和，不删）**：5 · `zero-knowledge`(raw=3) · `ti:"egocentric" AND cat:cs.RO`(raw=2) · `robot data`(raw=1) · `ti:"data engine" AND cat:cs.RO`(raw=1) · `ti:"EIP-1559"`(raw=1)
- **有新增**：0

## 窗口内最新收录日期

**2026-10-22** — 连续第 5 天没动。今日两轮窗口只差 1 小时，原始命中都是 8 条，且全部来自 10-22 及之前的存量：索引侧这一小时零进账，7 天窗的有效覆盖仍是 10-19 → 10-22 这 4 天。此条件下 19 个真零无判别力，按铁律一条不删。

## 判据级发现

**① 去重链路首次在真实数据上跑通。** 今日 07:31 那轮的 3 条幸存（`EgoForesight` `2610.31845`、`EgoRayFormer` `2610.26641`、`FLORA` `2610.31779`）本轮全部落进 seen=6，同窗口复跑不再重报。前几轮都是零新收，`hit_ids → arxiv-seen.json` 的写盘分支从未真正执行过，这次验证通过。

**② 饱和 5 词是「活查询 + 旧库存」，与真零 19 词形成对照。** 它们的 raw 全部来自 10-22 前存量，新收为 0 —— 查询本身打得中索引，只是没新货。真零那 19 个仍分不清是死查询还是窗口没货，必须等索引恢复后补跨 7/30/60 三窗复核。

**③ 环境坑复现（已记入日志）。** 照 SKILL.md 抄 `scan.py "${var}"` 会被权限层直接拒（`A variable in braces in this command can't be checked before it runs`），拒绝发生在执行前，与密钥无关 —— 必须传字面量 `""`。

## 状态

`memory/arxiv-seen.json` 仍 78 个 id（本轮 `hit_ids` 空，写盘分支跳过）· `output/arxiv/out.json` = `[]` · `report.md` 未生成（零命中）· `audit.log` 已更新。

## Summary

- **做了什么**：跑完 arxiv-radar 默认 7 天窗扫描，24 词、原始 8、幸存 0；核实索引停更第 5 天；确认跨 run 去重首次在真实数据上生效；写日志并提交推送。
- **文件改动**：`memory/logs/2026-10-26.md`（追加 `### arxiv-radar — 第二轮` + under-the-hood 两节）· `output/arxiv/audit.log` / `out.json` · commit `54b084a` 已推 `main`。
- **后续动作**：索引恢复收录后，对 19 个真零词补跑跨 7/30/60 三窗复核，才能判定是否真降温；未发起 PR、未改词表。

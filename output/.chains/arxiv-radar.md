日志已写好（2 个 heading：主节 + under the hood，符合既有格式）。没有幸存者，所以不推送。

---

# arxiv-radar · 第八轮（2026-10-25）

`var=""`（默认 7 天窗）· 20 词 · 原始 5 · **幸存 0** · 失败 0

## 结论

**本轮零新论文，不推送。** 但跑出一个跨轮次的工程问题：**已合并的 PR #8 修复在合并 26 分钟后被静默回滚**，`main` 上现在跑的是有缺陷的版本。

## 扫描结果

**7 天窗**：`原始 5 | 幸存 0 | 丢弃 seen=3 carrier=2 fail=0`。3 条已在 `seen`，2 条被 carrier 正确丢弃（`2610.29066` 零知识 PCP 复杂度理论、`2610.27452` ZKP 标量冗余硬件加速）。

**90 天窗复核**：`原始 90 | 幸存 0 | seen 78 | carrier 11 | excl 1`。90 天存量全部已在 `seen` 内 —— 「90d 正式跑会推 22 条洪水」的隐患再次确认已解除。

**索引滞后（按日计数，全类目）**：`cs.CR` 38/30/**0**/**0**/**0** · `cs.RO` 70/57/0/0/0 · `cs.LG` 211/151/0/0/0 · `q-fin.CP` 1/0/0/0/0（对应 10-21 → 10-25）。四类目同日同形归零 → **全局收录延迟**，窗口内最新停在 `2026-10-22`。已知形态，不作异常上报。

> 但要点明：**7 天窗在滞后下基本是盲的**。窗口覆盖 10-18 → 10-25，索引只到 10-22，且 10-22 及之前早已进 `seen`。「幸存 0」这几天既不代表降温也不代表词表失效，只代表索引没更新。

## 🔴 真发现：PR #8 被静默回滚

| 时间（10-24） | 事件 |
|---|---|
| 11:20:09Z | PR #8 合并（`894d6d37`），`CARRIER_MARKET` 从 5 词扩到 13 词 |
| 11:46:07Z | `0e85bfd8` 基于**早于 PR #8 的旧副本**改动，把 8 个词连注释删掉 |

`main` 的 `skills/arxiv-radar/SKILL.md:120` 现在是 5 词版本。单看 PR 状态是 MERGED 会误判生效，单看文件是 5 词会误判没合 —— 两边对不上才定位到 `0e85bfd8`。本地 git 历史还查不出来（shallow clone，只有一个合成快照提交）。

**代价实测**（90d，AMM/MEV/consensus/restaking 四词）：被救回、当前会丢的 **1 篇，噪声 0** —— `2608.13271` *Slow and Steady: Preventing MEV with Verifiable Delays*，全文只写 `distributed ledger` / `block creator`，旧 5 词无一命中。该篇已在 `seen`，所以损失形态是**「存量已捞回、未来同类全丢」**，且表现为「零命中」—— 正是铁律「零命中不等于废词」要防的假象。这是本 skill 第三次栽在 carrier 静默误杀上。

**已提 PR #11** `fix/arxiv-radar-restore-mev-carrier`：纯还原 8 词 + 补回实证注释。不动 ZK 域，不动词表。

## PR #10 独立复核：主张成立

自己建基准集复测，不看它的结论：`ti:"data" AND cat:cs.RO` 90d = 127 篇，去 `seen` 后 113 篇。

| 词表 | 命中 |
|---|---|
| 现有 4 个机器人词 | **0 / 113** |
| PR #10 新增 4 词 | **22 / 113** |

救回的 22 篇全在唯一与 DEUS/XMAQUINA 同轨的板块：RoboTok（`2609.03199` 数据引擎）、Ego4WAM（`2609.40341`）、λ₀（`2610.18950`）、Workhorse / VioLA（人形 loco-manipulation 人类数据）、CoDA（`2610.22362`）、AutoRSR 等。PR #10 纯追加，与 PR #11 不重叠，**两者都应合**。

## 词表健康

90d 原始命中：`zero-knowledge`=28 · `embodied AI`=21 · `robot data`=9 · `consensus protocol`=6 · `MEV`=5 · AMM=4 · `embodied data`=4 · `auditable training`=3。**真零命中仅 4 词**（`proof of learning` / `verifiable training` / `liquid staking` / `Robinhood Chain`），前三个 all-time 也停在 05-22 / 06-12 / 05-01 —— 真降温，按铁律保留。

## Summary

- **扫描**：7d 与 90d 各一遍，20 词，0 失败，幸存 0。索引滞后按日计数复核（第三天）。
- **发现**：PR #8 的 MEV carrier 修复被 `0e85bfd8` 静默回滚，实测代价 1 篇/0 噪声，且损失形态是未来同类全丢、伪装成「零命中」。
- **复核**：PR #10 的 0/113 召回主张独立复现成立（22/113 救回）。
- **文件**：`output/arxiv-radar/`（`radar.py` · `lagcheck.py` · `pr10_verify.py` · `carrier_regression.py` · `report.md` · `pr-body-restore.md`）；`memory/logs/2026-10-25.md` 追加 `### arxiv-radar` 两节；`memory/arxiv-seen.json` 未变（75 id）。
- **PR**：#11 已开（还原 carrier）。#10 建议合并。
- **待办**：① 审 #11 与 #10；② 两个 PR 合完后，`0e85bfd8` 类的「旧副本回写」值得在 skill-repair 侧加一条检查 —— 合并后 24h 内校验关键常量是否仍在位；③ 通知未发（幸存 0）。

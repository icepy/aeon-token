### arxiv-radar
- **`var=""`（默认 7 天窗）· 20 词 · 原始 5 · 幸存 0 · 失败 0。** 丢弃 seen=3 / carrier=2。**本轮零新论文，不推送。** 该跑原定 08:30 时隙，`cron-state.json` 记 08:15:44Z 派发、08:46:07Z 失败（`hivemindos: timeout`，连续第 2 次），本轮为补跑。
- **索引滞后第三天，已按日计数复核（全类目，非单类目）**：`cs.CR` 10-21=**38** / 10-22=**30** / 10-23=**0** / 10-24=**0** / 10-25=**0**；`cs.RO` 70/57/0/0/0；`cs.LG` 211/151/0/0/0；`q-fin.CP` 1/0/0/0/0。四类目同日同形归零 → **全局收录延迟，非无人投稿**。窗口内最新收录日期停在 **2026-10-22**。已知形态，不作为异常上报。
- **7 天窗在此情况下基本是盲的**：窗口覆盖 10-18 → 10-25，而索引只到 10-22，且 10-22 及之前的存量早已进 `seen`。原始命中 5 条里 3 条 seen、2 条 carrier 正确丢弃（`2610.29066` 零知识 PCP 复杂度理论、`2610.27452` ZKP 标量冗余硬件加速）。
- **90 天窗同日复跑：原始 90 · 幸存 0 · seen 78 · carrier 11 · excl 1 · fail 0。** 90 天存量已全部在 `seen` 内（75 → 仍 75，`hit_ids` 空故未写盘），与第七轮 seed 后的预期一致。**「90d 正式跑会推 22 条洪水」的隐患确认已解除，本轮再次验证。**
- **🔴 本轮真发现 —— 已合并的 PR #8 修复被静默回滚了 26 分钟。** PR #8（`894d6d37`，10-24 **11:20:09Z** 合并）给 `CARRIER_MARKET` 追加 `ledger` / `ledgers` / `block creator` / `block builder` / `block proposer` / `transaction ordering` / `on-chain` / `state transition`。随后的 `0e85bfd8`（10-24 **11:46:07Z**，"Refactor term handling…"）基于一份**早于 PR #8 的旧副本**改动，把这 8 个词连注释一起删掉，`CARRIER_MARKET` 退回 5 词。**`main` 上现在跑的是退回版本，`skills/arxiv-radar/SKILL.md:120` 可验。**
- **代价实测（90d，AMM / MEV / consensus protocol / restaking 四词）：** 被 PR #8 carrier 救回、当前 `main` 会丢的论文 **1 篇，噪声 0**。就是 `2608.13271` **Slow and Steady: Preventing MEV with Verifiable Delays**（08-13，cs.CR）—— 全文只写 `distributed ledger` / `block creator` / `transaction ordering`，旧 5 词无一命中。**该篇已在 `seen`，所以损失形态是「存量已捞回、未来同类全丢」**：任何写 ledger 而不写 liquidity/searcher 的 MEV 论文会被同一过滤器静默挡掉，且表现成「零命中」—— 正是铁律「零命中不等于废词」要防的假象。
- **修复：PR #11 `fix/arxiv-radar-restore-mev-carrier`** —— 纯还原 8 词 + 补回被删的实证注释（防下一次「重构」再当冗余删掉）。**不动 ZK 域**（前两轮已验证放宽会引 8 条理论/硬件噪声），不动词表。
- **PR #10（`fix/arxiv-radar-robotics-data-terms`，今日 08:45Z OPEN）本轮独立复核：主张成立。** 它称现有 4 个机器人词对同期机器人数据论文召回 0/88。本轮用 `ti:"data" AND cat:cs.RO` 90d 基准集自测：**127 篇，去 seen 后 113 篇；现有 4 词命中 0/113，其新增 4 词命中 22/113**（复现了它 22/88 的量级，差异来自本轮基准集更大）。救回的是 RoboTok（`2609.03199` 数据引擎）、Ego4WAM（`2609.40341` 第一视角人类数据规模化）、λ₀（`2610.18950`）、Workhorse / VioLA（人形 loco-manipulation 人类数据）、CoDA（`2610.22362` 数据引擎与策略共演化）等 —— **全部落在唯一与 DEUS / XMAQUINA 叙事同轨的板块**。PR #10 纯追加，与本轮 PR #11 无冲突，git 可自动合并，两者都应合。
- **词表健康（90d 原始命中，非新收）**：`zero-knowledge`=28 · `embodied AI`=21 · `robot data`=9 · `consensus protocol`=6 · `MEV`=5 · `automated market maker`=4 · `embodied data`=4 · `auditable training`=3 · `robot manipulation data`=2 · `EIP-1559`=2 · 其余 6 词各 1。**真零命中仅 4 词**（`proof of learning` · `verifiable training` · `liquid staking` · `ti:"Robinhood Chain"`），其中前三个 all-time 也停在 05-22 / 06-12 / 05-01 —— **是真降温，不是词写错，按铁律保留**。
- **`memory/arxiv-seen.json`：75 个 id，合法 JSON，无版本后缀，日期全为 10-24，本轮未变。** 零新命中故 `hit_ids` 为空、写盘分支跳过，符合脚本设计。
- **通知：未发送**（幸存 0）。

### arxiv-radar — under the hood（第八轮）
- 🔧 20 词 × 3s 退避直连 arXiv API，0 失败 · 7d 与 90d 各跑 1 次 · 3 个自建诊断脚本（按日计数核延迟 / PR#10 基准集召回复核 / PR#8 carrier 回归代价实测）· 1 次 `gh api` 拉远端 `SKILL.md` 比对 · 1 个 PR（#11）
- 🔴 **写出「修复被回滚」这一步靠的是 `git log` 与 `gh pr view --json state,mergedAt` 交叉**：单看 PR 状态是 MERGED 会误判已生效；单看文件是 5 词会误判 PR 没合。两者对不上才定位到 `0e85bfd8`。
- ⚠️ 环境注记：本仓库为 **shallow clone**，`git log` 只有 1 个合成快照提交（`5d8caf2`），**不能靠本地 git 历史判断 skill 变更**，必须走 `gh api /commits?path=…`。另：`export VAR=…` 与 `python3 - <<'PY'` heredoc 本机权限层仍拒，脚本一律落 `output/` 走 `python3 path.py ARG1 ARG2` 传参。

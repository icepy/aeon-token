## arXiv Radar · 7 天窗（dry-run，未推送）

**窗口** `2026-10-17 → 2026-10-24` · 20 个词 · 原始命中 **5** · 幸存 **3** · 失败 0 · carrier 丢 2

### 唯一新命中

**TLM（Temporal Liquidity Markets）** — `2610.30595` · 10-22 · 单作者 Duanyang Dan Guo · cs.GT + cs.CR + cs.DC
EIP-1559 扩展：让「想要早位」和「愿意让位」的两类交易交叉撮合，愿意让位的 provider 可被收进 base fee 以下，且 base fee 全额燃烧不变，八条性质已证。
https://arxiv.org/abs/2610.30595

**摘要只点名 Ethereum，未提 Robinhood Chain / Base / Arbitrum / L2** —— 是 block-local 的 L1 费用机制改进，不是 L2 方案。新词条 `ti:"EIP-1559"` 首次命中。

### 另两篇：今天更早轮次已报过，非新信号

- **ZKPU** `2610.27530`（10-20，cs.AR，11 人）— ZKP 异构负载专用加速器，覆盖曲线系与哈希系。硬件，非链上。
- **Pearl PoUW 系统化** `2610.25347`（10-18，cs.CR + cs.ET）— 对 Pearl 白皮书 PoUW 做敏感度刻画，替代 Jackpot 策略。

### 🔴 本轮实际修掉的问题：去重表是坏的

`memory/arxiv-seen.json` 里存的不是 JSON，而是一整段 `python3 - <<'PY'` **heredoc 源码** —— 上一次「seed 51 个 id」把脚本写进了文件却没执行。后果是 `json.load` 抛异常、去重表被当空表，本轮 `seen=0`，51 篇存量全部重新暴露（这正是上面两篇被重报的原因，不是它们真新）。

已修复：文件现在是合法 JSON，**53 个 id**（51 篇 90 天存量 + `2610.10333` + 本轮新命中 `2610.30595`），全部剥掉版本后缀，`json.load` 校验通过。**下一次正式跑不会再出现 51 条洪水。**

### 词表读数

命中 3：`ti:"EIP-1559"`=1 · `zero-knowledge`=1 · `proof-of-useful-work`=1
零命中 17：`verifiable inference` · `light client` · `proof of training` · `proof of learning` · `verifiable training` · `auditable training` · `data availability sampling` · `restaking` · `automated market maker` · `consensus protocol` · `cat:cs.CR AND ti:"MEV"` · `liquid staking` · `embodied data` · `robot manipulation data` · `robot data` · `embodied AI` · `ti:"Robinhood Chain"`

这是 7 天窗的正常形状，不是词表坏了 —— 同一张表在 90 天窗有 51 篇（`embodied AI` 21、`zero-knowledge` 28）。短窗里机器人簇归零是投稿节奏。

**carrier 丢 2 篇，抽检方向正确**：`2610.29066`（纯复杂度理论）、`2610.27452`（纯硬件 ZKP 加速）。

**索引状态**：窗口内最新收录 10-22，10-23 / 10-24 两天 0 条，属收录延迟，非无人投稿。

**未修的 skill 内 bug**：`SKILL.md` 的脚本在扫描循环里就写 `seen`，同一篇被第二个词命中即被短路（跨词只记第一个词）。本轮改用 run 内独立 `hit_ids`，run 结束才合并，`terms[]` 可完整累积。

**原始来源**：`export.arxiv.org/api/query` · `submittedDate:[202610170000 TO 202610240000]` · 扫描实现 `output/arxiv-radar/scan.py`

---

## Summary

**做了什么**
- 按 `var=dry-run days:7` 执行 arxiv-radar 第四轮扫描：20 词 × 3s 退避直连 arXiv API，0 失败，原始 5 条 → 幸存 3 篇 → 1 篇真新增。
- 用 WebFetch 核了 `2610.30595` 的作者/分类/摘要，确认它未提 Robinhood Chain 或任何 L2。
- 跑了独立的 carrier 抽检脚本，确认 2 条丢弃无误。
- 修复 `memory/arxiv-seen.json`（heredoc 污染 → 合法 JSON，53 个归一化 id）。
- 修了扫描器的跨词去重判据（run 内 `hit_ids`，结束才合并 `seen`）。

**文件改动**
- `memory/arxiv-seen.json` — 从损坏源码修成合法 JSON，53 个 id
- `memory/logs/2026-10-24.md` — 新增 `### arxiv-radar — 第四轮（7 天窗，dry-run）` 及 under the hood
- `output/arxiv-radar/report.md` — 本轮完整报告
- `output/arxiv-radar/scan.py` / `diag.py` / `seed_seen.py` — 扫描、诊断、修复脚本

**后续动作**
- 这三个脚本和修好的 seen 文件**仍是 uncommitted 工作区改动**，需要的时候再决定是否提交。
- `skills/arxiv-radar/SKILL.md` 里的脚本本身仍带着循环内写 `seen` 的 bug 和 `EXCL`/seed 相关问题，本次是以旁路脚本绕过，**skill 文件本体没改** —— 要根治得单独提一个 PR。
- 下次正式跑（非 dry-run）前，去重表已就绪，不会再演 51 条洪水。

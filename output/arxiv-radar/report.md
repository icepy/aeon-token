# arxiv-radar · 第八轮（2026-10-25）

`var=""`（默认 7 天窗）· 20 词 · 原始 5 · **幸存 0** · 失败 0

---

## 1. 结论先行

**本轮零新论文，不推送。** 但跑出一个跨轮次的工程问题：**已合并的 PR #8 修复在合并 26 分钟后被静默回滚**，`main` 上现在跑的是有缺陷的版本。已提 PR #11 还原。

---

## 2. 扫描结果

### 7 天窗（默认）

```
扫 20 词 | 窗口 7d | 原始 5 | 幸存 0 |
丢弃 seen=3 excl=0 carrier=2 fail=0
窗口内最新收录日期: 2026-10-22
```

- 原始 5 条里 **3 条已在 `seen`**。
- 2 条被 carrier 正确丢弃：
  - `2610.29066` Zero Knowledge for Free up to Linear Query Bounds…（纯复杂度理论）
  - `2610.27452` SRE: Accelerating ZK Proofs via Scalar Redundancy Elimination（纯硬件加速）

### 90 天窗（复核存量）

```
扫 20 词 | 窗口 90d | 原始 90 | 幸存 0 |
丢弃 seen=78 excl=1 carrier=11 fail=0
窗口内最新收录日期: 2026-10-22
```

90 天存量 **全部已在 `seen` 内**，与第七轮 seed 后的预期一致。**「未来 90d 正式跑会一次推 22 条洪水」的隐患再次确认已解除。**

`excl` 唯一一条判对：`2610.14038` "From bits to atoms: A survey of cross-layer safety in Embodied AI" —— 标题含 survey，真综述。

### 索引滞后（按日计数，全类目核）

| 类目 | 10-21 | 10-22 | 10-23 | 10-24 | 10-25 |
|---|---|---|---|---|---|
| cs.CR | 38 | 30 | **0** | **0** | **0** |
| cs.RO | 70 | 57 | **0** | **0** | **0** |
| cs.LG | 211 | 151 | **0** | **0** | **0** |
| q-fin.CP | 1 | 0 | **0** | **0** | **0** |

**四类目同日同形归零 → 全局收录延迟，非无人投稿。** 窗口内最新收录停在 `2026-10-22`。这是已知形态（第七轮已定），不作为异常上报。

⚠️ 但要点明：**7 天窗在滞后下基本是盲的**。窗口覆盖 10-18 → 10-25，而索引只到 10-22，且 10-22 及之前早已进 `seen`。所以「幸存 0」在这几天里既不代表话题降温，也不代表词表失效 —— 它只代表**索引没更新**。

---

## 3. 🔴 真发现：PR #8 的修复被静默回滚

### 时间线

| 时间（10-24） | 事件 |
|---|---|
| 11:20:09Z | PR #8 `fix/arxiv-radar-mev-carrier-ledger` 合并（`894d6d37`），`CARRIER_MARKET` 从 5 词扩到 13 词 |
| 11:46:07Z | `0e85bfd8` "Refactor term handling and CARRIER_MARKET definition" —— 基于**早于 PR #8 的旧副本**改动，把 8 个词连注释删掉 |

### 现状

`main` 的 `skills/arxiv-radar/SKILL.md:120`：

```python
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher"]
```

PR #8 加的全部丢失：`ledger` · `ledgers` · `block creator` · `block builder` · `block proposer` · `transaction ordering` · `on-chain` · `state transition`。

### 为什么 26 分钟没人发现

单看 PR 状态是 **MERGED**，会误判已生效；单看文件是 **5 词**，会误判 PR 没合。两边对不上才定位到 `0e85bfd8`。**本地 git 历史还查不出来** —— 本仓库是 shallow clone，只有一个合成快照提交。

### 代价实测（不是推断）

90 天窗，`automated market maker` / `MEV` / `consensus protocol` / `restaking` 四词，对比 5 词 vs 13 词 carrier：

| 项 | 值 |
|---|---|
| 被 PR #8 carrier 救回、当前 `main` 会丢的论文 | **1 篇** |
| 已进 `seen` | 1 |
| 新增噪声 | **0** |

唯一一篇：

> **`2608.13271`** — *Slow and Steady: Preventing MEV with Verifiable Delays*（08-13，cs.CR，拜占庭 + 博弈两类正结果、负界、真实数据实现讨论）

全文只写 `distributed ledger` / `block creator` / `transaction ordering`，旧 5 词无一命中 → 被静默丢弃。

**因为这篇已在 `seen`，当前损失形态是「存量已捞回、未来同类全丢」。** 任何未来写 ledger 而不写 liquidity/searcher 的 MEV 论文，都会被同一过滤器挡住，且**表现为「零命中」** —— 正是 `SKILL.md` 铁律「零命中不等于废词」要防的那类假象。这是本 skill 第三次栽在 carrier 静默误杀上（PR #7、#8，以及这次的回滚）。

### 处理

**PR #11** `fix/arxiv-radar-restore-mev-carrier` —— 纯还原 8 词，并补回被删的实证注释（防下一次「重构」再当冗余删掉）。**不动 ZK 域**（前两轮已验证放宽会引 8 条理论/硬件噪声），不动词表。

---

## 4. PR #10 独立复核：主张成立

今日 08:45Z 另有一个 open PR #10 `fix/arxiv-radar-robotics-data-terms`，称现有 4 个机器人词对同期机器人数据论文召回 **0/88**。本轮不看它的结论、自己建基准集复测：

**基准集** `ti:"data" AND cat:cs.RO`，90 天 = **127 篇**，去 `seen` 后 **113 篇**。

| 词表 | 命中基准集 |
|---|---|
| 现有 4 词（`embodied data` / `robot manipulation data` / `robot data` / `embodied AI`） | **0 / 113** |
| PR #10 新增 4 词（`data engine` / `human data` / `egocentric` / `data generation`，均带 `cat:cs.RO`） | **22 / 113** |
| 两者都漏 | 91 |

召回量级复现（PR #10 记 22/88，本轮基准集更大故为 22/113）。**被救回的全部落在唯一与 DEUS / XMAQUINA 叙事同轨的板块**：

- `2609.03199` **RoboTok** — Internet 演示视频检索与灵巧操作的数据引擎
- `2609.40341` **Ego4WAM** — 扩展第一视角人类数据时什么才要紧
- `2610.18950` **λ₀** — 开放世界第一视角人类数据规模化（人形 loco-manipulation）
- `2610.09117` **Workhorse** / `2610.12435` **VioLA** — 从人类数据学人形全身 loco-manipulation
- `2610.22362` **CoDA** — 数据引擎与动作策略共演化
- `2609.18293` Function-Preserving Data Generation（Zero-Shot Real2Sim2Real）
- `2610.20336` **AutoRSR** — 自动化 Real2Sim2Real 数据生成
- 等共 22 篇

PR #10 是纯追加（只加词表 4 行 + `CARRIER_BY_TERM` 4 行），与本轮 PR #11 改的 `CARRIER_MARKET` 定义**不重叠，git 可自动合并**。两者都应合。

---

## 5. 词表健康（90d 原始命中，非新收）

`zero-knowledge`=28 · `embodied AI`=21 · `robot data`=9 · `consensus protocol`=6 · `MEV`=5 · `automated market maker`=4 · `embodied data`=4 · `auditable training`=3 · `robot manipulation data`=2 · `EIP-1559`=2 · 其余 6 词各 1。

**真零命中仅 4 词**：`proof of learning` · `verifiable training` · `liquid staking` · `ti:"Robinhood Chain"`。前三个 all-time 最新也停在 05-22 / 06-12 / 05-01 —— **是真降温，不是词写错，按铁律保留不删**。

---

## 6. 状态

- `memory/arxiv-seen.json`：**75 个 id**，合法 JSON，无版本后缀，日期全为 10-24，本轮未变（零新命中 → `hit_ids` 空 → 写盘分支跳过，符合脚本设计）。
- 通知：**未发送**（幸存 0）。
- 本轮为 08:30 时隙的补跑 —— `cron-state.json` 记 08:15:44Z 派发、08:46:07Z 失败（`hivemindos: timeout`，连续第 2 次失败）。

## 7. 原始来源

- arXiv API：`https://export.arxiv.org/api/query`（`ti:` + `submittedDate`，20 词 × 3s 退避，0 失败）
- PR #8 `894d6d37` / 覆盖提交 `0e85bfd8` / PR #11 / PR #10 — `gh api repos/icepy/aeon-token/commits?path=skills/arxiv-radar/SKILL.md`
- 论文：`https://arxiv.org/abs/2608.13271` · `2608.13271` · `2609.03199` · `2609.40341` · `2610.18950` · `2610.22362`

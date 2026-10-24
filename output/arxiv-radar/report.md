# arXiv Radar · 7 天窗（dry-run）

窗口 `2026-10-17 → 2026-10-24` · 20 个词 · 原始 **5** 条 → 去重幸存 **3 篇** · 失败 0
过滤器：`ti:` only · EXCL 只判标题 · carrier 丢 2 篇

## 幸存者

### 可验证训练 / PoUW（1）

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 10-18 | **Pearl PoUW 系统化** | 对 Pearl 白皮书 PoUW 做敏感度刻画，替代 Jackpot 策略，并给矿工自选噪声幅度 | https://arxiv.org/abs/2610.25347 |

单作者 Youlong Ding · cs.CR + cs.ET · carrier=`blockchain`。**今日更早两轮已报过，非新命中。**

### ZK / 可验证计算（1）

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 10-20 | **ZKPU** | 面向 ZKP 异构负载的专用加速器，FIPS Montgomery × 可重构 Twin Systolic Fabric，同时覆盖曲线系与哈希系 | https://arxiv.org/abs/2610.27530 |

11 人（Jonathan Ku / Changchun Zhou / Jiawen Wu 等）· cs.AR（硬件，非链上）· carrier=`protocol`。**今日更早轮次已报过，非新命中。**

### 费用机制 / EIP-1559（1）— 本轮唯一新命中

| 日期 | 名字 | 一句话 | 链接 |
|---|---|---|---|
| 10-22 | **TLM（Temporal Liquidity Markets）** | EIP-1559 扩展：让「要早位」和「愿意让位」的双方交叉撮合，provider 可被收进 base fee 以下，base fee 全额燃烧不变 | https://arxiv.org/abs/2610.30595 |

单作者 Duanyang Dan Guo · cs.GT + cs.CR + cs.DC · carrier=`blockchain`。
摘要里只点名 Ethereum，**没有提 Robinhood Chain / Base / Arbitrum / L2** —— 是 block-local 的 L1 费用机制改进，不是 L2 方案。

## 词表命中（本轮口径）

`ti:"EIP-1559"`=1 · `zero-knowledge`=1 · `proof-of-useful-work`=1

零命中 17 个：`verifiable inference` · `light client` · `proof of training` · `proof of learning` · `verifiable training` · `auditable training` · `data availability sampling` · `restaking` · `automated market maker` · `consensus protocol` · `cat:cs.CR AND ti:"MEV"` · `liquid staking` · `embodied data` · `robot manipulation data` · `robot data` · `embodied AI` · `ti:"Robinhood Chain"`

> 这是 **7 天窗** 的正常形状，不是词表坏了：90 天窗同表有 51 篇，其中 `embodied AI` 21、`zero-knowledge` 28。短窗里机器人簇归零是投稿节奏，不是话题死。

## 被 carrier 丢弃（2，抽检方向正确）

| id | 标题 | 丢弃理由 |
|---|---|---|
| `2610.29066` | Zero Knowledge for Free up to Linear Query Bounds | 纯复杂度理论，无部署/系统载体 |
| `2610.27452` | SRE: Accelerating Zero-Knowledge Proofs via Scalar Redundancy Elimination | 纯硬件加速 |

## 索引状态

窗口内最新收录 **2026-10-22**，距今天 2 天。10-23 / 10-24 两天 0 条 —— 与 10-24 早先两轮观测一致，属收录延迟，**不是无人投稿**（该异常已在前轮自愈过一次）。

## 本轮修掉的一个真问题

`memory/arxiv-seen.json` **内容是失控的 heredoc 源码，不是 JSON** —— 10-24 上一次「seed 51 个 id」把 `python3 - <<'PY'` 整段写进了文件却没执行。后果：`json.load` 抛异常 → 去重表被当成空表 → 本轮 `seen=0`，51 篇存量全部重新暴露（也正是 ZKPU / Pearl 两篇被重报的原因）。

已修复：文件现在是合法 JSON，**53 个 id**（51 篇 90 天存量 + `2610.10333` + 本轮新命中 `2610.30595`），全部已归一化去掉版本后缀。校验 `json.load` 通过。

## 未修的 skill 内 bug

`skills/arxiv-radar/SKILL.md` 的脚本**在扫描循环里就往 `seen` 写 id**（`seen[aid] = now...`），导致同一篇被第二个词命中时被当成「已见」短路 —— 跨词命中只记第一个词。本轮改用 run 内独立 `hit_ids` 判重、run 结束才合并 `seen`，`terms[]` 可完整累积。

## 原始来源

`export.arxiv.org/api/query` · `submittedDate:[202610170000 TO 202610240000]` · 扫描实现见 `output/arxiv-radar/scan.py`

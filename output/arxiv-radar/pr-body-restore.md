## 问题

PR #8（`fix/arxiv-radar-mev-carrier-ledger`，合并于 2026-10-24 11:20Z，merge commit `894d6d37`）给 `CARRIER_MARKET` 追加了 8 个词，救回只写「distributed ledger」的 MEV 论文。**该修复在合并 26 分钟后被静默覆盖。**

覆盖者是 `0e85bfd8`（2026-10-24 11:46Z，"Refactor term handling and CARRIER_MARKET definition"）。从 diff 看它是基于一份**早于 PR #8 的旧副本**做的改动，把 PR #8 新增的 8 个词连同注释一起删掉，`CARRIER_MARKET` 退回 5 词：

```
-CARRIER_MARKET = [..., "ledger", "ledgers", "block creator", "block builder", ...]
+CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher"]
```

`main` 上现在是退回后的版本。**这是本 skill 第二次出现同类问题**（PR #7 / PR #8 修的都是 carrier 静默误杀），而这次的性质不同：不是设计错，是修好的东西被回滚且没人发现。

## 代价（实测，不是推断）

90 天窗，`automated market maker` / `cat:cs.CR AND ti:"MEV"` / `consensus protocol` / `restaking` 四个词，对比旧 5 词与 PR #8 的 13 词 carrier：

| | 结果 |
|---|---|
| 被 PR #8 carrier 救回、当前 `main` 会丢的论文 | **1 篇** |
| 其中已进 `seen` | 1（`2608.13271`） |
| 新增噪声 | **0** |

唯一一篇是 `2608.13271` **Slow and Steady: Preventing MEV with Verifiable Delays**（08-13，cs.CR）。它全文只写 `distributed ledger` / `block creator` / `transaction ordering`，旧 5 词无一命中 → 被 carrier 静默丢弃。

因为这篇已在 `arxiv-seen.json` 里，**当前损失是「存量已捞回、未来同类全丢」**：任何未来写「distributed ledger」而不写「liquidity / searcher」的 MEV 论文，都会被同一个过滤器静默挡掉，且表现为「零命中」，正是 `SKILL.md` 铁律「零命中不等于废词」要防的那类假象。

## 改动

还原 PR #8 的 `CARRIER_MARKET`，并补上原注释里被删掉的实证说明，避免下一次「重构」再把它当冗余删掉：

```python
# 交易/MEV 域：市场微观结构，链上词常常不出现
# 追加 ledger 系：MEV 论文常写 "distributed ledger" / "block creator"，
# 实证 2608.13271（Slow and Steady）全文无一词命中旧 6 词而被静默丢弃。
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher",
                  "ledger", "ledgers", "block creator", "block builder",
                  "block proposer", "transaction ordering", "on-chain",
                  "state transition"]
```

纯还原，**不动 ZK 域**（前两轮已验证放宽会引 8 条理论/硬件噪声），不动词表。

## 与 PR #10 的关系

PR #10（`fix/arxiv-radar-robotics-data-terms`，OPEN）改的是词表与 `CARRIER_BY_TERM`，与本次改的 `CARRIER_MARKET` 定义**不重叠**，git 可自动合并。两者应当都合。

## 验证

- 用改后 `SKILL.md` 的 carrier 定义跑 90d 对比脚本，确认救回 1 篇、噪声 0（见上表）。
- 本轮 90d 全量扫描（20 词，原始 90，幸存 0，`seen` 78）在改前跑，改后不影响本轮结果 —— 这篇已在 `seen`。

## 备注

`0e85bfd8` 同时改了 `raw_term` 统计与 term 处理逻辑，那部分改动本身是对的、本轮保留不动；本次只还原被误删的 carrier 词。

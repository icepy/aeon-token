# arxiv-radar · 第二十九轮

- 窗口：30 天 · 词表 26 词 · `vM`
- 漏斗：原始 **90** → 幸存 **0**
- 丢弃：seen(记忆) 89 · seen(本轮重复) 0 · EXCL 1 · carrier 0 · 查询失败 0
- 索引最新收录：2026-10-27（距今 1 天）— 节律正常
- 六分类（单位=词）：未测到(试过失败) 0 · 未尝试(熔断跳过) 0 · 窗口内零命中 7 · 低频探针 0 · 全已见(饱和) 19 · 有新增 **0**

## 本轮无幸存论文

不是断流：19 个饱和词的 raw 最新发布日期全部落在 10-06 ~ 10-27（`egocentric` 停在 10-27），流量仍在进来，全部已被 `seen` 吃掉。

## 唯一 EXCL（每轮恒定常数项，不进 seen）

- 2026-10-02 `From bits to atoms: A survey of cross-layer safety in Embodied AI` — survey，连续第三轮同一条

## 零命中 7 词 · 跨窗全部「窗口太短」

| 词 | 本轮 | 60d | 90d |
|---|---|---|---|
| `verifiable inference` | 0 | 0 | 1 |
| `verifiable computation` | 0 | 1 | 1 |
| `light client` | 0 | 1 | 1 |
| `restaking` | 0 | 0 | 1 |
| `cat:cs.CR AND ti:"MEV"` | 0 | 3 | 5 |
| `RWA` | 0 | 1 | 2 |
| `robot manipulation data` | 0 | 2 | 2 |

跨窗有命中 → **非真零，不许删**。连续第二轮无一「跨窗皆 0」→ 无删词候选、无换写法候选。

## 本轮动作

无新增词 · 无删词 · 无改 carrier · labels 未写（幸存 0）· notify 未发（幸存 0）

`MEMORY.md` 8,182 字节（8 KB 线内，余 10 字节）· 零幸存 → 无 labels 可写、无通知可发。

---

# arxiv-radar（第 40 轮）

**VERSION** `vM` · **窗口** 30 天（默认）· **26 词** · **var** 空 · 耗时 143s

## 漏斗

```
原始 73 → 幸存 0
  ├ seen(记忆) 73    ← 100% 全吃（连续第二轮）
  ├ seen(本轮重复) 0
  ├ EXCL 0 · carrier 0 · 查询失败 0 · 兜底 0
```

**索引滞后**：窗口内最新收录 **2026-11-05（周四）**，今天周日 = 距今 3 天。按「周一看到上周五算正常」的节律，11-05 是周四，**连续第三天停在这里**（11-07、11-08 两轮读数相同）→ 已踩到「连续两天不动才算真滞后」的线，**下一轮若仍停 11-05 则确认滞后**，不是因为周末不公告。

## 六分类（分开写）

| 分类 | 词数 | 说明 |
|---|---|---|
| 未测到（试过失败） | **0** | 无 `failed_t`，本轮不是「失败伪装成零命中」 |
| 未尝试（熔断跳过） | **0** | 未触发 `_DEGRADED` |
| 窗口内零命中 | **9** | 见下方跨窗 |
| 低频探针 | **0** | |
| 全已见（饱和） | **17** | 别删 |
| **有新增** | **0** | 连续第三轮为 0 |

## 跨窗结论

**判死清单只剩 2 个，且两者 60d 与 90d 都为 0：**

| 词 | 30d | 60d | 90d |
|---|---|---|---|
| `verifiable inference` | 0 | **0** | **0** |
| `restaking` | 0 | **0** | **0** |

**7 个窗口太短、别删**（跨窗有命中）：
- `verifiable computation` 60d=1 / 90d=1
- `proof of training` 60d=1 / 90d=1
- `light client` 60d=0 / 90d=1
- `cat:cs.CR AND ti:"MEV"` 60d=3 / 90d=4
- `RWA` 60d=1 / 90d=2
- `embodied data` 60d=1 / 90d=3
- `robot manipulation data` 60d=2 / 90d=2

这两个 0 词**已走到最宽档**，所以下一步不是删词 —— 按「换写法 → 降级低频 → 删」的禁令，该做的是同义写法量测（`verifiable inference` → `proof of inference` / `verifiable ML`；`restaking` → `restaking protocol` / `shared security`）。

**饱和 17 词的 raw 最新发布日期**：`embodied AI` 11-05 · `egocentric` 11-05 · `robot data` 11-03 · `hand-object` 11-03 · `zero-knowledge` 11-04 · `consensus` 11-04 —— 话题全活。最旧两个：
- `ti:"human demonstration"` 11-02
- **`ti:"staking"` 10-10 —— 距 29 天，明天（11-09）滑出 30d 窗**

## 判据级发现

1. **`seen` 吃干率连续两轮 100%（73/73、76/76），有新增连续三轮 0。** 窗滑动一天（10-09 → 10-10）raw 76 → 73，即 10-09 贡献 3 条沉积、**0 条新**。在此口径下「0 命中 = 词表失效」和「0 命中 = 话题降温」两个结论**都不成立** —— 该通道目前只能证饱和，加过滤器无效，出路只有换窗 / 加词 / 扩源。

2. **`staking` 滑出 30d ≠ 降温，本轮还判不了。** 它不在窗口内零命中的 9 词里，所以本轮**没有被量测 60d 值**（跨窗量测只覆盖零命中的那 9 个）。它明天会从「饱和」栏掉进「窗口内零命中」栏，**下一轮必须补上它的 60d 才能判** —— 只看「滑出窗」就降温是把饱和误读成消失。

3. **未配 carrier 表的词仍是 14 个** —— 加密侧 10 个（`verifiable inference` / `verifiable computation` / `verifiable training` / `auditable training` / `proof of training` / `proof-of-useful-work` / `light client` / `zero-knowledge` / `consensus` / `data availability sampling` / `restaking` / `staking` / `RWA` / `EIP-1559`）。这是**第 14 个轮次**记录同一数字，说明「词表扩了、carrier 表没跟」是结构性的。

4. **本轮无 `?` 样本，精度地面真值不可更新。** 审计报 `领域命中` 0 / `carrier 丢弃` 0 —— 因为 0 条进入 carrier 层，**这是「没有输入经过」不是「过滤器挡住了」**。真实精度只认我们自己打的 `?`，幸存 0 → 本轮无新样本。carrier 判别力抽检**连续第二轮不可测**，顺延至第一次有幸存时。

## 幸存者

**无。** 原始 73 条全部命中 `memory/arxiv-seen.json`，无新论文可报。

## 待办

- **下一轮（11-09）必做**：`ti:"staking" AND (cat:cs.CR OR cat:cs.DC OR cat:q-fin.GN)` 滑出 30d 后补测 60d= —— 有命中即「窗口太短」，60d 也为 0 才进降温候选。
- **同义写法量测**：`verifiable inference` 与 `restaking` 各跑一次 `check:<新写法>`，判据 60d total 5–60、已见低于 1/3、领域命中 >80%。
- **索引滞后确认**：下一轮若最新收录仍为 11-05 且非周末因素，则确认为真滞后并记录。
- **未配 carrier 表 14 词**：已连续 14 轮同值，需一次系统性补齐（或明确「默认 crypto 表」为可接受终态，把这条从待办里划掉）。

## Summary

- 跑了 `python3 skills/arxiv-radar/scan.py ""`（默认 30d 窗，26 词），原始 73 · 幸存 0 · `STATUS: ARXIV_RADAR_OK`。
- 修改文件：`memory/logs/2026-11-08.md`（追加 `### arxiv-radar（第 40 轮）` 一节）、`memory/MEMORY.md`（发现层 arxiv-radar 行原地改写，8,182 字节仍在 8 KB 线内）。
- **未写 labels**（零幸存，无条目可追加）、**未发通知**（按铁律零命中不发）。
- 后续动作：11-09 补测 `staking` 的 60d；对 `verifiable inference` / `restaking` 跑同义写法量测；确认索引是否真滞后一轮。

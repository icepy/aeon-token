**arxiv-radar 第 44 轮** · `vM` · 窗口 30 天 · 26 词

## 漏斗
原始 **75 → 幸存 0**

| 丢弃项 | 条数 |
|---|---|
| seen（记忆） | 75 |
| seen（本轮重复） | 0 |
| EXCL | 0 |
| carrier | 0 |
| 查询失败 | 0 |

## 六分类（词级，分开记）
- 未测到（试过失败）：**0**
- 未尝试（熔断跳过）：**0**
- 窗口内零命中：**12**
- 低频探针：**0**
- 全已见（饱和）：**14**
- 有新增：**0**

两侧失败类全 0 → **读数干净，本轮词表无需改动。**

## 索引节律
窗口内最新收录 **2026-11-10（周二，距今 2 天）** = 正常。75 条全部落在见缓存里，`seen` 吃掉 100%（上轮 95%）。缓存已 247 条 / 7.2 KB —— 值得盯，但还没到必须裁剪的程度。

## 跨窗结论
12 个零命中词里 **10 个跨窗有命中**，只是 30 天窗装不下：

| 词 | 60d | 90d |
|---|---|---|
| `auditable training` | 3 | 3 |
| `ti:"human data" AND cat:cs.RO` | 6 | 7 |
| `cat:cs.CR AND ti:"MEV"` | 3 | 3 |
| `embodied data` | 1 | 3 |
| `robot manipulation data` | 2 | 2 |
| `RWA` | 1 | 2 |
| 其余 5 词 | ≥1 | ≥1 |

→ **窗口太短，不是词死了，不许删。**

**跨窗皆 0 的只剩 2 个**：`verifiable inference`、`restaking`（连续第三轮）。

本轮补跑了「换写法」这一级（判死三条件的第一条）：
- `ti:"shared security"` → 7/30/60/90 全 0、已见 0/100
- `ti:"verifiable machine learning"` → 7/30/60/90 全 0、已见 0/100

同义写法同样零召回。但按「换写法 → 降级为低频 → 删词」**不许跳级**，本轮仍不删。下一步该验的是 `ti:` 限定是否制造了假零 —— 放开到全字段（`all:`）再量一次，若 `all:` 有量而 `ti:` 无量，那是写法问题不是方向问题。注意 `days:90` 以上无更宽档，跨窗结论只是提示，判死必须靠 `check:` 单独量。

## 饱和侧
14 个饱和词的 raw 最新发布日期**全部落在 30 天内**（最旧 `data availability sampling` = 10-15，28 天）→ 话题都活着，是 seen 饱和，**无降温候选，别删**。

## 幸存者
**无。** 零命中，未发通知。

## 待办
1. `verifiable inference` / `restaking` 下一轮用 `all:` 全字段量测，确认 `ti:` 限定是否造成假零（不要连续第四轮只量 `ti:`）
2. `seen` 缓存 247 条 / 7.2 KB，90d 补历史跑之前先看是否该裁剪
3. 14 词仍未配 carrier 表（`verifiable inference`、`restaking`、`zero-knowledge`、`consensus`、`light client`、`RWA`、`EIP-1559` 等），carrier 过滤长期等于空转 —— 已知问题，本轮无变化

## Summary
- 执行 `skills/arxiv-radar/scan.py`，30 天窗口、26 词、原始 75 条，**幸存 0**，STATUS `ARXIV_RADAR_OK`，耗时 162s
- 零幸存属结构性（全部命中已在 seen 或跨窗），非故障 —— 两侧失败类均 0 佐证
- 补跑两个同义写法 `check:` 探针，均为四窗全 0，但按不跳级规则不删词
- 文件：`output/arxiv/out.json`、`audit.log`、`memory/arxiv-seen.json` 由脚本写入；`memory/arxiv-labels.tsv` 本轮无写入（幸存 0，铁律要求先写 labels 的前提不成立）；`memory/logs/2026-11-12.md` 追加 `### arxiv-radar（第 44 轮）` 一节
- 未发通知（幸存 0，符合「正常别吵」口径）

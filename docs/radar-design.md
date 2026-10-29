# 探针系统设计（v2）

> 来源：2026-10-28 的设计图。这份文件只承载需要成文的约束，不是全景复刻。

## 三层

| 层 | 干什么 | 通道 |
|---|---|---|
| 第一层 | 机制从哪来（词表维护） | `citation-radar`（引用图 → 候选词）· `probe`（仓名反查 → 候选词） |
| 第二层 | 名字有没有出现 | `arxiv-radar` · `github-radar` · `defillama-radar` |
| 第三层 | join 与判断 | 人工 · 候选卡 |

同一个名字在几条通道上依次点亮，那个次序才是信号。机制到板块的推断由人做，agent 只出机制、证据、计数。

## 交接面

层与层之间只通过这三样交换：

- `memory/logs/` —— 每轮的审计结论
- `memory/decisions.md` —— 已想清楚的决定，防推翻
- 候选词 —— 目前落在 `memory/github-candidates.md`；目标形态是 `memory/candidates/`（待建）

**名字清单不在交接面上。** 每个通道自己一份（`memory/universe-names.txt` 归 arxiv、`memory/defillama-names.txt` 归 defillama），因为两边吃法相反：arxiv 拿它当标题查询词、每词一次 API，defillama 拿它当本地子串、要短名。共用一份，改哪边都得拿另一边的尺子量一遍。

## 术语

- **probe** 只指 `github-radar` 里那个拿仓名反查、产候选词的动作，属第一层。别的 skill 里同名但不产候选词的，一律不叫 probe。
- **cross-window** 指零命中词的跨宽档 total_count 量法（arxiv 的 `cross_windows()`），属第二层判据辅助。
- **信息探针** 指整个系统，是比喻，不是某个函数。

## 通则

- **窗口只决定成本，不决定语义。** 任何依赖窗口的判据，必须同时声明「无更宽档时怎么办」。
- **轮次里的跨窗结论只是提示，判死必须靠 `check:` 单独量。**
- 失败 ≠ 零命中；`_DEGRADED` 时不动词表。
- carrier 只装摄像头；出现非 0 丢弃才谈收紧。
- 不为了让读数好看去动阈值。

## 待定

- **`probe` 归属。** 它现在寄住在 `github-radar` 里，但产物是候选词、周跑、`PROBE_WIN=60` 与 run 窗口脱钩 —— 按上表应归第一层，与 `citation-radar` 同格。怎么搬未定。

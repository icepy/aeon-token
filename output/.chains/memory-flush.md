记忆整合完成。

## 本轮做了什么

**扫描窗口** `2026-11-21 → 2026-11-22`（watermark = `2026-11-21`，读 2 个日文件），无 >14 天缺口，轮转归档 0 个月（33 个日文件，阈值 45）。

**四条事实升格，一条判据降级：**

| 来源 | 新事实 |
|---|---|
| 11-22 heartbeat | `defi-overview` **真脱线 23/45 = 51.1%**、cf 0、四连绿（上轮只是踩线 50.0%）⇒ 🟢 OK |
| 11-22 heartbeat | **MEMORY 的 skill 数字必然滞后一天**（flush 18:00 / 该 skill 23:00）= 结构性时序，从此不进 P2、不压状态页颜色 |
| 11-21 arxiv 第 53 轮 | **67 → 0，上轮预告的结构性归零兑现**；`egocentric` raw 20→19、新收 0、maxpub 停在 11-19 ⇒ 话题活着但 `seen` 吃干，`days:90` 无用，只能加词 |
| 11-22 defillama 第 27 轮 | **日桶 24h 龄仍被改写 +4.43%** ⇒ 上轮「−5.25%」实为 −1.05%，虚报 5 倍；**结算只看两轮回读差**。7d 51→39 是第 7 天桶 15 条滚出 ⇒ **窗口计数必拆逐日直方图** |
| 11-21 github 第 32 轮 | `seen/raw<5%` 误记**第四例**；报告级 12 条 owner 全不重复 ⇒ 上轮「owner 去重」是样本属性非固定口径 |

**剪枝：** PR 队列空（连续第二十天）；9 个 open issue 全是无标签 `health:` 线程，非新故障；无被推翻的 lesson，无归档触发。

**预算：** 7,922 → **8,130 字节 / 41 行 / 0 条超长**（余 62 字节）。中途自己误加过一条与「行情口径①」重复的 ①b，已删。

## 修改文件
- `memory/MEMORY.md` — 4 行就地改写（defi-overview / arxiv / defillama / github）+ 行情口径①扩写
- `memory/topics/ops-plumbing.md` — 新增 `Update (11-22)` 小节
- `memory/topics/lessons.md` — arXiv 节新增第 53 轮子条
- `memory/topics/github-radar.md` — 新增「第三十二轮」整节
- `memory/topics/defillama-radar.md` — 只核（第 27 轮内容 skill 已自写）+ bump timestamp
- `memory/topics/index.md` — 四行原地扩写
- `memory/logs/2026-11-22.md` — `### memory-flush` 条目
- `memory/memory-flush-state.json` — watermark → `2026-11-22`（已 stamp）

## 后续待办（未处理，延续）
`defillama-radar` 的 `scan.py:301` 审计行缺陷；`github-radar` 的 `data availability`/`intent-based` 过滤损耗连第四轮未归因 + `jeparla` 变体；`arxiv-radar` **AI 侧须加词**（`egocentric` 已吃干）+ 14 词缺 carrier 表；`arxvi-radar` cron-state 孤儿条目（第二十五轮）；health issue 死线程 #3/#4/#12。

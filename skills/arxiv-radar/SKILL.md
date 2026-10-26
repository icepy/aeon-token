---
name: arxiv-radar
description: 扫 arXiv 新预印本，按话题词过滤，把命中的项目名推给我。只做发现，不做判断。
metadata:
  title: arXiv Radar
  category: crypto
  var: "days:30"
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（**默认 30**）；`names` 切到"机制/名字反查"模式（词表改读 `memory/universe-names.txt`）。**原样传给脚本，不要自己解析。**

发现层的第一条通道。

## 为什么是 30 天，不是 7 天

**窗口是流量旋钮，但这条通道的旋钮被索引滞后卡死了。**

- 索引滞后实测 **5 天**（`窗口内最新收录` 连续 5 天没动）→ 7 天窗有效覆盖只剩 **2 天**
- 30d 首跑实测：26 条幸存，与 `seen` 重叠 **0**，`published` 全在 09-28→10-17 —— **7d 跑结构上看不见这批**（同日三跑对照：7d 0–3 条 vs 30d 26 条）
- 成本几乎为零：24 词 / 62 原始 / 77s

所以 30d 不是"稳健性偏好"，是**7d 结构性不够**。首跑会一次性推出沉积层（一次 26 条，`NOTIFY_TOP=30` 不会截断），之后即稳态。

## 各通道有自己的有效域

**本通道结构上就是 AI / 机器人传感器。** 实测：同一有效窗口内加密词 0 条、机器人词 26 条（真零 10 词里 9 个是链上/加密词）。

- 加密词留着当**低频探针**，别因 0 命中删
- **跨通道比较只在有效域内做** —— 别假设三条平行探针会同步点亮
- 单侧读数（一侧 0 / 一侧 26）每轮必须记

## 为什么用 arXiv

它是唯一"项目起源 + 有中心索引"的交叉点：论文先于主网、先于上市、先于叙事。PEARL 那篇 2026-06-03 的论文如果被扫到，提前量是 4 个月。

**但记住：arXiv 索引的是「机制」，不是「项目」。** 项目名（XMAQUINA）多半全期零命中；普通英文词（NOTE）会被英文用法污染。所以词表要写**持仓依赖的机制**，不是持仓的名字。

## 词表在哪

**全在 `skills/arxiv-radar/scan.py`。** `TERMS` / `CARRIER_BY_TERM` / `EXCL` 都在那个文件里，改词改那里，**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算是铁律：全程 ≤ 6 次工具调用。** 成本 = 调用数 × 每次重读上下文（~53k）。脚本自己的请求数不算在预算里。
- **审计全文打在 stdout —— 它本来就短（~35 行），不需要 digest。** 全文同时落 `output/arxiv/audit.log`。`--full` 尚未实现，会被当未识别 token 忽略。
- **不许现写 `python3 -c`；日志用 bash `>>` 追加，不 Read。**
- **产物文件名固定**（`out.json` / `audit.log` / `report.md`）。轮次号写进日志内容，不写进文件名。
- **只用 `ti:`。** arXiv 的 `abs:` 是松散匹配（`abs:"MEV"` 会命中兆电子伏特）。绕不开时用 `cat:` 约束整条查询。
- **写长短语，不写单词。** 单词必然撞别的学科（MEV / SNARK / liquidation 都是这么死的）。多词**必须带引号**：`ti:foo bar` 会被解析成 `ti:foo AND bar`，后面的词掉成全字段搜索。
- **零命中 ≠ 废词，也 ≠ 可删词。** 判断一个词死没死看 `raw_term`，不看 `per_term`（后者只统计本轮新收）。**脚本会对真零词自动补比本轮窗口更宽的档（窗口 30 → 补 60d；窗口 7 → 补 30d/60d），7d ⊂ 30d ⊂ 60d 所以更窄的档是蕴含的、不重复请求。** 跨窗有命中 = 活的；**跨窗全零也要连续两轮才谈删。**
- **加新领域的词必须同时配 carrier 并登记 `CARRIER_BY_TERM`。** 一组链上 carrier 会把整个机器人簇误杀（实证：20 篇 `embodied AI` 论文一个链上 carrier 都不含）。
- **看到 0 命中，先看 `raw_term`、跨窗三档和「窗口内最新收录日期」。** 收录日期比今天早 **5 天以上**就是索引滞后，不是零命中。
- **单词集中度每轮必记。** 实测 `egocentric` 单词覆盖 18/26 = **69%** —— 机器人侧实际上是"单词传感器"，调词优先调它，且要盯它是否过宽。集中度高但主题词在词表语义内 → 判真簇，不改词。
- **不做判断，不复述内容。** 只给名字 + 一句话 + 链接。

## Config

读：
- `skills/arxiv-radar/scan.py` 里的 `TERMS`
- `memory/arxiv-seen.json` — 已见 arxiv id（跨 run 去重；key 不带版本后缀）
- `memory/MEMORY.md` — 用来标相关性
- `names` 模式额外读：`memory/universe-names.txt`

写（脚本自己写，模型不用管）：
- `output/arxiv/out.json` · `audit.log` · `report.md`
- `memory/arxiv-seen.json`（`dry-run` 不写）
- 通知：只在有幸存者且非 `dry-run` 时发，最多 `NOTIFY_TOP` 条

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/arxiv-radar/scan.py "${var}"
```

脚本自己解析 var、拉取、过滤、写全部产物、按需发通知。审计全文打 stdout。

### 2. 写日志（bash 追加，不 Read）

往 `memory/logs/${today}.md` 追加一节 `### arxiv-radar`：口径 + 漏斗 + 四分类（**必须分开写**）+ 窗口内最新收录日期 + 单侧读数 + 单词集中度 + 你自己的判据级发现。零命中就只写一行。

### 3. 输出

- 通知正文由脚本写进 `output/arxiv/report.md` 并发出去
- 只给名字 + 一句话 + 链接，按簇分组，不做判断
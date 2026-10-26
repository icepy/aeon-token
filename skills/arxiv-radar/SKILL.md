---
name: arxiv-radar
description: 扫 arXiv 新预印本，按话题词过滤，把命中的项目名推给我。只做发现，不做判断。
metadata:
  title: arXiv Radar
  category: crypto
  var: ""
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 7）；`names` 切到"机制/名字反查"模式（词表改读 `memory/universe-names.txt`）。**原样传给脚本，不要自己解析。**

发现层的第一条通道。

## 为什么用 arXiv

它是唯一"项目起源 + 有中心索引"的交叉点：论文先于主网、先于上市、先于叙事。PEARL 那篇 2026-06-03 的论文如果被扫到，提前量是 4 个月。

**但记住：arXiv 索引的是「机制」，不是「项目」。** 项目名（XMAQUINA）多半全期零命中；普通英文词（NOTE）会被英文用法污染。所以词表要写**持仓依赖的机制**，不是持仓的名字。

## 词表在哪

**全在 `skills/arxiv-radar/scan.py`。** `TERMS` / `CARRIER_BY_TERM` / `EXCL` 都在那个文件里，改词改那里，**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算是铁律：全程 ≤ 10 次工具调用。** 脚本静态化之前，每轮都要重发 150 行 heredoc。
- **产物文件名固定**（`out.json` / `audit.log` / `report.md`）。轮次号写进日志内容，不写进文件名。
- **只用 `ti:`。** arXiv 的 `abs:` 是松散匹配（`abs:"MEV"` 会命中兆电子伏特）。绕不开时用 `cat:` 约束整条查询。
- **写长短语，不写单词。** 单词必然撞别的学科（MEV / SNARK / liquidation 都是这么死的）。多词**必须带引号**：`ti:foo bar` 会被解析成 `ti:foo AND bar`，后面的词掉成全字段搜索。
- **零命中不等于废词。** 可能是太前沿，也可能是没人写进标题 —— 留观察，别删。**判断一个词死没死看 `raw_term`（原始命中），别看 `per_term`** —— 后者只统计本轮新收。
- **加新领域的词必须同时配 carrier 并登记 `CARRIER_BY_TERM`。** 一组链上 carrier 会把整个机器人簇误杀（实证：20 篇 `embodied AI` 论文一个链上 carrier 都不含）。
- **看到 0 命中，先看 `raw_term` 和「窗口内最新收录日期」。** 收录日期比今天早 3 天以上就是索引滞后，不是零命中。
- **窄窗会把稀有词读成「真零」** —— 判词表死活必须跨 7/30/60 三个窗口量。
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

脚本自己解析 var、拉取、过滤、写全部产物、按需发通知。**审计全文打在 stdout**，不用再 `cat`。

> `export` 那套现在是脚本内做的 —— `DRY=1 python3 ...` 这种前缀形式会被权限层拒、导致"dry-run 其实没 dry"，静态化之后这个坑没了。

### 2. 写日志

往 `memory/logs/${today}.md` 追加一节 `### arxiv-radar`：口径 + 漏斗 + 四分类（**必须分开写**）+ 窗口内最新收录日期 + 你自己的判据级发现。零命中就只写一行。

### 3. 输出

- 通知正文由脚本写进 `output/arxiv/report.md` 并发出去
- 只给名字 + 一句话 + 链接，按簇分组，不做判断
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

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify 且不写 `seen`/`hits`；`days:N` 换窗口（默认 30）；`names` 切到"机制/名字反查"模式（词表改读 `memory/universe-names.txt`）；`check:<词>` 只量这一个候选词然后退出。**原样传给脚本，不要自己解析。**
>
> ⚠️ **`check:` 必须放最后** —— 其后全部内容（含空格、含 `cat:`）都算词。放中间会被 `var.split()` 切碎、静默量成别的词（实测踩过：`check:consensus protocol` 量成了 `ti:"consensus"`）。

发现层的第一条通道。

## 为什么用 arXiv

它是唯一"项目起源 + 有中心索引"的交叉点：论文先于主网、先于上市、先于叙事。PEARL 那篇 2026-06-03 的论文如果被扫到，提前量是 4 个月。

**但记住：arXiv 索引的是「机制」，不是「项目」。** 项目名（XMAQUINA）多半全期零命中；普通英文词（NOTE）会被英文用法污染。所以词表要写**持仓依赖的机制**，不是持仓的名字。

## 为什么是 30 天，不是 7 天

`seen` 去重一旦存在，窗口就不再是语义参数，只剩「成本」和「冗余」两个属性 —— 所以窗口取「冗余够用」的最短值。而 arxiv 额外有两个约束：**索引滞后 3–5 天**、**周五周六不公告**。7 天窗一有延迟就漏；30 天的搜索代价对 arxiv 是秒级。

**改词表 / 改 carrier / 失败词造成空洞之后，跑一次 `days:60` 补历史，然后回 `days:30`。** 60 天窗不是日常口径，是补历史口径。

## 词表在哪

**全在 `skills/arxiv-radar/scan.py`。** `TERMS` / `CARRIER_BY_TERM` / `EXCL` 都在那个文件里，改词改那里，**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算是铁律：全程 ≤ 8 次工具调用。** 实证曾到 213 次 = 30 分钟超时（脚本只占 284 秒）。每次调用要重读 ~53k 上下文 —— **调用数就是成本**。别现写 `python3 -c`，先看 `scan.py` 有没有子命令。
- **产物文件名固定**（`out.json` / `audit.log` / `report.md`）。轮次号写进日志内容，不写进文件名。
- **写 / 覆写文件一律用 Write 工具，不要用 `echo >`。** 实测 `Bash(echo>)` 会被权限层拒 —— 那一轮就是因为这个，中文稿没写成、机械英文版原样发了出去。**任何 shell 重定向都会被权限层拒（`cat >>` 也一样），写文件一律用 Write / Edit。**
- **只用 `ti:`。** arXiv 的 `abs:` 是松散匹配（`abs:"MEV"` 会命中兆电子伏特）。绕不开时用 `cat:` 约束整条查询。
- **写长短语，不写单词。** 单词必然撞别的学科（MEV / SNARK / liquidation 都是这么死的）。多词**必须带引号**：`ti:foo bar` 会被解析成 `ti:foo AND bar`。
- **「失败」和「零命中」是两件事。** `read timeout` / `HTTP 429` 是 **arXiv 侧**的问题（它没答）；`total=0` 才是**词**的问题（它答了，答案是"没有"）。前者跟词表一个字的关系都没有 —— 别据此改词。
- **`STATUS: ARXIV_RADAR_DEGRADED` 意味着「这轮没数据」，不是「这轮零命中」。** 审计里的 `未测到`（试过、失败）和 `未尝试`（熔断跳过、连试都没试）是两种不同的空洞，都要单独记。
- **看到 `↻ … 重试 n/N（原因，等 Ns）` 别 Ctrl-C。** 它在退避，不是卡死。stdout 进管道会块缓冲，表格要等进程结束才出 —— 用 stderr 的进度行判断死活。
- **零命中不等于废词。** **判词死没死看 `raw_term`（原始命中），别看 `per_term`**（后者只统计本轮新收）。
- **跨窗量测已进代码。** 窗口内零命中的词，脚本自动回退到更宽的档量 `opensearch:totalResults`；全部为 0 才判真零，判词是「**先用 `check:` 换同义写法**」—— arXiv 的 `ti:` 是**词干化短语匹配**，0 命中多半是写法不对，不是方向死了。**换写法优先于降级，降级优先于删词。**
- **加新领域的词必须同时配 carrier 并登记 `CARRIER_BY_TERM`。** 一组链上 carrier 会把整个机器人簇误杀（实证：20 篇 `embodied AI` 论文一个链上 carrier 都不含）。
- **看到 0 命中，先看 `raw_term`、跨窗 total、和「窗口内最新收录日期」。** 那行现在带 `（周X，距今 N 天）`：周一/周二 3–4 天是**周末不公告的正常节律**；**周中出现 3 天以上**才该去查 arXiv status。
- **审计的 `领域命中` 比真实精度乐观约 30%**（它的词表含 `network`，把什么都算进去）。**你自己标的 `?` 才是地面真值，那个数不是。**
- **标签首次即冻结。** 一条命中的方向打上就不再改。装不下就写 `?`，不自造标签。方向可多选（`A/B`），所以新增标签不会抢走老标签的历史。
- **不做判断，不复述内容。** 只给名字 + 一句话 + 链接。

## Config

读：
- `skills/arxiv-radar/scan.py` 里的 `TERMS`
- `memory/arxiv-seen.json` — 已见 arxiv id（跨 run 去重；key 不带版本后缀）
- `memory/directions.md` — 受控方向标签表（只能从里面挑）
- `memory/MEMORY.md` — 用来标相关性
- `names` 模式额外读：`memory/universe-names.txt`

写（脚本自己写，模型不用管）：
- `output/arxiv/out.json` · `audit.log` · `report.md`
- `memory/arxiv-seen.json`（`dry-run` 不写）
- `memory/arxiv-hits.tsv`（3 列 `日期/键/名字`，`dry-run` 不写）
- 通知：只在有幸存者且非 `dry-run` 时发

写（**模型写**）：
- `memory/arxiv-labels.tsv`（`键 \t 方向`，无表头，append-only）

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/arxiv-radar/scan.py "${var}"
```

脚本自己解析 var、拉取、过滤、写全部产物、按需发通知。**审计全文打在 stdout**，不用再 `cat`。

> `export` 那套现在是脚本内做的 —— `DRY=1 python3 ...` 这种前缀形式会被权限层拒、导致"dry-run 其实没 dry"。

### 2. 发通知（非 `dry-run` 且幸存 > 0）

**用 Write 工具覆写 `output/arxiv/report.md`**（不是 `echo >`），按簇分组、**每行带 `[方向]`**，然后一次 bash：

```bash
./notify -f output/arxiv/report.md
```

**改不了就直接 `./notify -f output/arxiv/report.md` 发机械版**（已去噪，能读）——**别不发。**

### 3. 写标签

用 Write / Edit 往 `memory/arxiv-labels.tsv` 追加本轮每个新键的方向（一行一条，`键 \t 方向`）。**只从 `memory/directions.md` 里挑**，装不下写 `?`。

### 4. 写日志

往 `memory/logs/${today}.md` 追加一节 `### arxiv-radar`：口径 + 漏斗 + **五/六分类（必须分开写）** + 窗口内最新收录日期 + 你自己的判据级发现。零命中就只写一行。

## 不要做的事

- **别把 `DEGRADED` 当零命中写进日志。** 两者含义相反。
- **别在 `check:` 放中间**，也别自己解析 `${var}`。
- **别手改 `skills.json`** —— 它是生成物。改任何 `skills/*/SKILL.md` 后 `ci-skills-json` 会红一次、`register-skill` 一分钟内自动重生成并转绿，**不要动**。
- **别改框架层**（`scripts/` `bin/` `.github/` `apps/`）。
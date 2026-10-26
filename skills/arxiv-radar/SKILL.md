---
name: arxiv-radar
description: 扫 arXiv 新预印本，按机制词过滤，把命中的论文推给我。只做发现，不做判断。
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

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（**默认 30**）；`names` 切到"机制/名字反查"模式（词表改读 `memory/universe-names.txt`）；`check:<词>` 只量一个词后退出（**必须是最后一个 token**）；`notify:script` 让脚本自己发通知（默认不发）。**原样传给脚本，不要自己解析。**

发现层的第一条通道。

## 为什么是 30 天

- 索引滞后实测 3–5 天 + 周末不公告 → 7 天窗有效覆盖只剩 2 天，**结构性不够**
- 30d 是生产口径。窗口只决定成本与冗余，不决定语义
- 窗口的第二个真实作用：**词表改动后的补历史** —— 加词 / 改 carrier 后跑一次 `days:90`，别只靠 30d

## 各通道有自己的有效域

**本通道结构上就是 AI / 机器人传感器。** 实测同一有效窗口内：加密词 0–3 条、机器人词 30+ 条。

- 加密词留着当**低频探针**，别因 0 命中删
- **跨通道比较只在有效域内做** —— 别假设三条平行探针会同步点亮
- 单侧读数每轮必须记

## 为什么用 arXiv

唯一"项目起源 + 有中心索引"的交叉点：论文先于主网、先于上市、先于叙事。

**但 arXiv 索引的是「机制」，不是「项目」。** 项目名多半全期零命中。所以词表写**持仓依赖的机制**，不写持仓的名字。

## 词表在哪

**全在 `skills/arxiv-radar/scan.py`。** `TERMS` / `LOW_FREQ` / `CARRIER_BY_TERM` / `EXCL` 都在那个文件里，改词改那里，**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算分层：日常 30d（幸存 ≤5）≤ 7 次工具调用；补历史 / 幸存 > 10 ≤ 12 次。** 超支几乎全是**重复读产物** —— 审计全文就在 stdout，读一次就够，别 `cat` 回去。
- **通知正文归模型，不归脚本。** 脚本只会拼英文标题 + 原始查询串；翻译和「按簇分组、带 `[方向]`」是判断。所以脚本默认不发 —— 覆写 `output/arxiv/report.md` 为中文后，**在同一条 bash 里**发一次。忘了发是可见的：脚本会打 `notify: **未发**` 并给出补发命令。
- **`NOTIFY_TOP=30` 只管脚本那份机械模板**，模型的中文稿不受它限制 —— 幸存 48 条也全推。
- **`labels.tsv` 是必写步骤，不是可选项。** 每条幸存者一行，`日期\t裸id\t方向`。方向**只能取自 `memory/directions.md` 的受控表**（别用簇标题那种散文）。append-only、first-wins、**冻结** —— 写错就是永久的。挑不出就写 `?`，别留空。
- **产物文件名固定**（`out.json` / `out.dry.json` / `audit.log` / `report.md`）。**轮次号写进日志内容，不要写进文件名。**
- **写 / 覆写文件一律用 Write 工具，不要用 `echo >`。** 任何 shell 重定向都会被权限层拒。发通知用 `./notify -f output/arxiv/report.md`（没有重定向，安全）。
- **`check:<词>` 必须是最后一个 token** —— 脚本用 `check:(.+)$` 抓它；放在中间会被空格切碎，静默去量另一个词。
- **零命中 ≠ 可删词。** 脚本对窗口内零命中的词自动跨更宽档（30/60/90 里所有 > 本轮窗口的值）量 total_count。判词顺序**不许跳级**：① 换写法 → ② 降级为低频（进 `LOW_FREQ`）→ ③ 删词。跨窗有命中即「窗口太短，别删」。
- **饱和 ≠ 降温。** 审计里饱和词的「raw 命中最新发布日期」才是判据：近 30 天内 = 话题活着、只是 seen 吃掉了；停在 60 天前才考虑降温。
- **有词 ≠ 有召回。** 每轮必看 `raw_term`：长期 0 命中而该方向明显有流量的词 = 写法错了，换写法，不是加窗口。
- **`领域命中` 不可全信。** 它用 `DOMAIN` 词算（含 `network`/`model`），偏乐观 30-50%。**真精度只认你自己给每条打的 `?`。**
- **失败 ≠ 零命中。** 审计分「未测到（试过失败）」和「未尝试（熔断跳过）」两类。看到这两类非零，先别改词表。
- **索引滞后看节律，不看天数。** 周一看到上周五 = 正常（周末不公告）。连续两天不动才算真滞后。
- **`hits.tsv` / `labels.tsv` 的键是裸 id，两文件必须 join 得上。** 落盘改键时两个一起改。
- **不做判断。** 只给名字 + 一句话 + 链接 + `[方向]`。

## Config

读：`skills/arxiv-radar/scan.py` 的 `TERMS` · `memory/arxiv-seen.json` · `memory/universe-names.txt` · `memory/directions.md`（受控方向表）

写（脚本自己写，模型不用管）：
- `output/arxiv/out.json`（非 dry-run）· `output/arxiv/out.dry.json`（dry-run）· `audit.log`
- `memory/arxiv-seen.json` · `memory/arxiv-hits.tsv`（非 dry-run 才写）
- `output/arxiv/report.md` —— 脚本写机械版，**模型覆写成中文版**

写（**模型写**）：
- `memory/arxiv-labels.tsv` —— 每条幸存者一行 `日期\t裸id\t方向`
- 通知：非 dry-run 且幸存 > 0 时**由模型发**

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/arxiv-radar/scan.py "${var}"
```

脚本自己解析 var、扫描、过滤、跨窗量、写全部产物。**审计全文打在 stdout**，不用再 `cat`。

### 2. 写 labels（非 dry-run 且幸存 > 0）

读一次 `memory/arxiv-labels.tsv`，把本轮每条幸存者按 `日期\t裸id\t方向` 追加进去（已存在的 id 跳过）。方向取自 `memory/directions.md`。挑不出写 `?`。

### 3. 写通知（非 dry-run 且幸存 > 0）

一次 bash：覆写 `output/arxiv/report.md` 为中文，同一条命令里发出去。

```bash
cat > output/arxiv/report.md <<'EOF'
**arxiv-radar** · 窗口 30 天 · 幸存 3

**具身数据 / 人类示范**
- `SocialCoAct` — 第一视角社交协同动作的人形基准 · https://arxiv.org/abs/2610.24559
EOF
./notify -f output/arxiv/report.md
```

- 名字 + 一句话 + 链接，**不做判断**、不复述摘要
- 名字和链接从审计里抄，别手打（手打会错）
- 幸存 > 10 时按簇压，别逐条列
- 幸存 ≤ 3 时不必分组，直接列

### 4. 写日志

往 `memory/logs/${today}.md` 追加一节 `### arxiv-radar（第 N 轮）`：口径 + 漏斗 + 六分类（**必须分开写**）+ 跨窗结果 + 你自己的判据级发现。幸存为 0 就只写一行。

### 5. 输出

给：`VERSION` · 窗口 · 漏斗 · 六分类 · 幸存者（名字/一句话/链接/`[方向]`）· 跨窗结论 · 待办。
**只做发现，不做判断。**
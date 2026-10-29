---
name: github-radar
description: 按方向词扫 GitHub 新建仓库，看「有没有人在写代码」。与 arxiv-radar 平行，只做发现，不做判断。
metadata:
  title: GitHub Radar
  category: crypto
  var: "days:7"
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（**默认 7**）；`min:N` 换 star 地板（**默认 0**）；`chk:N` 换核验门槛（默认 5）；`probe` 强制跑专名簇反查（**dry-run 下默认不跑，要验 probe 必须显式带 `probe`**；非 dry-run 才按 7 天到期自动跑）；`--full` 打全文审计（默认只打 digest）。**原样传给脚本，不要自己解析。**

发现层第二条通道。**与 `arxiv-radar` 平行，不是它的下游。**

| 成熟度 | 通道 | 提前量 |
|---|---|---|
| 有人在研究 | `arxiv-radar` | ~4 个月 |
| 有人在写代码 | **本 skill** | ~1–2 个月 |
| 有人在发币 | `gecko-radar`（未建） | 0 |

**同一个词在几条通道上依次点亮 —— 那个次序才是信号。**

**实证**：`SkillWeaver` 在 arxiv 是 09-28，GitHub 仓 10-08 —— **论文 → 代码滞后 10 天**。

**本通道的真实产出在 AI / 机器人侧**，加密侧顺带。

**窗口是流量旋钮，不是语义轴。** 有 `seen` 去重之后，7 天窗和 30 天窗在稳态下**产出完全相同**（都是「上次跑之后新建的仓」），差别只在搜索成本与冗余。所以取最短够用值：7 天（6 天冗余，抗一天跑挂）。**加词 / 改 carrier 时手动跑一次 `days:60` 补历史**，之后回 7 天。

## 词表与过滤器在哪

**全在 `skills/github-radar/scan.py`。** `TERMS` / `NEG_BY_TERM` / `CARRIER_BY_TERM` / `EXCL` / `SITE_SUFFIX` / `CODE_SKELETON` / `GLUE` / `THEME_LEXICON` 都在那里（常量若已拆到同目录 `words.py`，改那边），**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算是铁律：全程 ≤ 8 次工具调用。** 成本 = 调用数 × 每次重读上下文（~53k）。上一轮 97 次调用 = 5M 量级重读，脚本只占 349 秒。**要砍的是调用数，不是脚本行数。** 一轮的标准形状见下。
- **审计默认只打 digest（~50 行）。** 全文落 `output/ghradar/audit.log`，要归因时才 `--full`。**`dropped.json` 永远不整读**（全量千级），只看 digest 里的计数与误杀两行。
- **`gh api` 不带 `--jq` 视为没写。** 默认根本不 profile 任何仓 —— digest 里报告级已自带 desc；只有要判「是不是页形态」时才补一次 `gh api repos/O/R/contents --jq '.[].name'`。
- **不许现写 `python3 -c`。** 先看 `scan.py` 有没有子命令（`replay` / `liveness`）。每个一行流 = 1 次调用 + 一次全文重读。
- **日志用 bash `>>` 追加，不要 Read 后 Edit。**
- **产物文件名固定**（`out.json` / `out.dry.json` / `audit.log` / `report.md` / `clusters.json` / `dropped.json`）。**轮次号写进日志内容，不要写进文件名**（脚本会算好并打进 digest）。
- **`output/ghradar/` 由脚本自己清，不用你手动删。** 每次开跑前它会把目录里不在上面六个名字内的文件删掉，并把这行打进审计（`🧹 清理 …`）。想跨轮保留某个文件，文件名以 `keep` 开头。
- **旁路脚本不进 `output/ghradar/`。** 要留档的判据写进 `memory/logs/${today}.md`。
- **不要重写脚本。** 只有改过滤器时才 Edit `scan.py`。
- **核验宁可全量。幸存数 ≤ 上限时，一个都别漏。** 实证：`PER_TERM_CAP=25` 按 star 排序，只核了 76/234，报告级被低估 3.85×。7 天窗下幸存量本身很小（个位数），全量是廉价的。
- **分页：subdivide-to-one-page。** 整窗探针只定初始子窗数 `ceil(total/100)`，之后每个子窗**只取 page 1**；子窗自身 `total` 仍超一页就对半再分，切到 ≤ 一页为止。**7 天窗下几乎不拆** —— 旧的固定 300 条硬上限只在大窗口下才咬人（第十五轮：修好后幸存 4→49，`world model` 覆盖率 66.5%→100%）。**长窗（`total>1000`）曾比短窗更瞎**（上轮实测 `sim2real` 52.7% / `restaking` 83.3%），这条修的就是它。到二分上限仍超一页的叶子窗进审计（`capped`）。
- **star 排序会切掉 ★0 长尾。** 实证第十一轮：幸存 70 个里 ★≥5 只有 1 个、全轮最高 ★7，报告级 35 里 34 个是 ★0。**只要机制词还在，star 就不该出现在排序或采样里。**
- **star 与 commits 可能反相关。** 跟这一支只能按 commits 读。
- **换词前先量两个口径：total_count + 重叠度。不能只看污染率。** `vla`→全称双赢；`jepa`→全称灾难（654→35）。**分界不是「缩写脏不脏」，是这个术语在生态里实际怎么被书写。**
- **仓库名常写合成词，搜索按 token 切分** —— **description 比 name 更可靠**。
- **缩写若留着，必须配 `NEG_BY_TERM`**。
- **`per_term == 0` 必须分四类。** 查询失败 / 真零 / **全已见（饱和）** / 有新增。**「饱和」留着，「真零」才谈删词。** digest 的逐词表里四类是分开打的。
- **窄窗会把稀有词系统性读成「真零」** —— 判词表死活必须跨 7/30/60 三个窗口量 total_count。
- **同窗口连跑会读出「幸存 0」。** 非 `dry-run` 把幸存者写进 `seen` 之后，同窗口再跑必然 0 —— 那是算术。**dry-run 不写 seen，所以同窗口 dry-run 复跑 = 原样重放，数字不含新信号。**
- **词表对新生专名是全盲的（结构性，与窗口无关）。** 实证：`SuperMimic` 55 仓簇，18 词只捞到 2 个。**修法是反向做**：拿仓名 token 反查 —— 就是 `probe`。
- **`probe` 的定位是「候选词发现」，不是「仓库发现」。** 它索引的是**名字**（词表索引的是机制）。产物是「这几个名字在积累，考虑加进监控」，不是「今天多了几个仓」。所以它挂周跑、挂在比对层，不进日跑输出。
- **`probe` 判真簇要三条，缺一不可：① `total` 小；② 簇内同主题（`cohesive`）；③ 主题词落在 `THEME_LEXICON` 语义内（`thematic`）。** 前两条全中也还是假 —— 第十六轮 3 个非通用且 cohesive 的候选**3/3 全假**（`senku` 主题词只有 `with`×11、`uniview` 是海康大华 NVR、`pouw` 撞荷兰语货运）。脚本已把 `GLUE` 剔出主题词。**看着像专名不代表是我们的题。**
- **`probe` 跑 60 天窗，不跟日跑窗口。** 它问的是「这个名字在积累吗」= 周/月尺度；7 天窗下真簇 6 仓 vs 撞名 4 仓，**都在噪声底下面，判不出**。`PROBE_WIN=60` 必须独立于 run 窗口。
- **`probe` 到期用 `memory/ghradar-probe-last.txt` 戳判（≥7 天），`dry-run` 不写戳，显式带 `probe` 时无视戳。** 跑挂不写戳 → 次日自愈。
- **`dry-run` 默认不跑 `probe`。** dry-run 不写戳，不设这道闸就会在调别的规则时天天白跑一轮反查。要验 probe 就显式带 `probe`。**闸的顺序是「显式 → dry-run → 戳」，不许把 dry-run 挪到戳后面。**
- **`probe` 报簇必须同时给 `owner` 数与 `repo` 数。** 单 owner 多仓（一人铺开几个仓）不构成趋势。
- **共享脚手架 owner 黑名单抓不到**。判据：同短名跨 ≥3 owner 且 desc 前 80 字符相同。
- **EXCL 要同时查仓库名和 description。**
- **star 地板是反向的。** 默认 `min:0`。
- **30 天提交高 ≠ 现在在写。** 必须同时看近 7 天 —— 实测跨窗稳定在 55–60% 爆完即停。
- **高提交数 ≠ 代码仓。** 看 `language` 字段与根目录形态。
- **`commits=100` 是 `per_page` 上限**，标 `≥100`。
- **限速要重试，不能放弃。429（限速）和 409（真空仓）必须分开 —— 404 / 409 不触发认证降级（已进代码）。** gh 掉线次数、末次原因、未认证调用次数都进 digest 末行。
- **`_DEGRADED` 时不动词表、不动 `EXCL`。** 日志写清末次原因与掉线次数，等下一轮；同一原因连续两轮才升级给人。限流是 gh 侧的事，不是词表的事。
- **description 越像论文，越要查 commits。**
- **只匹配 `in:name,description`，不要 readme。**
- **脏词必须配 carrier**（`world model`）。**discard 量大 ≠ 误杀大**。**carrier 判据 = desc ∪ topics 任一命中**；`EXCL` 仍只看 name+desc。`len(desc)<25` 留逃生口：只有**无 topics** 才丢。**误杀率自动量**：`dropped.json` 全量落名单，digest 打 `carrier_named_uniq` / `carrier_named_alive_7d` + 幸存者对照。**放宽前先看这两行，别盲改。**
- **覆盖率必须报。** <50% 的绝对数不可引用；覆盖率是「叶子窗取满比例」，不是真实总量。
- **`template` / `demo` / `sniper` = 练手仓库或农场。**
- **站点仓按后缀无条件丢**（`.github.io` / `-page` / `-site` / `-website` / `-homepage` / `-showcase` / `-docs`）—— 体量不是判据。**同名仓**才需要「体量小 + 无 language」两个条件。
- **纯静态站还有第二种形态**：根目录 `index.html` + `.nojekyll` 且无任何代码骨架 → 页。
- **每条丢弃规则都要能被审计。** `carrier` 与 `short_desc` 的全量名单落 `dropped.json`。
- **农场只认黑名单。**
- **报「零命中」必须分开写四类。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天 / 7 天提交数。

## 一轮的形状（调用预算）

```
1. python3 skills/github-radar/scan.py "${var}"     ← digest，1 次
2. gh api repos/O/R/contents --jq '.[].name'        ← 只在要判页形态时，0–1 次
3. bash >> memory/logs/${today}.md                  ← 1 次
                                             合计 2–3 次
```

digest 里已经有：口径 / 漏斗 / 逐词四分类 / 报告级 + desc / probe 三段 / 误杀两行 / 异常行。**需要补调用，说明 digest 缺字段 —— 先补 digest，别补调用。**

## Config

读：
- `skills/github-radar/scan.py` 里的 `TERMS`
- `memory/github-seen.json` · `memory/github-farms.txt`（**黑名单，行内可带 `#` 注释**）
- `memory/ghradar-probe-last.txt`（probe 到期戳）

写（脚本自己写，模型不用管）：
- `output/ghradar/out.json` · `audit.log` · `report.md` · `dropped.json`（`probe` 时另有 `clusters.json`）
- `output/ghradar/out.dry.json` —— `dry-run` 时快照写这里，**不覆盖 `out.json`，也不覆盖 `report.md`**
- `memory/github-seen.json`（全部幸存者，`dry-run` 不写）
- `memory/github-candidates.md`（只写报告级，`dry-run` 不写）
- 通知：只在报告级 > 0 且非 `dry-run` 时发，最多 `NOTIFY_TOP` 条
- 清：开跑前删掉 `output/ghradar/` 里除上述六个名字外的文件（`keep*` 前缀除外）

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/github-radar/scan.py "${var}"
```

脚本自己解析 var、扫描、过滤、核验、写全部产物、按需发通知。**默认只把 digest 打 stdout**，全文落 `output/ghradar/audit.log`。要归因时加 `--full`。

### 2. 写日志（bash 追加，不 Read）

往 `memory/logs/${today}.md` 追加一节 `### github-radar（第 N 轮）`：口径 + 漏斗 + 四分类（**必须分开写**）+ 你自己的判据级发现。报告级为 0 就只写一行。digest 的行可以直接抄。

### 3. 输出

- 通知正文由脚本写进 `output/ghradar/report.md` 并发出去。`dry-run` 不写 `report.md`。
- 只给仓库 + 一句话 + 链接 + star + 30d/7d，不做判断。

### 4. 跑完交付

最终输出在日志之外，必须另给操作者两块，每块几行：

- **下一步** — 下一轮跑什么、改不改脚本。本轮没踩到的已知洞不夹带。
- **你要处理的** — 只有人能定的事（删词、这条仓算不算你的题、要不要合并）。没有就写「这轮不用你处理」。

改脚本只根据本轮结果里已经出现的缺陷。词表动作仍是三级：换写法 → 降级为低频 → 删词。不升 `VERSION`，除非这版行为要单独在飞；`gh-v4` 留给 `supermimic` 正样本。本地 `dry-run` 改写的 `audit.log` / `dropped.json` / `out.dry.json` 不提交，跑完还原。
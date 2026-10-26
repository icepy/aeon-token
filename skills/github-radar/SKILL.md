---
name: github-radar
description: 按方向词扫 GitHub 新建仓库，看「有没有人在写代码」。与 arxiv-radar 平行，只做发现，不做判断。
metadata:
  title: GitHub Radar
  category: crypto
  var: ""
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 30）；`min:N` 换 star 地板（**默认 0**）；`chk:N` 换核验门槛（默认 5）。**原样传给脚本，不要自己解析。**

发现层第二条通道。**与 `arxiv-radar` 平行，不是它的下游。**

| 成熟度 | 通道 | 提前量 |
|---|---|---|
| 有人在研究 | `arxiv-radar` | ~4 个月 |
| 有人在写代码 | **本 skill** | ~1–2 个月 |
| 有人在发币 | `gecko-radar`（未建） | 0 |

**同一个词在几条通道上依次点亮 —— 那个次序才是信号。**

**实证**：`SkillWeaver` 在 arxiv 是 09-28，GitHub 仓 10-08 —— **论文 → 代码滞后 10 天**。

**本通道的真实产出在 AI / 机器人侧**，加密侧顺带。

## 词表与过滤器在哪

**全在 `skills/github-radar/scan.py`。** `TERMS` / `NEG_BY_TERM` / `CARRIER_BY_TERM` / `EXCL` / `SITE_SUFFIX` 都在那个文件里，改词改那里，**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算是铁律：全程 ≤ 10 次工具调用。** 脚本静态化之前，每跑一轮要重写 200 行，实测 213 次调用 = 30 分钟撞 timeout。
- **产物文件名固定**（`scan.py` / `out.json` / `audit.log` / `report.md`）。**轮次号写进日志内容，不要写进文件名** —— 写 `audit10.log` 会让 `audit.log` 永远是旧的，下个会话找不到当前审计。
- **不要重写脚本。** 只有改过滤器时才 Edit `scan.py`；要临时验证某条过滤器，才另写 `output/ghradar/probe_*.py` 旁路。
- **核验宁可全量。幸存数 ≤ 上限时，一个都别漏。** 实证：`PER_TERM_CAP=25` 按 star 排序，只核了 76/234，报告级被低估 3.85×。
- **star 排序会切掉 ★0 长尾。** 在一个全是 ★0 的簇里（`jepa`），按 star 排序等于随机切。
- **star 与 commits 可能反相关。** 实证：`jepa` 全簇 ★0，但全轮冠亚军都在里面。**跟这一支只能按 commits 读。**
- **换词前先量两个口径：total_count + 重叠度。不能只看污染率。** `vla`→全称双赢（污染 22%→1.4%）；`jepa`→全称灾难（654→35）。**分界不是「缩写脏不脏」，是这个术语在生态里实际怎么被书写。**
- **仓库名常写合成词，搜索按 token 切分**（`smolvla`/`InfraVLA` 打不中 `vla`）—— **description 比 name 更可靠**。
- **缩写若留着，必须配 `NEG_BY_TERM`**（`jepa` 撞 jepang/jepara）。
- **`per_term == 0` 必须分四类。** 四类：查询失败 / 真零 / **全已见（饱和）** / 有新增。**「饱和」留着，「真零」才谈删词。**
- **窄窗会把稀有词系统性读成「真零」** —— 判词表死活必须跨 7/30/60 三个窗口量 total_count，别用单轮窄窗下结论。
- **共享脚手架 owner 黑名单抓不到**（同短名跨 8 owner、desc 逐字相同，每人只 1 个仓）。判据：同短名跨 ≥3 owner 且 desc 前 80 字符相同。
- **EXCL 要同时查仓库名和 description。**
- **star 地板是反向的。** 默认 `min:0`。
- **30 天提交高 ≠ 现在在写。** 必须同时看近 7 天 —— 实证 **59.7% 爆完即停**。
- **高提交数 ≠ 代码仓。** 看 `language` 字段与根目录形态。
- **`commits=100` 是 `per_page` 上限**，标 `≥100`。
- **限速要重试，不能放弃。429（限速）和 409（真空仓）必须分开。gh 掉线必须进审计。**
- **description 越像论文，越要查 commits。**
- **只匹配 `in:name,description`，不要 readme。**
- **脏词必须配 carrier**（`world model`）。
- **覆盖率必须报。** <50% 的绝对数不可引用。
- **`template` / `demo` / `sniper` = 练手仓库或农场。**
- **站点仓按后缀无条件丢**（`.github.io` / `-page` / `-site` / `-website` / `-homepage` / `-showcase`）—— 体量不是判据，304MB 的静态站照样是站。**同名仓**才需要「体量小 + 无 language」两个条件（`UniWAM/UniWAM` 是真代码仓，必须留）。
- **每条丢弃规则都要能被审计。**
- **农场只认黑名单。**
- **报「零命中」必须分开写四类。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天 / 7 天提交数。

## Config

读：
- `skills/github-radar/scan.py` 里的 `TERMS`
- `memory/github-seen.json` · `memory/github-farms.txt`（**黑名单，行内可带 `#` 注释**）

写（脚本自己写，模型不用管）：
- `output/ghradar/out.json` · `output/ghradar/audit.log` · `output/ghradar/report.md`
- `memory/github-seen.json`（全部幸存者，`dry-run` 不写）
- `memory/github-candidates.md`（只写报告级）
- 通知：只在报告级 > 0 且非 `dry-run` 时发，最多 `NOTIFY_TOP` 条

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/github-radar/scan.py "${var}"
```

脚本自己解析 var、扫描、过滤、核验、写全部产物、按需发通知。**审计全文打在 stdout**，不用再 `cat`。

### 2. 写日志

往 `memory/logs/${today}.md` 追加一节 `### github-radar（第 N 轮）`：口径 + 漏斗 + 四分类（**必须分开写**）+ 你自己的判据级发现。报告级为 0 就只写一行。

### 3. 输出

- 通知正文由脚本写进 `output/ghradar/report.md` 并发出去
- 只给仓库 + 一句话 + 链接 + star + 30d/7d，不做判断
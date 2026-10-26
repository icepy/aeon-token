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

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 30）；`min:N` 换 star 地板（**默认 0**）；`chk:N` 换核验门槛（默认 5）；`probe` 额外跑专名簇反查找漏掉的簇。**原样传给脚本，不要自己解析。**

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

**全在 `skills/github-radar/scan.py`。** `TERMS` / `NEG_BY_TERM` / `CARRIER_BY_TERM` / `EXCL` / `SITE_SUFFIX` / `CODE_SKELETON` 都在那个文件里，改词改那里，**不要在 SKILL.md 里再抄一份**。

## 铁律

- **预算是铁律：全程 ≤ 15 次工具调用。** 第十一轮 48 次、耗时 16 分钟（脚本只占 147 秒，其余全是模型往返）。旁路探测走 `probe`，别每轮现写脚本。
- **产物文件名固定**（`out.json` / `out.dry.json` / `audit.log` / `report.md` / `clusters.json`）。**轮次号写进日志内容，不要写进文件名。**
- **`output/ghradar/` 由脚本自己清，不用你手动删。** 每次开跑前它会把目录里不在上面五个名字内的文件删掉，并把这行打进审计（`🧹 清理 …`）。想跨轮保留某个文件，文件名以 `keep` 开头。
- **旁路脚本不进 `output/ghradar/`。** 要留档的判据写进 `memory/logs/${today}.md`；真需要临时脚本，放这个目录也行，下一轮会被自动删掉 —— 所以别指望它跨轮存在。
- **不要重写脚本。** 只有改过滤器时才 Edit `scan.py`。
- **核验宁可全量。幸存数 ≤ 上限时，一个都别漏。** 实证：`PER_TERM_CAP=25` 按 star 排序，只核了 76/234，报告级被低估 3.85×。
- **star 排序会切掉 ★0 长尾。** 实证第十一轮：幸存 70 个里 ★≥5 只有 1 个、全轮最高 ★7，报告级 35 里 34 个是 ★0。**只要机制词还在，star 就不该出现在排序或采样里。**
- **star 与 commits 可能反相关。** 跟这一支只能按 commits 读。
- **换词前先量两个口径：total_count + 重叠度。不能只看污染率。** `vla`→全称双赢；`jepa`→全称灾难（654→35）。**分界不是「缩写脏不脏」，是这个术语在生态里实际怎么被书写。**
- **仓库名常写合成词，搜索按 token 切分** —— **description 比 name 更可靠**。
- **缩写若留着，必须配 `NEG_BY_TERM`**。
- **`per_term == 0` 必须分四类。** 查询失败 / 真零 / **全已见（饱和）** / 有新增。**「饱和」留着，「真零」才谈删词。** 注意「饱和」是混的：`new_term` 只在全部过滤器跑完之后才自增，「被过滤丢光」和「真被 seen 吸收」会落进同一类 —— 脚本会把这两者分开打。
- **窄窗会把稀有词系统性读成「真零」** —— 判词表死活必须跨 7/30/60 三个窗口量 total_count。
- **窗口长度是「提前量 vs 覆盖率」的取舍，不是质量轴。** 第十一轮：30 天窗比 7 天窗多救回 5 个 7d≥5 的活仓；但两轮报的「新增」全部来自窗口算术，**0 个真漏检**，不能当增量引用。
- **同窗口连跑会读出「幸存 0」。** 非 `dry-run` 把幸存者写进 `seen` 之后，同窗口再跑必然 0 —— 那是算术，不是词表饱和，也不是故障。这时核验层和 `probe` 层**整段不会被执行**，所以「没报错」不等于「验过了」。
- **词表对新生专名是全盲的（结构性，与窗口无关）。** 实证：`SuperMimic` 55 仓簇，18 词只捞到 2 个（7 天窗、30 天窗各验证一次）。**修法是反向做**：拿报告级里 commit 最高的几个，用仓名 token 反查 —— 就是 `probe`。`probe` 的种子池是「报告级 → 幸存 → 丢弃堆最新」，所以幸存 0 时它照样能跑。
- **共享脚手架 owner 黑名单抓不到**。判据：同短名跨 ≥3 owner 且 desc 前 80 字符相同。
- **EXCL 要同时查仓库名和 description。**
- **star 地板是反向的。** 默认 `min:0`。
- **30 天提交高 ≠ 现在在写。** 必须同时看近 7 天 —— 实测跨窗稳定在 55–60% 爆完即停。
- **高提交数 ≠ 代码仓。** 看 `language` 字段与根目录形态。
- **`commits=100` 是 `per_page` 上限**，标 `≥100`。
- **限速要重试，不能放弃。429（限速）和 409（真空仓）必须分开。gh 掉线必须进审计。**
- **description 越像论文，越要查 commits。**
- **只匹配 `in:name,description`，不要 readme。**
- **脏词必须配 carrier**（`world model`）。**discard 量大 ≠ 误杀大**（第十一轮 carrier 丢 479 个，是最大单条规则，但没重放就不能算净增）。**carrier 只查 description、不查 topics，且允许词表全是机器人词** —— 所以「desc 一句话里没机器人词」的真代码仓会被整条丢掉（第十三轮实证：`latent-horizon/pytorch-world` 85 commits、`gimocimo/aero-adapt` 84 commits，都是活仓，都死在 carrier）。
- **覆盖率必须报。** <50% 的绝对数不可引用。
- **`template` / `demo` / `sniper` = 练手仓库或农场。**
- **站点仓按后缀无条件丢**（`.github.io` / `-page` / `-site` / `-website` / `-homepage` / `-showcase`）—— 体量不是判据。**同名仓**才需要「体量小 + 无 language」两个条件。
- **纯静态站还有第二种形态**：根目录 `index.html` + `.nojekyll` 且无任何代码骨架（`src`/`tests`/`pyproject.toml`/`package.json`/…）→ 页。第十/十一轮三次独立命中（含 39MB、115MB），已进代码。
- **每条丢弃规则都要能被审计。**
- **农场只认黑名单。**
- **报「零命中」必须分开写四类。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天 / 7 天提交数。

## Config

读：
- `skills/github-radar/scan.py` 里的 `TERMS`
- `memory/github-seen.json` · `memory/github-farms.txt`（**黑名单，行内可带 `#` 注释**）

写（脚本自己写，模型不用管）：
- `output/ghradar/out.json` · `audit.log` · `report.md`（`probe` 时另有 `clusters.json`）
- `output/ghradar/out.dry.json` —— `dry-run` 时快照写这里，**不覆盖 `out.json`**（否则一次 0 幸存就会把上一轮的真快照写成 `[]`）
- `memory/github-seen.json`（全部幸存者，`dry-run` 不写）
- `memory/github-candidates.md`（只写报告级，`dry-run` 不写）
- 通知：只在报告级 > 0 且非 `dry-run` 时发，最多 `NOTIFY_TOP` 条
- 清：开跑前删掉 `output/ghradar/` 里除上述五个名字外的文件（`keep*` 前缀除外），删了什么打进审计

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/github-radar/scan.py "${var}"
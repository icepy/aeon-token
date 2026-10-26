# Handoff —— 交接索引

> 新会话先读这一页，再按指针去读细节。**别读整个仓库。**

## 这个仓库是什么

`github.com/icepy/aeon-token` —— aeon 的公开 fork，当**客观数据传感器**用。
只出数据，不做判断；深度分析在 Venice 手做。输出语言：简体中文。

**2026-10-25 起主线 = 发现层**。DEUS / NOTE 的价格监控已停，
仓位细节归档在 `memory/MEMORY.md` 的「归档：DEUS / NOTE」节 —— **别再往主线上搬**。

## 当前状态（2026-10-26）

**发现层：**
- `arxiv-radar` ✅ 每天 07:30 UTC · 20 机制词 · 已修两轮 carrier 误杀 · **仍是 heredoc，待静态化**
- `github-radar` ⚠️ 手动 · 18 词 · **已优化完成**：工具调用 213→48、耗时 30m34s→11m（脚本仅 284s）
  - `scan.py` 已静态化（模型不再重写 200 行）· `pages` 根目录规则已固化 · `probe` 专名簇反查已上线
  - `seen` 已落盘 1891 条（此前从第六轮起就没更新，重复回捞已断）
  - ⚠️ 通道产出**高度集中在 `world model` 一个词**（65 幸存里 43 个来自它）—— 这是风险也是 SuperMimic 全盲的原因

**第四个信息源（不在 aeon 里）：** grok 的 `crypto-narrative-brief-3day`，周一/周四 09:00，
写 `memory/topics/narratives.md`。**目前是覆盖式，每三天丢一份 —— 待改 append。**
它带打分和操作建议，是四个源里唯一有判断的，比对时别拿它的结论当输入。

**已停（2026-10-25）：** `price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。
**仍在跑：** `defi-overview` · `heartbeat` · `memory-flush` · `aeon-update`（周一）· `register-skill`

**已排未启：** `narrative-convergence` —— 第四个 skill 写之前先读本页待办 5。

## 立即待办（按顺序）

1. **覆盖 `skills/github-radar/scan.py`**（gh 降级加 60s 冷却 + probe 改成先反查再排序）→ 跑 `dry-run days:30 probe` 验证：
   `gh 认证曾掉线` 不该再出现；probe 应把 `supermimic`（total=55、簇内 25 个 30d≥5、全不在幸存者里）排到专名候选最前
2. **`arxiv-radar` 同一套静态化** —— 它现在是 heredoc，比 Write 更容易被权限层拦。搬成 `skills/arxiv-radar/scan.py`，模型只调用
3. **`narratives.md` 改 append 攒历史**（grok 侧，不碰 aeon）—— 历史最贵，越早开始越好。同时定它的标签表是否固定（自由文本漂移会让比对永远对不上）
4. **`gecko-radar` 第三条通道** —— 先定它在阶梯上的位置，以及它和叙事（第四源）的先后
5. **四个源都有历史 + 都解析得出 `(键, 日期)` 之后**，再写第三个 skill 做比对。第一版只出一张表：
   `方向 | 各通道首次 | 滞后(天) | 覆盖状态`，不做判断
6. 悬着的小事：`SITE_SUFFIX` 要不要补 `-docs`

## 发现层的设计（一句话）

三条**平行**探针，同一批方向词，测同一条方向的不同成熟度：
论文（arxiv，~4 个月）→ 代码（github，~1–2 个月）→ 代币（gecko，未建）。
**同一个词在几条通道上依次点亮，那个次序才是信号。** 耦合在词表，不在结果。

**注意**：四个源**不是同一条阶梯上的四条腿**。前三源是原始探针（机制词、只出数据）；
narratives 是加工层（叙事标签、带判断）。而且 AI 线是 论文→代码，加密线是 叙事→代码 —— **方向相反**。

## 已知的坑（每条都付过代价）

- **arxiv**：只用 `ti:` · 写长短语 · 多词必须带引号 · 零命中不删词 · 看到 0 先看 `raw_term` 和收录日期
- **github**：star 地板反向 · 判真伪只看 commits（30d+7d）· 采样按簇不按 star · 缩写换全称前先量两口径 · `per_term==0` 要分四类（饱和≠查不到）· 窄窗会把稀有词读成假零
- **harness**：`--timeout 1800` **硬编码**在 `.github/workflows/aeon.yml` 的 `RH_ARGS`，没有 env / repo var 可调。
  **超时不算 provider 失败 → 永不降级**，且 `gateway: provider:` 显式指定 = 单候选。判据：`exit 124` + `not a provider failure`。
- **工具调用数是真正的成本**：213 次 = 30 分钟超时；脚本只占 284 秒。**省调用 = 省时间 = 省额度**（每次调用重读 ~53k 上下文）。
- **gh 并发太高会触发二级限流**：`gh api` 掉线后原代码整轮不恢复。已改成 60s 冷却自动重试 + 并发降到 6。
- **通用**：每条丢弃规则都要能被审计 · 「查询失败」和「真零」必须分开写 · 假零有三类 · **评估某条过滤器前必须把其余过滤器一起重放**（否则把复合结果记到单个规则头上）
- 细节全在 `memory/topics/lessons.md` 与 `memory/topics/github-radar.md`

## 工作方式约定（重要）

- **本地没有 `gh`** —— 给 GitHub 操作一律给**界面点击路径**，不给 `gh` 命令
- **`git add/commit/push` 本地可用**，可以给
- **改动一律给完整文件 + 在开头列出改了哪几处。** 不逐行改 —— 逐行找容易改错、也浪费时间
- **不修改框架层**（`scripts/` `bin/` `.github/` `apps/`）—— 新东西只加在 `skills/` 下
- 仓库公开；不提交仓位数据和钱包地址

## 文件地图

- `STRATEGY.md` —— 北极星与阈值
- `memory/MEMORY.md` —— 一行教训索引（8KB 预算）· 含 DEUS/NOTE 归档节
- `memory/decisions.md` —— 决策日志（防回滚，给 agent 读）
- `memory/fork-maintenance.md` —— 加 skill 的流程、触发链、PR 规则、踩坑史
- `memory/topics/` —— 各主题细节
- `skills/<name>/SKILL.md` —— 通道本体；静态脚本放同目录
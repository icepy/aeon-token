# Handoff —— 交接索引

> 新会话先读这一页，再按指针去读细节。**别读整个仓库。**

## 这个仓库是什么

`github.com/icepy/aeon-token` —— aeon 的公开 fork，当**客观数据传感器**用。
只出数据，不做判断；深度分析在 Venice 手做。输出语言：简体中文。

持仓：DEUS（XMAQUINA 机器人 DAO）· NOTE（Robinhood Chain）· PEARL。
北极星：把 DEUS 仓位拉回不追加现金的盈亏平衡。见 `STRATEGY.md`。

## 当前状态（2026-10-25）

**已上线的发现层通道：**
- `arxiv-radar` ✅ 每天 07:30 UTC · 20 机制词 · 已修两轮 carrier 误杀
- `github-radar` ✅ 手动跑为主 · 18 词 · 第八/九轮在打磨过滤器

**监控层：** price-alert · onchain-monitor · token-movers · defi-overview ·
unlock-monitor · heartbeat · memory-flush —— 全部在跑。

**维护层：** `register-skill` 自动化注册 · `aeon-update` 周一 04:00 UTC ·
`memory/decisions.md` 决策日志 · `memory/fork-maintenance.md` 流程手册。

**已排未启：** `narrative-convergence`（交叉验证层，见下）。

## 立即待办（按顺序）

1. **push 最新的 `skills/github-radar/SKILL.md`**（核验改全量 + 站点仓按后缀丢 + 审计加核验覆盖率）
2. **跑一次正式 `days:60`**（去掉 `dry-run`）—— 落 seen、发通知
3. **启用 `narrative-convergence`**，同时新建 `memory/topics/signal-categories.md`
   （要把 `discovery` 那一行加上，否则自建通道落 other，跨类别分拿不到）
4. 观察一周，看它报的「收敛」是不是真信号

## 发现层的设计（一句话）

三条**平行**探针，同一批方向词，测同一条方向的不同成熟度：
论文（arxiv，~4 个月）→ 代码（github，~1–2 个月）→ 代币（gecko，未建）。
**同一个词在几条通道上依次点亮，那个次序才是信号。** 耦合在词表，不在结果。

## 已知的坑（每条都付过代价）

- **arxiv**：只用 `ti:` · 写长短语 · 多词必须带引号 · 零命中不删词 · 看到 0 先看 `raw_term` 和收录日期
- **github**：star 地板反向 · 判真伪只看 commits（30d+7d）· 采样按簇不按 star · 缩写换全称前先量两口径 · `per_term==0` 要分四类（饱和≠查不到）
- **通用**：每条丢弃规则都要能被审计 · 「查询失败」和「真零」必须分开写 · 假零有三类
- 细节全在 `memory/topics/lessons.md` 与 `memory/topics/github-radar.md`

## 工作方式约定（重要）

- **本地没有 `gh`** —— 给 GitHub 操作一律给**界面点击路径**，不给 `gh` 命令
- **`git add/commit/push` 本地可用**，可以给
- **偏好整文件替换**，不要一行一行改
- **不修改框架层**（`scripts/` `bin/` `.github/` `apps/`）—— 新东西只加在 `skills/` 下
- 仓库公开；不提交仓位数据和钱包地址

## 文件地图

- `STRATEGY.md` —— 北极星与阈值
- `memory/MEMORY.md` —— 一行教训索引（8KB 预算）
- `memory/decisions.md` —— 决策日志（防回滚，给 agent 读）
- `memory/fork-maintenance.md` —— 加 skill 的流程、触发链、PR 规则、踩坑史
- `memory/topics/` —— 各主题细节
- `skills/<name>/SKILL.md` —— 通道本体
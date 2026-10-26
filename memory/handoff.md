# Handoff —— 交接索引

> 新会话先读这一页，再按指针去读细节。**别读整个仓库。**

## 这个仓库是什么

`github.com/icepy/aeon-token` —— aeon 的公开 fork，当**客观数据传感器**用。
只出数据，不做判断；深度分析在 Venice 手做。输出语言：简体中文。

**2026-10-25 起主线 = 发现层**（arxiv-radar / github-radar）。DEUS / NOTE 的价格监控已停，
仓位细节归档在 `memory/MEMORY.md` 的「归档：DEUS / NOTE」节 —— **别再往主线上搬**。
北极星仍是把 DEUS 拉回不追加现金的盈亏平衡，但日常只看价格、不跑监控。见 `STRATEGY.md`。

## 当前状态（2026-10-25）

**发现层（唯一主线）：**
- `arxiv-radar` ✅ 每天 07:30 UTC · 20 机制词 · 已修两轮 carrier 误杀
- `github-radar` ⚠️ 手动跑 · 18 词 · 第九轮完成过滤器硬化，**但 `days:60` 首次跑超时失败**
  - `SKILL.md` 三处修复（核验改全量 / 站点仓按后缀丢 / 审计加核验覆盖率）已推 main `bbd6e84`，`-showcase` 补丁 `228ff6f`
  - ⚠️ `dry-run days:60` 撞 harness 硬顶 1800s（`exit 124`）。归因见「已知的坑 · harness」

**已停（2026-10-25）：** `price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`
—— 价格自己每天看，额度全部让给发现层。**重开前先读 `memory/decisions.md`。**

**仍在跑：** `defi-overview` · `heartbeat` · `memory-flush` · `aeon-update`（周一 04:00 UTC）· `register-skill`

**已排未启：** `narrative-convergence`（交叉验证层，见下）。

## 立即待办（按顺序）

1. **github-radar 超时归因** —— 先跑一次**默认窗口**的 `dry-run`（`var` 只填 `dry-run`，不带 `days:N`）。
   过了 = 是 60 天的量；也超时 = 模型或脚本本身。
   **别连着瞎试**：`consecutive_failures` 已 2/3，再失败一次断路器会拦它 6 小时。
   同时 `aeon.yml` 把 `gateway: provider: hivemindos` 改成 `auto`（显式指定 = 单候选、无降级）。
2. **若归因是「量」** —— 改 `scan.py` 两处：核验阶段并发（8 路）+ 墙钟预算（超预算的标 `unverified`，
   audit 本来就会报「未核验」，不违反「核验宁可全量」）。都在 SKILL.md 内，不碰框架层。
3. **启用 `narrative-convergence`**，同时新建 `memory/topics/signal-categories.md`
   （要把 `discovery` 那一行加上，否则自建通道落 other，跨类别分拿不到）
4. 观察一周，看它报的「收敛」是不是真信号
5. 悬着的小事：`SITE_SUFFIX` 要不要补 `-docs`（第八轮只提过 `-showcase`，已补）；`gecko-radar` 第三条通道未建

## 发现层的设计（一句话）

三条**平行**探针，同一批方向词，测同一条方向的不同成熟度：
论文（arxiv，~4 个月）→ 代码（github，~1–2 个月）→ 代币（gecko，未建）。
**同一个词在几条通道上依次点亮，那个次序才是信号。** 耦合在词表，不在结果。

## 已知的坑（每条都付过代价）

- **arxiv**：只用 `ti:` · 写长短语 · 多词必须带引号 · 零命中不删词 · 看到 0 先看 `raw_term` 和收录日期
- **github**：star 地板反向 · 判真伪只看 commits（30d+7d）· 采样按簇不按 star · 缩写换全称前先量两口径 · `per_term==0` 要分四类（饱和≠查不到）
- **harness**：`--timeout 1800` **硬编码**在 `.github/workflows/aeon.yml` 的 `RH_ARGS`，没有 env / repo var 可调。
  **超时不算 provider 失败 → 永不降级**（`scripts/gateway-failover.sh` 的设计），且 `gateway: provider:` 显式指定 = 单候选。
  所以超时只能靠「让这一轮本身别超时」解决，不能指望兜底。判据：`exit 124` + `not a provider failure`。
  另：`gateway.provider: hivemindos` 会把 `model: claude-opus-5-5` 实际路由成 flash 模型，长工具循环里更慢。
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
- `memory/MEMORY.md` —— 一行教训索引（8KB 预算）· 含 DEUS/NOTE 归档节
- `memory/decisions.md` —— 决策日志（防回滚，给 agent 读）
- `memory/fork-maintenance.md` —— 加 skill 的流程、触发链、PR 规则、踩坑史
- `memory/topics/` —— 各主题细节
- `skills/<name>/SKILL.md` —— 通道本体
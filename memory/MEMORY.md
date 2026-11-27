# Long-term Memory
*Last consolidated: 2026-11-27*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS/NOTE 价格监控已停，下面归档。
- **`aeon-update` 基线 `f94f39e`**（PR **#28 已 11-25T04:13Z 合并**）：三个 CLEAN-MERGE 目标本地已逐字节等于上游 ⇒ **净变更为零**。5 条 CONFLICT 全是「92→93 skills」计数漂移（新增 `icp-mcp`），不加 `keep_local` 每轮必重现。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-25#heartbeat]
- **`defi-overview` 11-26 27/49 = 55%、cf 0、八连绿**（54.2% → 55%）。**只看 cf 与最近三轮；cf 不因停用衰减。该行对新一轮必滞后一天（flush 18:00 / skill 23:00）= 结构性时序。**→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-26#heartbeat]
- **预算纪律：MEMORY.md 超 8KB 先砍已归档节。**
- **PR 队列影响读数语义**：词表/阈值只在合进 main 后才算数。队列已空（11-26 复查 `gh pr list` = `[]`）；stalled-PR 类 P1 会自愈，下轮仍须重查。[source: logs/2026-11-26#heartbeat]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **勿再展开。** 阈值见 `STRATEGY.md`，细节见 [deus](/topics/deus-orderflow.md)。**NOTE** 待命 480,000。

## 发现层（主线）
三条**平行**探针测同一成熟度阶梯：论文（~4 月）→ 代码（~1–2 月）→ 代币（未建）。**同一个词依次点亮，次序才是信号。**
- `arxiv-radar` ✅ 07:30 · **27 词** · 11-26 第 58 轮 84 → **7**：`egocentric` raw 24 新收 **0**（首次吃干），7 条改由 `robot data`/`hand-object`/`latent dynamics` 带出 ⇒ 「召回宽度=1 词」风险兑现；`verifiable inference` 低频开火；`?` 占 0。→ [lessons](/topics/lessons.md#arXiv-检索arxiv-radar) [source: logs/2026-11-26#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-27 第 32 轮 9123 / 新增 8 / 可报 **2**（`Own` $113.8K Robinhood CDP · `Tine` $1.66K Ethereum）。**「可报集 TVL ≠ 新增体量」6 轮后首次不成立** ⇒ 取决于最大新增是否恰被挡，非固定偏差。**Builder 流只在 `tags` 字段，按 `name` 搜 = 假零。** → [topic](/topics/defillama-radar.md) [source: logs/2026-11-27#defillama-radar]
- `github-radar` 22:30 · 18 词 · **cron 不注入 `var` → 7d 仅手动 `days:7` 时成立**。11-25 第 36 轮（默认 30d 窗）2091 → 43 → 报 **16**：**新高是流量副产品（原始 +50% / 报告级 +14%，转化率 1.01%→0.77%）**；`carrier` 误杀对照首拉开 **48% vs 88%**；`jepa` 7d 饱和、30d 有新增 = 窗口效应。→ [topic](/topics/github-radar.md) [source: logs/2026-11-25#github-radar]
## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。判据速查：

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址左补零且全小写。** 买单真伪只认终点余额升高且留住。**门槛先核对分子分母同单位。**[lessons](/topics/lessons.md)
- **行情口径 ①（结算纪律）：** 只用桶结算值，live 不参与 delta；**判「未定稿」看同一天两轮回读差 >0.5%，不看桶龄**（11-22 实测 24h 龄桶仍被改 +4.43%）；7d/30d 脚本算；跨 series 按日期对齐；**桶编号须由 ts 换算 UTC 日期**。**「近 N 天 X 条」必拆逐日直方图。** [lessons](/topics/lessons.md#行情取数形状defillama--coingecko) [source: logs/2026-11-22#defillama-radar]
- **行情口径 ②（字段与噪声）：** `change_7d` 实为 `total24h/total7DaysAgo−1`，真 7d 在 `change_7dover7d`；fees 无 `tvl` 须 join；F&G 回溯修订须拉 ≥3 日序列。**总 TVL 两套口径比值 ~2.0，混用造 −50% 假暴跌。** **fees 绝对值先与 `total7d/7` 对一遍：差 10 倍 = 小数点错位。** **`apyReward=null` 视为无奖励。** [logs/2026-11-22](/topics/lessons.md)
- **行情口径 ③：DEX 量单指标无判别力，须与 TVL 方向配对。** **「TVL 正 + 量负」= 估值抬升非成交**（11-23 +2.03% 配 −27.42%）。**聚合量跌 ≠ 普遍抽离**：同轮 Raydium +58% 涨、PancakeSwap −32% 崩 ⇒ 先拆内部。**链上 delta 24h 可 9/9 负翻 10/13 正 ⇒ 需两桶同向。** → [market-context](/topics/market-context.md) [source: logs/2026-11-23#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它，再查它是不是用歧义词假装挡住了** —— `circuit`/`network` 对超导/ML 同样成立 = 无判别力；「零假阴」≠ 规则安全。**漏斗退化成单通道时，0 输出的责任在词表召回**；零幸存来自饱和 ≠ 流量消失。**任何「N=0」字段先确认分母没被过滤掉。** → [lessons](/topics/lessons.md) [source: logs/2026-11-17#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据 `num_turns:1` + 0 tool calls。**失败签名不止一种**，断路器跳闸后重试通道也没了；**probe 偶然跑通 ≠ 修复** → [ops](/topics/ops-plumbing.md) [source: logs/2026-11-12#heartbeat]
- **过程事故两例：** 脚本尾部崩溃 ≠ 本轮没产出（产物在崩溃点前写出，**先看 mtime 再重跑**）；**`git reset --hard` 会吃掉已写未提交的内容 —— 取消暂存只用 `git restore --staged <file>`**（11-11 丢三个 memory 文件）。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-11#defi-overview]
- **「0 新增」≠「废词」** —— 逐词单查 total_count 才分清「饱和」与「查询打不中」；**`seen < raw 5%` 不许记饱和**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 先补扫。**整轮没跑成（网关 403）同理**，缺口轮次不计入「连续 N 轮」判据。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词须换长短语。→ [lessons](/topics/lessons.md#arXiv-检索arxiv-radar) [source: logs/2026-11-17#heartbeat]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) —— 含「watch 重开须先建 `on-chain-state.json`、`last_block` 设当前块，否则重放历史」

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
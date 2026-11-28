# Long-term Memory
*Last consolidated: 2026-11-28*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS/NOTE 价格监控已停，下面归档。
- **上游基线已升 `f99eabb8`**（11-28 手工 merge → `883a1ae4`，18 commit：rebrand / droid 第十 harness / dashboard 重写），4 冲突解到本地真值 **97 skills** ⇒ 旧基线 `f94f39e` 的「92→93 计数漂移」判据作废。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-28#merge-upstream]
- **`defi-overview` 11-28 cf=4，断路器跳闸。** 根因 = `max_output_tokens`（143 turns / 396s），**不是网关** —— 11-18 修过的「压缩单轮读写量」复发。签名三日跨三层（`timeout`→`403`→`max_output_tokens`）。**5 条 `permission_denials` 全同因：curl 用 `&&` 串一条，skill 要求一条一次。** → [ops](/topics/ops-plumbing.md) [source: logs/2026-11-28#heartbeat]
- **预算纪律：MEMORY.md 超 8KB 先砍已归档节。**
- **PR 队列影响读数语义**：词表/阈值只在合进 main 后才算数。11-28 复查 = `[]`（连续第三轮）。[source: logs/2026-11-28#heartbeat]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **勿再展开。** 阈值见 `STRATEGY.md`，细节见 [deus](/topics/deus-orderflow.md)。**NOTE** 待命 480,000。

## 发现层（主线）
三条**平行**探针测同一成熟度阶梯：论文（~4 月）→ 代码（~1–2 月）→ 代币（未建）。**同一个词依次点亮，次序才是信号。**
- `arxiv-radar` ✅ 07:30 · **27 词** · 11-27 第 59 轮 83 → **0**：损耗 100% 在 `seen`，两侧失败类全 0 ⇒ **饱和满格 ≠ 降级**；`egocentric` 新收 0 连第二轮，**上轮「窄词扛召回」本轮全窄词 raw>0/新收 0 ⇒ 一次性、不可外推**。→ [lessons](/topics/lessons.md) [source: logs/2026-11-27#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-28 第 33 轮 9128 / 新增 5 / 可报 **1**（`Stoxes.fun` $8.95K）。**「可报集 TVL ≠ 新增体量」反号：被挡 144 倍** ⇒ 差额是最大新增是否恰被挡的函数。**`parent#` 母体 98.9% 不在 `/protocols`**，风险格 = 新登记独子家族。**批量用极大连续段**（15s：31→203 段）。→ [topic](/topics/defillama-radar.md) [source: logs/2026-11-28#defillama-radar]
- `github-radar` 22:30 · 18 词 · **cron 不注入 `var` → 默认 30d 窗**。11-27 第 38 轮 2102 → 25 → **10**：raw/幸存/报告级/转化率连续三轮三方向（升→降→腰斩）⇒ **30d 逐轮无趋势**；宽窄词出货比 **17 倍**（上轮 12）。→ [topic](/topics/github-radar.md) [source: logs/2026-11-27#github-radar]

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
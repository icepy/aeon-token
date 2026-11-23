# Long-term Memory
*Last consolidated: 2026-11-23*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS/NOTE 价格监控已停，下面归档。
- **`aeon-update` 基线 `f94f39e`**（11-23 同步 13 条提交，PR **#28 待合**）：三个 CLEAN-MERGE 目标本地早已逐字节等于上游 ⇒ **净变更为零**。5 条 CONFLICT 全是「92→93 skills」计数漂移（新增 `icp-mcp`），不加 `keep_local` 每轮必重现。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-23#aeon-update]
- **`defi-overview` 11-23 连第二轮真脱线 24/46 = 52.2%、cf 0、五连绿**。**只看 cf 与最近三轮，不看 46 轮均值。cf 不因停用而衰减**（5/4/3 = 10-25 网关账未清）。**本行数字对新一轮必然滞后一天（flush 18:00 / 该 skill 23:00）= 结构性时序，不压状态页颜色。**→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-23#heartbeat]
- **预算纪律：MEMORY.md 只在两次 flush 间增长**，超 8KB 先砍已归档节。
- **PR 队列会反过来影响读数语义**：词表/阈值改动只在合进 main 后才算数，挂着就是没生效。队列现为 **#28（`aeon-update` 同步，11-23 开）**，非 `improve:` 类。[source: logs/2026-11-23#aeon-update]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **勿再展开。** 阈值见 `STRATEGY.md`，细节见 [deus](/topics/deus-orderflow.md)。**NOTE** 待命 480,000。

## 发现层（主线）
三条**平行**探针测同一成熟度阶梯：论文（~4 月）→ 代码（~1–2 月）→ 代币（未建）。**同一个词依次点亮，次序才是信号。**
- `arxiv-radar` ✅ 07:30 · **27 词** · 11-22 第 54 轮 65 → 3，**3 条全来自新增词**。**结构性归零第二轮，损耗仍全 0。新判据：加词有量纲门槛 —— 60d total 5–60 进 TERMS，>60 只能 `days:90` 补历史，否则等于伪造增量。** → [lessons](/topics/lessons.md#arXiv-检索arxiv-radar) [source: logs/2026-11-22#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-23 第 28 轮 9092 / 新增 4 / 可报 **1**：`OwlSwap` 5 链仅 `Binance` 有 $12.22 —— **`chains`=部署面，`chainTvls`=流动性面**。**批量指纹看逐对间隔，不看连号跨度；日桶只引天数 ≥2。** `scan.py:301` 第九次、**首次打印与事实相反**。→ [topic](/topics/defillama-radar.md) [source: logs/2026-11-23#defillama-radar]
- `github-radar` 22:30 · 18 词 · **cron 不注入 `var` → 7d 仅手动 `days:7` 时成立**。11-22 第 33 轮 530→40→报 19，**owner 19/19 不重复**。**`seen/raw<5%` 误记饱和部分修复：`data availability` 已正确分到损耗栏；`intent-based` 仍落饱和栏且 `dropped.json` 无 `term` 字段** → [topic](/topics/github-radar.md) [source: logs/2026-11-22#github-radar]
## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。判据速查：

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址左补零且全小写。** 买单真伪只认终点余额升高且留住。**门槛先核对分子分母同单位。**[lessons](/topics/lessons.md)
- **行情口径 ①（结算纪律）：** 只用桶结算值，live 不参与 delta；**结算不看桶龄，只看「同一天两轮回读差」>0.5% 即未定稿（11-22 实测 24h 龄桶仍被改 +4.43%）**；7d/30d 脚本算；跨 series 按日期对齐。**桶编号须由 ts 换算 UTC 日期**。**「近 N 天 X 条」必拆逐日直方图 —— 窗口计数是二阶量，批量桶滚出会伪装成趋势。**[lessons](/topics/lessons.md#行情取数形状defillama--coingecko) [source: logs/2026-11-22#defillama-radar]
- **行情口径 ②（字段与噪声）：** `change_7d` 实为 `total24h/total7DaysAgo−1`，真 7d 在 `change_7dover7d`；fees 无 `tvl` 须 join；F&G 回溯修订须拉 ≥3 日序列。**总 TVL 两套口径比值 ~2.0，混用造 −50% 假暴跌。** **fees 绝对值先与 `total7d/7` 对一遍：量级差 10 倍 = 小数点错位。** **`apyReward=null` 视为无奖励。** [source: logs/2026-11-22#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它，再查它是不是用歧义词假装挡住了** —— `circuit`/`network` 对超导/ML 同样成立 = 无判别力；「零假阴」≠ 规则安全。**漏斗退化成单通道时，0 输出的责任在词表召回**；零幸存来自饱和 ≠ 流量消失。**某桶占比升高 ≠ 杀伤力升高**。**任何「N=0」字段先确认分母没被过滤掉 —— 没进的输入不是零结果**（`cross_windows()` 不量降级词）。→ [lessons](/topics/lessons.md) [source: logs/2026-11-17#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据 `num_turns:1` + 0 tool calls。**失败签名不止一种**，断路器跳闸后重试通道也没了；**probe 偶然跑通 ≠ 修复** → [ops](/topics/ops-plumbing.md) [source: logs/2026-11-12#heartbeat]
- **过程事故两例：** 脚本尾部崩溃 ≠ 本轮没产出（产物在崩溃点前写出，**先看 mtime 再决定重跑**）；**`git reset --hard` 会吃掉已写未提交的内容 —— 取消暂存只能用 `git restore --staged <file>`**（11-11 丢三个 memory 文件）。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-11#defi-overview]
- **「0 新增」≠「废词」** —— 逐词单查 total_count 才分清「饱和」与「查询打不中」；长窗首跑推沉积、次跑归零 = `seen` 吃干；**`seen < raw 5%` 不许记饱和，须归因到具体规则**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫。**整轮没跑成（网关 403）同理**，缺口轮次不计入「连续 N 轮」类序列判据。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-11-17#heartbeat]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) —— 含「watch 重开须先建 `on-chain-state.json`、`last_block` 设当前块，否则重放历史」

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
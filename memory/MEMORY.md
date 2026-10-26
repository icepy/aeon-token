# Long-term Memory
*Last consolidated: 2026-10-25*

## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `memory/cron-state.json` 的 `last_dispatch` 和 `logs/`。`scheduler.yml` 用精确时隙债务模型（`cron-due.sh` + `CATCHUP_HOURS=12`）。
- **2026-10-25 起主线 = 发现层。** DEUS / NOTE 的价格监控已停（价格自己每天看），下面归档。

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **归档，勿再展开。** 只保留这一层，盘口细节留在 `memory/topics/`，别再往 MEMORY.md 里搬。

- **DEUS** `0x940A319B75861014A220D9c6c144d108552B089B`（base）· 出口 $0.041，**需提前 5 天 unstake** · `0xbb0f7533` 持 xDEUS #1396 至今未烧 → 那个 5 天 clock 从未启动。
- **NOTE** 待命 480,000 ≈ $20,400，三钱包 nonce 0 / ETH 0；**扳机 = 第一笔 ETH 入账**。owner 自持 630,000。
- 停用时的最后读数：NOTE 线性派发 ~40,000/天（schedule #25/#26/#27）；DEUS 24h 净通缩 −12,373.69，连续五轮同数 = 通缩走平。
- 细节 → [deus-escrow](/topics/deus-escrow.md) · [deus-orderflow](/topics/deus-orderflow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- 已停 skill：`price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。**重开前先读 `memory/decisions.md`。**

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一条方向的不同成熟度：论文（arxiv，~4 个月）→ 代码（github，~1–2 个月）→ 代币（gecko，未建）。**同一个词在几条通道上依次点亮，那个次序才是信号。** 耦合在词表，不在结果。
- `arxiv-radar` ✅ 每天 07:30 UTC · 24 机制词 · 第六轮（60d）**加密侧首次点亮**：`ti:"consensus" AND cat:cs.DC` 单词产出 13/13，机器人侧首次归零 —— 是补词的算术结果，**别读成方向升温**；该词仍未量两口径。`github-radar` 手动跑 · 18 词 · 第十六轮。
- **github-radar 第十七轮判据（2026-10-26）**：**carrier 误杀率首次有同口径对照组 → 50% vs 50%，无差异，不放宽**（丢弃侧 74/149 存活 · 幸存者对照 12/24），第十六轮「误杀率偏高」的 12 样本粗估作废。**新回归：自适应开窗（17 整窗 + 1 拆窗，`WIN_SPLIT_TOTAL=1000`）让 `sim2real` 52.7% / `restaking` 83.3% 首次跌破 95%，但手工复量 `sim2real` 两页并集正好 163 = total，不是 GitHub 封顶，差额来自整窗 `total_count` 与实际 `items` 不符。** 单样本先不改代码。probe 第三判据（`thematic`）首轮全额生效，`uniview`/`senku`/`pouw`/`eidolon`/`physguard` 全被挡下，0 个真簇。
- **github-radar 第十六轮判据（2026-10-26）**：`dropped.json` 上线，carrier/short_desc 首次全量落仓名 —— 「每条丢弃规则可审计」补齐。**carrier 丢的 886 个里 190 个（21.4%）仓名自带 `world-model`、177 owner，抽样 12 个有 9 个近 7 天在推** → carrier 在「活着且明确叫世界模型」的仓上误杀率高，但**别据此放宽，先按 owner 去重全量核 7d 再对照**。同窗口 dry-run 复跑 = 原样重放（4004/49/10，与上轮逐项相同），**不含新信号，勿当增量引用**。
- **probe 判据再退一步（第三修正）：`total` 小、`cohesive` 都不充分，还需「主题词落在我们词表语义内」。** 本轮 3 个 cohesive 簇全假：`senku` 主题词只有 `with`×11（**连接词不在 `STOPWORDS`**）、`uniview` 是海康大华 NVR、`pouw` 撞荷兰语「货运」。→ 两处可修：`STOPWORDS` 补高频虚词、probe 加第三判据。第十五轮的 `PhysGuard` 悬念已关：老仓 `ZhouChaunge` pushed 2026-05-05 停摆，**非占名**。
- 前轮判据：**第十五轮翻页修好，幸存 4→49（12.3×）**，页数改 `min(10, ceil(total/100))`，60 天窗现优于 30 天窗，carrier 改 `desc ∪ topics`。probe 历史种子池只取最近 200 条（`PROBE_HIST_CAP`），candidates 已 335 行 → 老仓反复当种子。

- **github-radar 第十二轮判据**：pages 根规则已进 scan.py 生效，一次清掉 5 个脏报告级（7.1%）；409 空仓仍触发全局认证降级（第五轮复现至第十四轮，代码未修）。
- 早轮判据全文见 [github-radar](/topics/github-radar.md)：第十一轮换窗口 = 制造伪「新增」（44 个里 0 个真漏检）；第十轮 7 天窗把稀有词读成假零（判死活须量 7/30/60 三窗）；第九轮 `PER_TERM_CAP=25` 抽样致报告级 20→77（3.85×），**核验永不按 star 分配**；`jepa` ★0 但 commit 密度最高、star 与 commits 反相关；`vla`→全称双赢 · `jepa` 留缩写；共享脚手架黑名单抓不到。


## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。这里只留判据速查。

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0，像清仓**）· **API `h1=null` 当成 0**。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **Solidly Swap 字序 `(a0In, a1In, a0Out, a1Out)`**，按 UniV2 解会把卖读成买 → 用储备差对照符号。**x·y=k：`D>0` 才是净买。**
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d 全 0；单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **`eth_getCode`=`0x` 才是 EOA；`0xef0100…` 是 EIP-7702。** 地址左补零且全小写。**view revert 先怀疑 selector。**
- **门槛数学先核对分子分母同单位**（曾把 DEUS 数量除以美元金额，424 倍 vs 真值 8.2 倍）；**24h 涨跌幅别用 `ohlcv_list[0]`**。
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。
- **有 seen 基线后「0 新增」≠「废词」** —— 逐词单查 total_count 才分得清「窗口饱和」与「查询打不中」。

## Reference
- [github-radar](/topics/github-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) —— WAM 提法 60 天 **99 仓 / 94 owner**；star≠活跃度（★1107/11 提交 vs ★48/10 vs ★199/2）。
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md) · [market-context](/topics/market-context.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md)

## 归档：取数 / watch / 预警框架
- **链上取数**：Base 直打 `base.gateway.tenderly.co`（`eth_getLogs` 限 1000 块）；RH 4663 免 key、24k 块窗口。见 [base-rpc-access](/topics/base-rpc-access.md)。
- **watch（`memory/on-chain-watches.yml`，5 个，已停）**：DEUS escrow · xDEUS · NOTE timelock · NOTE owner EOA · NOTE vesting `0xfdd9`。**重开必须在 `on-chain-state.json` 建条目并把 `last_block` 设为当前块**，否则重放历史。
- **预警框架**：完整框架见 `memory/alert-framework.md`。用相对量，不用绝对美元阈值。优先级：解锁 > 流动性 > 价格结构 > 筹码 > 协议事件。
- **DeFiLlama `/v2/chains` 无 `change_1d`**，用 `/v2/historicalChainTvl/{chain}` 自算；**CoinGecko `/global` 的 24h mcap 不可信**，用 `/coins/markets` 加权重算。

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
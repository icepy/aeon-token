# Long-term Memory
*Last consolidated: 2026-10-28*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `memory/cron-state.json` 的 `last_dispatch` 和 `logs/`。`scheduler.yml` 用精确时隙债务模型（`cron-due.sh` + `CATCHUP_HOURS=12`）。
- **2026-10-25 起主线 = 发现层。** DEUS / NOTE 的价格监控已停（价格自己每天看），下面归档。
- **`aeon-update` 上游基线已锚定**（2026-10-26 首跑）：`aeonfun/aeon` HEAD `6eddd85`，与本地 `main` 实测 `ahead=0`（界面 `behind=603` 全是本仓自动化提交）。状态存 `memory/topics/aeon-update-state.json`。[source: logs/2026-10-26#aeon-update]

## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **归档，勿再展开。** 只保留这一层，盘口细节留在 `memory/topics/`，别再往 MEMORY.md 里搬。

- **DEUS** `0x940A319B75861014A220D9c6c144d108552B089B`（base）· 出口 $0.041，**需提前 5 天 unstake** · `0xbb0f7533` 持 xDEUS #1396 至今未烧 → 那个 5 天 clock 从未启动。
- **NOTE** 待命 480,000 ≈ $20,400，三钱包 nonce 0 / ETH 0；**扳机 = 第一笔 ETH 入账**。owner 自持 630,000。
- 停用时的最后读数：NOTE 线性派发 ~40,000/天（schedule #25/#26/#27）；DEUS 24h 净通缩 −12,373.69，连续五轮同数 = 通缩走平。
- 细节 → [deus-escrow](/topics/deus-escrow.md) · [deus-orderflow](/topics/deus-orderflow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- 已停 skill：`price-alert` · `token-movers` · `onchain-monitor` · `unlock-monitor`。**重开前先读 `memory/decisions.md`。**

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一方向的不同成熟度：论文（arxiv，~4 个月）→ 代码（github，~1–2 个月）→ 代币（gecko，未建）。**同一个词在几条通道上依次点亮，那个次序才是信号。** 耦合在词表，不在结果。
- `arxiv-radar` ✅ 每天 07:30 UTC · **26 词 · vM** · 10-28（30d）原始 98 / 幸存 4。**`第一视角感知` 首次被真实流量填上**（`egocentric` 25/3，17 个饱和词里唯一多头）；`hand-object` 7/1 补上 `灵巧操作` 首条实证；14 加密词全零（跨窗有命中，连两轮「窗口太短」）。开跑前遇 **arXiv IP 级 429**（首次 `ARXIV_RADAR_DEGRADED`），静默冷却 12 分钟恢复。待办：`consensus` 同形三轮 → 加 `多智能体验证` 标签。[source: logs/2026-10-28#arxiv-radar（第二十八轮）]
- `github-radar` cron 07:45 UTC · 18 词 · gh-v3。10-27 连跑五轮：7d 正式原始 462→幸存 7→报告级 2；90d 正式 5404→629→54。**日跑回 7 天窗，90d 只在加词/补历史时用** —— 90d 跟在 7d 后跑，增量全被 `seen` 吃干（第二次拿到算术证据）。star 第 10/11 次失效（报告级 ~70% 是 ★0）。[source: logs/2026-10-27#github-radar（第二十轮）]


## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。这里只留判据速查。

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0，像清仓**）· **API `h1=null` 当成 0**。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **Solidly Swap 字序 `(a0In, a1In, a0Out, a1Out)`**，按 UniV2 解会把卖读成买 → 用储备差对照符号。**x·y=k：`D>0` 才是净买。**
- **买单真伪只认一条：终点地址余额升高且留住。** 新钱要 −1h/−6h/−24h/−7d/−30d 全 0；单池「N 买 / 0 卖」常是同秒双池套利的一半。
- **`eth_getCode`=`0x` 才是 EOA；`0xef0100…` 是 EIP-7702。** 地址左补零且全小写。**view revert 先怀疑 selector。**
- **门槛数学先核对分子分母同单位**（曾把 DEUS 数量除以美元金额，424 倍 vs 真值 8.2 倍）；**24h 涨跌幅别用 `ohlcv_list[0]`**。
- **跨 series 做 diff 必须先按日期对齐**（各取尾部 = 两个不同日期的差；判别式：per-chain delta 总和必须等于 aggregate）；**`/overview/dexs` 的 `change_1d` 会和自家 `totalDataChart` 打架时一律信后者**；**单腿读数恰为 0 → 快照缺口不是流出，几小时后会自己恢复**（OKX −40% 实例，10-27）。
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据：`num_turns:1` + 0 tool calls + `api_error_status`。
- **脚本尾部崩溃 ≠ 本轮没产出** —— 产物写在崩溃点之前时，stdout 像「跑挂了」而 `out.*.json` 其实是新的；**先看产物 mtime 再决定重跑**（`scan.py:910` 元组下标事故，10-27）。
- **有 seen 基线后「0 新增」≠「废词」** —— 逐词单查 total_count 才分得清「窗口饱和」与「查询打不中」。**换长窗首跑会一次性推出「沉积层」、次跑即归零，那是 `seen` 吃干不是查询坏了。**
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫（60d 轮 16/24 死于 429），别下结论。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-10-26#arxiv-radar（60d 第四/七轮）]

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
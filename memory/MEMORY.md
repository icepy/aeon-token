# Long-term Memory
*Last consolidated: 2026-11-13*
## About This Repo
- GitHub Actions 上的自主 agent。**外部时钟** = Cloudflare Worker `aeon-cron`；GitHub fork 的 `schedule` 基本不投递。
- `enabled: true` ≠ 跑过 —— 看 `cron-state.json` 的 `last_dispatch`。补跑让整批技能同秒触发 → **「几点跑」≠ cron 时间**；**frontmatter 的 `var:` 不注入**；`arxvi-radar` 孤儿待清。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-02#heartbeat]
- **2026-10-25 起主线 = 发现层。** DEUS/NOTE 价格监控已停，下面归档。
- **`aeon-update` 基线 `2ff25a3`**：PR #24 已关未合，内容由 catalog commit 直落 main（ICP 三件套、catalog 96、lockfile 99）。**待决策：上游 `aeon.yml` 5 条新技能未抄。** [source: logs/2026-11-09#aeon-update]
- **待盯（唯一 OPERATOR 决策）：`defi-overview` 成功率 0.56，cron 仍卡 `0 23`（403 窗），再连败即破 chronic 线。** WebSearch 连 5 轮不可用 → `narrative-brief` 的 `unverifiable_claim` 本仓不可修。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-13#heartbeat]
- **预算纪律：MEMORY.md 只在两次 flush 间增长**，超 8KB 先砍已归档节。
## 归档：DEUS / NOTE（已停监控 2026-10-25）
> **勿再展开。** 阈值见 `STRATEGY.md`，细节见 [deus](/topics/deus-orderflow.md)。**NOTE** 待命 480,000，扳机 = 首笔 ETH。

## 发现层（主线）
三条**平行**探针，同一批方向词，测同一成熟度阶梯：论文（~4 个月）→ 代码（~1–2 个月）→ 代币（未建）。**同一个词依次点亮，那个次序才是信号。**
- `arxiv-radar` ✅ 07:30 · 26 词 · 11-12 第 44 轮 **75 → 0**（上轮 83→4），两侧失败类全 0 = 读数干净。12 个零命中词里 **10 个跨窗有命中 → 窗口太短不许删**。14 词仍未配 carrier 表。→ [source: logs/2026-11-12#arxiv-radar]
- `defillama-radar` ✅ `dl-v1` · 11-14 第 19 轮 9028 / 新增 2 / **可报 0**（全过滤）。**空 `chains` 1621 条 ⟺ `module=dummy.js`，`chains=[]` ⇒ `tvl` 缺失（反向不成立，850 条非空链无 TVL）** → 空链旁路捞回的全是「无 TVL 适配器」条目。加链边际四轮 $514→$2.6K→$48.5K→**$0**，不加。**任何 id 缺席都不是永久空洞证据**（`9382` 连缺四轮）。**`chains` 是声明、`chainTvls` 才是量**。→ [topic](/topics/defillama-radar.md) [source: logs/2026-11-14#defillama-radar]
- `github-radar` 22:30 · 18 词 · gh-v3。**cron 不注入 `var` → 7d 仅手动 `days:7` 时成立**。11-12 第 25 轮 420/33/12：`30天=`≡`7天=` **12/12 第六轮**（定死为仓龄）· 加密侧**第十连轮** 0（`mev` 缩写仍未量）· 入口换代到 `robot manipulation`。→ [topic](/topics/github-radar.md) [source: logs/2026-11-12#github-radar]


## Lessons Learned
> 全文 + 触发场景见 [lessons](/topics/lessons.md)。判据速查：

- **假零七件套：** RPC 429 返空 · `mainnet.base.org` 整批 revert · topic0 只给 4 字节 · RH UA 403 · `-32602` 被 `||[]` 兜空 · 地址靠记忆拼（**12 位前缀补零静默返 0**）· **API `h1=null` 当成 0**。
- **假零八：CDN 快照让 id 差集恒为 0**（10-28）—— 差集为空先断言 `cf-cache-status != HIT` 或加 `?_cb=` 复取。**反向也有坑：id 集合相同 ≠ 字段值最新**，`parentProtocol` 这类补录字段会在两份快照间翻转（11-03）。
- **`eth_getLogs` 判别力测试：** 真 topic0 必回真日志、**故意错 1 字符必回 0**。不可区分 = 端点坏。公共 RPC 硬限 1000 块，长窗 999 分片。
- **链上速查（DEUS 归档后仍通用）：** Solidly Swap 字序 `(a0In,a1In,a0Out,a1Out)`，按 UniV2 解会读反 → 用储备差对照符号。**`eth_getCode`=`0x` 才 EOA，`0xef0100…` 是 7702；地址左补零且全小写。** 买单真伪只认终点余额升高且留住。**门槛先核对分子分母同单位。**[lessons](/topics/lessons.md)
- **行情口径 ①（结算纪律）：** 只用桶结算值，live 不参与 delta；**当日桶隔日复查才可当历史引用**（11-07 下修 −17.1%）；7d/30d 脚本算；跨 series 按日期对齐（per-chain 总和 = aggregate）。**桶编号须由 ts 换算 UTC 日期**，「倒数第 N 个」差一位会把结论翻反（11-11 实测）。[lessons](/topics/lessons.md#行情取数形状defillama--coingecko) [source: logs/2026-11-11#defi-overview]
- **行情口径 ②（字段与噪声）：** `change_7d` 实为 `total24h/total7DaysAgo−1`，真 7d 在 `change_7dover7d`；**`/overview/fees` 的 `protocols[]` 无 `tvl`，须 join `/protocols`**；星期效应先归一；fees 剔尖峰后按日均比；|Δ|>5% 当日 F&G 作废；**「缩量」报同星中位**；**F&G 会回溯修订**须拉 ≥3 日序列。[lessons](/topics/lessons.md) [source: logs/2026-11-13#defi-overview]
- **聚合字段口诀：先说清它量的是什么，再决定信不信。** `/protocols` 的 `change_1d` = 当日 00:00 桶内值，不是今昨差；`/v2/chains` 已删 `change_1d`/`change_7d` → 旧写法静默拿缺省值，链涨跌只能走 `/v2/historicalChainTvl/{chain}` 自算。**成因查 `hallmarks`**。[source: logs/2026-11-05#defi-overview]
- **某过滤器长期「0 丢弃」先查有多少输入真经过它，再查它是不是用歧义词假装挡住了** —— `arxiv-radar` carrier 连九轮空转（14 词没配表），第 37 轮又证明 `circuit`/`network` 对超导/ML 同样成立 = 无判别力。「零假阴」≠ 规则安全。**某桶占比升高 ≠ 该桶杀伤力升高**。[source: logs/2026-11-05#arxiv-radar]
- **漏斗退化成单通道时，0 输出的责任在词表召回，不在过滤器** —— 过滤层已无调节空间；零幸存来自饱和 ≠ 任一侧流量消失。[source: logs/2026-10-31#arxiv-radar]
- **「owner 转账 = 砸盘」是错的默认假设** —— 先看 `tx.to` 是不是自家合约。**网关错误会被误记成 skill 回归** —— 判据 `num_turns:1` + 0 tool calls。**失败签名不止一种**（403 配额窗口 / `max_output_tokens`），且断路器跳闸后重试通道也没了；**probe 偶然跑通 ≠ 修复** → [ops](/topics/ops-plumbing.md) [source: logs/2026-11-12#heartbeat]
- **过程事故两例：** 脚本尾部崩溃 ≠ 本轮没产出（产物在崩溃点前写出，**先看 mtime 再决定重跑**）；**`git reset --hard` 会吃掉已写未提交的内容 —— 取消暂存只能用 `git restore --staged <file>`**（11-11 因此丢三个 memory 文件，靠 `.tmp` 缓存重建）。→ [ops](/topics/ops-plumbing.md) [source: logs/2026-11-11#defi-overview]
- **「0 新增」≠「废词」** —— 逐词单查 total_count 才分清「饱和」与「查询打不中」；长窗首跑推沉积、次跑归零 = `seen` 吃干；**`seen < raw 5%` 不许记饱和，须归因到具体规则**。[source: logs/2026-10-29#github-radar]
- **查询失败会伪装成「零命中」** —— 有 `failed_t` 就先补扫，别下结论。**词干化污染：`staking` 精度 11%（撞 `stakes`）**，单词必须换长短语。详见 [lessons](/topics/lessons.md#arXiv-检索arxiv-radar)。[source: logs/2026-10-26#arxiv-radar]

## Reference
- [github-radar](/topics/github-radar.md) · [defillama-radar](/topics/defillama-radar.md) · [lessons](/topics/lessons.md) · [world-action-models](/topics/world-action-models.md) · [market-context](/topics/market-context.md)
- 归档：[deus-orderflow](/topics/deus-orderflow.md) · [deus-escrow](/topics/deus-escrow.md) · [deus-buyers](/topics/deus-buyers.md) · [deus-events](/topics/deus-events.md) · [note-systems](/topics/tokens/note-systems.md)
- [base-rpc-access](/topics/base-rpc-access.md) · [ops-plumbing](/topics/ops-plumbing.md) —— 含「watch 重开须先建 `on-chain-state.json`、`last_block` 设当前块，否则重放历史」

## 输出语言
**一律简体中文。** 所有 notify、报告、日志正文都用中文写。代币名、合约地址、协议名、代码、命令保留原文，不翻译。
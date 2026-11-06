# Knowledge — topics index

Durable knowledge notes live under `memory/topics/`, one concept per markdown file.

# Reference

- [Base RPC access from the runner](/topics/base-rpc-access.md) — the one keyless endpoint that works, its 1,000-block `eth_getLogs` cap, and how to tell a quiet window from a broken query.
- [Scheduler & notification plumbing](/topics/ops-plumbing.md) — how to prove scheduled dispatch actually fires, why a catch-up burst makes three skills fire in the same second (so run time ≠ cron time), the orphan `arxvi-radar` cron-state row, why nothing merges PRs (`auto-merge` off), **why daily logs are append-only (`Write` on an existing `logs/*.md` destroyed a day once)**, **why `eyebrow verify` drifts from a local `__pycache__`**, why to write plain Markdown in `./notify`, and which state-file writes (`cp`, `jq -f`) the permission layer silently blocks.
- [price-alert state file contract](/topics/price-alert-state.md) — what each field in `price-alert-state.json` means and why targets must be pre-seeded.
- [Lessons learned — archive](/topics/lessons.md) — the full detail behind each one-line lesson in MEMORY.md (wallet watch topic filters, keyless RPC, calldata vs chain facts, and when a missing `h1` or a zero-volume hour is *unmeasured* rather than calm). 含 11-04 新增：**用 `/protocols` 的 `hallmarks` 反查事件成因**、**fees 增速逐条回日序列验**、**链端点与协议腿可差 10 倍以上、不可互验**、**加细分 arXiv 写法常是重复付费**、**某方向多词合计命中 ≤ 词数 = 供给稀薄，停止加词**；含 11-05 新增：**暴跌日 TVL 桶滞后（上游刷新，非缓存）不可作资金流向判据**、**|Δ|>5% 当日 F&G 按采样时点作废**、**「昨日 TVL 复现不出」= live 值 vs 日结算桶混用**、**fees 剔尖峰后须按日均比较**、**CoinDesk RSS + WebFetch 取代全挂的 WebSearch 拿宏观成因**、**carrier 用跨域歧义词 = 假装挡住**、**`cat:cs.DC` 是弱约束**、**`-1` 与 `None` 双哨兵导致失败格被误归「窗口太短」**。
- [World Action Models (WAM)](/topics/world-action-models.md) — the 2026 WAM term on GitHub: weekly convergence curve, the paper-repo → engineering-repo split, and why star order is not activity order (★1106 with 11 commits vs ★48 with 10).
- [github-radar — 实现缺陷与判据](/topics/github-radar.md) — 三十二轮实证的过滤器陷阱：`PER_TERM_CAP` 抽样低估 3.85×、`MAXPAGE` 撞顶静默丢整条、`pages` 两侧误判、缩写→全称只在类别通名上成立（`vla` 赢 / `jepa` 亏 94.6%）、**carrier 误杀率八轮同向复现（35–36% vs 94%）但只在长窗可读 —— 7 天窗下两侧恒 100%，是测不到不是没误杀**、「窗口是流量旋钮不是语义轴」的两次算术证据、**窄窗还会改变报告级分布**（7d 幸存 35 / 报告级 7 vs 30d 33 / 9）、**`commits_30d == commits_7d` 意味着本周新建**、**入口词会换代 —— `teleoperation` 第 32 轮首次居报告级之首**、**「`jepa`+`world model` 双通道退化」判据第 32 轮被否（单轮回摆）→ 占比类判据须两条件同时成立**、**raw=1 / seen=0 连两轮 = 靶子稳定，不等于词表无效**、**短名聚合量不能当正样本**、以及「已合并 ≠ 已生效」「脚本尾部崩溃 ≠ 本轮没产出」。
- [defillama-radar](/topics/defillama-radar.md) — 发现层第三通道（部署并拿到 TVL）：为什么新度只能靠全量 `id` 求差、`id` 单调递增的实测证明（但**「永久空洞」已作废 —— 那是延迟批量回填，校验改为「同分钟 ≥3 条即真新增」**）、**CDN 快照会让差集恒为 0，但证明不了字段值最新（`parentProtocol` 会翻转）**、`Interface` 类目为何不进 `EXCL_CATEGORY`、**`url` 与 `description` 两条旁路实为同族（去桥后打平，真增量在并集）**、**`address` 前缀不能替代 `chains`（6.1% 噪声）**、**`chains` 是部署声明、量必须看 `chainTvls`（多链 DEX 常有多条 0 值链）**、**`filtered` 的不可逆性会咬到自己的清单**、**`parent` 桶可单轮成为主导并吃掉体量最大的新增，但下一轮即回落 —— 两轮连续读数才是否定「某桶成为常态产能」的最短证据长度**、**`only_seen` 非空而 `only_raw` 空 = 下架痕迹而非损坏**、以及同秒批量登记的污染如何伪装成「桥噪声」。
- [叙事风向](/topics/narratives.md) — 每周一/四由 Grok 更新的市场叙事笔记，判断时参考、不复述。

## Tokens

- [Note Systems (NOTE)](tokens/note-systems.md) — Robinhood Chain 4663 结构化票据代币；timelock 持 25.42%，48h 延迟解锁，owner 为单个 EOA。含两轮砸盘手法、`0xfdd9` 整块风险修正
- [DEUS / xDEUS watch addresses](/topics/deus-escrow.md) — token, escrow, and xDEUS NFT addresses; why xDEUS being an ERC-721 needs no config change; stake/unstake pairing; counterparty map.
- [DEUS 事件流水](/topics/deus-events.md) — 10-23 → 10-24 逐小时明细归档：四次 claim-and-dump、跨场所拆分、复活/静默、escrow 逐 wei 闭合。MEMORY.md 只留当前状态，历史看这里。


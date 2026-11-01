Flush complete and stamped. Final output below.

## 本轮 memory-flush 结果（窗口 2026-10-31 → 2026-11-01）

读了 `memory/logs/2026-10-31.md`（145 行）与 `2026-11-01.md`（68 行），覆盖 8 个 skill 运行。MEMORY.md **8,327 → 8,093 字节 / 52 → 51 行 / 无超 300 字符行**，余量 99 字节。

### 最重要的一件事：推翻了一条自己写下的判据

10-30 那轮从**单次观测**（10-29 桶上修 +57.7%）写下「残桶只会被向上修」。10-31 同法复核抓到反例：**10-30 桶由 $18.129B 向下修正到 $12.258B（−32.4%）**，而同期 10-29 桶仍在向上修。已把 lessons 与 MEMORY.md 两处改成「**修正双向都有风险**」，保留原观测日期与推翻轮次，并把方法论一并写下：凡从单次观测写成通则的判据，下一轮必须主动找反例，不能顺势沿用。

### 纳入的实质发现

- **`arxiv-radar` 第 32 轮（30d）：原始 84 → 幸存 0，漏斗退化为 seen 单通道。** 83 条被 seen 吃、EXCL 常数项连续五轮、carrier 连续九轮 0 丢弃。含义是过滤层已无调节空间，产出能力完全由「26 个词窗口内是否产生 unseen 命中」决定 —— 之后再出 0，问题只能指向词表召回。饱和 19 词的最新发布全在近 30 天内，无一该降温。
- **`github-radar` 第 13 轮（30d）：carrier 误杀第四次同窗口复现。** 四轮序列 36/97 → 35/96 → 36/96 → **34/97**，丢弃侧只有放行侧的三分之一，判据升为结论、放宽可动手。本轮报告级 10 个全 ★0、9/10 落机器人侧 → **star 若参与采样排序会切掉整批**。
- **`defillama-radar` 第 6 轮：空 `chains` 从「疑似漏报」升为「已确证漏报」。** `Daejin` description 明写 Binance/Ethereum/Solana，`chains` 却是 `[]` —— 字段级自证。description 旁路比 url 旁路更干净（增量相近，桥噪声 23% vs 46%）；被挡桶拆分显示改旁路收益是加链的 3 倍。
- **fees 指纹升为可扫全表：** `total7d/24h ≈ 1` 的「新接入序列」判据不再只对可疑条目逐个看 —— 全表扫出 6 条、合计占全日 24h fees 的 26%。

### 剪枝与预算

无整节下沉，全为就地压缩：归档段 DEUS/NOTE 4 行并 2 行、取数/watch 框架 4 行并 3 行、多条长句去掉已在 lessons 里的复述。原先 386 字符的超长行已解决。`gh pr list` 有 1 个 open PR（#21，defi-overview 快照，非 improve PR），无 Open Improvement PRs 段可清；MEMORY.md 无 Next Priorities 段。

新增了一条常驻条目「**预算纪律**」—— 上一轮压到 8,190，本轮起点却是 8,327，被其他 skill 吃掉 137 字节，说明预算在两次 flush 之间只增不减。

## Summary

- **技能**：`memory-flush`（write 模式），执行完毕并已 `stamp`（watermark `2026-11-01`）。
- **修改文件**：`memory/MEMORY.md`（3 条主线改写 + 2 条 lessons 改写 + 1 条新增 + 预算压缩）、`memory/topics/github-radar.md`（新增第二十七轮 #63–#65，frontmatter 与首段轮次同步）、`memory/topics/lessons.md`（4 处：残桶双向修正、fees 指纹扫全表、carrier 四轮结论、漏斗单通道归因）、`memory/topics/index.md`（github-radar 行更新）、`memory/logs/2026-11-01.md`（新增 `### memory-flush` 条目）、`memory/memory-flush-state.json`（stamp 写入）。
- **未改动**：`memory/topics/defillama-radar.md` —— 第 6 轮发现已由该 skill 当轮自行写入，本轮只核对未重复。
- **未发送通知** —— 元技能，无对外信号。
- **遗留待办**（未处理，非本轮范围）：`memory/topics/` 下 10 个 `.py` 临时脚本与 `price-alert-state.json.bak`（100KB）待 PR 删除；`memory/on-chain-state.json.new` 与 `arxvi-radar` 孤儿条目待清。
- **未提交** —— 改动留在工作区，未建分支、未推送。

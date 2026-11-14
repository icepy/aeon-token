记忆整理完成（`memory-flush`）。扫描窗口 `2026-11-13 → 2026-11-14`，读 2 个日文件，无缺口未 clamp，轮转归档 0 个月。

## 预算轨迹

起点 8,190 字节 / 43 行 / 1 条超长行（第 16 行 366 字符）→ 中途被新增内容顶到 8,331 → 三步压回 **8,185 字节 / 43 行 / 0 条超 300 字符**（余 7 字节，`within budget`）。压缩只在措辞层，事实与 `[source:]` 标签一条未丢；`chains`/`chainTvls` 那句从 MEMORY 行移进 topic（那里已有第 19 轮整节）。

## promote 三条

**① arxiv-radar 第 45 轮 → 发现层行原地改写 + lessons 两条**

原始 76 → 幸存 5（上轮 75→0），六分类 未测到 0 / 未尝试 0 / 零命中 11 / 低频 0 / 全已见 12 / 有新增 3，两侧失败类全 0。**五条全落受控表、首次无 `?`**。最可操作的一条：`ti:"human data"` 与 `ti:"egocentric"` 首扫分别 `read timeout` / 429，冷却 20s 后补扫**都救回**，而 `egocentric` 本来就是本轮最大召回词（raw=20 / 新收 2）—— 不补扫会白丢最活的词。零命中 11 词里 9 个跨窗有命中 → 不许删。新判据（跨通道错位）：arxiv 加密侧真有召回 3 条 ⟺ github-radar 加密侧十连轮 0，两者有效域不同（0–3/窗 vs 0/窗），**不互证**。

**② defillama-radar 第 19 轮 → 发现层行原地改写 + index 行**

9028 / 新增 2 / 可报 0（`eleos` 9426、`Volta` 9427 皆 `chains=[]`、`tvl=None`、`module=dummy.js`）。新钉死：全量空 `chains` 1621 条与 `module=dummy.js` 1621 条**集合完全相等**（双向差集皆空）→ `chains=[]` ⇒ `tvl` 缺失成立，反向不成立（850 条非空链无 TVL）。新增 14→2 已用 CF 双取（`HIT` vs `?_cb=` 源站 `MISS`，etag/last-modified 逐字节相同、全量 TVL 零差异）排除假零。加链边际 $514→$2.6K→$48.5K→**$0**，上轮的「单调上升」被打断，四轮无趋势。

**③ heartbeat 11-14 → ops 新增一节 + index 行**

`403`→`402` 是错误码换族、自愈路径相反：403 认证窗会恢复，402 是余额等不回来。`github-radar` 22:30 那跳跑 6 turn 花 $0.176 才 402 = 额度跑到一半耗尽；另两跳 `num_turns:1`/`duration_api_ms:0` = 请求没出网关。`defi-overview` 三个失败是两种病（23:00/23:30 是 402，00:11 是 `max_output_tokens` 119 turn/580s）—— 即使余额恢复，单轮输出量本身也撞上限。成功率 **0.51（19/37）**，再连败 2 轮破 `<0.5`。另记一条取数事故判据：`gh run view --log` 里带 ANSI 转义（`^[[36;1m`）的行永远是脚本体回显，不是运行输出，先 `grep -v "36;1m"` 再筛 `claude exited`/`api_error_status`。

## 剪枝

`gh pr list --state open --search "improve:"` = `[]`（连续第十二天），无 PR 段可清；MEMORY 无 Next Priorities 段；未删任何 lesson（本轮新增均为判据加强，无被推翻项）；各节未超 10–15 行，未触发归档。

## Summary

- 扫描窗口 `2026-11-13 → 2026-11-14`，watermark 已从 `2026-11-13` 推进到 `2026-11-14`（`memory-flush-state.json` + MEMORY.md 镜像行双写，`updated_at` 2026-11-14T18:06:47Z）。
- 修改文件：`memory/MEMORY.md`、`memory/logs/2026-11-14.md`、`memory/memory-flush-state.json`、`memory/topics/index.md`、`memory/topics/lessons.md`、`memory/topics/ops-plumbing.md`。
- 未新建 topic / archive 文件，故索引无新增条目，只更新三行。
- 未处理（延续）：`defi-overview` 两条修复（cron 挪离 `0 23`、削减单轮输出量）属配置决策，须 OPERATOR 拍板；网关余额未补前两 skill 的断路器 probe 会继续 402；`memory/topics/market-context.md` 仍是 `2026-11-13T00:15:00Z`（昨夜 defi-overview 00:11 那跳在写出前已失败）。
- 本轮为常规维护、无信号，未发通知。

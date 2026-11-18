已完成 11-18 的 memory-flush。核心是一次**判据翻转**：MEMORY 里「`defi-overview` 是共用网关故障」这条诊断被本轮全日志推翻了一半。

## 本次改动

**1. 心跳行整条重写（判据翻转）**

11-17 把 `defi-overview` 与 `github-radar` 并成「共用 HivemindOS 网关间歇性拒绝一个对象」。本轮读 run `44195522715` 全日志后：

| 证据 | 值 |
|---|---|
| `num_turns` | 138 |
| `output_tokens` / 限额 | 147604 / 128000 |
| `api_error` | `max_output_tokens` |
| `terminal_reason` | `api_error` |
| 耗时 / 花费 | 1026s / $4.88 |

这不是网关拒绝（网关拒绝 = `num_turns:1` + 0 工具调用 + `duration_api_ms:0`），是跑到 138 轮、写到一半撞输出上限。两种病**一行可辨**，不该合并。附带三条：该轮 23:01→23:18Z 全程网关可达，403 带未复现 ⇒「挪 cron 避开 23:00–23:31Z」失去对象；`github-radar` 11-17T22:36Z 已自愈（cf→0）；成功率 48%→46%，第三次只有分母在动。

**2. 发现层三行全部推进到最新轮次**

- `arxiv-radar` 第 49 轮：71 → 幸存 2。新判据 —— **11 个零命中词跨窗 11/11 命中「窗口太短」，无一条真零**，年化仅 1–6 条/季 ⇒ 对低频词窗口决定「看得见/看不见」，`RWA`/`light client`/`embodied data` 该用 `days:90` 主动补历史。
- `defillama-radar` 第 23 轮：9070 / 新增 14 / 可报 2。`9455`/`9456` 回填但其 `listedAt` 早于上轮快照却缺席 ⇒ **`/protocols` 可见性滞后约 20 小时，`listedAt` 不可反推入库时间**（推翻第 22 轮单样本推论）。
- `github-radar` 第 28 轮：445/66/20。`30d==7d` 本轮 0 条 ⇒ 11-15「9 条里 8 条」只是样本条件。

**3. 三条新判据进 lessons**

- 低频词可见性由窗口边界决定（与第 47 轮同族但方向相反：那边边界滑走货，这边边界没覆盖货）。
- **「低频探针 N=0」是「未量」而非「跨窗皆 0」** —— `cross_windows()` 只跑未降级词，降级词不进分母。推广成通则：任何「N=0」字段先确认分母没被过滤掉。
- **饱和栏也会误读**：第 28 轮 5 个「饱和」里 `embodied data`(raw=4, seen=0)、`intent-based`(6/0) 是过滤损耗，按「`seen < raw 5%` 不许记饱和」不能读成饱和 —— 这条规则此前只用在零命中栏。

**4. 预算**

8,299 → **7,905 字节**，42 → 41 行，超长行 2 → 0。起点已超 107 字节，全靠同义压缩 + 细节留 topic 压回，事实与 `[source: ...]` 标签一条未丢。

**5. 剪枝**：`gh pr list --state open` = `[]`（连第十六天），无 Improvement PR 段、无 Next Priorities 段可清；本轮无被推翻的 lesson 需删除（「轮次缺口」那条是补限定，旧事实保留并注明已被填上）。未新建 topic 文件，index 三行更新，`ops-plumbing` / `lessons` / `github-radar` 的 `timestamp` bump 到 `2026-11-18T18:00:00Z`。

## Summary

- **做了什么**：memory-flush 扫描窗口 `2026-11-17 → 2026-11-18`（watermark 11-17，读 2 个日文件，无 >14 天缺口、未 clamp，轮转归档 0 个月）。
- **文件改动**：`memory/MEMORY.md`（心跳行整条重写 + 发现层三行改写）、`memory/topics/ops-plumbing.md`（新增 `Update (11-18)` 小节）、`memory/topics/lessons.md`（+2 条 arxiv 判据）、`memory/topics/github-radar.md`（新增第 28 轮整节 + 更正「轮次缺口」节）、`memory/topics/index.md`（三行）、`memory/logs/2026-11-18.md`（`### memory-flush` 记录）、`memory/memory-flush-state.json` + MEMORY 镜像行（stamp → 2026-11-18）。
- **待跟进**：`defi-overview` 的修法改回「砍单轮输出」；`scan.py:301` 审计行缺陷可单独提 PR；health issue `#9` 在 `github-radar` 恢复后未被回访（线程与 dispatch 状态解耦的第二例）；`arxiv-radar` 14 词缺 carrier 表；遗留物 `on-chain-state.json.new`、`price-alert-state.json.bak`、`arxvi-radar` 孤儿 cron 条目。
- **未发通知**：纯内部维护，无触发条件，按策略静默。

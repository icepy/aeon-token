记忆整理完成。MEMORY.md 8167 字节 / 42 行 / 无超长行，watermark 已推进到 2026-11-10。

## 本轮整理结果

**扫描窗口** `2026-11-09 → 2026-11-10`，读 2 个日志文件，无 >14 天缺口，未触发日志轮转（21 个日文件 / 阈值 45）。

### 四条 skill 事实原地改写（未新增重复条目）

**`defillama-radar` 第 15 轮** — 8975 / 新增 9 / **可报 2**，是自第 11 轮以来首次真正出报告。`Hollow`(9370) Ethereum $10.7K、`MING`(9367) BSC $744.6 但 `misrepresentedTokens=true` 读数不可直接用。新判据：**同秒 ≤10s + 同一 parent ⇒ 整组不必细看**（`Syndicate` 隔 6s、`Bitso` 隔 1s，第三次复现）。两份快照 etag 首次全等 → 非缓存假阳。`only_seen=['4818']` 连续第六轮，真下架。

**`arxiv-radar` 第 41 轮** — **75 → 3，打破「有新增 0」三轮序列**。三条判据级：① `ti:""…""` 双层引号失真的指纹是**四个窗口 total 全等**（5764/36341/78069/110276）+ 前 3 标题相同，既非零命中也非流量；② `staking` 判据了结，**60d=1/90d=1 → 窗口太短不是降温**；③ 收录日期停在上周五是**周末节律**，第 40 轮的滞后预警撤销。零命中 10 词里 8 个跨窗有命中，别删；跨窗皆 0 只剩 `verifiable inference`/`restaking`。

**`github-radar` 第 22 轮** — 459/28/6，核验 28/28。**头号发现：低频词（raw≤5）四分类逐轮翻转**，第 21 轮的饱和组本轮翻成「有新增」→ **单轮分档不可当趋势读，须连续 3 轮同档**。`30天=`≡`7天=` 6/6 累计三轮复现，已成稳定形态。加密侧第七连轮报告级 0，但 raw>0 → **是转化被封在门槛，不是没代码**。`embodied data` raw=4/seen=0 第二轮确认为过滤损耗。

**11-10 heartbeat** — `defi-overview` 连败 3 轮越 🔴 线，**且逐轮读 log 证明是两个病因**：23:00Z 是 403 但跑了 13.7 分钟（`duration_api_ms:824635`），23:30Z 同 403 但秒拒（`0`），00:15Z 是 **`max_output_tokens`（76298/128000，95 turns）根本不是 403**。11-09 的「重试自愈」假设落空。**首次量化：三轮烧约 $10 换零产出**。新判别器：`duration_api_ms` 为 `0` = 请求没出网关，数千毫秒 + `num_turns:1` = 跑了才失败。副作用：`market-context.md` 停在 11-09T00:30Z，宏观快照旧两天。

### 剪枝与压缩
- 起点 8174 → 中途冲高 8322 → **终点 8167 字节**；`行情口径` 那条一度被合并成 717 字符单行，已拆回 ①② 两条并各自精简。
- `gh pr list` 全部为空（连续第八天），无 Open Improvement PRs 段可清；无 Next Priorities 段；Lessons 无失效条目，唯一改动是把「网关错误」一条补上「签名不止一种」的纠正。
- 发现层 3 行、Lessons 12 行，均未超 10–15 行归档线。

### 未处理（延续）
`on-chain-state.json.new` 遗留物、`arxvi-radar` cron 孤儿条目、`price-alert-state.json.bak` 待删、上游 `aeon.yml` 五条 disabled 技能取舍（唯一 OPERATOR 决策）、**`defi-overview` 的 cron 是否从 `0 23` 挪开 + 单轮输出量削减（两个病因须分开修）**、github-radar 下一轮戳满 7 天将自动跑 probe。

## Summary

- 执行 `skills/memory-flush/SKILL.md`，窗口 2026-11-09 → 2026-11-10（watermark 驱动，无缺口、无 clamp、无轮转）
- **MEMORY.md**：4 条发现层/Lessons 事实原地改写（defillama-radar 第 15 轮、arxiv-radar 第 41 轮、github-radar 第 22 轮、defi-overview 双签名失败），未新增重复条目；8167 字节 / 42 行 / 0 超长行，在预算内
- **memory/topics/ops-plumbing.md**：新增「三轮失败、两个签名」整节（含成本表与 `duration_api_ms` 判别器），timestamp → 2026-11-10T18:20Z
- **memory/topics/lessons.md**：新增 3 条（双层引号失真指纹、`staking` 判据了结、周末节律），Citations 补一行，timestamp → 2026-11-10T18:22Z
- **memory/topics/github-radar.md**：新增「第二十二轮」整节，timestamp → 2026-11-10T18:24Z
- **memory/topics/index.md**：lessons / github-radar / ops-plumbing 三行更新
- **memory/logs/2026-11-10.md**：追加 `### memory-flush` 条目
- **watermark**：`memory_prep.py stamp` 已执行，`last_consolidated=2026-11-10`（state-file + MEMORY.md 镜像同步）
- 未发通知（干净整理，无需要决定的事项）

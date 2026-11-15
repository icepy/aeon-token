memory-flush 已跑完，水位线已推进到 2026-11-15。

## 本次刷新

**扫描窗口 `2026-11-14 → 2026-11-15`**（读 2 个日文件，无 >14 天缺口、未 clamp；日志轮转 0 个月，26 个日文件 / 阈值 45）。

### 提升进长期记忆的四件事

1. **defillama-radar 第 20 轮**（9050 / 新增 22 / 可报 2）— 更新了发现层那一行。新增 22 条与 11-12 并列在案最高，但仍按「单轮不作趋势」写。真正值钱的是两个口径：`parent` 唯一真边际 1 条（`Drakewell SPYdw`，$561,619 = 全部可报的 89 倍），以及**「新增」= 新进 `/protocols`，不是新登记** —— 3 条新增的 `listedAt` 早于上轮快照 4 小时以上，两条时间轴不同源。审计行 `本次通知` 恒写「零可报」是 `scan.py:301` 硬编码，可报 >0 时不可信。

2. **github-radar 第 26 轮 —— 推翻了一条被降成「定律」的判据。** 前六轮 `30天=`≡`7天=` 都是 12/12、8/8、7/7 全等，上一轮把它从「观察项」降为「既成前提、后续不必逐轮举证」。第 26 轮 25 条报告级里 **6 条两数不等**（最大仓龄 35 天，一条 19→0）。它一直是「候选仓龄全部 < 30 天」这个样本属性，不是窗口的数学后果。topic 里已把降级撤回。另一条：加密侧 4 词有 raw 新增却零报告级 —— **raw 有、幸存无 = 过滤层吃掉的**，与「召回打不中」是两种病、两种修法。

3. **arxiv-radar 第 46 轮 —— 判别力对照首次做实，这是本轮最可操作的一条。** 真词 `abs:blockchain` 7d=11、故意错拼 `all:restakinq` 7d=0，且对照组自己的 30/60/90d 三档撞了 429 被记为「查询失败」—— 反过来证明失败在这个工具里能被识别，所以那个「0」是真 0。写法：**不要给「零」找理由，给「零」配对照。** 另两个跨窗全零词走完换写法后降 `LOW_FREQ` 不删（已有货但 60d=2 低于门槛的词，「有货但不够」与「无货」动作相同，都降频）。

4. **heartbeat 11-15 —— 一条判据更正，写进 ops。** 昨天记的「402 是余额、等不回来」下得太强：同一个 skill 在同一时段的码序是 `402`→`402`→`max_output_tokens`→**`403`**，**两种码交替 = 网关侧状态自己在抖，不能据单一码推测成因**。能判的只剩失败位置（`duration_api_ms:0` = 请求没出网关；有真 turn = 半路死）。OPERATOR 的决策本身不变（补余额 / pin 换 provider），变的只是「等着没用」这个推断的置信度。同时 `github-radar` 已自愈（cf=0、81%），`defi-overview` 停在 **0.50（19/38）—— 规则是严格 `<`，再败 1 轮即 48.7% 破 chronic 线**，而 `market-context.md` 已冻结 48.3 小时，因为只有它会刷新那个文件。

### 剪枝与预算

`gh pr list --search "improve:"` = `[]`（连续第十三天），无 Open Improvement PRs 段可清。全量 open PR 有 1 条（`#25`，chore 类、未满 24h），不构成需跟踪的队列，未入档。**未删任何旧 lesson** —— 本轮无被推翻项，ops 那条是「更正」而非删除，旧推理作为历史留在新小节里。

预算先涨到 8,607 字节、三条行超 300 字符，压回 **8,181 / 43 行 / 0 条超长行（余 11 字节）**：手段是只留判据、把数值细节下沉到 `lessons.md` 和两个 topic，事实与 source 标签一条没丢。

### 遗留（未处理，延续）

- `defi-overview` 两条修复仍未落地（cron 挪离 `0 23`、削减单轮输出量）— 配置决策，须 OPERATOR 拍板
- 网关抖动未定位前，断路器 probe 会继续失败
- `defillama-radar` 的 `scan.py:301` 审计行缺陷待 PR
- `arxvi-radar` cron-state 孤儿条目（连报十七轮）、`memory/on-chain-state.json.new`、`memory/topics/price-alert-state.json.bak`

## Summary

- 扫描 11-14 / 11-15 两个日文件，提升 4 组事实（defillama-radar 第 20 轮、github-radar 第 26 轮、arxiv-radar 第 46 轮、heartbeat 错误码判据更正）。
- 修改：`memory/MEMORY.md`（发现层 3 行 + 「待盯」行原地改写，未新增重复段）、`memory/topics/lessons.md`（+3 条）、`memory/topics/ops-plumbing.md`（+1 更正小节 + frontmatter）、`memory/topics/github-radar.md`（+第二十六轮整节 + frontmatter 撤回旧降级）、`memory/topics/index.md`（4 行更新）、`memory/logs/2026-11-15.md`（`### memory-flush` 记录）。
- 预算 8,132 → 8,181 字节（余 11），43 行，0 条超长行。
- 水位线已 stamp 到 `2026-11-15`（`memory/memory-flush-state.json` + MEMORY.md 镜像）。
- 未提交 git —— 按 skill 约定由工作流处理；未发通知（无触发条件成立的新信号）。

Watermark advanced to 2026-11-12 and MEMORY.md is within budget. Done.

## 本轮 memory-flush 做了什么

**扫描窗口 `2026-11-11 → 2026-11-12`**（watermark 由 `memory_prep.py` 算出，读 2 个日文件；无 >14 天缺口，未 clamp；日志轮转 0 个月，23 个日文件未过阈值）。

### promoted 四条事实（全部原地改写，无重复标题）
1. **arxiv-radar 第 43 轮** `83 → 4`（`seen` 吃掉 95%）。头号判据是**单侧读数会「换边」亮**：第 42 轮 ZK 占 3/7、本轮机器人占 3/4 —— 这反证「某侧升温」，指向「加密侧长期 0–1 条」的结构常数。另记**词级/论文级计数首次不等**（`egocentric` 一词出 2 条），跨轮别混口径。→ lessons +1 条
2. **github-radar 第 24 轮** `428/30/7`。`30天=`≡`7天=` **7/7 第五轮**（两栏已定死为「仓龄」，不该再当活跃度证据）；加密侧**第九连轮**报告级 0，下一步量 `mev` 缩写；`jepa` 连出第 4、5 个「不训模型、只搬/只验」样本 = GitHub 上它是「读论文的入口」；probe 未跑，`clusters.json` 不可引用。→ github-radar +1 整节
3. **defi-overview 恢复 + 三条口径**：①**桶编号必须由 ts 换算 UTC 日期** —— 上一份文件把 11-09 的值贴了 11-08 的标签，「真资金流出」翻转成「纯计价贬值、ETH 计价仍在流入」；②**F&G 会回溯修订**（28→29→32→29 是冲高回落，不是持平）；③**「缩量」须报同星中位**（连四桶 −10~−24% 才是合格证据）
4. **两例过程事故**：`git reset --hard` 吃掉已写未提交内容（取消暂存只能用 `git restore --staged`）；**probe 偶然跑通 = 恢复≠修复**（`defi-overview` 两病根原地未动，状态页只该 🔴→🟡）。→ ops +2 节

### 剪枝
`gh pr list --state open --search "improve:"` = `[]`（连续第十天清空），无 Open Improvement PRs 段。未删任何 lesson —— 唯一的「作废」是 11-09 那条桶编号结论，已在 lessons 显式标注保留作反向样本。各节未超 10–15 行，未触发归档。

### 自查修正一处
写 defillama-radar 索引行时先写成「第 16/17 轮是 `parent` 连续两轮不回落」，核对日志后第 16 轮实为 **3**（15 轮 5 → 16 轮 3 → 17 轮 11）→ 不存在连续上行，已改为「单轮跳升，仍按两轮连续读数判」。

### 预算
起点 8,060 → 终点 **8,167 字节 / 42 行 / 0 超 300 字符**（余 25 字节）。中途一度冲到 8,857（超 665）且 line 33 达 327 字符，靠合并口径 ①②③ 为两行、合并两例事故、削冗余修饰词回线 —— 只削字，未丢事实或 source 标签。

### 文件改动
`memory/MEMORY.md`（发现层 3 行 + Lessons 2 行原地改写）、`memory/topics/lessons.md`、`memory/topics/github-radar.md`、`memory/topics/ops-plumbing.md`、`memory/topics/index.md`（四行）、`memory/logs/2026-11-12.md`、`memory/memory-flush-state.json`（stamp）。

### 待跟进（operator 决策，非本 skill 可动）
**`defi-overview` 两条修复仍未落地** —— cron 挪离 `0 23`（403 高发窗）、削减单轮输出量。心跳已连报三轮，今晚 23:00Z 复发概率仍高。另有 `arxvi-radar` cron-state 孤儿条目、上游 `aeon.yml` 五条 disabled 技能取舍。

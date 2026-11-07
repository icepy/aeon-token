memory-flush 完成。扫描窗口 `2026-11-06 → 2026-11-07`,读了 2 个日志文件,水位线已推到 `2026-11-07`。

## 本轮提升(新增判据)

### defi-overview 11-07 — 一条旧结论被推翻,七条新口径

**① 11-05「TVL 滞后来自上游刷新周期」的归因被修正。** 11-05 桶本身从 81.10B 被回溯上修到 **85.053B(+4.87%,补进约 $3.95B)**,而 11-04 桶只动 **+0.00%** —— 说明只有暴跌当日桶被盘中低估、收盘补正,不是普遍漂移。修正后 11-05 → 11-06 = **−5.12%**,与 ETH −7.73%、BTC −5.52% 对齐。「滞后」现象真实,但成因是**读到了未结算桶**,不是上报时差。已在 lessons 原地改写(保留现象、修正成因),没有静默删除旧事实。

**② `/overview/dexs` 的 `total24h` / `change_1d` 是「上一个完整日」。** 11.684/11.366−1 = +2.80% 精确复现 11-05/11-04 桶,与当场 11-06 桶的 9.576B 无关。当日真实量只能走 `totalDataChart`。
**③ `/protocols` 的 live `change_1d` 与链桶对桶是两套账本。** Sky Lending 的隐含前值 4.7687B 精确等于其 11-06 00:00 桶值 4.7801B;强行桶对桶会把 Aave 的 +4.45% 算成 −5.7%。纪律:链 delta 走 `historicalChainTvl`,协议 delta 用现成 `change_1d`,两条永不互验。
**④ real-yield 过滤器对 Uniswap LP 系统性偏心** —— 前 8 名全是 `ilRisk: yes`(波动率溢价,不是可持续收益),须加 `ilRisk=='no'` 或取 `exposure=='single'`。
**⑤ Polymarket `tag_slug=crypto` 参数失效**,BTC 盘须按标题二次筛。
**⑥ 稳定币单币大跌先找同链对手方** —— USDS −13.97% 对 USDe +7.76%,同链对撞 = 收益率轮动非恐慌出逃。
**⑦ TVL 的 7d/30d 不许口算** —— 本轮首版通知把 −0.97% 算成正号、30d 把 −13.92% 写成 +3.18%,已重发。

### arxiv-radar 第 38 轮 — 三条

`carrier` 歧义词清单扩容到 4 个,且**首次落在 robot 侧表**(`embodied` 对 `eess.SP` 无线论文同样成立);「用 `cat:` 挡污染」在 consensus 上**二次失败 → 该路线判死**(`cs.CR` 已被 LLM 安全占满);第 37 轮标记的两格失败**次日复测结清**(`proof of training` 90d=1、`light client` 60d=0)。另单列「分类看贡献形态,不只看关键词」。

### github-radar 第 33 轮 — 新增六条(#90–#95)

**静态站逃逸两例**:`SITE_SUFFIX` 只覆盖 `-website` / `.github.io` 后缀,**不覆盖「名字本身是 website」** —— 推翻了「站点仓按后缀无条件丢」的覆盖假设。`teleoperation` 连两轮最大入口(6/14)但质量最差,真信号仅 `unitreerobotics/R1-7A` 且 7d=2;加密侧第四连轮近零,唯一幸存是 `commits≥100` 撞 per_page 上限的农场高危形态;carrier 九轮同向(35% vs 100%)**结案**。

### heartbeat 11-07 — 网关 403 与 skill 回归的区分(写入 ops-plumbing)

`defi-overview` 11-06 两次 403,签名相同、`num_turns:1` + 0 tool calls + `duration_api_ms:0` = **网关侧鉴权拒绝,非逻辑回归**;同窗口相邻 skill 全成功 → 窗口性;00:15Z 重派在 00:36Z 成功、`cf` 已归零(我用 `cron-state.json` 复核确认)。

## 剪枝

`gh pr list --state open --search "improve:"` = `[]`,全部 open PR 也是 `[]`;MEMORY.md 无 Open Improvement PRs / Next Priorities 段 → 无可清理。Lessons 无失效条目。`arxvi-radar` 孤儿(cron-state,连报十一轮)与 `memory/on-chain-state.json.new`(连续十五轮)仍未解决,保留。

## 预算

MEMORY.md **8,090 → 8,174 字节**(余 18)、42 → 43 行、超长行 0 → 0。中途一度冲到 8,222 字节 + 第 26 行 353 字符,靠删例子、压修饰词、精简三条发现层行压回线内。

## Summary

- **做了什么**:执行 `memory-flush`,扫描 11-06 / 11-07 两个日志,提升 11 条 lessons、arxiv-radar 第 38 轮 3 条、github-radar 第 33 轮 6 条、ops-plumbing 新增 1 节,并原地修正了一条被 11-07 推翻的旧归因。
- **修改的文件**:`memory/MEMORY.md`、`memory/topics/lessons.md`、`memory/topics/github-radar.md`(bump `timestamp` 至 11-06T22:35Z)、`memory/topics/ops-plumbing.md`(bump 至 11-07T00:40Z)、`memory/topics/index.md`(三行)、`memory/logs/2026-11-07.md`(自写 `### memory-flush`)、`memory/memory-flush-state.json`(stamp)。
- **待跟进**:① `arxiv-radar` 的 `circuit`/`network`/`embodied` 判别力抽检,与 `consensus` 的纯 `ti:` 组合候选(下轮量测);② `github-radar` 静态站 desc 侧窄判据的误杀量测;③ `arxvi-radar` cron-state 孤儿条目与 `on-chain-state.json.new` 遗留物(均需写路径时机)。
- **未发送通知**:本轮为记忆整理,无对外信号 —— 按「正常别吵」不发。

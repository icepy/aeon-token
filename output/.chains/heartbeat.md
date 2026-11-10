🚨 heartbeat: defi-overview 连败 3 轮

🔴 **heartbeat · 00:32Z** - `defi-overview` 连败 3 轮，已过 🔴 线

**不是同一个错，是两种。** 这是昨天假设（「23:00-23:31Z 周期性鉴权窗口」）解释不了的部分：

| 时间 (Z) | 错误 | 判据 |
|---|---|---|
| 11-09 23:00 | 403 All target providers failed | `num_turns:1`、`duration_api_ms:824635` - 跑到一半才 403 |
| 11-09 23:30 | 同上 403 | `num_turns:1`、`duration_api_ms:0` - 秒拒 |
| 11-10 00:15 | **128000 output token 上限** | `num_turns:95`、输出 76298 / 上限 128000、`terminal_reason:api_error` |

第三轮是自愈重试，**换了个死法** → 昨天「等重试结果」的假设落空。403 窗口仍然成立（11-06 / 11-08 / 11-09 同槽位），但它不是唯一病因。

**影响**
- `last_success` 停在 **11-09 00:46Z**，已 24h 无成功读数。
- `memory/topics/market-context.md` 的 `timestamp` 仍是 **11-09 00:30Z** → DeFi 宏观快照已两天未刷新，引用它做判断会偏。
- 花费：三轮失败共烧 **$2.83 + $3.79 + 约 $3**（第 1、2 轮实数已核），≈ $10 换零产出。

**要动手的话，两件事分别修**
1. 给 `defi-overview` 设 `CLAUDE_CODE_MAX_OUTPUT_TOKENS`（当前撞 128000 上限，说明单轮上下文溢出，不是简单加大就完事 -- 更该砍单轮读取量/输出量）。
2. 403 槽位已连续三天出现在 23:00-23:31Z：考虑把 `defi-overview` 的 cron 从 `0 23` 挪开，或给 gateway 加第二条 cascade。

**其余全绿**：`defillama-radar` 00:04Z ✅ · `github-radar` 22:30Z ✅ · `arxiv-radar` 22:00Z ✅ · `memory-flush` 18:00Z ✅ · `narrative-brief` 10:02Z ✅ · `aeon-update` 11-09 11:00Z ✅ · heartbeat 自检 23.9h（36h 线内）。PR 队列 0（连续第七天）。无 urgent/critical issue。

状态页：`STATUS_PAGE=DEGRADED`
⚠️ 🟡 heartbeat

## 🟡 heartbeat — 网关 403 打了四个 skill，只剩一个还在线

**根因不是 skill 逻辑，是 `hivemindos` 网关认证。** 四个 skill 的 `last_error` 逐字相同：`Failed to authenticate. API Error: 403 All target providers failed.` —— 共享依赖，不是各自的回归。

| skill | 连败 | 最后成功 | 现在还在跑？ |
|---|---:|---|---|
| `defi-overview` | 3 | 10-24 12:09Z | ✅ 每天 12:00Z |
| `price-alert` | 5 | 10-25 08:20Z | ❌ 已停用 |
| `onchain-monitor` | 4 | 10-24 21:10Z | ❌ 已停用 |
| `token-movers` | 3 | 10-24 12:06Z | ❌ 已停用 |

**只有 `defi-overview` 还值得管。** 另外三个你在今天 02:50Z 已 `enabled: false`，连败数字会冻在那里，不用处理 —— 但状态页会把它们当历史读，别被吓到。

**网关现在已经活了：** `memory-flush` 10-26 00:13Z 成功、`arxiv-radar` 07:33Z 成功、`github-radar` 07:55Z 成功。403 窗口大致是 **10-25 21:00Z → 10-26 00:13Z**。

**⚠️ 真正要盯的是今天 12:00Z。** `defi-overview` 的上一败在 10-25 13:01Z，是在网关恢复**之前**。今天这轮如果成功 → 自愈，`consecutive_failures` 清零；再失败 → 那就不是网关，得查 `COINGECKO_API_KEY` 那侧。

**另一个信号：两个 radar 今天都在凌晨撞过 30 分钟墙。** `github-radar` 04:54Z、`arxiv-radar` 06:29Z 各一次 `hivemindos: timeout`，随后 07:33Z / 07:55Z 都重跑成功了 —— 同一晚两次超时，指向网关侧抖动而非单轮任务过重。先记着，别改 skill。

**其余全绿：** 无 stuck（无 `dispatched` >45min）、无 chronic、heartbeat 自身距离上次成功 23.9h（36h 线内）、无 open PR。GitHub 上 7 个 issue 全是自动的机器健康线程，无 label、无 critical/high。

STATUS_PAGE=DEGRADED — 已重写 `docs/status.md`；Token pulse 因最新报告是 10-24（>24h）按规则置空。
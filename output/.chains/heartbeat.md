🚨 心跳巡检：两个 skill 断路器跳闸（402）

## 🔴 两个 skill 断路器跳闸，且错误码从 403 换成了 402

**`defi-overview` cf=3 · `github-radar` cf=3**，两者昨晚同一批失败，签名相同：`402 All target providers failed`。

### 关键判据：403 → 402 不是同一件事
- 此前多轮是 `403`（认证窗），会自己恢复，所以「重试一下就好」成立。
- 本轮是 `402`（付款/余额），且 `github-radar` 22:30 那跳**先跑了 6 turn、花了 $0.18 才 402** -- 说明额度是跑到一半耗尽的，不是网关门禁拒绝。
- **含义：断路器每 ~5h 自动 probe 会继续失败，直到余额补上或 pin 换一个 `gateway.provider`。** 这不是等窗口能等回来的。

### 明细
| skill | 失败时刻 (UTC) | 轮次 | 备注 |
|---|---|---|---|
| github-radar | 11-13 22:30 | 6 turn / $0.18 | 跑到中途 402 |
| github-radar | 11-13 23:00 | 1 turn / $0 | 未出网关 |
| github-radar | 11-13 23:30 | 1 turn / $0 | 未出网关 |
| defi-overview | 11-13 23:00 | 1 turn / $0 | 未出网关 |
| defi-overview | 11-13 23:30 | 1 turn / $0 | 未出网关 |
| defi-overview | 11-14 00:11 | **119 turn / 9.7min** | **另一因：`max_output_tokens` 128k 超限** |

- 断路器状态（`scheduler: cron` run `43534664526` 日志原文）：`Circuit breaker OPEN: defi-overview (3 consecutive failures) - skip, next probe in 331m` / `github-radar ... 301m`。
- `defi-overview` 成功率 **51%（19/37）**，再连败 2 轮破 `<50%` chronic 线（19/38=50.0% 不算，19/39=48.7% 才算）。
- `defi-overview` 00:11 那跳证明：**即使网关恢复，单轮输出量本身也会撞 128k 上限** -- 这是两个独立病，缺一不可修。

### 已排除
- `memory-flush` / `arxiv-radar` / `narrative-brief` / `defillama-radar` / `aeon-update` 全绿，无 stuck、无 chronic。
- PR 队列 **0**（连续第十一天）。
- 状态页已重写：`docs/status.md`，🟡 WATCH → **🔴 DEGRADED**。

### 需要你拍板（两件，都属配置/账户，我没擅自改）
1. **网关余额**：`gateway.provider: hivemindos`。补余额，或 pin 到另一个 provider。
2. **`defi-overview` 两条结构性病**（已挂四轮未动）：cron 挪离 `0 23`（`aeon.yml:29`）+ 削减单轮输出量以免撞 128k。

来源：`memory/cron-state.json`、`scheduler: cron` run `43534664526`、`skill: defi-overview` run `43531239772`、`skill: github-radar` run `43527668402` / `43519867759`。
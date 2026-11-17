🚨 Heartbeat: github-radar 连败 3 轮

## 🔴 github-radar 也倒了 -- 发现层丢了一轮

`consecutive_failures` 到 **3**，11-16 23:31 UTC 那跳失败，最后一次成功停在 11-15 22:33。**11-16 的第 28 轮扫盘等于没发生。**

失败签名和 `defi-overview` 一模一样：
```
hivemindos: Failed to authenticate. API Error: 403 All target providers failed
```
1 turn / 0 tool calls = 请求根本没出网关。

**判据变了：** 同一晚 23:00-23:30 两个 skill 连续撞同一堵墙，而 22:00 的 `arxiv-radar`、18:00 的 `memory-flush`、00:00 的 `defillama-radar` 全绿。**网关是间歇性失败，不是宕机** -- 现在把两个 skill 当个案修就错了，方向是那个共用依赖。

## 附带读数

| | 现状 | 上次报告 |
|---|---|---|
| `defi-overview` | 连败 **6**，成功率 **48%**（19/40） | 连败 5，49% |
| `market-context.md` 冻结 | **~96h**（11-13 00:15 UTC） | ~72h |

`defi-overview` 这轮没单独推（48h 内报过），但 `market-context` 从 72h 累到 96h -- 任何引用它的判断都在用四天前的宏观读数。

**可执行动作没变，还是那三选一：** 补 HivemindOS 余额 / pin 换 provider / 砍单轮输出量。现在多一条理由：再拖下去丢的是发现层的日常轮次，不是单个报告。

其余 enabled skill 全绿，无 stuck，heartbeat 自检 24.0h 在线内。
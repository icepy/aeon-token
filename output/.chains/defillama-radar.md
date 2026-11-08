## defillama-radar · 第 13 轮（`dl-v1`，2026-11-08）

**结论：可报 0，未发通知。** 全量 8965 · 新增 id 9 · 过滤 9 · `seen` 命中 8956 · `STATUS: DEFILLAMA_RADAR_OK`。

### 漏斗读数

| 桶 | 条数 |
|---|---|
| `seen` 命中 | 8956 |
| `parent` | 7 |
| `category` | **0（真 0）** |
| 空链 / 链白名单 | 2（合计） |
| 无 id / 拉取失败 | 0 / 0 |
| 重报（上轮未通知） | 0 |

9 条新增全部被挡：`BNQ`(9354, Hemi, Lending, $538) · `Rocketswap Anubis V3`(9355, Anubis, Dexs, **$131.8K 全轮最大**) · `PeddleSwap V2`/`V3`(9356/9357, Anubis+Robinhood Chain+Base+Arc, TVL $0.796/$0.088) · `Jupiter Native Staking`/`VRFD`/`Developer Platform`/`Rent Reclaim`(9358–9361, 全 `chains=[]`+`tvl=None`) · `Yellow Onchain`(9362, XRPL 社交交易, `chains=[]`)。

### 四条判据级发现

**① `id` 不是整数 —— `<5471>` 这种带尖括号的 id 存在。** 本地校验脚本按 `int(id)` 排序直接崩在 `OpenTrade`（RWA，TVL **$245.6M**，`chains=['Avalanche','Ethereum','Plume Mainnet']`，`listedAt=2024-12-06`）。它自基线轮就在 `seen`、`notified=baseline`，尖括号是 DefiLlama 原格式。`scan.py` 全程用 `str()` 做键是对的；但副作用是 `seen` 键空间不归一化 —— 一个 id 从 `<N>` 变 `N` 会被当成新协议重报一次（本轮未发生）。

**② `链白名单` 桶首次非零，但 2 条里只有 1 条真属于它。** `Yellow Onchain`(9362) 是 `chains=[]`（空链），只有 `BNQ`(9354) 真是「链不在白名单」（Hemi）。`scan.py` 的 `if not hit` 同时吞掉两种情形 —— 与上轮 `parent→category` 同源的有损桶，桶名比语义窄。

**③ `parent` 真边际可逐条数清 = 2/7。** `Rocketswap Anubis V3` 与 `Jupiter` 四条是「parent + 空链」双帽，只有 `PeddleSwap V2/V3` 是 parent 唯一 —— 而这两条 TVL 分别为 $0.796 / $0.088，`chainTvls` 里 Robinhood Chain 与 Base **都是 0**，量全在非白名单的 Anubis 上。**本轮不存在「本可报却被误挡」的条目**（上轮 `Vesper V2` 那种 $10M 真边际本轮没有）。`category` 桶这次是真 0：9 条里无任何 CEX/Chain/Interface，与上轮「5 条双帽 Interface 造成的假 0」不同。

**④ 同秒批量的第三种形态。** 全量 `listedAt` 同秒 ≥3 条只有 6 簇，最新一簇是 11-07T14:26:04Z 的 4 条 —— 全部是 Jupiter 子条目（间隔 0s、同一 parent）。不同于 10-07 那次交易所回填（22 条桥）：**同秒 ≥3 条 + 同一 parent ⇒ 整组不必细看**。其余新增间隔 4–306s，逐条录入。

### 校验与稳定性

- **CF 校验通过**：`HIT`(etag `6aefaddf-918df0`, lm 11-07 23:01:51Z, age 1063) vs `?_cb=` 源站 `MISS`(etag `6aefb657-918c8b`, lm 23:37:59Z)，两份 8965 id 逐条相同。9 条新增**十字段零差异**，`parentProtocol` 翻转**连续四轮未复现**。
- `listedAt` 跨度 14.35h（02:12:39Z → 16:33:48Z），最小间隔 0s（Jupiter 组）。
- 数字 id 最大 9362，9340–9362 **连续无缺口**，连续五轮无「暂未回填的分配号」。
- 反向差集 `only_seen=['4818']`、`only_raw=[]` **连续第四轮** → 真下架。seen 8966 = 8965 命中 + 1 残留。
- 全量 `chains=[]` = 1591/8965 = **17.75%**（上轮 17.6%，五轮区间 17.4–17.75），稳定。
- 单侧读数：加密侧 0 / AI 侧 0。本源只有加密，高命中不是词表变准。

### 落盘

`out.json` 为空数组、`report.md` **未重写**（mtime 仍是 11-08 00:00 之前那一版，符合「报告级 0 不发通知、不重写」铁律）。`memory/defillama-seen.json` 写入 8966 条；`audit.log` 已更新。

## Summary

- 执行 `skills/defillama-radar` 第 13 轮正式扫描（`var` 为空）：全量 8965、新增 9、**可报 0**，未发通知。
- 修改 `memory/topics/defillama-radar.md`：新增 4 节（非数字 id、链白名单桶名窄于语义、parent 真边际 2/7、同秒批量第三形态）+ 本轮漏斗口径 + 8 条 citation，`timestamp` → `2026-11-08T00:20:00Z`。
- 修改 `memory/MEMORY.md`：defillama-radar 行更新到第 13 轮读数，压缩到 8179 字节（上限 8192）。
- 新建 `memory/logs/2026-11-08.md`，`### defillama-radar` 条目已按健康循环可解析的格式写入。
- 跟进项：无。可报 0 属结构性，本轮无一误挡；`<5471>` 键空间裂缝仅作已知风险记录，不改 `scan.py`（改 id 归一化会破坏 id 求差，且需重做基线）。

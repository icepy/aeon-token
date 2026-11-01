## defillama-radar · 第 6 轮 · 2026-11-01

**`STATUS: DEFILLAMA_RADAR_OK · 原始 8892 · 可报 0`** · `基线轮=False` · 审计无 ⚠️ · `seen` 写入 8893 条
**本轮未发通知**（可报 0 属结构性），**`report.md` 未重写**（mtime 仍是 10-30 那版）。

### 漏斗

全量 8892 · 新增 id 4（**可报 0 / 过滤标记 4**）· 重报 0 · `seen` 命中 8888
丢：`parentProtocol` 1 · `category` 0 · 链白名单 3 · 无 id 0 · 拉取失败 0

链命中：Ethereum=1895 · Binance=1145 · Arbitrum=1045 · Base=915 · Solana=466 · Optimism=393 · Robinhood Chain=297 · Hyperliquid L1=213 · Ink=33 · **BSC=0 · OP Mainnet=0** —— 白名单校验通过，孪生常量空转如常。

### CF 校验（可报 0 也必须做）

常规请求 `HIT`（`last-modified Sat, 31 Oct 2026 23:38:24 GMT`）vs `?_cb=` + `Cache-Control: no-cache` → `MISS`，**etag 相同 `W/"6ae67bf0-903d78"`**。两份各 8892 个 id，`only_busted` / `only_bus` **均为空集** → **本轮 0 不是 CDN 快照假零**。这是连续第三轮正面证据，且比前两轮更强（前两轮 etag 都变过）。差集 9286–9289 全部 ≥ 历史最大 id 9289，无旧条目回流。

### 今日 4 条（全部 `chains=[]` 或 parent，全部 `filtered`）

| id | 协议 | 类目 | 判定 |
|---|---|---|---|
| 9286 | `NABLA` | Trading App | 空 `chains` · desc "**Solana** trading terminal." |
| 9287 | `Daejin` | Prediction Market | 空 `chains` · desc "…on **Binance, Ethereum and Solana**" |
| 9288 | `Ride Launchpad` | Launchpad | `parentProtocol` → 该挡 |
| 9289 | `FusedPad` | Launchpad | 空 `chains` · desc "**Solana** memecoin launchpad on Meteora" |

listedAt 全挤在 10-31 18:54–19:12Z。

### 判据级发现

**① 空 `chains` 从「疑似漏报」升级为「已确证漏报」。** 前几轮只能靠人工读描述说「像真协议」。本轮 `Daejin` 是**字段级矛盾**：description 点名三种白名单链，`chains` 却是 `[]` —— 缺的字段和它的值同时在响应里。4 条里只有 `Ride Launchpad` 是真的该被挡。

**② description 旁路优于 url 旁路。** 对「空 `chains`+非 parent+非 EXCL」群体（770 条）：

| 分支 | 近 30d 增量 | 桥噪声 | 误命中 |
|---|---|---|---|
| `url` 非空 | +45 → **+39%** | 21/46 = **46%** | 未逐条核 |
| 描述命中白名单链 | +30 → **+38%** | 7/30 = **23%** | **2/30 = 6.7%**（逐条核过） |

增量几乎相同，噪声减半。误命中仅 `Snowbridge`（Polkadot 桥，"between Ethereum and Polkadot"）、`Agglayer`、`Golem Foundation`。

**③ 泛词实测无害：** `\bmainnet\b` / `\beth\b` 在 7d/30d/90d 三窗口 strict vs loose **差集全为 0** —— 误报是理论风险、实测为零；同时收紧也不换增量。`\bbase\b` 是全表唯一有真实误命中风险的词。

**④ 两个「空 chains 占比」不可混用。** 全量 **17.4%**（1550/8892，10-30/10-31/11-01 三轮完全一致）vs 带 `listedAt` 子集内的滚动窗 3d 70.6% / 7d 65.3% / 30d 63.2%（三轮同形、缓慢上升）。后者只覆盖 81.2% 的条目，有选择偏差。

**⑤ 群体画像补全：** 空 `chains` 1550 条里 `tvl` 非空 **0 条**（第三轮确认）、**有 `url` 1295 条 = 83.5%**、带 `listedAt` 仅 37.0%。这个群体不是「一无所有」，是「有站点、有描述、无链、无 TVL」——这正是描述旁路可行的前提。

**⑥ 被挡桶拆分（近 30d 漏斗输入 183 条）：** 通过 80（43.7%）· **只被空 `chains` 挡 76（41.5%）** · 只被链不在白名单挡 27（14.8%）。**改旁路的收益上限是加链的 ~3 倍** —— 方向继续压旁路，不加链。

### 下轮待办

1. `scan.py` 旁路从「`url` 非空」改为「description 正则命中白名单链名」；
2. 必须同时加桥类目子过滤或同秒 `listedAt` 批量去重（10-07T13:38:45Z 有 22 条同秒入库、15 条桥）；
3. 先确认「改过滤器不触发基线重做」的语义边界：旧 `filtered` 永不回退 ⟹ 8888 条历史条目不会因新旁路复活，**生效从下一轮起**，须在报告里写明。

**单侧读数：加密侧 0 / AI 侧 0** —— 本源只有加密侧，本轮 0 不构成 AI 方向任何证据。

## Summary

- 执行 `skills/defillama-radar/scan.py`（`dl-v1`，第 6 轮）：8892 条、新增 4、**可报 0**、`OK`、无 ⚠️。
- 按纪律做了 cache-busted 复取（`HIT` vs `MISS`，etag 相同，两份 id 集逐条相同）→ 确认 0 不是假零。
- 抓到「空 `chains` 挡真协议」的首个字段级硬证据（`Daejin` / `FusedPad` / `NABLA`）。
- 量化出 description 旁路：增量与 `url` 分支相当、桥噪声减半、误命中 6.7%。
- 拆开被挡桶，得出「改旁路收益 ≈ 加链 3 倍」的方向结论。
- 未发通知、未重写 `report.md`（均符合铁律）。
- 文件：新建 `memory/logs/2026-11-01.md`；改 `memory/topics/defillama-radar.md`（+5 节）、`memory/MEMORY.md`（条目更新）、`memory/defillama-seen.json`（脚本写，8893 条）、`output/defillama/{out.json,audit.log}`；遗留临时审计脚本 `output/defillama/audit2–8.py`、`cbverify.py` 可清。
- 跟进：下轮改 `scan.py` 前确认基线语义边界。

本轮已完成。可报 0，未发通知，`report.md` 未重写。

## defillama-radar 第 7 轮 · 2026-11-02

**STATUS: DEFILLAMA_RADAR_OK · 原始 8899 · 可报 0 · 基线轮=False**

### 漏斗

| 项 | 读数 |
|---|---|
| 全量 | 8899 |
| seen 命中 | 8892 |
| 新增 id | 7（可报 0 / 过滤标记 7） |
| 重报（上轮未通知） | 0 |
| 桶 | parent 3 · category 1 · 链白名单 3 · 无 id 0 |

链命中：Ethereum=1895 · Binance=1145 · Arbitrum=1045 · Base=915 · Solana=466 · Optimism=393 · Robinhood Chain=297 · Hyperliquid L1=213 · Ink=33 · **BSC=0 · OP Mainnet=0**（白名单校验通过，孪生常量空转如常）。

### 假零校验（可报 0 也照做）

常规请求 `cf-cache-status: HIT`（`last-modified 2026-11-01T23:38:10Z`、`age 382`、etag `W/"6ae7cd62-905a80"`），`?_cb=` + `no-cache` 取到 `MISS` —— **etag 与 last-modified 与 HIT 份完全相同**，两份各 8899 个 id，`only_hit` / `only_miss` 均为空集。连续第四轮正面证据，且本轮 etag 相等比前几轮更强（前几轮都变过）。**本轮 0 可报不是缓存假零。**

### 今日 7 条（全 `chains=[]`，全记 `filtered`）

| id | 名称 | 类目 | 描述里的链 | 被挡原因 |
|---|---|---|---|---|
| 9294 | Highbar | Launchpad | Solana | 链白名单 |
| 9295 | WenLong | **Interface** | Hyperliquid | category（唯一真该挡） |
| 9296 | The Standard Reserve | Reserve Currency | **Robinhood Chain** | 链白名单 |
| 9297 | Uxuy Perps V2 | Derivatives | — | parent#uxuy |
| 9298 | Scrooge DEX Aggregator | DEX Aggregator | Robinhood | parent#scrooge |
| 9299 | Scrooge Bridge Aggregator | Bridge Aggregator | Robinhood | parent#scrooge |
| 9300 | Imperial | Derivatives | **Solana** | 链白名单 |

### 判据级发现

**① 推翻上轮结论：`description` 旁路并不优于 `url`。** 11-01 记的「+38% vs +39%、桥噪声 23% vs 46%」是把两个不同分母的结果并排写。同一份 payload、同一套正则、窗口对齐后重算：

| 窗口 | 通过 | 空 `chains` 挡 | url 召回 | url 净 | desc 召回 | desc 净 | 并集净 |
|---|---|---|---|---|---|---|---|
| 7d | 8 | 15 | 11 | 11 | 10 | 10 | 15 |
| 30d | 77 | 76 | **44** | 21 | **31** | 23 | **36** |
| 90d | 256 | 139 | 73 | 48 | 56 | 47 | 78 |

召回量 url 反而更高；去桥/Foundation 后两者打平。全量 773 条空 `chains` 里 url 命中 586 / desc 命中 190 / **交集 132** —— desc 独有仅 58 条。**两条旁路是同族的，不是替代关系，真增量在并集。**

**② `url` 分支的 46% 桥噪声是一个同秒批污染的单点。** 30d url 分支 44 条里 22 条是桥，其中 **18 条全落在 `listedAt = 1791380325`（10-07T13:38:45Z）同一秒**（Squid / Layerswap / Relay / Snowbridge / Hyperbridge …）。剔除这一秒后 30d 空挡只剩 55 条：url 26（桥 4）、desc 28（桥 4）—— 几乎完全一致。10-31 与 11-01 两轮桥噪声读数差异由此可解释。

**③ id 有整段永久空洞，`id` 是分配号不是登记号。** 本轮差集 9294–9300，而 **9290–9293 四个 id 从未出现在任何一轮 payload、也从未进 seen**。所以「id 连续无缺口」不能当求差校验条件，只能校验方向：差集元素 ≥ 历史最大 id 才是新登记。

**④ 同秒去重可行且代价极低。** 全量 8899 条里只有 28 个 `listedAt` 秒含 ≥3 条，涉及 115 条（1.3%）。按「同秒 ≥3 条整批剔除」即可根除这类批量污染。

### 给下轮的可执行方案

旁路改为 `chains 为空 → (url 非空 OR description 命中白名单链)` 的并集 + 同秒批量去重，不要二选一。**但先接受上限：并集净后 30d 只多 36 个名字、90d 78 个 —— 是「每周多几条可看」的量级，不是能翻转漏斗的量级。** 若今日启用，会救回 Highbar / The Standard Reserve / Imperial 三条；WenLong 仍被 Interface 挡，Uxuy 与 Scrooge 两条仍被 parent 挡。

未发送通知（可报 0 属结构性，按铁律静默）。

## Summary

- 跑了 `skills/defillama-radar/scan.py`（`dl-v1`，第 7 轮，2026-11-02）：全量 8899、新增 7、可报 0、`STATUS: DEFILLAMA_RADAR_OK`、`基线轮=False`、无 ⚠️。
- 做了 cache-busted 复取（`HIT` vs `MISS`，etag 相同 `W/"6ae7cd62-905a80"`，两份 8899 个 id 逐条相同）→ 确认本轮 0 不是 CDN 假零。
- **推翻 11-01 的「description 旁路优于 url」结论**：那是不同分母的假比较；真实结论是两条旁路同族、增量在并集（30d +36）。
- 定位 `url` 分支 46% 桥噪声的来源：10-07T13:38:45Z 一个秒内的 18 条桥批量入库，非常态。
- 发现 id 存在永久空洞（9290–9293），确立「id 是分配号，只校验方向不校验连续性」。
- 文件改动：`memory/logs/2026-11-02.md`（新建）、`memory/topics/defillama-radar.md`（重写，推翻旁路结论 + 新增两节）、`memory/MEMORY.md`（就地改写该行，8,149 字节）、`memory/defillama-seen.json`（8900 条，脚本写）、`output/defillama/out.json` + `audit.log`（脚本产物）。未发通知、未重写 `report.md`。
- 跟进：① `scan.py` 改并集旁路 + 同秒去重；② **仍未确认**「改过滤器不触发基线重做」的语义边界（旧 `filtered` 永不回退，8888 条 baseline/filtered 不会复活）—— 这条从 11-01 挂到现在，改代码前必须先定。

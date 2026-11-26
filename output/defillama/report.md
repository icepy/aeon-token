**defillama-radar** · 第 31 轮 · 全量 9115 · 新增 9 · 可报 **3**

三条都是自建适配器（非 `dummy.js` 空壳），且都带真实 TVL —— 这是 30 轮里第一次可报集全部满足「有适配器 + 有量」。

## 1. `Theorem` · Ethereum · Dexs · TVL $46,173
- **一句话**：代币化 RWA 的 DEX，做 NAV 感知的流动性池 + 做市商报价 + 合规交易（`theorem_markets`）。
- 链：`Ethereum` 单链，`chainTvls` 全部落在 Ethereum，无跨链摊薄。
- 适配器 `theorem/index.js` · audits 0 · `listedAt 2026-11-25T18:23:21Z`（约 5.7h，本轮最新可报）
- 原始来源：`https://api.llama.fi/protocols` · slug `theorem` · id `9514`
- 备注：`Theorem` 这个名字在 DefiLlama 里只此一条（无同名/同 slug 冲突）。

## 2. `Tapir` · Base · Derivatives · TVL $45,507
- **一句话**：生息资产的「脱锚保险」市场，把一个生息凭证拆成两份可交易债权 —— `Depeg Protected`（脱锚有保护）与 `Yield Boosted`（先吃损失换更高收益），两份都保留 100% 底层收益。
- 链：`Base` 单链 · 适配器 `tapir/index.js` · **audits 2**（Quantstamp + Hashlock，本轮唯一有审计链接的可报条目）
- `listedAt 2026-11-25T00:34:02Z`（约 23.5h）· slug `tapir` · id `9510`
- 原始来源：`https://api.llama.fi/protocols` · twitter `Tapir_Protocol`

## 3. `QHooks` · Robinhood Chain 为主 · Launchpad · TVL $18,138
- **一句话**：面向人和 AI agent 的代币发行/交易生态 —— Uniswap v4 hook 发行、交易终端、agent 工具。
- 链：声明 8 条（`Robinhood Chain`/`Solana`/`Base`/`Arbitrum`/`Binance`/`Ethereum`/`Monad`/`Elysium Kinetiq`），**但量几乎全在 Robinhood Chain（$18,107，99.8%）**，Solana 仅 $29.6、Elysium Kinetiq $1.5，其余 5 条 = 0。
- 适配器 `qhooks/index.js` · audits 0 · `listedAt 2026-11-25T09:59:34Z`（约 14.0h）· id `9512`
- 地址：`robinhood:0x20429af7ca3b0ce4d99edbaa0693f26c5df05195` · **`gecko_id: qhooks`**（近 7d 新增 41 条里唯一带 CoinGecko 映射的一条）
- 原始来源：`https://api.llama.fi/protocols` · twitter `qHooks_`

## 被挡的 6 条（不进报告，只留痕）
- `9513 Curve Stellar`（Dexs · **TVL $1.50M，本轮新增里最大**）→ `parent#curve-finance`
- `9515 PicoSwap Aggregator` → `parent#picoswap`（与 11-25 的 Perps/Spot 同一母协议第三次铺开）+ 空链 + `dummy.js`
- `9511 Eloscape`（`Elysium Kinetiq`，非白名单链；staking $71.9K 但主 TVL 仅 $3.66K）
- `9509 Pylona`（`Sonic`，非白名单）· `9507 Xyper Market`（`UNIT0`，非白名单，TVL 0）· `9508 HelmSwap`（空链 + `dummy.js`）

## 本轮读数
- 丢弃：`parent` 2 · `category` 0 · 链白名单 4 · seen 9106 · 无 id 0 · 拉取失败 0
- `STATUS: DEFILLAMA_RADAR_OK` · 基线轮 False · 无 degraded、无 ⚠️
- seen 写入 9117 条 · 双向差集 `only_raw=[]` / `only_seen=['4818','5496']`（均为历史下架残留）
- CF 双取通过：常规取 `HIT`（etag `W/"6b07716c-942b1d"`，`last-modified 2026-11-25T23:38:20Z`），`?_cb=20261126a` + `no-cache` 取源站 `MISS`，**etag 与 last-modified 逐字符相同、9115 个 id 两向差集均空、逐条字段差异 0 条** ⇒ 本轮 9 条新增不是缓存假零。

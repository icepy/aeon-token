**defillama-radar · 第 17 轮 · 2026-11-12**

全量 9012 · 新增 22 · 可报 4 · 过滤 18

## 可报四条

- **Horizen Bridge**（9405）· Base · TVL **$24,128.7** · Canonical Bridge · Base 与 Horizen（OP Stack L3，结算落到 Base）之间的官方桥。`horizen.io` · `listedAt 11-11T22:23:02Z` · 本轮唯一上万。
- **Flowlex**（9390）· Base + Robinhood Chain · TVL **$7,323.7**（Robinhood Chain 只 **$0.55**，量几乎全在 Base）· Liquidity Manager · 非托管的 Uniswap V3 收费策略：存 USDC 选策略，在自己的智能钱包里开仓管集中流动性。
- **Indexfy**（9396）· Base · TVL **$1,421.4** · Indexes · 非托管加密指数代币，每个指数（如 I5：BTC/ETH/XRP/SOL/BNB）是全额背书的 ERC-20，USDC 一笔交易申购赎回。`base:0x6D21812b58E2B4667DB37B8b8B85C534a9771ceC`。
- **Gully Core**（9400）· Base + Binance + Robinhood Chain（另挂 Anubis、Elysium Kinetiq）· TVL **$0.83** · Dexs · AMM + 打新台，一个 Vault 持有所有池子代币，打新币从第一块就在真池子交易。

## 一句话读数

**可报 4 条 TVL 合计 $32.9K，被 `parent` 挡掉的 `Pendle Loop`（9393）单条 $42.0M -- 差 1279 倍。** 可报集按定义不含体量，读「本轮最大新协议」必须回看差集全集。

## 过滤 18 条

- **`parent` 桶 11 条（历史最高），真边际 4/11**：`Pendle Loop`（9393，$42.0M，Ethereum 主量 $40.5M）· `Jupiter Vaults`（9392，$292.1K）· `HedgeHood Options`（9398，$451）· `HedgeHood StockLend`（9397，$53.6）-- 去掉 parent 即可全通过。另 7 条是 parent + 空 `chains` 双帽（`STRATO DEX` 挂非白名单链 `Strato`；`Homer Swap`/`Valdora Vaults`/`GrowStreams Perps`/`ElysPump V1-V3` 全空链）。
- **`category` 桶 0，且是真 0**：22 条新增无任何 CEX / Chain / Interface。
- **空 `chains` 8 条** · **链不在白名单 2 条**：`Parchment`（Sui，$8.1K）、`H10X Index`（Hedera，$990）；`Helios DEX`（9394）挂 `Elysium Kinetiq`。

## 加链：仍然不加

`Elysium Kinetiq` 现共 15 条（Uniswap V2/V3/V4、Aero 两版、Ramses 三版早已在录）。本轮加链唯一多出的是 `Helios DEX`（9394，**$2.6K**）。**边际 1 条 $2.6K，代价是删 seen 重做 9012 条基线 -- 不加。**

## 数据校验

- **CF 双取通过**：`HIT` etag `W/"6af4fc70-924986"` / `last-modified 11 Nov 2026 23:38:24 GMT` / `age 31`；`?_cb=`+`no-cache` 源站 `MISS`，**etag 与 last-modified 完全相同**，9012 条逐字段零差异。22 条新增零差异，`parentProtocol` 翻转连续八轮未复现。
- **`listedAt` 滞后第二例**：`Valdora Vaults`（9395）`listedAt=11-10T08:40:00Z`，比上轮快照 `last-modified`（11-10T23:38:18Z）**早 15 小时**却本轮才出现 → 再证它只是「登记意图时刻」，不能倒推漏报、不能测延迟。且它是整分 `:00` 秒（`STRATO DEX` 9402 亦然）-- 全量 7336 条带 `listedAt` 里仅 69 条整分（0.94%），该字段有人工填写成分。
- **`9382` 连续第二轮缺席**，本轮另有 `9391`、`9412-9415` 缺口 → 分配了号未回填，非永久空洞，不改求差逻辑。
- **`only_seen=['4818']` 连续第八轮** → 真下架。seen 9013 = 9012 命中 + 1 残留。
- 全量 `chains=[]` = **1613/9012 = 17.90%**（上轮 17.83%，九轮 17.4-17.90 窄带）。
- `listedAt` 跨度 **22.36h**，最小间隔 **1s**；同秒 ≥3 条批量指纹新增 **0 组**（`ElysPump V1/V2/V3` 相隔 11s 最近）。22 条里 8 条落 11-11 22 时、6 条落 17 时 -- 两小时吃掉 64%，单轮形态不作趋势。

`STATUS: DEFILLAMA_RADAR_OK` · 无告警 · 无动作（本 skill 只做发现，不做判断）。

---
来源：`https://api.llama.fi/protocols`（快照 `last-modified 2026-11-11T23:38:24Z`，9012 条）· `skills/defillama-radar/scan.py`（dl-v1）· 原始读数 `output/defillama/out.json` / `audit.log`。
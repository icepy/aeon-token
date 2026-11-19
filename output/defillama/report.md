**defillama-radar** · 第 24 轮 · 可报 1 / 新增 5

## 可报（1）

**Coffer Protocol** · `9470` · Ethereum · TVL **$56,436** · `Lending`
以太坊验证者质押背书的无许可非托管债券：验证者以质押为抵押发固息债券募 ETH，债券为可转让 NFT。`listedAt 2026-11-18T00:00:55Z`，`parentProtocol` 空、`url` 空。来源 `api.llama.fi/protocols` id 9470。
口径提醒：`tvl $56.4K` 但 `chainTvls.borrowed $222.2K`（3.94×，全量 Lending 头部 12 家区间 0.06–0.93）—— 字段口径待人工核，本通道不下判断。

## 被过滤（4，全 parent）

`EtherFi Cash Swaps`(9471) · `True Markets Perps`(9472) · `True Markets Spot`(9473) · `RXN Prediction Markets`(9474)

四条 `tvl` 全 `null`、`module=dummy.js`。**parent 真边际 = 0**：去掉 parent 后全被空 `chains` 挡，其中 3 条再被 `Interface` 挡。桶序有损第七次复现。

## 读数

- 全量 **9075** · 新增 5 · `category` 0 · 链白名单 0 · 拉取失败 0 · 重报 0 · `STATUS: DEFILLAMA_RADAR_OK` · 无 ⚠️（孪生 `BSC`/`OP Mainnet` 仍 0）。
- CF 双取通过：常规 `HIT`（etag `6afe36e5`、`last-modified 11-18T23:38:13Z`）；`?_cb=`+`no-cache` 取 `MISS`，两份 9075 id 逐条相同、`tvl` 差异 0 → 非假零。
- 反向差集 `only_seen=['4818']`（第十五轮真下架）。id 9470–9474 连号无缺口，`max_id=9474`；9000 以上仍 4 段缺口（`9135`/`9257`/`9382`/`9391`）。
- `chains=[]` **1658/9075 = 18.27%**（连续第四轮新高），空链 ⟺ `dummy.js` 第七轮两向完全相等。
- 全量 TVL **$442.77B**（上轮 $451.36B，−1.90%，连续第二轮回落）；近 7d 登记 59 / 近 30d 300（纯窗口滚动）。
- 单侧读数：加密侧 1 / AI 侧 0 —— 本源只有加密，别把高命中读成词表变准。

## 一条纪律更新

`Coffer` 的 `listedAt` 是 `00:00:55Z`（接近整点），全量另有 6 条落在整点、`Pons V1/V2` 秒级完全相同 ⇒ **部分条目 `listedAt` 只到日精度**。第 23 轮那句「`/protocols` 滞后 `listedAt` 约 20 小时」须限定为只对秒级可信条目成立，日精度条目会污染滞后期推断。

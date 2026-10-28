基线轮完成，无信号可报，未发通知（符合 SKILL「基线轮不出报告」）。

# defillama-radar · 第 1 轮（基线轮）

**VERSION** `dl-v1` · var 为空 · 单次请求 `https://api.llama.fi/protocols` · 耗时 0s
`STATUS: DEFILLAMA_RADAR_OK · 原始 8859 · 可报 0`

## 全量
payload 8859 条协议，**id 无重复**（8859 distinct / 8859 行），无空 id。`memory/defillama-seen.json` 首建，8859 条全部 `notified="baseline"`。

## 四桶（分开写）
| 桶 | 条数 |
|---|---|
| 全量 | 8859 |
| **可报**（`notified is None`） | **0** |
| 过滤：`parentProtocol` 存在 | 2613 |
| 过滤：`category ∈ {CEX, Chain}` | 164 |
| 过滤：不在链白名单 | 3328 |
| 已 seen / 重报 | 0 / 0 |

可报 0 是因为**基线轮把 2754 条全写成了 `baseline`**，不是过滤变严。这 2754 条是下一轮起 id 求差的底池。

## 链命中
`Ethereum=1891 · Binance=1145 · Arbitrum=1044 · Base=912 · Solana=465 · Optimism=392 · Robinhood Chain=292 · Hyperliquid L1=210 · Ink=33 · BSC=0 · OP Mainnet=0`

**白名单启动校验通过**（审计无 ⚠️ 行）。实测 payload 共 520 个 distinct 链名，`BSC` / `OP Mainnet` 今天**完全不存在** —— `/protocols` 只用 `Binance` / `Optimism`，与 SKILL 记载一致，孪生常量是防御性冗余。`CHAIN_MIN_HITS` 告警被 `CHAIN_TWINS` 正确排除，否则每天误报两条。

## 单侧读数
**加密侧 2754 / AI 侧 0。** 本源只有加密，2754 这个高数**不能**读成词表变准；第三层 join 时会显得命中率高，那是源偏差。

## 可报明细
无（基线轮）。`output/defillama/out.json` 2754 行已落盘，`report.md` 按规则未生成。

## 补充审计（三条判据级发现）

**① `★清单内` 目前没有判别力。** 103 条命中里 **96 条是 description 撞词、0 条是协议名命中**（唯一名字级命中是 `Robinhood Chain Bridge`）。根因：`memory/universe-names.txt` 把链名 `Robinhood Chain` 当项目名收着，而该链上 91 个协议的描述都会写自己的链名 → 整条链被批量点亮。`USDG` 同理（14 条，全是"以 USDG 计价"）。**只能当弱提示。**

**② `listedAt` 缺失不是随机的，但也不与规模相关。** 全量覆盖 81.1%，按 TVL 十等分一律 85–98%；真正缺的是头部大协议（TVL≥$1B 的 68 个缺 16 个：Lido / LayerZero V2 / Robinhood / SSV Network / WBTC / Sky Lending / Arbitrum Bridge）。SKILL 判「新度只能靠 id 求差」成立 —— 但**近期新登记上 `listedAt` 是完整的**，可作 id 求差的交叉校验，不能替代。

**③ 新噪声源 `Interface` 类目。** 10-27/10-28 两天 15 条新登记里 9 条是 `Interface`，全部 `chains=[]` + `tvl=None`，目前被链白名单自然挡掉。若其中某个后续补上 chains，就会以"新协议"身份进报告。

## 待办
1. 决定 `Interface` 是否加入 `scan.py` 的 `EXCL_CATEGORY`。
2. `universe-names.txt` 去掉 `Robinhood Chain`，或把 `in_names` 改成仅匹配 `name` 字段。
3. 下一轮验证：id 求差的新增量是否都落在 `listedAt` 近 30 天集合内（校验求差本身）。

## Summary
- 执行 `python3 skills/defillama-radar/scan.py ""` — 首跑即基线轮，8859 条入 seen，可报 0，未发通知。
- 产物：`memory/defillama-seen.json`（新建，8859 条）、`output/defillama/out.json`（2754 行）、`output/defillama/audit.log`。
- 修改：`memory/logs/2026-10-28.md` 追加 `### defillama-radar（第 1 轮）`；`memory/MEMORY.md` 加一行发现层状态。
- 未发通知：基线轮按 SKILL 铁律不出报告，且无信号可推。
- 后续：上面 3 条待办里前两条需要改 `scan.py` / 词表（本轮未动，等确认后再提 PR）。

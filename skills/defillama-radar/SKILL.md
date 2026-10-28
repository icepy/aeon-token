---
name: defillama-radar
description: 扫 DefiLlama 上指定链新出现的协议，只出名字与地板字段。只做发现，不做判断。
metadata:
  title: DefiLlama Radar
  category: crypto
  var: ""
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔。`dry-run` 跳过 notify、不写 `memory/`；`send` 发送并标记；`mark-sent` 只标记。**原样传给脚本，不要自己解析。**

第二层（名字）的第一条通道。与 `arxiv-radar` / `github-radar` **平行，不是它们的下游**。

| 成熟度 | 通道 | 提前量 |
|---|---|---|
| 有人在研究 | `arxiv-radar` | ~4 个月 |
| 有人在写代码 | `github-radar` | ~1–2 个月 |
| 有人在部署并拿到 TVL | **本 skill** | ~0 |

**同一个名字在几条通道上依次点亮，那个次序才是信号。**

## 有效域

**只有加密侧。** 第三层 join 时方向命中率会显得很高——那是源偏差，不是词表变准了。每轮审计必须记一行单侧读数，写明这一点。

## 判「新」的机制

DefiLlama 没有可靠的创建时间：`listedAt` 大面积缺失（实测 `Lido` / `SSV Network` / `LayerZero V2` / `Robinhood` 都没有）。所以新度**只能靠全量 id 求差**：`memory/defillama-seen.json` 存全量 id，本轮差集即新增。

**seen 存全量 id，不筛链。** 同一个协议跨多条链仍是同一个 `id`，所以"多链上同一个协议"天然只算一次。

**seen 命中就跳过，不看过不过滤。** 所以已入库的协议永远不会再进报告——包括当时被链白名单挡掉的那些。

## `notified` 四态

| 值 | 含义 | 再报？ |
|---|---|---|
| `null` | 过了过滤、没通知成 | **会**（自愈） |
| `"YYYY-MM-DD"` | 已通知 | 不会 |
| `"filtered"` | 首次出现就没过过滤 | **不会**（扩张不算新） |
| `"baseline"` | 基线轮批量入表 | 不会 |

入库那一刻逐条定死：被任一桶丢掉写 `filtered`，全通过写 `null`。**`filtered` 永不回退、永不补报。** 可报集合 = `notified is None`。

基线轮把**全量**（不只是可报的）写成 `baseline`，所以那 6105 条被过滤掉的也一起钉死了。推论：

- **补 `chains` 不补报。** 一个 `chains=[]` 的协议后来接上主网，仍然是 `baseline`，进不来。
- **加链不回溯。** 往 `CHAINS` 加一条新链，该链上已有协议一条都不会报，全都在 seen 里。

## 加链 = 必须重做基线

往 `CHAINS` 加链（或改任何会让旧 `filtered` 变可报的过滤器）之后：

1. 删 `memory/defillama-seen.json`
2. 手动 dispatch 一轮
3. 确认审计里 `基线轮=True`、有 `⚠️` 之外无异常
4. 这一轮不出报告、不发通知，属预期

不删就直接跑，加链等于没加，而且不会有任何报错。

## 词表与白名单在哪

**全在 `skills/defillama-radar/scan.py`**：`CHAINS` / `CHAIN_TWINS` / `EXCL_CATEGORY` / 阈值。**这里不抄一份。**

链名拼写以 `/protocols` 为准，**不是** `/v2/chains` 的显示名——两组孪生（`BSC`↔`Binance`、`OP Mainnet`↔`Optimism`）在 `/protocols` 里用的是后者。白名单是常量，写错不报错、只会静默 0 命中，所以启动校验必须进审计。

## 铁律

- **只读 `https://api.llama.fi/protocols`**，一轮 1 次请求，不碰 RPC。
- **只信 `chains` 数组。** `chain` 字段常是 `Multi-Chain`，不许拿它过滤。
- **不设 TVL 地板、不排 TVL。** TVL=0 也报——地板是第三层的活儿。
- **`parentProtocol` 存在即丢。** 版本号铺开是最大噪声源。
- `category` ∈ `EXCL_CATEGORY`（CEX / Chain / Interface）丢。
- `listedAt` 缺失记 `null`，不猜、不回填。
- 不做方向映射（`category` 原样带）；不做判断；**不写候选卡**（卡留第三层）。
- 不读 `output/arxiv` / `output/ghradar`。
- 基线轮（seen 为空）只入 seen、不出报告。
- **加链后必须删 seen 重做基线**（见上节）。
- 报告级 0 时不发通知、**不重写 `report.md`**。
- **发送与标记是同一个动作**：只有 `send` 成功才标 `notified`，不许先标后发。
- 产物文件名固定（`out.json` / `out.dry.json` / `seen.dry.json` / `audit.log` / `report.md`）。轮次号只进日志内容。
- 本 skill 不产方向标签，没有写 labels 这一步。
- 全部输出简体中文；**通知正文里协议信息（名字、类目、一句话）用中文，其余可英文**。

## 判据（读数怎么读）

- **`基线轮=True` 且 seen 文件本来就在** = 不正常。seen 文件存在但解析失败时，审计打 `⚠️ seen 解析失败`、`STATUS` 走 `DEFILLAMA_RADAR_DEGRADED`，然后按基线轮重灌。**非 dry-run 才会把坏文件备份到 `memory/defillama-seen.broken.json`；dry-run 不写 `memory/`，只重灌 `out.dry.json` / `seen.dry.json` 快照。** dry-run 下看到这个 ⚠️ 要当真——没有 `seen.dry.json` 时读的就是正式 seen，说明正式 seen 本身坏了，别当快照噪声放过。**看到这个 ⚠️ 要进日志的判据级发现，写清丢了哪一轮的记录。**
- `STATUS: ..._DEGRADED` 有两种来源：拉取失败、seen 损坏。两种都必须写进日志，不许只写「本轮 0」。
- 正常日可报应接近 0。可报忽然上三位数，先查 seen 有没有被重灌，再怀疑词表。

## Config

读：`scan.py` 的 `CHAINS` · `memory/defillama-seen.json` · `memory/universe-names.txt`

写（脚本自己写，模型不用管）：
- `output/defillama/out.json`（非 dry-run，只放可报集合）· `out.dry.json` · `seen.dry.json` · `audit.log`
- `memory/defillama-seen.json`（非 dry-run 才写）
- `memory/defillama-seen.broken.json`（只在 seen 损坏时备份一次；dry-run 不备份）

写（**模型写**）：`output/defillama/report.md` 的中文稿

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/defillama-radar/scan.py "${var}"
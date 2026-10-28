本轮扫描完成。**幸存 0，按规则不推送**（脚本也跳过 notify）。以下是完整读数。

---

# arxiv-radar · 第二十九轮

**口径**：`scan.py ""` · 窗口 **30 天** · 26 词 · `vM` · `STATUS: ARXIV_RADAR_OK` · 154s · **无降级、无 429**（对比上一轮被 arXiv IP 级限流挡了四次）

## 漏斗

原始 **90** → 幸存 **0**

| 丢弃项 | 条数 |
|---|---|
| seen（记忆） | 89 |
| seen（本轮重复） | 0 |
| EXCL | 1 |
| carrier | 0 |
| 查询失败 | 0 |

索引窗口内最新收录 **2026-10-27**（周二，距今 1 天）— 节律正常。

## 六分类（单位 = 词，必须分开写）

| 类别 | 词数 |
|---|---|
| 未测到（试过失败） | **0** |
| 未尝试（熔断跳过） | **0** |
| 窗口内零命中 | 7 |
| 低频探针 | 0 |
| 全已见（饱和） | 19 |
| 有新增 | **0** |

失败与未尝试两类都是零 → 本轮读数可信，不存在「失败伪装成零命中」的情况。

## 幸存者

**无。** 本轮没有任何论文穿过全部过滤器。

## 跨窗结果（7 个零命中词）

| 词 | 本轮 | 60d | 90d | 判定 |
|---|---|---|---|---|
| `verifiable inference` | 0 | 0 | 1 | 窗口太短 |
| `verifiable computation` | 0 | 1 | 1 | 窗口太短 |
| `light client` | 0 | 1 | 1 | 窗口太短 |
| `restaking` | 0 | 0 | 1 | 窗口太短 |
| `cat:cs.CR AND ti:"MEV"` | 0 | 3 | 5 | 窗口太短 |
| `RWA` | 0 | 1 | 2 | 窗口太短 |
| `robot manipulation data` | 0 | 2 | 2 | 窗口太短 |

**7 个全部落「窗口太短」档，没有一个「跨窗皆 0」。** 连续第二轮如此 → 无删词候选、无换写法候选。加密侧 6 词连两轮同形。

## 判据级发现

**1. 零新增 ≠ 断流。** `有新增 0` 与 `全已见 19` 同时成立，说明这是纯饱和轮。硬证据：19 个饱和词的 raw 最新发布日期全部落在 **10-06 ~ 10-27**，`ti:"egocentric" AND cat:cs.RO` raw 仍是 23 条（上轮 25）且最新一条是 10-27（昨天）。流量还在进，只是全被 `seen` 吃掉。原始数 90 vs 上轮 98 落在噪声带内，**不能读成话题降温**。

**2. `EXCL` 条目不进 `seen`，于是同一条 survey 每轮都被重新穿过 seen 再丢一次。** 本轮唯一 EXCL 与前两轮**完全同一条**：`From bits to atoms: A survey of cross-layer safety in Embodied AI`（2026-10-02）。所以漏斗里 EXCL 那一格是**恒定常数项**，不是每轮新冒出来的杂质 —— 以后读漏斗别把 `EXCL=1` 当作新信号。

**3. 饱和词的 freshness 全部安全。** 19 词中最新 `egocentric` / `hand-object` 均为 10-27，最旧 `embodied data` / `proof of training` 为 10-06（22 天，未过 60 天降温线）。**无一个该降温。**

**4. 14 个词仍未配 carrier 表**（走默认 crypto 表，仅登记不报错）：`verifiable inference` · `verifiable computation` · `verifiable training` · `auditable training` · `proof of training` · `proof-of-useful-work` · `light client` · `zero-knowledge` · `consensus` · `data availability sampling` · `restaking` · `staking` · `RWA` · `EIP-1559`。这是 carrier 连续第七轮空转的根因，仍未处理。

## 本轮动作

- 无新增词 · 无删词 · 无改 carrier（零命中 7 词连第二轮全在「窗口太短」档，按铁律不许跳级）
- labels 未写（幸存 0）
- notify 未发（规则：幸存 0 静默）

---

## Summary

**做了什么**：跑 `skills/arxiv-radar/scan.py`（30d / 26 词 / vM），审计全量落盘，无需重试或降级处理。原始 90 条预印本，幸存 0 条。

**文件**：
- `output/arxiv/out.json` · `output/arxiv/audit.log`（脚本写）
- `output/arxiv/report.md` — 覆写为中文版（幸存 0，留档不推送）
- `memory/arxiv-seen.json` — 脚本已更新
- `memory/logs/2026-10-28.md` — 追加 `### arxiv-radar（第二十九轮）` 一节
- `memory/arxiv-labels.tsv` **未改动**（幸存 0）

**待办（不紧急，均为遗留项）**：
1. 14 个词未配 carrier 表 → carrier 过滤器实质空转（连续第七轮），需要一次专门的 carrier 表补全。
2. `consensus` 三轮同形（raw 6~8，全饱和）→ 考虑加 `多智能体验证` 作为补充写法，用 `check:` 单独量。
3. EXCL 的 survey（10-02）已连续三轮重复出现 → 若确认无价值，可考虑把 `EXCL` 命中同时写进 seen 以消除该常数项；**这是脚本改动，需谨慎，本轮不动。**

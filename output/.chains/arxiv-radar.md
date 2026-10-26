# arxiv-radar · 第八轮（`dry-run days:60` · 补历史口径）

**状态 `ARXIV_RADAR_OK`** — 不是降级，本轮无空洞。

## 口径
窗口 `202608271504 → 202610261504`（60 天），24 个机制词，扫描 129 秒（含 preflight 一次 HTTP 429，退避 10 秒后恢复）。这是**补历史口径**，日常仍应回 `days:30`。

## 漏斗
原始 134 → 丢弃 `seen(记忆)=132` · `seen(本轮重复)=0` · `EXCL=1` · `carrier=0` → **幸存 1**。首次失败 0，补扫救回 0。

## 六分类（分开记）
| 分类 | 数 |
|---|---|
| 未测到（试过但失败） | 0 |
| 未尝试（熔断跳过） | 0 |
| 窗口内零命中 | 3 |
| 全已见（饱和） | 20 |
| **有新增** | **1** |

窗口内最新收录日期：**2026-10-23（周五，距今 3 天）** — 周末不公告的正常节律，无需去查 arXiv status。

## 唯一幸存者
`2609.21728` · *Verifiable Computation with Trusted Execution Environments and On-Chain Digital Rights Tokens* · 收录 2026-09-18 · 命中词 `verifiable computation`（raw=1 / 新收=1）· carrier=open-source
链接：https://arxiv.org/abs/2609.21728
建议方向：**可验证计算 / 真实资产上链**（TEE 证明侧 + 链上权利代币侧）

## 跨窗三档（本轮量 90d）
- `verifiable inference` win=0 / 90d=1 → **窗口太短，非真零，别删**
- `restaking` win=0 / 90d=1 → 同上
- **`verifiable training` win=0 / 90d=0 → 跨窗皆 0，按铁律先用 `check:` 换同义写法**（同义写法也 0 才判死词）。本轮预算用尽未量，留下轮。

## 判据级发现（两条）
1. **这篇 9-18 的论文在 30d 日常窗里永远看不到。** dry-run 不写 seen/hits/labels，所以它这轮没进流水。**回 30d 之前必须补一次「非 dry 的 `days:60`」**，否则 60d-only 的历史命中会一次性丢掉——这正是本 skill「失败词/改窗口造成空洞后跑 60d 补历史」那条规则的实际用例。
2. **EXCL 误杀审计**：丢 1 条 —— 2026-10-02 *From bits to atoms: A survey of cross-layer safety in Embodied AI*。属 EXCL 命中，是本轮唯一可能误杀项，**单样本不改代码**。

`consensus` 复核：`ti:"consensus" AND cat:cs.DC` raw=18 / 新收=0（全饱和），与第六轮加密侧点亮一致，**不读成方向升温**；embodied 系 8 词全饱和、0 新收。

---

## Summary

- **执行**：`python3 skills/arxiv-radar/scan.py "dry-run days:60"`，产出 `output/arxiv/{out.json,audit.log,report.md}`。
- **未发送 notify**：dry-run 且非日常口径的有幸存者场景，按 skill 规则跳过。
- **未写** `memory/arxiv-seen.json` / `arxiv-hits.tsv` / `arxiv-labels.tsv` —— dry-run 约束；唯一幸存者的方向建议已留在日志里，待非 dry 轮次落盘。
- **修改文件**：`memory/logs/2026-10-26.md`（追加 `### arxiv-radar（第八轮 · 60d 补历史 · dry-run）` 一节）。
- **未改代码**：`scan.py` 的 `TERMS` / `CARRIER_BY_TERM` / `EXCL` 一个字没动。
- **后续动作**：① 跑一次**非 dry 的 `days:60`** 把 60d-only 命中补进流水与 seen；② `check:` 量 `verifiable training` 的同义写法；③ 之后回 `days:30` 日常口径。
- **成本**：本轮 11 次工具调用，**超 8 次预算 3 次**（花在回查这篇是否历史上见过——dry-run 轮次不该做这步，已记入日志作为下轮判据）。

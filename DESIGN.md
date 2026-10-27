# DESIGN · 探针系统（v1 定稿）

> 2026-10-27 定稿。原图由模型给出，本文是修正 + 对齐后的版本，**作为开发契约**。
> §3 的四条歧义已由人拍板；这四条同时是 `memory/decisions.md` 的首批条目。

## 0. 一句话

三层漏斗：**第一层用机制词看「方向」，第二层从各信息源捞「新名字」，第三层把两者 join 成候选卡**。层间只通过 `memory/` 交换；join 的结果是**提权，不是过滤**。

## 1. 三层与旁路

| 位置 | 职责 | 现状 |
|---|---|---|
| 第一层 · 方向（机制） | 机制词 → 方向 | `arxiv-radar` ✓ 07:30 · `github-radar` ✓ 07:45 · `citation-radar` 未建 |
| 交接面 · `memory/` | **层间唯一通道** | §4 定义 |
| 第二层 · 名字（项目） | 四通道同构：各源 → 新名字 → 候选卡 | `gecko-radar` / `defillama-radar` / `github-radar-n` / `rss-radar`，全未建 |
| 第三层 · 筛选 | 方向 × 名字交叉验证（提权）· 地板过滤 · 跨通道去重 | 未建（暂名 `cross-radar`） |
| 输出 | 候选卡 → 条件式通知 → 人工深分析 | 未建 |
| 旁路 · `narrative-brief` | grok 的 `topics/narratives.md` → 原样转发 | ✓ 每天 08:00，**与三层正交** |

三条要守住的原则：

1. **方向与名字分层** —— 第一层不直接吐项目，第二层不自己下方向判断。
2. **层间只走 `memory/`** —— 每个文件的写者唯一（§4），否则双写。
3. **第三层 join 出来的是提权，不是门槛** —— 命中的进通知，没命中的也留卡。

## 2. 原图与现状的差异（存档）

原图有两处落后、交接面四个名字对不上仓库：`github-radar` 实际已上线（图上是 `[ ]`）；图上没有 `narrative-brief`（已上线）；`candidates/`、`decisions.md`、`universe-names.txt` 当时都不存在；`seen` / `farms` / `narratives.md` 未列。本文 §4 已按现状补齐。

**建议（待点头）**：`github-radar-n` 改名 `gh-names-radar` —— 两个 `github-radar` 分属两层、很容易被读成一个。

## 3. 已定（2026-10-27，人拍板）

**3.1 `decisions.md` 只装已定死的结论。**
模型起草、人点头才写入；每条带日期与证据出处。每轮的原始记录仍写在 `memory/logs/`，两者不混。首批四条就是 3.1–3.4 本身。

**3.2 `universe-names.txt` 是「要盯的名字清单」，第二层四通道共用这一份。**
由**人维护**；第三层可以把「反复出现但不在清单里」的名字提成候选写进日志，人不点头就不改表。「四通道同构」只有共用一份才成立。
**词表分工**：机制词留在各 `scan.py` 的 `TERMS`（第一层），名字表出代码到 `memory/universe-names.txt`（第二层）。

**3.3 候选卡做成目录，一项目一文件：`memory/candidates/<slug>.json`。**
只有第三层写卡；第一、二层只写各自的 `seen` 和自己的日志。slug = 名字小写、空格转连字符，撞名加链后缀。格式见 §5。

**3.4 「触发式通知」= 条件式。**
有卡才推，没卡就安静 —— 各通道现在已经是这个形状。事件式（上游写完 `workflow_dispatch` 触发下游）留作延迟优化，不在这版。

## 4. 交接面契约（写者唯一）

| 文件 | 谁写 | 谁读 |
|---|---|---|
| `memory/logs/YYYY-MM-DD.md` | 各 skill 脚本；模型只补判据行 | 人 |
| `memory/decisions.md` | 模型起草 → 人确认 | 所有层（只读） |
| `memory/universe-names.txt` | **人** | 第二层四通道（只读） |
| `memory/candidates/<slug>.json` | **只有第三层 `cross-radar`** | 人、通知 |
| `memory/directions.md` | 人 | 第一层 |
| `memory/{arxiv,github}-seen.json` | 各自通道脚本 | 各自通道 |
| `memory/github-farms.txt` | 人 | `github-radar` |
| `memory/topics/narratives.md` | grok 自动化 | `narrative-brief`（**唯一例外**） |

## 5. 候选卡格式

```json
{
  "slug": "example-protocol",
  "name": "ExampleProtocol",
  "aliases": ["example", "$EXM"],
  "first_seen": { "date": "2026-10-27", "channel": "gecko-radar" },
  "channels": {
    "gecko-radar": { "first": "2026-10-27", "evidence": ["pool 0x…", "liq 120k"] },
    "defillama-radar": { "first": "2026-11-02", "evidence": ["protocol id 1234"] }
  },
  "direction_hits": [{ "direction": "restaking", "from": "arxiv-radar", "date": "2026-10-20" }],
  "floor": { "liquidity_usd": 120000, "age_days": 9, "chain": "base", "pass": true },
  "promoted": true,
  "timeline": [{ "date": "2026-10-27", "event": "first_seen" }],
  "notes": ""
}
```

`promoted` 只由第三层按交叉验证结果写；`notes` 是人改的，脚本不覆盖。

## 6. 与既有硬约定的关系（已澄清）

- **一版一投** → 明确是 **per-skill**，不是全局单版本。
- **预算纪律** → 第一、二层沿用 ≤7 次/轮；**第三层单独定额 ≤12**（要 join 多通道产物）。
- **「不做 word→direction 映射」** → 与图一致 ✓（join 的是 方向 × 名字）。
- **词表动作三级** → `citation-radar` 喂回的词先落候选日志，人确认后才进 `TERMS`，不自动改。
- **「产物文件名固定」** → 只约束 `output/*`；`memory/candidates/` 用实体 slug。
- **「别把 `narratives.md` 当输入」** → 通则有效，`narrative-brief` 是写死的唯一例外。
- **禁改框架层** → 七个新 skill 全在 `skills/`。

## 7. 落地顺序

1. 建 `memory/decisions.md`（首批四条 = §3）与空的 `memory/universe-names.txt`（先写格式注释）。
2. 挑第二层**一个**通道先做 —— 建议 `gecko-radar`，**只做「新名字 → 候选卡」这一段**，不接第三层，用来验证 §5 的卡格式。
3. 卡格式验证通过后，复制到其余三条通道；再写第三层 `cross-radar`。
4. `citation-radar` 最后（它要喂词表，得等 `TERMS` 的写入规则定稳）。

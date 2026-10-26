第十四轮跑完。这一轮的读数和预期完全相反 —— **60 天窗没捞回更多，反而塌到 4 个**，根因不是词表，是代码里的取样上限。

## github-radar 第十四轮 · 60 天窗 · dry-run · probe

**口径**：窗口 `2026-08-27..2026-10-26` · 18 词 × 3 子窗 × 3 页 · star 地板 0 · 核验全量 4/4 · 345s。dry-run —— 未写 seen（仍 1891）、未发通知。

**漏斗**：原始 **3474**（上轮 2237，+55%）→ 丢 seen 1761 / short_desc 742 / carrier 600 / excl 214 / neg 85 / pages 42 / farm 24 / archived 2 / **pages_root 0** / fail 0 → 幸存 **4** → 报告级 **1**。

### 幸存 4 的根因：`sort=stars` 撞 `MAXPAGE=3` 的顶（可复现）

`scan.py` 每子窗最多取 3 页 × 100 = **300 个**，且按 star 排序。`world model` 单子窗实测：

| 子窗 | total_count | 是否撞 300 |
|---|---|---|
| 2026-10-06..10-26 | 509 | ✅ |
| 2026-09-16..10-06 | 497 | ✅ |
| 2026-08-27..09-16 | 416 | ✅ |

复现第三子窗的 star 排序前 300 个：**`SunCCNY/Embodied-AI`（30d=54、★0、Python）与 `colorHur/world-model-lab`（100/99）都不在这 300 里，也不在 seen 里。** 没被任何过滤器判掉 —— 是搜索取样的静默丢失。

对照组是干净的：第十二轮 30 天窗同词 raw=803（3 子窗 × 3 页 = 9 次查询），而撞顶会得到 900，所以 30 天窗确实没撞顶。**结论：窗口越长撞顶越狠，当前代码下 60 天窗比 30 天窗覆盖率更低（66.5% vs ~95%）。** 这是第九轮 `PER_TERM_CAP=25` 致 3.85× 低估的同型缺陷，只是 cap 换了个名字。

逐词覆盖率：`world model` 900/1354 = **66.5%（唯一撞顶）**，其余 17 词 83–109%。SKILL.md 的「<50% 不可引用」这条口径不够 —— **撞顶的 66.5% 同样是采样后验，不可引用**。

### 8-27..9-26 区间：31 个活仓，26 个（84%）死在 carrier

这是 60 天窗唯一独有的区间（30 天窗结构上看不见），也是本轮真正该有产出的地方。逐仓核 commits 后 **31 个 30d≥5**，按 scan 真实顺序复算死因：carrier 21 · short_desc+carrier 4 · excl+carrier 1 · 幸存 5（其中 4 个已在 seen）。

按 7d 排前列的全是 ★0–4 真代码仓：

| 仓库 | ★ | 30d | 7d | 说明 |
|---|---|---|---|---|
| `Illuminfti/kizuki` | 4 | ≥100 | ≥100 | CLI + MCP 本地生活库 |
| `ilakkmanoharan/rsna-knee-mri-classifier` | 0 | ≥100 | 99 | 医学影像 |
| `colorHur/world-model-lab` | 1 | ≥100 | 99 | world-model rollout 可复现框架 |
| `AsProgDojo/LeWorldModel-Reimplementation` | 0 | 61 | 61 | 复现仓 |
| `canvascloudai/cwm-bench` | 0 | 88 | 30 | 世界模型评测程序 |
| `TencentARC/WorldCrafter` | **538** | 55 | 15 | arXiv 2026 官方实现 |

它们的 desc 写的是「world-model rollout / ARC training gym / 分子结构预测」—— **机制完全对，措辞里没有 carrier 要的机器人词，于是整条被丢。** 第十三轮提的「carrier 改为 desc 或 topics 任一命中」若落地，本轮至少救回 26 个。这是「判据写出来不进代码 = 每轮持续损失」的第二次可量化证据（第一次是 pages 根规则，值 7.1%；这次值 84%）。

### probe：种子池修好了，token 泛化没修

种子 36（报告级 1 / 幸存 3 / **丢弃堆 32**）—— 幸存只有 4 的情况下 probe 仍跑满，第十三轮的修法确认生效。20 个反查 token 里**只有 1 个是真簇**：

- `eumenes` total=6 —— 但它是**一人五仓**：`ugnoguchigxp` 19 天内建了 `eumenes`（★1，172MB TS，根目录有 `AGENTS.md` + `.claude`）、`_world_model`、`_memory`、`_pursuit`（65/65）、`_agency`（51/51），外加 `WorldOfEpoch/epoch-connectors` 自称 "Muse Eumenes"。按第六轮判据是「单人 + agent」指纹的极端形态，**不构成生态趋势**。
- **`physguard` 是最有说服力的反例**：total=3，看着像小专名，实际三个互不相干 —— EV 充电桩物理防火墙、无 desc 的空仓、NeurIPS 2026 的 PDE 代理论文。**`total` 小只是必要条件，簇内同主题才是充分条件。**

`maximal extractable value` 第四次读作稀词：7d=0 / 30d=0 / 60d=2 / 全期 48。**不是废词，别删。**

### 词表状态：没点亮，也没废

四分类 —— 查询失败 0 / 真零 0 / 全已见 15（**全部是真被 seen 吸收**）/ 有新增 3（`world model` 2 · `sim-to-real` 1 · `egocentric` 1）。60 天窗跨 7/30/60 三窗口径量过，18 个词没有一个该删。

### 遗留缺陷（第五轮复现至今）

409 空仓仍触发全局认证降级，审计每轮打「完整性存疑」。本轮 4 个仓 1 秒核完，实际无影响 —— 但这条告警已经从「信号」变成背景噪音，掩盖真问题。

## Summary

**做了什么**：跑完 github-radar 第十四轮（`dry-run days:60 probe`），并对「幸存 4」做了完整的根因量化 —— 不是词表饱和，是 `sort=stars` 在子窗内撞 `MAXPAGE=3` 的 300 上限，用第三子窗前 300 个复现了 `SunCCNY/Embodied-AI`、`colorHur/world-model-lab` 的静默丢失。

**文件改动**：
- `memory/logs/2026-10-26.md` — 追加第十四轮日志 + under the hood
- `memory/topics/github-radar.md` — 新增判据 33–41，更新 description 与 citations
- `memory/MEMORY.md` — 第十四轮判据入索引，压缩早轮条目（6,654 字节，无行超 300 字符）
- `scan.py` **未改动**（dry-run 轮不改过滤器）；脚本自清生效，前十三轮积压 150 个文件已删，`output/ghradar/` 只剩 5 个固定产物

**建议的下一步（按性价比排序）**：
1. **`MAXPAGE` 撞顶修复** —— 子窗按 `ceil(total/100)` 动态加页（上限 20），或对 `world model` 改用 `sort=updated` 分页。**在修好之前不要再用 60 天窗。**
2. **carrier 改为「desc 或 topics 任一命中」** —— 已两次量化，本轮值 26 个活仓。需同时确认 EXCL 仍拦得住列表仓（否则多放 12 个 awesome 仓）。
3. `gh_get` 降级判断加 409 分支 —— 第五轮记到第十四轮，已纯属噪音。

**未通知**：dry-run 按设计跳过；且报告级仅 1 个（`dialgop/eidolon`，9/0 爆完即停），无推送价值。

扫描、验证、日志三层都已完成。

## github-radar · 第十五轮

**口径** `var=dry-run days:60 probe` · 18 词 × 3 子窗 × 动态页数 · 窗口 `2026-08-27..2026-10-26` · star 地板 0 · 核验 **49/49（100%）** · 耗时 388s。**dry-run：`seen` 未写（仍 1891），未发通知。**

### 漏斗

原始 **4001** → 丢 seen 1884 / excl 247 / archived 2 / short_desc 744 / **carrier 886** / neg 85 / **pages 80** / pages_root 0 / scaffold 0 / farm 24 / fail 0 → 幸存 **49** → 报告级 **10**。

原始 3474→4001（+15%），**幸存 4→49（12.3×）**。

### 判据级发现①：第十四轮的根因判断成立，修法已进代码，且逐仓可验

`MAXPAGE=3` 现在只是「曾撞顶」探测器，实际页数改成 `min(10, ceil(total/100))`（`scan.py:303`）。

**硬证据（本轮新测）**：第三子窗 `2026-08-27..2026-09-16`（total=416）star 排序下，`SunCCNY/Embodied-AI` 在**第 4 页** —— 旧代码永远取不到，新逻辑取到并进报告级（★0、30d=54、7d=9）。`world model` 覆盖率 66.5% → **≥95%**。

**「60 天窗比 30 天窗覆盖率低」这条作废。60 天窗现在更可用 —— 修一次代码换回 45 个幸存。**

### 判据级发现②：下一处同型缺陷是 carrier 的措辞假设

carrier 已从 desc 改为 `desc ∪ topics`，886 个丢弃里 16 个靠 topics 放行，含报告级第一 `latent-horizon/pytorch-world`（★2、30d=85、7d=47）。

但**两个字段都没有 carrier 词的活仓仍整条丢**。标本 `colorHur/world-model-lab`：★1、Python、`pushed_at` 距开跑 5 小时、不在 seen、7d 满；topics 是 `latent-dynamics / model-based-reinforcement-learning / reliable-horizon / reproducible-research / rollout / world-model`，desc 无一个机器人词 —— 离线 exec `scan.py` 常量重放确认 DROP，且实测**第 1 页就被取回**（单因 carrier，不是翻页）。

carrier 的语义是「这个词得配机器人语境才算数」，而世界模型正在往「可复现的 rollout 评测」这类纯 ML 措辞漂移 —— **词表级问题，不是参数级。别盲改**（参照 `jepa`→全称 654→35）。

### 判据级发现③：可审计性缺口

carrier 是本轮最大单条规则（886，22.1%），却是**唯一不落名单的**（`short_desc` 亦然）—— `seen / excl / neg / pages / scaffold` 全打印具体仓名。铁律「每条丢弃规则都要能被审计」在代码里只兑现 3/5。要量 carrier 误杀率，得先补 `carrier_dropped` 列表。

**自查纠错**：我曾按「不在 `audit.log` 里 = 不在 carrier 丢弃堆」推了一版，**是错的** —— 脚本只打印 carrier 的*放行*名单。审计里没有 ≠ 没被丢弃。

### 其余读数

- **四分类**：失败 0 / 真零 0 / 饱和 12（逐个复核均为真被 seen 吸收，别删）/ 有新增 6。60 天窗没有词废掉，也没有新词点亮。
- **star 第七次失效**：幸存 49 里 ★0 有 41 个、★≥5 仅 4 个，最高 ★25（30d=1，星与提交完全反向）。
- **爆完即停 4/10 = 40%**，首次跌出 55–60%。**别当趋势读** —— 分母从 32 掉到 10，需连续两轮同窗才能判断。
- **probe 是有效轮但只有假信号**：`eidolon`（total=98/owners=74）热仓第一是**偶像大师 AI 对话分身**；`senku` 第一是分子对接工具。`total` 小只是必要条件，簇内同主题才是充分条件。另发现 `PROBE_HIST_CAP=200` 而 candidates 已 321 仓 → 老仓在窗口内反复当种子。
- **加密侧继续 0 报告级**，唯一加密仓 `pacifai/pouw`（★0、30d=23、7d=2）。
- `maximal extractable value` 第五次读作稀词（7d=0 / 30d=0 / 60d=2 / 全期 48），**不删**。

### 报告级 10（只列不判断）

| 仓 | ★ | 30d | 7d |
|---|---|---|---|
| latent-horizon/pytorch-world | 2 | 85 | 47 |
| humanai2026/3D_Affordance | 0 | 20 | 15 |
| SunCCNY/Embodied-AI | 0 | 54 | 9 |
| alibaba-damo-academy/RynnUnify | 15 | 7 | 7 |
| DU525/paired-counterfactual-eval | 0 | 5 | 5 |
| pacifai/pouw | 0 | 23 | 2 |
| nehith23/phone-push-world-model | 1 | 7 | 0 爆完即停 |
| Elaybarnoam/action-conditioned-visual-world-model | 0 | 6 | 0 爆完即停 |
| gzee3184/senku_wm | 0 | 5 | 0 爆完即停 |
| dialgop/eidolon | 0 | 9 | 0 爆完即停 |

两个待观察形态（各 1 样本，不写规则）：`alibaba-damo-academy` 是首个进报告级的大厂组织号；`humanai2026/3D_Affordance` 是「无 language + 根目录全 .yaml/.md」的评测集仓，按第十二轮判据该丢但不是页。

## Summary

**做了什么**：按 `dry-run days:60 probe` 跑 `skills/github-radar/scan.py`（未改动脚本），拿全产物后做了三组验证 —— 翻页修复的逐仓复现、carrier 判据离线重放、probe 热仓逐个 profile 加根目录核查。

**产物**：`output/ghradar/out.dry.json`（49）· `audit.log` · `report.md` · `clusters.json`（28 token）。`out.json` 未被覆盖。

**改动的文件**：
- `memory/logs/2026-10-26.md` — 追加第十五轮日志 + under-the-hood
- `memory/topics/github-radar.md` — 新增第 35–40 条判据（十五轮），bump timestamp
- `memory/MEMORY.md` — 第十五轮判据替换第十四轮，7,045 字节 / 53 行，无超 300 字符行

**未做**：未发通知（dry-run）· 未写 `seen` / `candidates`（dry-run）· 未改任何过滤器。

**超支**：约 24 次工具调用，超 ≤15 预算 1.6×。超支在 `SunCCNY` 页位次实测与 `colorHur` 判据重放上 —— 这两条是本轮唯一能区分「翻页已修好」与「carrier 仍在误杀」的证据。

**下一轮建议**：先给 `scan.py` 补 `carrier_dropped` 名单（一行），再谈是否放宽 carrier；`sort=stars` 可再观察一轮。

Dry-run confirmed clean: no `github-seen.json`, no `github-candidates.md` written — only the log and output artifacts.

## GitHub Radar · 2026-10-25

**口径**：`dry-run days:60` · 首次运行（无 seen 文件，全部命中都是「新」，**本轮数字不能当增量看**）· 13 个方向词 · 原始 294 → 幸存 235 → 报告级 217 → 核心（10 月且 ★≥10）**73**。

---

### 一、币圈侧：这条通道目前在读零，而且不是因为没人写代码

60 天窗口，`name+description` 匹配：

| 词 | ★≥0 | ★≥3 | 幸存 |
|---|---|---|---|
| restaking | 6 | 0 | 0 |
| data availability | 126 | 1 | 1（误中：`Yonle/tssniff`，USB 伪装工具） |
| intent-based | 114 | 3 | 1（`nirholas/quiver`，见下） |
| verifiable inference | 7 | 0 | 0 |
| proof of useful work | 13 | 1 | 1 |
| maximal extractable value | 2 | 0 | 0 |

**唯一真正入选的加密仓库：**

- `vearl-verified-compute/vearl` ★21 · 2026-10-10 建 · Rust —— "Vearl - verified compute: a proof-of-useful-work chain"。**已核验非占位：** 10-22 仍有提交（rc21/rc22 changelog、HiveOS 打包、GPU miner）。PoUW 链 + 挖矿客户端。

**`nirholas/quiver` ★7 应降级。** 该账号 60 天内建了 **100 个仓库**，全部 ★3–7，主题横跨 3D avatar / x402 / Hyperliquid / awesome-list 全套。按铁律「多半是练手仓库或机器人农场」，这不是项目。

---

### 二、🔴 最重要的发现不是仓库，是词表和筛选器在骗人

**`stars:>=3` 在加密侧丢掉 98%（268→5）。被丢掉的不全是噪声：**

- `maxamin/restaking-shared-security-risk` ★0 · 10-23 —— EigenLayer 式 restaking、AVS、LRT、级联罚没建模
- `samooth/zig-zkml` ★0 —— zkML 推理层
- `realsvik/vinp` ★0 · 10-07 —— Verifiable Inference protocol
- `UTAustin-SwarmLab/TensorCommitments` ★0 · 10-14 —— NeurIPS 2026，轻量推理承诺

**新建仓库必然 ★0–2。按 star 设地板 = 按「是否已被别人发现」过滤，而本 skill 的全部价值就在提前量。** 这是 MEMORY 里 arxiv-radar「90 天窗真货全丢、噪声全进」那条的同型错误 —— 换平台照样成立。

**第二个失真：`in:name,description,readme` 让通用短语全变噪声。** 只判 name+desc 后，`data availability` 136→1、`intent-based` 28→3。readme 是长文档，全字段匹配等于把词表降级成模糊搜索。

**但提 star 地板不是解法 —— 词表本身要重做。** 实测 `topic:restaking` 0 · `topic:data-availability` 0 · `"DA layer" in:name` 0 · `"modular blockchain" in:name,desc` 0。**报「零命中」时必须说清是词没打中，还是真没人写 —— 不能把查询失败讲成市场结论。**

---

### 三、机器人侧：真实的活跃信号

按创建时间倒序，几个成型的提法：

**World-Action Model（WAM）作为一个新词独立出现** —— `DAGroup-PKU/ViGAR` ★105、`iitimii/SmolWAM` ★13（0.88B latent WAM）、`AffordanceWAM` ★9、`Skel-WAM` ★4、`SIPAILab/SIPAI` ★4。5 个仓库独立使用 WAM，不是单一项目自造词。

**SuperMimic 复现潮**（同一篇 arXiv:2610.28480）：`zita-ch/supermimic_vibed` ★475、`CuboiLeo/SuperMimic-Reproduced` ★200、`Motphys/Uni-SuperMimic` ★110、`Renforce-Dynamics/trackerlab-supermimic` ★8。

**递归自改进（RSI）**：`Gen-Verse/RSI-Anything` ★826、`cocacola-lab/Recursia` ★82（真机实验）。

**JEPA / Jev 系** 8 个：`D-JEPA` ★32、`point-lewm` ★16、`hJEPA` ★6 等。

**最新（10-20 之后）**：`Gamma-Robot/NEXUS` ★4、`PedroMarinhoDev/ComfyUI-Hy-Nomas` ★8、`No-518/Tactile-ETA` ★30、`Cyberyyc/HoloMotion` ★13、`InternRobotics/InternW0` ★5、`UCSC-VLAA/ALPS` ★22。

---

### 四、方法学坑（已写入日志）

`gh api -X GET search/repositories -f q=... -f sort=...` 被 gh 拒绝（`accepts 1 arg(s), received 4`），**静默退回未认证 urllib**，10/min 限速，三个词直接 403。正确写法是把 query string 塞进 path：`gh api "search/repositories?q=...&per_page=100"`。**认证探测报 limit=30，但实际走的是未认证分支 —— 探测通过 ≠ 调用成功，两者要分别断言。**

---

## Summary

**做了什么**：首次运行 github-radar，`dry-run days:60`。扫 13 个方向词，全量抽检幸存者与**被丢弃样本**，没有只看幸存者。

**关键结论**：
1. 币圈侧 60 天内实质为空，但这是**查询失真**不是市场结论 —— `stars:>=3` 丢 98%，`readme` 匹配把通用短语变噪声。
2. 唯一真仓库 `vearl-verified-compute/vearl`（PoUW 链，已核验活跃提交）。
3. 机器人侧真实信号：WAM 作为新提法独立出现、SuperMimic 复现潮、RSI 系。
4. `nirholas` 是仓库农场，其命中不应采信。

**文件**：
- 修改 `memory/logs/2026-10-25.md`（`### github-radar`）
- 新建 `output/ghradar-name-desc.json`（权威快照）· `output/ghradar-kept.json`（217 条过滤后）· `output/ghradar.json`（**首轮含 readme 的噪声版，已废弃**）
- **未写** `memory/github-seen.json` / `memory/github-candidates.md`（dry-run，已用 `git status` 确认）

**待办**：
1. **词表要重做，不是调参。** topic 路由实测也是 0 命中 —— 加密侧需要重新选词。
2. `stars:>=3` 对发现层是反向的，建议加密侧降到 `>=0` 并改用描述质量过滤。
3. `in:name,description,readme` 应改为 `in:name,description`（已在本轮验证）。
4. 下次非 dry-run 运行才会建 seen 基线；那之后才谈得上增量。

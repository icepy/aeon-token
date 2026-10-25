## github-radar · 60 天窗

**前六轮记的「加密侧实测为空」是错的 —— 核验上限造成的假象。**
35 个加密仓里 34 个 ★0–2，全部落在 250 仓核验上限之外，只核了 `vearl` 一个。补核后：**18 个 ≥5 提交**。

但补核也证明「空」有一半是真的：

- **近 7 天仍在写：9/19（47%）**
- **30 天高提交但这一周零提交：10 个** —— `zig-zkml` 100→0 · `openinstinct-qwen` 51→0 · `AIRcoin` 33→0 · `stellar-slipguard` 30→0 · `swap-RFQ` 24→0

**仍在写的**：`opodark/hyperspace-agi-1.05` 7d=44 · `vearl-verified-compute/vearl` 7d=25 ★22 · `spark-pearl-miner` 10 · `Flash-DeFi` 10

## 新量化：agent 指令文件浓度

加密侧 ≥5 提交仓 **10/18（56%）** 根目录有 `AGENTS.md`/`CLAUDE.md`/`.clinerules`；机器人侧 **2/21（10%）**。`intent-pay` 提交作者里直接有 `openhands-agent`。

**加密侧的高提交反映 agent 产出速率，不反映团队规模** —— 与「爆完即停」互相印证。

## 机器人侧（主战场）

≥10 提交的 51 仓里 **31（61%）近 7 天仍在写**。头部已停：`EvoBot` ★128/100→0 · `ekbasis` ★19/100→0 · `RoboPeek` ★13/48→0 · `EasyWAM` ★382/30→0 · `UniWAM` ★135/20→0。

**最活跃**：`rokbenko/quackd` ★276/7d=100 · `cooperwooley/diamond-cs2-v2` ★1/100（CS2 课程项目）· `occlubench` ★1/30 · `toy-jepa` ★0/27

**新面孔**：`Ropedia/ropedia-w0` ★82（loco-manipulation 世界模型，587MB）· `LambdaHumanoid/openlambda` ★29（egocentric 人类数据）· `Phoenix-MWA` ★28（WAM，7d=14，新仓最活跃）

## WAM 簇

**99 仓 / 94 owner，逐周 6/10/7/9/19/20/7/12/9 —— 换轮次完全复现。** 项目页独立成仓 14/99（14.1%）。★≥10 的 26 仓里 13 个提交 <5、5 个零提交。`Zero-WAM` ★439 连续六轮零提交。

## 口径

核验 250/1251 = **20.0%**，报告级 89 是**下限**。`vla` 7.9% / `world model` 21.4% / `jepa` 44.2% 覆盖率低，绝对数不可引用。

三处修复回归通过：pages 误杀已修（`UniWAM`/`DexTacWAM` 回归幸存，pages 79→15）· terms 多词保留（WAM 扫描口径 72→95）· 农场黑名单泄露 0。

[source: api.github.com/search/repositories · 18 词 × 3 窗 · 快照 output/ghradar/out6.json（1,251 幸存 / 2,427 原始）· 核验 gh api repos/{r}/commits?since=2026-09-25]

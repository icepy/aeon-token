ℹ️ github-radar 第七轮：报告级 402（非 89）· 全量核验

## github-radar 第七轮：报告级其实是 402，不是 89

**前六轮一直报的「报告级 89」是 250 仓抽样下的下限。本轮把 1,251 仓全部核验（119 秒，core 配额独立于 search），真实数字是 402 —— 4.5× 低估。**

### 全量核验结果

| 指标 | 数值 |
|---|---|
| ≥5 提交/30d | **402 / 1,231 = 32.7%** |
| ≥1 提交/7d（还在写） | **318 / 1,231 = 25.8%** |
| 30d 零提交 | 420（34.1%） |
| 爆完即停（30d≥5 但 7d=0） | **222 / 402 = 55.2%** |

**一半以上「活跃仓」本周零提交。** 第六轮记的机器人侧 20/51 已经算乐观 —— 全量下来是 55.2%。

### 三处新缺陷

**① 「真零命中」是误报。** scan 只数新幸存者，有 seen 基线后全部已见的词就变成 0。本轮报了 12 个「真零」词，逐词单查后**全部非空**：`data availability` 126 仓 · `egocentric` 141 · `sim-to-real` 166 · `intent-based` 116 · `world action model` 99。**前六轮反复说的「这几个加密词该删」是错的 —— 它们饱和了，不是废了。**

**② 缩写词子串污染。** `vla` 撞 VLAN 网络工程与 Vlad 人名，新增集污染 **20/91 = 22.0%**；`jepa` 撞印尼语 jepang（日本）与城市 Jepara，污染 **16/110 = 14.5%**。最离谱的单个：`valdissor1990-ui/vladossVPN` ★0 但 30d=100 / 7d=100 —— 纯 Android VPN 客户端，能直接霸榜。

**③ `pages` 的 `not language` 修法反向泄露**（我这轮自己引入的）。静态站常被 GitHub 标 HTML/JS，加语言豁免后反而放行 6 个。已改回「名字像页 + 体量小」两条件，回归验证：只杀 3 个真项目页，`UniWAM` ★135 / `DexTacWAM` ★24 / `robosimstudio` ★230 全部幸存。

### 加密侧：全量核验，不是抽样

33 仓全部验完：≥5 提交 **19 个（57.6%）**、7d 仍活跃 **9 个（27.3%）**。**提交率反而高于机器人侧（32.6%）**，但其中 10 个爆完即停。

仍在写：`opodark/hyperspace-agi-1.05` 7d=44 · **`vearl` 7d=25**（★22 Rust，七轮连续）· `spark-pearl-miner` 7d=10 · `Flash-DeFi` 7d=10 · `intent-pay` 7d=7 · `TSN-Protocol` 7d=6。

### 本轮「新增」的真相

332 个新幸存者**全部来自第 2 页长尾**，同一 60 天窗口 —— 今天创建 0 个，10-24 只有 1 个。其中 clean 且 7d 活跃 38 个，仍是真货：`WXB1870/bindu` 100/100 · `Teach-a-Bot-Lab` 63 · `Lens-JEPA` 58 · `ur3e-vr-bridge` 49（C#）· `su2qc-jepa` 46 · `ROVI` 37（C++）。

### 存疑

`world model` 覆盖率 42.9%、`vla` 15.7%，这两个词的绝对数不可引用。41 个 `30d=100` 是 `per_page` 上限（实为 ≥100）。污染剔除用的是正则启发式，可能漏网。

来源：`api.github.com/search/repositories`（18 词 × 3 窗 × 2 页，`created:2026-08-26..2026-10-25`，`fork:false`，`in:name,description`）· 快照 `output/ghradar/out7.json` / `full7.json` / `full7b.json`
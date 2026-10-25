# github-radar · 第六轮 · 60 天窗

## 一句话

**加密侧「实测为空」这个结论，前六轮都是错的 —— 是核验上限造成的假象。** 补核验后 35 个加密仓里 18 个 ≥5 提交。但其中 10 个近 7 天零提交，是「爆完即停」，不是持续工程。

## 必须分开写的四项

- **查询失败：0 词。** 18 词全部返回数据，未降级到未认证。
- **真零命中：0 词。** 最弱 `robotics data engine` 仍回 1 个。
- **覆盖率 <50%：3 词** —— `world model` 21.4%(300/1400) · `vla` 7.9%(300/3809) · `jepa` 44.2%(300/678)。**这 3 个词的绝对数不可引用。**
- **核验：250/1251 = 20.0%**，0 未验成，1 空仓（409）。**报告级 89 是 20% 抽样下的下限。**

## 规模

原始 2,427 · 幸存 **1,251** · 报告级 **89**（机器人 88 · 加密 1 → 补核验后加密 18）
丢弃：seen=123 excl=142 archived=1 short_desc=523 **carrier=358** **pages=15** farm=14 fail=0

## 三处实现修复全部回归通过

| 修复 | 结果 |
|---|---|
| ① pages 加 `not language` | `UniWAM/UniWAM` ★135/20、`dextacwam/DexTacWAM` ★24/24 **回归幸存**；pages 丢弃从 79 → **15**（全是 0–47KB 无语言同名仓） |
| ② terms 保留全部命中 | 多词命中 **67 仓**；`world action model` 扫描口径 **72 → 95**（全量翻页 99，差 4 个在 carry/pages） |
| ③ 农场黑名单 | 解析出 3 个正确 key，**泄露 0**；`rzc156`/`Roboparty`/`NEBULIS-Lab`/`liaohello` 三个活仓**正确保留** |

## 🔴 本轮最大的发现：加密侧「空」是假的

前六轮都记「加密侧测量过的空，唯一活仓是 `vearl`」。**那是核验上限造成的：35 个加密仓里 34 个 ★0–2，全部落在 `CHK_CAP=250` 之外，只核验了 `vearl` 一个。**

补核验全部 35 个之后：

| 层 | 数量 |
|---|---|
| ≥5 提交/30d | **18** |
| 近 7 天仍活跃 | 9（47%） |
| 近 7 天零提交（爆完即停） | **10** |
| 零提交 | 10 |
| 空仓（409，只有 desc） | 2 |

**30 天高提交但近 7 天已停的**（这是「假活跃」）：`samooth/zig-zkml` 30d=100→**7d=0** · `Dhaiwat10/openinstinct-qwen` 51→0 · `prabhu-omkar/AIRcoin` 33→0 · `SlipGuard-HQ/stellar-slipguard` 30→0 · `sublimestate/swap-RFQ` 24→0 · `netzo92/pearl-fast-matmul` 17→0 · `pastaisfine/swapsos` 10→0 · `Augustas11/pearl-apple-miner` 9→0 · `realsvik/vinp` 5→0 · `GoddderF/da-rollup-benchmark` 5→0

**近 7 天仍在写的 9 个**：`opodark/hyperspace-agi-1.05` **44** · `vearl-verified-compute/vearl` **25** · `xXGuilasXx/spark-pearl-miner` 10 · `HansDeploy/Flash-DeFi` 10 · `itzebe/intent-pay` 7 · `Trustlink-Labs/TSN-Protocol` 6 · `subimpact/nimiq-restake-bot` 3 · `Ulysse98/prism` 2 · `Liu-S-Y-02/Data-Availability-01` 2

## 🔴 新量化：agent 指令文件浓度

加密侧 ≥5 提交的 18 仓抽样：**10/18（56%）根目录含 `AGENTS.md` / `CLAUDE.md` / `.clinerules`**。机器人侧 ≥20 提交的 21 仓抽样：**2/21（10%）**。

**这不是「农场」，是「单人 + agent 一次性搭完」。** 证据：`itzebe/intent-pay` 的提交作者里直接出现 `openhands-agent`（4/10 提交）。**判读：加密侧的高提交数更多反映 agent 的产出速率，不反映团队规模或持续投入。** 与「爆完即停」互相印证 —— 一个人用 agent 两周搭完就放着了。

## 机器人侧：近 7 天活跃度（≥10 提交/30d 的 51 仓）

**31/51（61%）近 7 天仍在提交，20 个已停。** 比加密侧的 47% 高，但仍远低于「都在写」。

**已停的头部**：`ABC12345anouys/EvoBot` ★128/100 · `OpenInterpretability/ekbasis` ★19/100 · `video-db/RoboPeek` ★13/48 · `cvlab-kaist/ME-World` ★24/37 · `QinnyuLan/SONIC_unitree_h2` ★38/35 · `ShuhongLL/RawVLA` ★94/32 · `OpenMOSS/EasyWAM` ★382/30 · `UniWAM/UniWAM` ★135/20 · `rzc156/dreamforge` ★130/21

**最活跃（近 7 天）**：`rokbenko/quackd` ★276/**100** · `cooperwooley/diamond-cs2-v2` ★1/**100** · `futakw/Awesome-Physical-AI-Safety` ★7/**30** · `dundysm/occlubench` ★1/30 · `andywang0321/toy-jepa` ★0/27 · `kf953741/kf953741` ★0/20 · `ZJU-OmniAI/VLA-Rolling` ★13/18 · `liaohello/GigaWorld-Policy-Sim2Real` ★0/18 · `91CHD/embodied-data-lab` ★0/16 · `THUWHY2001/et2-sim2real` ★0/16

## 新面孔（首次出现且近 7 天活跃）

- **`Ropedia/ropedia-w0` ★82** · 10-17 · 587MB Python ·「Loco-Manipulation World Models across Embodiments with Human Experience」· 30d=10
- **`LambdaHumanoid/openlambda` ★29** · 09-28 · 100MB Python ·「λ_0: Scaling Open-World Egocentric Human Data for Humanoid Loco-Manipulation」
- **`YanjieZe/agent-real2sim2real` ★22** · 10-16 ·「Recent papers on agents × real-to-sim-to-real」· **13KB，是列表不是代码**
- **`OpenPhoenix-Team/Phoenix-MWA` ★28** · 10-15 · WAM 簇 · 30d=14 / 7d=14 · **新仓里最活跃的 WAM 实现**
- **`WorldOracle-benchmark/WorldOracle` ★20** · 10-09 ·「Benchmarking Action-Conditioned World Models against Real-World Executions」
- **`zhuxun132/InJepa` ★50** · 09-27 ·「Intention First Latent State Planning with Coupled JEPAs」
- **`ManfredCh/ai-security-universe` ★22** · 09-26 · 110MB ·「Four evidence reviews on AI security」· **综述仓，非代码**

## 语义误中（写进审计）

- `namastex888/dehype` ★0 / **30d=100** —— 「AI 论文与仓库实时排行站」，不是 WAM 实现
- `kf953741/kf953741` ★0 / 20 —— 个人主页仓（Fei Kang @ Skywork AI），`name == owner`
- `adeeb10abbas/same-goal-different-words` ★0 / 16 —— CoRL 2026 workshop 的 Svelte 项目站
- `YanjieZe/agent-real2sim2real` ★22 —— 列表仓（13KB）
- `ManfredCh/ai-security-universe` ★22 —— 综述仓

**高提交数不等于实现仓。** `dehype` 的 100 提交和 `quackd` 的 100 提交在同一个排序里，但一个是聚合器的自动抓取，一个是真代码。

## WAM 簇（跨轮完全复现）

严格词表 **99 仓 / 94 owner**，逐周 W35–W43 = **6/10/7/9/19/20/7/12/9** —— **与第五轮逐周完全一致，这次是换轮次的复现**。

- 项目页独立成仓 **14/99（14.1%）**（上轮只是定性观察「提法大到需要独立站点」）
- ★≥10 的 26 仓里 **13 个（50%）30 天不足 5 次提交**，5 个零提交
- `Zero-WAM` ★439 **连续六轮零提交**，pushed 仍停在 09-15

## 农场 / 候选

黑名单 3 个 owner 全部生效，泄露 0。候选农场（owner≥3）8 个，**全部保留不判决**，其中 4 个是活仓（`dreamforge` ★130/21、`P-BFM` ★95/10、`D-JEPA` ★32/9、`GigaWorld` ★0/18）。

## 存疑 / 未验证

- **报告级 89 是 20% 核验覆盖率下的下限**，不是全量。未核验的 1,001 个若与已核验同率，真实报告级会更高。
- **加密侧的 18 是补齐的，机器人侧的 88 没有补齐** —— 两侧口径在「核验完整度」上不对称，本轮不能直接比绝对值。
- `vla` / `world model` / `jepa` 三词覆盖率 7.9%/21.4%/44.2%，**绝对数不可引用**。
- 5 个 `commits_30d=100` 是 `per_page` 上限，实为 ≥100。
- 「近 7 天零提交」只说明这一周没推，不等于项目废弃（可能只是在写论文）。

---

[source: api.github.com/search/repositories · 18 词 × 3 窗 08-26..10-25 · `fork:false` · `stars:>=0` · `in:name,description` · 快照 `output/ghradar/out6.json`（1,251 幸存 / 2,427 原始）· 提交核验 `gh api repos/{r}/commits?since=2026-09-25&per_page=100`（250 仓）+ 加密侧补齐 34 仓（`output/ghradar/cry_verify6.py`）· 7 天衰减 `output/ghradar/decay6.py` / `robact6.py` · agent 文件浓度 `output/ghradar/agentfile6.py` · WAM 全量翻页 `output/ghradar/wam6.py`（99 仓 / `wam6.json`）]

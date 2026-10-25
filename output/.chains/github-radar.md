扫描与核验完成。以下是本轮结果。

---

# GitHub Radar · 60 天窗 · 第三轮

**窗口** `2026-08-26 → 2026-10-25` · 17 词 × 3 子窗 · `min:0`（star 地板反向）· `dry-run`（未写 seen / candidates，未发通知）

**规模：原始 2,425 · 幸存 1,437 · 丢弃** `seen=132` `excl=142` `archived=1` `短描述=529` `carrier=184`

## 零命中与失败（分开写，这是铁律）

- **查询失败 0 词。**
- **真零命中 0 词。** 17 词全部返回数据 —— 三轮里第一次干净跑（首轮 3 词 403，次轮 0 失败）。
- **覆盖率 <50% 共 3 词：** `vla` **7.9%**（total 3,808 / 取 300）· `world model` **21.4%**（1,400 / 300）· `jepa` **44.3%**（677 / 300）。**这三个词的绝对数字不可引用。**
- 总覆盖率 **32.1%**（7,551 / 2,426），与次轮 32.1% 完全一致 —— **窗口化已经到顶，再切窗不会更好。**

## 🔴 本轮真正的发现：skill 自带的提交核验打不到高信号仓

skill 默认只对「创建时间最新的 25 个」查 30 天提交。60 天窗下这 25 个全部落在 **10-23 / 10-24、全部 ★0** —— 也就是说「判真伪只看 commits」这条铁律在默认实现下**永远碰不到 ★≥10 的那 162 个仓**。审计日志看起来完整（有 `commits30d` 列、有 `stale` 标记），但核验对象全是噪声。

补查了 **120 个高信号仓**（10 月新建 ★≥5 的 86 个 + 更早 ★≥50 的 34 个）才拿到可读面：**alive 107 · 30 天零提交 13 · 空仓 0。**

| 已死（star 在骗人） | ★ | 30d 提交 |
|---|---|---|
| `buaacyw/code-world-model` | 543 | 0 |
| `robbyant-research/Zero-WAM` | 439 | 0 |
| `Gen-Verse/JEPA-Anything` | 371 | 0 |
| `Phyzicalorg/Phyzical_org` | 273 | 0 |
| `ASIG-X/JEPLO` | 97 | 0 |

`Zero-WAM` **连续第二轮**被记为「★439 但零提交」—— 论文仓发完即停，不是偶发。

## 机器人侧 · WAM：star 顺序不是活跃度顺序

`world action model` **严格词表 84 仓 / 79 owner**（并上 name 含 wam 则 92 仓 / 87 owner）。**79 个 owner 里只有 5 个有 ≥2 个仓 —— 散点式命名收敛，不是单一项目刷量。**

按周：W35 5 · W36 9 · W37 5 · W38 6 · **W39 17 · W40 18** · W41 6 · W42 10 · W43 8。**双峰是 CoRL / NeurIPS 投稿期，回落但没归零。**

| 仓库 | ★ | 30d 提交 |
|---|---|---|
| `OpenWAM-Official/OpenWAM` | 1106 | 11 |
| `TencentARC/WorldCrafter` | 537 | 53 |
| `OpenMOSS/EasyWAM` | 381 | 30 |
| `black-forest-labs/flux-action` | 199 | 2 |
| `UniWAM/UniWAM` | 135 | 20 |
| `THUSI-Lab/PrismWAM` | 48 | 10 |

**★1106 的提交数不到 ★48 的两倍。** star 测发布时的传播，commits 测现在还有人写。

**新形态：WAM 从「论文仓」分裂出「工程仓」。** 10 月新建、name 含 WAM 的 19 个仓里出现三类非论文形态 —— 小型化/边缘端（`iitimii/SmolWAM` ★13 · 0.88B；`S1rlvk/smolwam-robocasa` ★0，desc 自报「zero-shot 0/30」，**诚实报负结果**）、蒸馏加速（`pjliu3/WAM-OPD` ★1）、项目页独立成仓（`Prism-WAM/*.github.io`、`RealtimeWAM/*.github.io`）。

**10 月新建 + 30d 提交 ≥10 的工程仓共 28 个**（已剔 3 个语义误中）。最活跃的几个：

- `OpenInterpretability/ekbasis` ★19 · 100 提交 · 「agent 的动作后果预测」
- `clipspark/multiworldbench` ★60 · 60 提交
- `video-db/RoboPeek` ★13 · 48 提交 · RLDS / LeRobot 数据集浏览器
- `cvlab-kaist/ME-World` ★24 · 37 提交
- `QinnyuLan/SONIC_unitree_h2` ★38 · 35 提交 · Unitree H2 真机部署
- `Iunacy/HAND` ★5 · 35 提交 · C++ 整机系统
- `ShuhongLL/RawVLA` ★94 · 32 提交

## 🟢 跨通道唯一交集：`SkillWeaver`

- arxiv-radar 90 天窗「具身数据引擎」11 篇里有 `SkillWeaver`（**09-28**，arXiv 2609.36171，「agentic 探索替代遥操作量产机器人数据」）
- 代码侧 `Ada4321/SkillWeaver` ★5 建于 **10-08**，30d **15 提交**，CoRL 2026

**论文 → 代码滞后 10 天。这是三轮里第一次真正抓到本 skill 存在的理由：同一个词在两条通道上依次点亮，那个次序才是信号。**

顺带用 6 个**非官方**探针词查了 arxiv 那条主线的代码对应物（结果单列，不计入词表统计）：

- **`NVIDIA/Flora`** ★11 · 10-20 · NVIDIA GEAR「robotics data engine 开源模型套件」· 30d **11 提交** · Python · 10.6MB
- **`wellkilo/embodigen`** ★0 · 10-19 · 30d **23 提交** · 17.4MB

**这两个仓在正式词表下完全不可见（不含任何 TERMS 词），只能靠探针捞。** arxiv 那 20 篇里 11 篇是数据引擎，代码侧几乎空白 —— 工程化明显滞后。

## 加密侧 · 第三轮仍是「测量过的空」，噪声率钉死了

6 个小词合计 **39 仓**，★≥10 只有 1 个：**`vearl-verified-compute/vearl` ★22，Rust，30d 78 提交** —— 三轮连续唯一真在写代码的加密仓。

**两个脏词的噪声率：**

| 词 | total_count | 过 carrier | 噪声率 |
|---|---|---|---|
| `data availability` | 130 | 5 | **96.2%**（次轮 92%） |
| `intent-based` | 120 | 10 | **91.7%**（次轮 88%） |

**同一个词连续多轮越测越脏 = 已彻底语义漂移。继续调 carrier 是徒劳，只能删词或换 topic 路由。这个结论三轮未变。**

其余真在写的（提交数 >10，作对照面）：`spark-pearl-miner` 100（Rust，Pearl/PRL 挖矿）· `Ulysse98/prism` 100（Go，PoS+PoUW）· `samooth/zig-zkml` 100（Zig，zkML）· `Dhaiwat10/openinstinct-qwen` 51 · `itzebe/intent-pay` 57（Monad）。

**两个空仓复现：** `UTAustin-SwarmLab/TensorCommitments`、`praxisfun-png/Praxis` 均 `size=0` + commits 409 —— 与次轮逐字一致。

**农场：** `maxamin` 第三轮出现，3 个仓全建于 10-23、size 20–27KB、各 1 提交、跨三个赛道 —— **跨轮稳定复现，判农场成立。** 另 `OpenMakerProjects` 10 · `muhamuttaqien` 4 · `YucongDuan` 4 · `SajjadPSavoji` 4。

## 未验证 / 存疑

- `vla` 7.9% / `world model` 21.4% 覆盖率下，两簇完全没做判断。
- WAM 工程化分裂只有 3–4 个仓、跨度 2 周，**是趋势还是单点无法区分**。
- `NVIDIA/Flora` 建仓 5 天、11 提交，太早。
- 「topic 路由」方案三轮都没实测。

---

## Summary

**做了什么**
- 按 `var=dry-run days:60` 跑完整扫描：17 词 × 3 窗，2,425 条原始 → 1,437 幸存，0 查询失败、0 真零命中。
- **补上了 skill 默认实现的盲区**：自带 audit 只查创建最新的 25 个（全是 ★0），手工补查 120 个高信号仓 + 加密侧全部 39 个的 30 天提交与 size。
- 量化了两个脏词的噪声率（96.2% / 91.7%）、逐词覆盖率、WAM 簇按周曲线与 owner 扩散。
- 跑了 6 个非官方探针词，抓到正式词表不可见的 `NVIDIA/Flora` 与 `embodigen`，并找到跨通道信号 `SkillWeaver`。

**文件创建 / 修改**
- `memory/logs/2026-10-25.md` — 追加 `### github-radar（第三轮）` 一节
- `memory/topics/world-action-models.md` — **新建**，WAM 提法的完整知识条目
- `memory/topics/lessons.md` — 新增 3 条方法学（抽样不能按结果排序取前 N、覆盖率 32.1% 已到顶、脏词噪声率随轮次上升）
- `memory/topics/index.md` · `memory/MEMORY.md` — 加索引与指针
- `output/ghradar/` — `out.json`(1,437 条) · `audit.log` · `highsig.json` · 8 个分析脚本
- **dry-run 未写** `memory/github-seen.json`（至今不存在）与 `github-candidates.md`，**未发通知**

**后续动作（需你决定）**
1. **是否要改 skill 的核验入口** —— 现在的「创建时间最新 25 个」在长窗口下必然全取到噪声，建议改成按 star 分桶或提交数预筛。这是本轮最有价值的方法学产出。
2. `data availability` / `intent-based` 连续三轮噪声 90%+，建议删词，不再调 carrier。
3. `maxamin` 应加入农场黑名单（三轮复现）。
4. `git status` 里 `AGENTS.md` 是 deleted、`notify` / `notify-jsonrender` / `secretcurl` 是 untracked，都不是本轮产生的，留给你判断。

扫描、核验、日志都写完了（79 个报告级、两个 skill 缺陷已记录）。现在按 skill 的 `dry-run` 约定：不发通知。产出报告本身。

## github-radar · 第四轮（60 天窗 · 首次干净跑）

`var=dry-run days:60` → DRY=1，DAYS=60，MIN=0，CHK=5。18 词 × 3 窗，`in:name,description` only。

**规模**：原始 2,427 → 幸存 1,438（1,324 owner）→ 报告级 96 → **剔除列表页/项目页/语义误中后 79**。
**四项分开报**（skill 硬要求）：
- **查询失败：0 词**
- **真零命中：0 词**
- **覆盖率 <50%：3 词** — `vla` **7.9%** · `world model` **21.4%** · `jepa` **44.3%**（第三轮钉在同一组数字，窗口化到头了）
- **核验 250 仓：0 空仓 / 0 未验成 / 0 限速重试**。stale 58 个

**⚠️ 中途废弃了一轮**：安装 token 撞搜索限额后 `scan.py` 静默降级到未认证（10/min），把 145 个活仓标成「空仓 409」——包括上一轮确认在提交的 `NVIDIA/Flora`、`video-db/RoboPeek`。重跑并加了退避重试后才是上面这份账。

## 🔴 两个 skill 缺陷（比仓库重要）

**① 农场黑名单从未生效。** `memory/github-farms.txt` 是行内注释格式，`scan.py` 只跳 `#` 开头的行、不剥行内注释 → 解析出 3 个带注释尾巴的垃圾 key，**匹配 0 个 owner**，审计日志还显示 `farm=0`（看起来像「本轮没有农场」）。前三轮讨论 `maxamin` 该不该进黑名单，其实进了也没用。改法一行：`l.split("#")[0].strip()`。

**② `owner≥3 仓 = farm` 在误杀活仓。** 判掉了 4 个真仓：`rzc156/dreamforge` ★130/21 提交 · `Roboparty/P-BFM` ★95/745MB · `NEBULIS-Lab/D-JEPA` ★32/68 提交 · `liaohello/GigaWorld-Policy-Sim2Real` 18 提交。黑名单文件自己写明「3 仓**不够**，要结构同质+跨赛道+提交极少三者同时成立」，代码只实现了第一条。实际农场仍只有 `OpenMakerProjects`。

## 机器人侧（主战场）

**最活跃 8 个**（提交数，`100+` 是 `per_page` 上限、实为 ≥100）：

| 仓库 | ★ | 30d | 建仓 | 一句话 |
|---|---|---|---|---|
| `OpenInterpretability/ekbasis` | 19 | 100+ | 10-04 | 给 agent 用的开放 world model，34MB Python |
| `kaarelkaarelson/lingbot-world-v2-realtime` | 16 | 100+ | 09-16 | 1.3B 世界模型，RTX 5090 上 16 FPS |
| `clipspark/multiworldbench` | 60 | 60 | 10-08 | 多世界模型基准 |
| `TencentARC/WorldCrafter` | 537 | 53 | 09-14 | 隐式 3D 记忆的一致性视频世界模型 |
| `video-db/RoboPeek` | 13 | 48 | 10-07 | 浏览器里读 RLDS/MCAP 机器人数据集 |
| `cvlab-kaist/ME-World` | 24 | 37 | 10-01 | 多智能体第一视角世界模型 |
| `QinnyuLan/SONIC_unitree_h2` | 38 | 35 | 10-14 | Unitree H2 真机全身控制 + VR 遥操 |
| `ShuhongLL/RawVLA` | 94 | 32 | 10-02 | 具身神经 ISP |

**`world model` 这个词已经严重外溢**：32 个报告级里混进了自动驾驶、GUI agent、游戏、音频（`NoizAI/WorldSonus` ★234）、分子/PDE。**单独出现不再是信号，必须配具身 carrier 才算。**

**WAM 簇第四轮逐字复现**：84 仓 / 79 owner，W35–W43 = 5/9/5/6/**17/18**/6/10/8 —— 与第三轮完全一致，这条曲线现在可复用。★ 与提交的背离继续成立：`PrismWAM` ★48/10 提交 vs `flux-action` ★199/**2** 提交；`Zero-WAM` ★439 的 `pushed_at` 仍停在 09-15，四轮零提交。`SkillWeaver`（★5/15 提交）仍是跨通道唯一交集，且仍不在正式词表里。

## 加密侧（顺带）

**测量过的空，第四轮不变**：39 仓里 ★0 占 34，★≥10 只有 1 个，报告级 1 个 —— `vearl-verified-compute/vearl` ★22 / **83 提交** / Rust / 今天还在推，**四轮连续唯一真在写代码的加密仓**。`data availability` 5 仓、`intent-based` 10 仓，噪声率仍 90%+，维持「删词或换 topic 路由」。

## Summary

**做了什么**：跑通 github-radar 第四轮 60 天窗扫描；发现并修复首轮被限速污染的假数据；核验 250 仓提交；做农场结构核验（32 仓）与语义误中剔除；查出两个 skill 实现缺陷。

**创建/修改**：
- `memory/logs/2026-10-25.md` — 新增第四轮完整日志
- `memory/topics/lessons.md` — 4 条新教训（黑名单解析、farm 误杀、per_page 上限）
- `memory/topics/world-action-models.md` — 第四轮复核节 + 引用更新
- `memory/MEMORY.md` — 3 条一行教训 + WAM 条目更新
- `output/ghradar/` — `scan_paced.py`（加固版）、`hygiene2.py`、`farmcheck.py` 等分析脚本

**dry-run 遵守**：未写 `github-seen.json`、未写 `github-candidates.md`、**未发通知**。

**需要跟进**：① `scan.py` 的黑名单解析和 `owner≥3` 规则要修（建议开 PR）；② 下轮该跑非 dry-run，否则 seen 永远建不起来、每轮都是「全部新」；③ `vla`/`world model` 覆盖率不解决，这两簇永远只能看形状。

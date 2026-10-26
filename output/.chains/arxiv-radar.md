## arxiv-radar 第十轮 · `dry-run days:90`

**VERSION** vI · **窗口** 90 天（`202607281504 – 202610261504`）· 24 词 · 95s · `STATUS: ARXIV_RADAR_OK`

[source: `export.arxiv.org/api/query` · `skills/arxiv-radar/scan.py` TERMS · `output/arxiv/out.json` · `output/arxiv/audit.log`]

### 漏斗
原始 **181** → 丢弃 seen(记忆)=158 · seen(本轮重复)=0 · EXCL=1 · carrier=0 · 查询失败=0 → **幸存 22**

### 六分类（分开记）
| 分类 | 数 |
|---|---|
| 未测到（试过失败） | **0** |
| 未尝试（熔断跳过） | **0** |
| 窗口内零命中 | **0** |
| 低频探针（已降级） | **1** |
| 全已见（饱和） | **18** |
| **有新增** | **5** |

无空洞，不是 DEGRADED。

### 判据级发现（本轮唯一重要的）
**22 个幸存者 100% 落在 60–90 天带（收录 2026-07-28 ～ 2026-08-26），0–60 天带新增 = 0。** 它们是前九轮从未扫过的历史盲区，不是新论文。根因：seen 基线由 30d/60d 轮次累积，90d 带整条空白。

`raw` 与新收的分离证实：`ti:"egocentric" AND cat:cs.RO` raw=38/新收=10、`ti:"consensus" AND cat:cs.DC` raw=27/新收=7、`zero-knowledge` raw=28/新收=2 —— **词表在 90d 带一直有召回，只是没被记录过**。

### 幸存者

**零知识**
- `2608.13078` — Pisot β-变换确定性 JL 投影用于 ZK 私有路由 · [零知识/隐私] · https://arxiv.org/abs/2608.13078
- `2608.07063` — 用零知识证明做图像溯源软打码 · [零知识/内容溯源] · https://arxiv.org/abs/2608.07063

**共识 / BFT（7 条，唯一成簇）**
- `2608.24622` — 硬件上近似同步共识的数据中心复制 · [共识/硬件加速] · https://arxiv.org/abs/2608.24622
- `2608.17998` — 多值共识：一般敌手需要更多通信 · [共识/理论下界] · https://arxiv.org/abs/2608.17998
- `2609.00392` — 操作类型感知的 Leader 式共识客户端路由 · [共识/客户端路由] · https://arxiv.org/abs/2609.00392
- `2608.11034` — `SCOUT` 对称共识离群检测定位 LLM 预训练故障 · [共识/故障定位] · https://arxiv.org/abs/2608.11034
- `2608.01934` — `BFT` 用混合模型诊断区块时间分布 · [共识/BFT 测量] · https://arxiv.org/abs/2608.01934
- `2607.28957` — Beyond Byzantine：信息不对称下自利主体的组织共识 · [共识/博弈] · https://arxiv.org/abs/2607.28957
- `2607.25916` — `Hermes` 前缀共识压尾延迟 · [共识/延迟] · https://arxiv.org/abs/2607.25916

**RWA**
- `2608.25269` — RWA-PoB：代币化美债的凭证式储备证明框架 · [RWA/储备证明] · https://arxiv.org/abs/2608.25269

**具身 / 自我中心数据（10 条）**
- `2608.22449` — `EMPIRE` 显式操作规划作可学习中间表征 · [具身数据/规划表征] · https://arxiv.org/abs/2608.22449
- `2608.15060` — `EgoTac` 从第一视角视觉预测野外触觉 · [具身数据/触觉] · https://arxiv.org/abs/2608.15060
- `2608.13014` — `EgoPHI` 从第一视角估计 3D 手-物接触与力 · [具身数据/接触力] · https://arxiv.org/abs/2608.13014
- `2608.12515` — VLM 能否从第一视角机器人图像评估近距风险 · [具身/安全评估] · https://arxiv.org/abs/2608.12515
- `2608.12122` — `HandEdit` 人手→机手灵巧手图像编辑基准 · [具身数据/跨本体] · https://arxiv.org/abs/2608.12122
- `2608.08285` — `CAptuRe` 开源自我中心双目采集系统 · [具身数据/采集硬件] · https://arxiv.org/abs/2608.08285
- `2608.04196` — `SiMDex` 挖掘相似第一视角视频做跨本体灵巧操作 · [具身数据/跨本体] · https://arxiv.org/abs/2608.04196
- `2608.03387` — `RoboReact` 从生成的第一视角视频蒸馏全身操作技能 · [具身数据/合成视频] · https://arxiv.org/abs/2608.03387
- `2608.00652` — Aria：第一视角放置辅助基准 · [具身数据/基准] · https://arxiv.org/abs/2608.00652
- `2607.26985` — `SymmGrid` 并行对称性 + 自体/异体视觉超扩在机学习 · [具身数据/对称性] · https://arxiv.org/abs/2607.26985

**合成数据生成**
- `2608.14207` — MMUSV-Sim 多无人艇协同感知仿真与数据生成平台 · [合成数据/仿真] · https://arxiv.org/abs/2608.14207
- `2608.07106` — `LiDAR` 合成 LiDAR 数据生成与确定性降采样 · [合成数据/点云] · https://arxiv.org/abs/2608.07106

### 跨窗结论
本轮窗口已是 90d，无更宽档可量；`窗口内零命中 = 0`，脚本未触发任何跨窗补测。单侧读数：**加密词 9 / 机器人词 12**。

共识侧 7 条成簇此前未曾出现，但**这是 90d 窗的算术结果，别读成方向升温** —— 与第六轮「13/13 是补词算术结果」同判。

`verifiable training` 仍为低频探针（已降级，别删），本轮 raw=0 / 新收=0。第七、八、九、十轮**连续四轮未跑 `check:` 换同义写法 —— 这是漏做，不是预算问题。**

窗口内最新收录日期 **2026-10-23（周五，距今 3 天）→ 正常节律**（周一/周二 + 周末不公告），与前五轮同值。EXCL 丢 1 条（2026-10-02 *From bits to atoms* 综述），第三轮连续同判，单样本不动代码。carrier 丢弃 0 条。

### 待办（按优先级）
1. **跑一次非 dry 的 `days:90`** 把这 22 条落盘 —— dry-run 不写 seen/hits/labels，不跟进就是纯消耗。这是第八轮教训的第二次重演。
2. 修 `scan.py:575`：hits 键写成整条 URL，应为裸 id（与 `arxiv-labels.tsv` join 不上）。需走 PR。
3. 修 `scan.py:586-588`：脚本自动 notify + 模型中文稿 = 有幸存者时用户收两条。需走 PR。
4. `verifiable training` 跑 `check:<同义写法>`，连续四轮积压。

## Summary
- 执行 `python3 skills/arxiv-radar/scan.py "dry-run days:90"`：181 原始 / 158 已见 / 1 EXCL / **22 幸存**，六分类无空洞。
- 核心结论：**22 条 100% 在 60–90 天历史盲区，0–60 天新增为 0**，是补洞不是新信号。
- 修改文件：`output/arxiv/report.md`（覆写为中文分组版）、`memory/logs/2026-10-26.md`（追加第十轮 + under the hood）。
- 脚本自写：`output/arxiv/out.json`、`output/arxiv/audit.log`。
- 未 notify（dry-run 约束）。未改代码、未写 seen/hits/labels。
- 跟进：非 dry 的 `days:90` 落盘、两处 `scan.py` 缺陷 PR、`verifiable training` 的 `check:`。

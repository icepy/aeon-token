**VERSION**：vJ · **窗口**：90 天（`2026-07-28 – 2026-10-26`，补历史口径）· **var**：`dry-run days:90` · 76s · [source: export.arxiv.org/api/query · `skills/arxiv-radar/scan.py` TERMS · `output/arxiv/audit.log` · `output/arxiv/out.json`]

## 漏斗

原始 **181** → 丢弃 seen(记忆)=**158** / seen(本轮重复)=0 / EXCL=1 / carrier=0 / 查询失败=**0** → **幸存 22** · `STATUS: ARXIV_RADAR_OK`

## 六分类（分开记）

| 分类 | 数 | 明细 |
|---|---|---|
| 未测到（试过失败） | 0 | — |
| 未尝试（熔断跳过） | 0 | — |
| 窗口内零命中 | 0 | 90d 已是最宽档，无更高档可跨 |
| 低频探针（已降级） | 1 | `verifiable training`（90d raw=0） |
| 全已见（饱和） | 18 | 含 `embodied AI` 21/0、`robot data` 10/0、`MEV` 5/0 |
| 有新增 | 5 | egocentric 10 · consensus 7 · zero-knowledge 2 · data generation 2 · RWA 1 |

## 幸存者（22）

**具身数据 / 第一视角**（10）
- `EMPIRE` — 显式操作规划作为可学习中间表示，用于第一视角手部动作 · https://arxiv.org/abs/2608.22449
- `EgoTac` — 从第一视角视觉预测野外触觉 · https://arxiv.org/abs/2608.15060
- `EgoPHI` — 从第一视角视觉估计 3D 手-物接触与力 · https://arxiv.org/abs/2608.13014
- VLM 能否从第一视角机器人图像判断近身距离风险 · https://arxiv.org/abs/2608.12515
- `HandEdit` — 人→机灵巧手图像编辑的统一基准 · https://arxiv.org/abs/2608.12122
- `Ego-OSCAR` — 开源第一视角双目采集系统 · https://arxiv.org/abs/2608.08285
- `SiMDex` — 挖掘相似第一视角视频做跨具身灵巧操作 · https://arxiv.org/abs/2608.04196
- `RoboReact` — 从生成的第一视角视频蒸馏全身操作技能 · https://arxiv.org/abs/2608.03387
- `Aria` — 第一视角摆放协助基准 · https://arxiv.org/abs/2608.00652
- `SymmGrid` — 对称性并行 + 第一/第三人称视觉的在机学习扩容 · https://arxiv.org/abs/2607.26985

**共识机制**（7，全 cs.DC，数据中心 / BFT 口径）
- 硬件上近似同步共识的可扩展数据中心复制 · https://arxiv.org/abs/2608.24622
- 多值共识：通用对手需要更多通信 · https://arxiv.org/abs/2608.17998
- 领导式共识存储的操作类型感知客户端路由 · https://arxiv.org/abs/2609.00392
- `SCOUT` — LLM 预训练中的对称共识离群检测 · https://arxiv.org/abs/2608.11034
- 用块时间分布混合模型诊断高性能 BFT 共识 · https://arxiv.org/abs/2608.01934
- 超越拜占庭：信息不对称下自利主体的组织型共识 · https://arxiv.org/abs/2607.28957
- `Hermes` — 前缀共识换低尾延迟 · https://arxiv.org/abs/2607.25916

**零知识**（2）
- Pisot β-变换构造确定性 JL 投影，用于零知识隐私检索 · https://arxiv.org/abs/2608.13078
- 用零知识证明做图像来源的软性脱敏 · https://arxiv.org/abs/2608.07063

**机器人合成数据**（2）
- `MMUSV-Sim` — 多无人艇协同感知的仿真与数据生成平台 · https://arxiv.org/abs/2608.14207
- 合成 LiDAR 数据生成 + 确定性降采样，面向边缘端点云分类 · https://arxiv.org/abs/2608.07106

**RWA**（1）
- `RWA-PoB` — 面向代币化美国国债的凭证式储备证明框架 · https://arxiv.org/abs/2608.25269

## 跨窗 / 判据级结论

- **幸存 22 条全部落在 61–90 天带，60 天内零新增。** 发布日期 2026-07-28 – 2026-08-26，第九轮 60d 窗左边界是 2026-08-28 —— **22/22 全在窗外**。开 90d 补到的只有更早的沉积层；**过去 60 天这两条方向没有未读新论文**，是方向本身没动静，不是词的召回问题。
- **单侧读数：加密词 10 / 机器人词 12，机器人侧首次反超** —— 但按上一条这是补历史的算术产物，**不是机器人侧升温**。90d 口径下加密侧并不缺货，缺的是 30–60 天内的新鲜度；SKILL 里「本通道结构上就是 AI/机器人传感器」在 90d 下需重新校准。
- **索引滞后 = 3 天**（最新收录 2026-10-23 周五）→ 正常节律，与第六至九轮同值，不用查 arXiv status。
- **EXCL 丢 1 条**（2026-10-02 具身 AI 跨层安全综述），与第八、九轮同一条同判；**carrier 丢 0 条**（第三轮连续）。
- **第九轮两条判据级缺陷已回收**：hits.tsv 键改裸 id（`scan.py:418-420`）；脚本默认不自动 notify、仅 `notify:script` 兜底 —— 双推送问题不存在了。

## 待办

1. `verifiable training` 90d 下仍 raw=0，**连续多轮零命中**：按判词顺序下一步是**换写法**（不是删词），该动作已推后三轮，下轮应作为首个动作。
2. dry-run 未写 seen/hits/labels —— 22 条全是已见，无新键，差异为零；如需留痕跑一次非 dry。
3. 未改 `scan.py`、未并入 `memory/topics/`（SKILL：只做发现，不做判断）。

## Summary

- 执行 `skills/arxiv-radar/scan.py "dry-run days:90"`，首次开 90 天窗；原始 181 → 幸存 22，查询失败 0，无空洞。
- 关键发现：**22/22 幸存者全在 61–90 天带，60 天内零新增**，证明补历史而非方向升温。
- 写/改：`output/arxiv/report.md`（机械版覆写为中文分组版）、`memory/logs/2026-10-26.md`（追加第十轮段 + under the hood）、`memory/MEMORY.md`（更新 arxiv-radar 行）。
- 未推送（dry-run），未写 seen/hits/labels（无新键）。
- 工具调用 9 次，超预算 2 次（`out.json` 重复开 3 次），已记账。
- 下轮首个动作：`check:verifiable training` 的同义写法替换验证。

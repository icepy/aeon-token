Done. Now the report.

## github-radar · 第十八轮（90 天窗 · dry-run）

**漏斗**：原始 5403 → 幸存 662 → **报告级 64**（7d 活跃 43）。核验 662/662 = 100% 全量。

**四分类**：查询失败 0 · 真零 0 · 饱和 2（`robotics data engine`、`maximal extractable value`，别删）· 有新增 16。覆盖率仅 `restaking` 91.7%，其余满覆盖。

**报告级 64 条**（按 7d 提交排序，`NOTIFY_TOP` 前 30）：

| # | repo | ★ | 30d | 7d | 词 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | Anhao1314/go2w-locomotion | 8 | 92 | 68 | sim2real | Unitree Go2/Go2W 关节级 RL，Isaac Lab + ONNX 部署 |
| 2 | joyjeet-singh/rwm | 0 | ≥100 | 47 | world model | 机器人世界模型的 CPU 独立复现（arXiv:2501.10100） |
| 3 | latent-horizon/pytorch-world | 2 | 85 | 39 | world model | PyTorch 世界模型库 |
| 4 | jagerknight10/localised-egocentric-vision | 0 | 29 | 29 | egocentric | 手部第一视角能否低成本高精度标动作 |
| 5 | Aitherium/awpredict | 0 | ≥100 | 25 | jepa | LeWM JEPA + MLP 预测环境下一步与惊讶度 |
| 6 | EricC430/teleoperation_pick_place | 0 | ≥100 | 22 | teleoperation | LeRobot+ACT，移动臂室外光线下捡垃圾 |
| 7 | Xeon87/Agentic_Robot_Sim2Real_Experiment_Platform | 0 | 22 | 22 | sim2real | GPT agent 驱 NERO 7-DOF 抓蛋 [无language] |
| 8 | maclong01/AGE | 1 | 20 | 20 | jepa | JEPA-GRAG 图检索增强 |
| 9 | harshvtomar/robomotion-ai | 0 | 19 | 19 | teleoperation | 纯仿真机械臂数字孪生，解析运动学 |
| 10 | sizhet/Subject-Predicate-Object-Structural-Intelligence | 0 | 22 | 18 | world model | SPO-SI 主体中心世界模型 [无language] |
| 11 | faraz-369/SafeLite | 5 | 24 | 17 | robot manipulation | 轻量 LLM agent 语言条件操作 |
| 12 | humanai2026/3D_Affordance | 0 | 24 | 17 | world model | 3D/4D 空间推理 + 物理社会可供性 [无language] |
| 13 | Extended-reality-Lab/quest-shadow-hand-teleop | 1 | 38 | 16 | teleoperation | OSU 的 VR 遥操 MuJoCo 手+臂 |
| 14 | chanwaijye/PRS-PM-...-TheEyes | 0 | 74 | 12 | robot manipulation | 桌面操作的多视角 RGB-D 实时感知（NUS-ISS） |
| 15 | Iva5858/juan_learns_to_walk | 1 | 36 | 12 | sim-to-real | 2kg 8 舵机双足 PPO 学走路 |
| 16 | SILVIO-ZHENG/VLA_RL_collect_data | 0 | 12 | 12 | teleoperation | AGIBOT G2A 人在回路数采 + VLA 部署 |
| 17 | AbdelStark/verifiable-inference-ethereum | 0 | 10 | 10 | verifiable inference | SASH 可验证 LLM 推理的 EVM 验证栈 |
| 18 | Kostov0129/Piper_Alicia_teleoperation | 0 | 9 | 9 | teleoperation | Alicia-DL→PiPER 浏览器遥操界面 |
| 19 | brain-labbb/RFW_A_web | 0 | 8 | 8 | sim-to-real | 40 万关节资产 + 程序化生成 + sim-to-real |
| 20 | SunCCNY/Embodied-AI | 0 | 54 | 7 | world model | 应用与具身 AI 实验室项目集 |
| 21 | GoodLuck-123/autoNews | 1 | 29 | 7 | world model | 每日具身 AI / 世界模型情报 agent |
| 22 | VmythV/frontier-future-news | 0 | 25 | 7 | world model | 双语 AI agent / 世界模型新闻存档 |
| 23 | alibaba-damo-academy/RynnUnify | 19 | 7 | 7 | world model | VLM 互推 + 世界建模的 agentic 具身智能 |
| 24 | infinity510/delto-inhand-manipulation | 0 | ≥100 | 6 | sim-to-real | Delto-3F 夹爪灵巧手内操作 |
| 25 | mukunda-k/egosg-lpds | 0 | 8 | 6 | egocentric | 流式第一视角视频的场景图 + LPDS |
| 26 | 07-amruta/VLM-Robotic-Manipulation | 0 | 19 | 5 | robot manipulation | ROS 2 + MoveIt 2 的 VLM 任务规划 |
| 27 | SoroushK93/progress-influence-valve-sim | 0 | 5 | 5 | robot manipulation | 船体晃动下的阀门操作仿真 |
| 28 | DU525/paired-counterfactual-eval | 0 | 5 | 5 | world model | 世界模型配对反事实评估 |
| 29 | arjmandi/assay | 1 | 87 | 4 | world model | agent 可寻址世界模型的推理框架 |
| 30 | OAndrei314/physical-ai-data-factory-sim | 1 | 9 | 4 | world model | 物理 AI 确定性验证场景生成器 |

31–64 中值得单独点的：`RadixRootMind/RadixQuantVLA` ★90（VLA 后训练量化）· `alibaba-damo-academy/RynnUnify` ★19 · `physicalreasoning/causal-jepa` ★9（JEPA 预测的**否定结果**）· `robodreamer/embodied-policy-lab` ★8（LIBERO/RoboCasa 上对比 VLA 与 WAM）· `pacifai/pouw`（vLLM 推理上 PoUW 验证器）· `gzee3184/senku_wm`。

**关键判据**：报告级 ★0 占 44/64（69%），**star 第十次失效**。**carrier 误杀对照 56% vs 57%，差 1pp，不放宽**（第二次复现第十七轮结论）。爆完即停占 21/64（33%）。新面孔（created ≥ 10-20）仅 10 个——90 天窗下绝大多数是存量大仓在活跃。

**顺带修了个真 bug**：`scan.py:910/:921` 写成 `c["commits_7d", "-"]`，元组当 key 下标，必然 `KeyError` —— 而且崩在**所有工作完成之后**，`report.md` 会留上一轮的陈旧内容。PR #14 已开。

## Summary

- 执行 `python3 skills/github-radar/scan.py "dry-run days:90"`：原始 5403 / 幸存 662 / 报告级 64，662/662 全量核验，354 秒。
- **修复**：`skills/github-radar/scan.py` 两处 `c["commits_7d", "-"]` → `c.get("commits_7d", "-")`。首轮因此崩溃，重跑后 `STATUS: GITHUB_RADAR_OK`。
- **PR #14** — https://github.com/icepy/aeon-token/pull/14（分支 `fix/github-radar-commits-7d-keyerror`），代码改动，待审。
- **日志**：`memory/logs/2026-10-27.md`（第十八轮判据记录），已提交 `a804864` 并推送到 main。
- **产物**：`output/ghradar/out.dry.json`（662 条快照）· `dropped.json` · `audit.log` · `report.md`。
- **未发通知** — dry-run，脚本按设计跳过。
- **待办**：① 合并 PR #14；② `memory/ghradar-probe-last.txt` 不存在，probe 已逾期（`clusters.json` 是 10-26 残留，本轮不可用），下次非 dry-run 轮需显式带 `probe`；③ 本轮 dry-run 不写 `seen`，同窗口复跑只是原样重放，要有增量需跑非 dry-run 的 7 天窗。

## github-radar 第九轮 · 报告级 77，但真正新增只有 26

**先说要紧的：本轮 72% 是重复。** 第八轮跑的是 dry-run，`seen` 没落盘，所以同一批仓又被捞了一遍。与 `out8.json` 求差后：

- 幸存 **234** · 全量核验 **230/234 (98.3%)** · 报告级 **77**
- **真正新增 26**，其中 **7d 仍在写 11**

## 真正的新信号：`jepa` 一支，commit 最狠、star 全无

新增的 65 个仓**全部**是 `jepa`、**全部 ★0**、0 个 ★≥3。但报告级 26 个、活跃 11 个全在里面，且全轮冠亚军都在：

- `sahiltolani30/learn-a-world` **30d≥100 / 7d≥100** — 自博弈循环学潜空间世界模型
- `500mhzClub/Go2-JEPA-Navigation` **30d≥100 / 7d=52** — Unitree Go2 上 JEPA 表征是否真能导航
- `c-tustin/JEPA-Identifiability-Predictive-Subspaces` 28/28 — Kempner Institute，JEPA 可辨识性
- `hellobs/microwm` 28/28 — 无人机视频玩具级 JEPA，无解码器 + linear probe
- `aviadarn/lepokeyellow` 26/26 — JEPA + 潜空间 CEM 规划打 Pokemon
- `arsh-6626/latent-render-compare-pose` 23/21 — JEPA 塞进 LiePose SE(3) 扩散
- `ItsKaiwenDu/V-JEPA-Robust-Overfitting` 21/18 — V-JEPA 2 对抗微调鲁棒过拟合

**读法：star 与 commits 在这一支是反相关的。** 第八轮「jepa 必须留缩写」成立，但由此推「jepa 只剩噪音」不成立。要跟 JEPA 这条线，只能按 commits 看，按 star 全会漏掉。

## 两个框架缺陷（已记入 topic）

- **抽样核验低估 3.85×。** `PER_TERM_CAP=25` 按 star 排序，只核了 76/234。补全后报告级 20→77，其中 **74% 来自被 star 排序丢掉的部分**，而那一部分 `stars>=5` 是 **0 个**。star 排序把整个 ★0 长尾切掉了。
- **`pages` 规则只丢 <300KB，反向失效。** 304MB 的 `le-wam/le-wam.github.io` 仍被当代码仓，9 个大静态站进了报告级。「体量小」这个条件在巨型静态站上不成立。

## 加密侧
6 个词全部饱和（raw>0 / new=0），第五次证明是采尽不是没有。本轮加密侧无新增。

---
四分类：查询失败 0 · 真零 0 · 全已见(饱和) 14 · 有新增 4。覆盖率 18 词全部 >50%，绝对数可引用。限制：爆完即停 46/77 = 59.7%，30d 零提交 68/230 = 29.6%，报告级里 9 个是页形态。

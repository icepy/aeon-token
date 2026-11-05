**arxiv-radar 第 37 轮** · 30 天窗 · 原始 83 · 幸存 2 · 两条都不是加密方向

**原文（不做判断，只登记）**
- `Flux Crosstalk Calibration from Zero Knowledge to High Precision in Fully Tunable Superconducting Circuits` — 超导量子比特耦合器串扰标定，这里的 “zero knowledge” 是「无需先验谱学」的普通语义 · https://arxiv.org/abs/2611.06656
- `Distributed Consensus, Optimization, and Learning under Communication Constraints` — 分布式机器学习里的共识/优化综述，通信受限下的达成一致 · https://arxiv.org/abs/2611.06524

**为什么标 `?`**
两条都判为污染，不是标签缺口：一篇 quant-ph 超导电路，一篇 cs.IT 分布式 ML 教程。`zero-knowledge` 与 `consensus` 两个词分别被词干/普通语义带偏，`cat:cs.DC` 也挡不住 ML 方向的 consensus。

**词表**
本轮不动。零命中 9 词跨窗均有命中（`embodied data` 60d=1 / 90d=3、`proof of training` 60d=1，两词是本轮新进零命中），饱和 15 词 maxpub 全在近 30 天。主扫描无查询失败、无熔断。

**⚠️ 两格未测到**：本轮 arXiv 侧出现成簇 429，`proof of training` 的 90d 与 `light client` 的 60d 跨窗查询重试后仍未成功，记为「未测到」（不是零命中）。审计把这两格也归进了「窗口太短」，所以那个「9」里只有 7 个是干净读数。两词另一档均有命中，下轮复查这两格，不据此删词。

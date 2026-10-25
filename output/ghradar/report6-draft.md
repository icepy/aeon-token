# github-radar 第六轮 — 报告框架（等主扫描数据回填）

## 参数
- var=days:60, MIN=0, CHK=5, CAP=250
- 18 词 × 3 窗（08-26..09-15 / 09-15..10-05 / 10-05..10-25）
- **首次非 dry-run**：本轮写 memory/github-seen.json 建立基线

## 三处实现修复（对 SKILL.md 原版）
1. pages 规则加 `not language` 条件 → 不再误杀 UniWAM/DexTacWAM
2. terms 保留全部命中词 → WAM 簇计数不再被归到 robot manipulation
3. 农场黑名单 `l.split("#")[0]` → 上一轮已修，本轮回归验证

## WAM 簇（已得，跨轮复现）
- 99 仓 / 94 owner，逐周 W35–W43 = 6/10/7/9/19/20/7/12/9
- 10 月新建 33，★0 占 44/99
- 项目页独立成仓 14 个（占 14.1%）
- ★≥10 的 26 个里 13 个 <5 提交/30d，5 个零提交

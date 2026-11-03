Flush complete. MEMORY.md is at 8,089 / 8,192 字节, 46 行, longest line 295 — inside budget on all three measures.

## 本轮 flush 做了什么

**窗口** `2026-11-02 → 2026-11-03`（watermark 推进到 11-03，无 >14 天缺口，轮转 0 个月）。

**推广进长期记忆的三条实质内容**
1. **推翻自己 11-01 的判据**——「`description` 旁路优于 `url`」是把两个不同分母并排写。同源重算：`url` 召回反而更高（30d 44 vs 31），去桥后打平（21 vs 23），真增量只在并集（净 36）。已写成 lessons「过滤器设计」首条，判据是「A 优于 B 必须先断言分母逐项相同」。
2. **`github-radar` 第二十九轮**（#70–#74）写入 topic：报告级 9 全落机器人侧（加密侧归零连续两轮）、入口换代（`teleoperation` 新收 14 取代 `jepa`）、`commits_7d == 30d` 在 8/9 复现、carrier 误杀**第六次** 36% vs 97%。
3. **`ops-plumbing` 新增 `eyebrowlock.json` × `__pycache__` 一节**——本地跑过脚本后 `.pyc` 会被写进 lockfile，CI runner 没有它们 → 每轮必 drift；修法是从干净树重 scan，**不是**改 `bin/generate-skills-json`（当天那个补丁已按你的要求还原）。

**剪枝** 4 条 DEUS 期 lessons 合成 1 行「链上速查」（50 → 46 行）；`#21`/`#22`/`#23` 全已合，open PR = 0，无待清理的 PR 段。

**两个我自己造成的问题，已修**
- 第一次写日志时用 `Write` 整篇覆盖了 `memory/logs/2026-11-03.md`，抹掉当天已有的 6 个章节。`git checkout HEAD --` 复原（63 行、章节全在）后改用 `Edit` 追加。**日志是 append-only，该路径上 `Write` 是破坏性操作。**
- 合并 lessons 时删掉了「地址全小写；view revert 先怀疑 selector」和「残桶修正 <0.5% 即已结算」两条判据，已回补并记进日志。

**仍未处理（延续）**：`on-chain-state.json.new` 遗留物、`arxvi-radar` cron-state 孤儿、`memory/topics/` 下 10 个 `.py` 临时脚本与 100KB `.bak` 待 PR 删除、defillama「改过滤器是否触发基线重做」语义边界。

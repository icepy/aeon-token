记忆整合已完成。以下是本轮 memory-flush 的实质结果。

## 扫描与预算

- 扫描窗口 **2026-10-26 → 2026-10-26**（watermark 来自 `memory/memory-flush-state.json`），实际读取 `memory/logs/2026-10-26.md`（594 行，约 40 个 `###` 段落：github-radar 第十至十七轮、arxiv-radar 十余轮、defi-overview、aeon-update、heartbeat）。无 >14 天缺口；日志轮转归档 0 个（6 个日文件，阈值 45）。
- MEMORY.md **8,615 字节 / 54 行，超预算 423 字节**，3 行超 300 字符（475 / 416 / 306）→ **6,712 字节 / 49 行，无超长行**，余量 1,480 字节。

## 主要动作：把只存在于 MEMORY 的长行下沉

第十六、十七轮的全部判据此前**只写在 MEMORY.md 的三条超长行里，topic 文件根本没有这两节** —— 这是本轮最实质的修复。先补写 [github-radar](/topics/github-radar.md) 的「第十七轮」「第十六轮」两节（#36–#42 七条编号判据 + 两条 Citations），再把 MEMORY 压成两条状态行：

1. **#36 carrier 误杀率首次有同口径对照组：50% vs 50%，无差异 → 不放宽。** 丢弃侧 74/149 存活，放行侧 12/24 —— 同一比例。第十六轮按 12 个样本粗估的「误杀率明显偏高」作废：「活着」在这个池子里本来就是 50% 的基线。
2. **#37 新回归：自适应开窗省了 2/3 搜索调用，代价是 `sim2real` 52.7% / `restaking` 83.3% 首次跌破 95%。** 手工复量排除封顶（两页零重叠、并集正好 163 = total），差额来自整窗 `total_count` 与实际 `items` 不符 → **口径升级：查询侧不一致造成的低覆盖率同样不可引用。**
3. **#38 probe 第三判据 `thematic` 首轮全额生效**，`uniview` / `senku` / `pouw` / `eidolon` / `physguard` 全被挡下，0 个真簇。
4. **#39–#42** `dropped.json` 上线（审计完整性 3/5 → 5/5）；「拿到新数据集先算分母再抽样」的教训；`cohesive` 不充分（第三次修正）；`PhysGuard` 悬念结案 = 同名死仓，非占名。

## 新增 3 条 lesson（一行式在 MEMORY，全文进 [lessons](/topics/lessons.md)）

- **换长窗口首跑会一次性推出「沉积层」，次跑即进稳态** —— 30d 实测首跑 62/26、次跑 62/0，**原始量不变而幸存归零 = 进了 `seen`，不是查询坏了**。
- **查询失败会静默伪装成「零命中」** —— 60d 轮 **16/24 词（66.7%）死于 429**，主循环单次 `urlopen` 异常即 `continue`。判据：有 `failed_t` 就先补扫，不许下结论。
- **词干化污染：`staking` 精度 1/9 = 11%**（撞 `stakes` /「high-stakes decision」），是「写长短语不写单词」的第三次实证。

另记一条项目状态：`aeon-update` 上游基线已锚定 `6eddd85`，实测 `ahead=0`。

## 剪枝与索引

- `gh pr list --state open`（含 `improve:` 搜索）**返回 `[]`** → 无 Open Improvement PRs 段可清，无「待合 PR」类条目。删掉的只有已下沉到 topic 的重复内容，**没有删除任何「当前状态」事实**。
- `topics/index.md`：github-radar 行由「九轮」更新为「十七轮」并补 `MAXPAGE` 撞顶与 carrier 对照组；新增 `narratives.md` 指针（此前是孤儿文件，虽只有一节、无需按 4 节规则清理）。

## 未处理项

`memory/topics/` 下仍有 10 个 `.py` 临时脚本（`.h1check.py` / `.writestate.py` 等）和 100KB 的 `price-alert-state.json.bak`，属 price-alert 停用后的遗留。不在 MEMORY.md 合并范围内，且删除需走 PR，本轮不碰。

## Summary

- **做了什么：** 执行 memory-flush —— 按 watermark 扫描当日日志，把只存在于 MEMORY.md 超长行的第十六/十七轮判据下沉到 topic，补 3 条 lesson 与 1 条项目状态，剪枝冗余，恢复预算。
- **修改的文件：** `memory/MEMORY.md`（8,615 → 6,712 字节，54 → 49 行）、`memory/topics/github-radar.md`（+2 节 / +7 条判据 / +2 Citations，timestamp 2026-10-26T23:40Z）、`memory/topics/lessons.md`（+3 条，timestamp 2026-10-26T23:45Z）、`memory/topics/index.md`（+2 处）、`memory/logs/2026-10-26.md`（新增 `### memory-flush` 两段）、`memory/memory-flush-state.json`（stamp 至 2026-10-26）。
- **状态：** `MEMORY_FLUSH_OK`，watermark 已推进。
- **后续动作：** 无阻塞项。遗留的 `memory/topics/*.py` 与 `.bak` 清理需要一个独立 PR，建议与 price-alert 重启评估一起做。

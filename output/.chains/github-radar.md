## github-radar 第十三轮 · 30 天窗 · probe · dry-run

**口径**：`var=dry-run days:30 probe`｜18 词 × 3 窗（9/26–10/26）× 3 页｜star 地板 0｜dry-run，未写 seen（仍 1891），未发通知。

### 漏斗
原始 2237 → 丢 seen 1085 / excl 139 / archived 2 / **short_desc 399** / **carrier 479** / neg 58 / pages 52 / farm 23 / fail 0 → 幸存 **0** → 报告级 **0**。查询失败 0，耗时 136s。`pages_root=0`——第十二轮加进代码的根目录规则已经把静态站全拦在上游了。

### 四分类（分开写）
- **A 查询失败**：0
- **B 真零**：1 — `maximal extractable value`
- **C 全已见(饱和)**：17
- **D 有新增**：0

**C 这个「饱和」是假的。** 这是本轮唯一实质发现。

### 判据级发现

**① 「饱和」标签本身错了。** `scan.py:443` 用 `raw_term>0 and new_term==0` 判饱和，而 `new_term` 只在**全部过滤器跑完之后**才自增，结果「被 carrier/short_desc 丢光」和「真被 seen 吸收」被算成了同一类。`world model` 一词在 30 天窗里复算：seen 吃掉 **54** 个，carrier 吃掉 **132**，short_desc 吃掉 **79**。**主体是过滤损耗，不是饱和。**

**② carrier / short_desc 正在吃掉活仓。** 抽两个丢弃堆里 `pushed_at` 最新的各 14 个逐仓核 commits：**carrier 堆 9/14 是活仓，short_desc 堆 8/14 是活仓。**

| 仓库 | 30d/7d | ★ | 死在哪 |
|---|---|---|---|
| `latent-horizon/pytorch-world` | 85 / 47 | 2 | carrier |
| `gimocimo/aero-adapt` | 84 / 37 | 0 | carrier |
| `mysukriramli/world-model-patch-wire` | 11 / 11 | 1 | carrier |
| `social-world-model/parabox` | 22 / 21 | 0 | short_desc |
| `Weizhi727/VLA-World-Model-Research` | 15 / 15 | 0 | short_desc |

全是 ★0–2——star 排序照样看不见。`short_desc` 的 25 字符门槛对「无 description 的论文官方实现」是硬伤（`Tsinghua-MARS-Lab/RepresentationWorldModel` 这类 desc 为空）。

**③ `sort=stars` 不是切长尾，是切掉整条。** 同一查询换 `sort=updated`：`world model` 100 个里 **76 个不在 seen**（jepa 52 · teleoperation 32 · VLA 22）。SKILL.md 第 42 条已写「star 不该出现在排序里」，**但 `scan.py:204` 仍是 `sort: stars`**——规则进了文档没进代码。

**④ probe 本轮静默空转。** 幸存 0 → `out.json` 写成 `[]`（2 字节）→ 无种子 → `clusters.json` **没有重新生成**（mtime 仍是第十二轮的 05:41）。**这恰恰是最该用 probe 的一轮**：活仓全躺在丢弃堆里，而 probe 只从报告级反查。种子池应改成「幸存 ∪ 高丢弃堆里 pushed_at 最新的 N 个」。

**⑤ `maximal extractable value` 是窄窗假零，不是死词。** 跨窗量：7d=**0** / 30d=**0** / 60d=**2** / 全期=**48**。脚本那句「可考虑删词」照做就是错的。

**⑥ `SuperMimic` 盲区第四次复现**：30 天窗 55 仓 / 55 owner，**只有 6 个在 seen**，49 个词表全盲，与第十二轮（53/55 盲）同水位。

### 本轮没做的事
`scan.py` 未改动（dry-run 轮不动过滤器）。三条待修都在同一个文件：`sort` 参数、四分类归属、probe 种子池。要动的话应该单独一轮改完再跑全量。

## Summary

**做了什么**：跑完 github-radar 第十三轮（`dry-run days:30 probe`），幸存 0 / 报告级 0，dry-run 未落 seen、未发通知。对「0 命中」做了归因验证，确认不是饱和而是过滤损耗。

**文件创建/修改**：
- `memory/logs/2026-10-26.md` — 追加第十三轮完整记录（漏斗 + 四分类 + 6 条判据级发现）
- `output/ghradar/verify13.py` · `tail13.py` · `where13.py` · `drop13.py` — 验证脚本
- `output/ghradar/out.json`（本轮 `[]`）、`audit.log`；`clusters.json` 未更新

**后续需要处理**：
1. `scan.py:204` 的 `sort=stars` → 改 `updated` 或去掉排序
2. `scan.py:443` 四分类改按丢弃规则归属，`new_term` 不能当饱和判据
3. carrier 词表要复核（`world model` 一支漏活仓 9/14）、`short_desc` 25 字符门槛对空 desc 论文仓放行
4. probe 种子池扩容到丢弃堆
5. `output/ghradar/` 积压十二轮一次性脚本，建议只留 `scan.py` / `out.json` / `audit.log` / `report.md`
6. 工具调用约 23 次，超 15 预算 1.5×——超支全在验证假饱和上

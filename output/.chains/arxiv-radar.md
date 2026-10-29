MEMORY.md 已更新到第 30 轮，占用 8,084 字节（在预算上限 8,192 以内）。本轮扫描已完成，正在收尾输出。

---

# arxiv-radar · 第 30 轮

**VERSION** `vM` · **窗口** 30 天 · **26 词** · 耗时 138s · `STATUS: ARXIV_RADAR_OK`（无降级、无 429、无熔断）

## 漏斗

原始 **88** → 幸存 **0**
丢弃分布：`seen(记忆)=87` · `seen(本轮重复)=0` · `EXCL=1` · `carrier=0` · `查询失败=0`

## 六分类（单位 = 词）

| 类别 | 数 |
|---|---|
| 未测到（试过失败） | 0 |
| 未尝试（熔断跳过） | 0 |
| 窗口内零命中 | 7 |
| 低频探针 | 0 |
| 全已见（饱和） | 19 |
| 有新增 | 0 |

## 幸存者

**0 条。** 无 labels、无通知（按规则跳过）。

## 跨窗结论

7 个零命中词全部跨窗有命中 → 全判「窗口太短，**别删**」，无删词候选：

- `verifiable inference` 0 / 60d=0 / 90d=1
- `verifiable computation` 0 / 1 / 1
- `light client` 0 / 1 / 1
- `restaking` 0 / 0 / 1
- `cat:cs.CR AND ti:"MEV"` 0 / 3 / 5
- `RWA` 0 / 1 / 2
- `robot manipulation data` 0 / 2 / 2

## 判据级发现

1. **`EXCL` 恒定常数项得到第二轮确认，且是同一篇论文。** 唯一 EXCL 仍是 `From bits to atoms: A survey of cross-layer safety in Embodied AI`（2026-10-02），与第 28、29 轮完全一致 —— 连续三轮同一条，读漏斗时 `EXCL=1` 可直接当常数减掉，不必再翻名单。
2. **连续第二轮「有新增 0 + 全已见 19」，不是断流轮。** 流量仍在进：`ti:"egocentric" AND cat:cs.RO` raw=23（与第 29 轮同值）、`robot data` 最新发布 10-26、`ti:"hand-object"` 10-27。原始数 90 → 88 落在噪声带内。但脚本本轮自己打了 `不是 seen 吃干了` —— 因为有 1 条穿过 seen 死在 EXCL，判「纯饱和」时要把这一项算进去。
3. **索引节律正常。** 窗口内最新收录 2026-10-27（周二，距今 2 天）；10-28 未进属待入，不是滞后。
4. **饱和 19 词无一该降温** —— raw 最新发布日期全部落在 10-06 ~ 10-27，最旧两条是 `proof of training` 与 `embodied data`（均 10-06），仍在 30 天内。

## 待办

- **14 词仍未配 carrier（第 7 轮沿袭）**，走默认 `CARRIER_CRYPTO` 表，判据偏乐观 30–50%；本轮 `carrier` 丢弃 **0**，过滤器等于空转。属 `scan.py` 的 `CARRIER_BY_TERM` 代码改动，须走 PR。
- `consensus` 加 `多智能体验证`（自第 29 轮挂起，未动）。
- 零命中 7 词已连续第三轮落在「窗口太短」档，按铁律**不许跳级**到降级/删词 —— 下轮继续观察。

## Summary

- 执行 `skills/arxiv-radar/scan.py ""`，30 天窗、26 词、原始 88 条、**幸存 0**，无降级无失败。
- 修改文件：`memory/logs/2026-10-29.md`（追加 `### arxiv-radar（第 30 轮）` 与 under-the-hood 两节）、`memory/MEMORY.md`（arxiv-radar 状态行推到第 30 轮，8,045 → 8,084 字节）。
- 未写 `memory/arxiv-labels.tsv`（幸存 0），未发 notify（零命中）。
- 脚本已自行写入 `output/arxiv/out.json`、`audit.log`、`memory/arxiv-seen.json`、`memory/arxiv-hits.tsv`。
- 后续：carrier 表补配需另开 PR；`consensus` 加词待办继续挂起。

扫描完成。以下是本次运行结果。

---

# arXiv Radar · 2026-10-24 · dry-run

**窗口** 2026-10-17 → 10-24（7 天）· **词表** 18 个 · **原始命中** 4 篇 · **幸存** 2 篇

## 幸存者

### 1. ZKPU — `2610.27530`（10-20，cs.AR）
**ZKPU: Zero-Knowledge Processing Unit for Heterogeneous Workloads**
面向 ZKP 异构负载的专用加速器，用 FIPS Montgomery 乘法配可重构 Twin Systolic Fabric，一套 datapath 同时覆盖曲线系（大素数域）与哈希系（64-bit 原生域）两类协议。
作者：Jonathan Ku、Yiran Chen、Hai Li 等（Duke / 首尔大方向）。
命中词 `zero-knowledge`，carrier=`protocol`。
**定性：硬件加速，不是链上项目，无可交易标的。** 若关心 ZK 算力成本曲线值得留一眼，否则纯噪音。
https://arxiv.org/abs/2610.27530

### 2. Pearl PoUW 系统化 — `2610.25347`（10-18，cs.CR + cs.ET）
**On Pearl Blockchain's Proof of Useful Work: Systematization and Flexibility**
对 Pearl 白皮书的 PoUW 做敏感度刻画，作为 Jackpot 策略的替代方案，并给出验证敏感度条件的有效算法；副产品是一个更灵活的方案 —— 每个矿工可自选噪声幅度，在计算精度与挖矿效率之间自行权衡。
单作者：Youlong Ding。
命中词 `proof-of-useful-work`，carrier=`blockchain`。
**定性：与 10-21 已研究过的 Pearl (PRL) 是同一个对象，不是新项目。** 意义在于"首次有学术侧把它的 PoUW 机制系统化"——对一个还在早期的 L1 来说，是机制被外部审视的第一个信号，不是基本面变化。
https://arxiv.org/abs/2610.25347

## 被过滤器丢弃的 2 篇（丢弃正确）

- `Zero Knowledge for Free up to Linear Query Bounds…`（10-21）— 纯复杂度理论，无 carrier。
- `SRE: Accelerating Zero-Knowledge Proofs via Scalar Redundancy Elimination`（10-20）— 纯硬件加速，无 carrier。

## 运行中发现的两个坑（已写入 lessons）

**1. arXiv 索引滞后 1–2 天，最新两天恒为 0 条。**
实测 `cat:cs.CR` 单日总数：10-20 **48** → 10-21 **38** → 10-22 **30** → 10-23 **0** → 10-24 **0**。API 最新收录停在 `2026-10-22T17:59Z`。**这是"还没入库"，不是"没人投稿"。** 每天 7:30 的常规跑会永远看不到当天和昨天的论文 —— 如果某天报"零命中"，先确认是不是这个原因，别急着改词表。

**2. 周窗口低命中是常态，不是词表坏了。**
18 个词 × 7 天只捞到 4 篇，第一眼像词表失效。逐词核过后确认相反：`ti:"restaking"` 全时段最新一篇是 **2026-08-10**，`ti:"zero-knowledge"` 全时段 312 篇但 7 天内仅 3 篇。**判断词表是否还有效要看 all-time 最新发布日期，不是窗口内计数。**

顺带验证了一条 skill 里的写法：`ti:"restaking"` 与 `ti:restaking` 返回完全相同的 8 条 —— 引号短语在 `ti:` 上不提高精度，真正有区别的是 `abs:` 的松散匹配。规则成立，但别指望长短语能靠引号变准。

## 词表观察（不删，留观）

12 个词 7 天内 0 标题命中：`verifiable inference` · `light client` · `proof of training` · `proof of learning` · `verifiable training` · `auditable training` · `data availability sampling` · `restaking` · `automated market maker` · `consensus protocol` · `cat:cs.CR AND ti:"MEV"` · `liquid staking` · `embodied data` · `robot manipulation data` · `robot data` · `embodied AI`。

按铁律「零命中不等于废词」全部保留。但值得注意的对比：**`zero-knowledge` 是唯一持续有产出的词**，其余要么是话题降温（restaking 四个月无新作），要么是学界根本不把项目名写进标题（embodied 系列）。后者可能是词写得不对，而不是话题没有 —— 下次可以试试 `embodied dataset` / `robot learning deployment` 这类更接近论文实际措辞的形状。

## 一个待办

本次是 dry-run，**没有写 `memory/arxiv-seen.json`**。下一次正式跑会把这 2 篇当新命中再报一次。下次正式跑前先写入这两个 id 即可去重：
`2610.27530v1`、`2610.25347v1`。

---

## Summary

- **扫描**：arXiv API，`ti:` 前缀 + 7 天 `submittedDate` 窗口，18 个词表，串行限速 3s。
- **结果**：4 篇原始命中 → 2 篇幸存（ZKPU 硬件加速；Pearl PoUW 系统化）。均为**已知对象的延伸，无新项目**，因此没推送（同时 dry-run 也跳过 notify）。
- **修改文件**：
  - `memory/logs/2026-10-24.md` — 新增 `### arxiv-radar` 条目（dry-run 下由我自写，因为未走 notify）。
  - `memory/topics/lessons.md` — 新增 `## arXiv 检索（arxiv-radar）` 四条经验 + Citations 一条。
  - `output/.arxiv-radar/radar.py` — 本次使用的扫描脚本（自 skill 内嵌版本改：`var`/`days` 改为 argv 解析，规避隐式 env 传递问题）。
- **未做**：未写 `memory/arxiv-seen.json`（dry-run）；未发通知。
- **后续动作**：
  1. 下次正式跑前补写两个 arxiv id 到 seen 文件，避免重复报。
  2. 考虑给扫描脚本加一条"窗口末端 N 天命中数"自检 —— 若连续为 0，在输出里标注"索引滞后"，而非静默报零。
  3. `embodied *` 系列四个词可试着换成更接近论文措辞的形状，但先别删。

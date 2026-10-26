ℹ️ github-radar 第十轮 · 7 天窗 · dry-run

## github-radar 第十轮 · 7 天窗 · dry-run

**口径**：`days:7`，18 词 × 3 窗 × 3 页，star ≥0，核验**全量 26/26**。dry-run，未落 seen、未写 candidates、未发通知。

**漏斗**：原始 592 → 幸存 **26** → 报告级 **5**。查询失败 0，gh 认证全程未丢。

### 报告级（30 天 ≥5 提交，按 7 天排序）

| 仓库 | ★ | 30d | 7d | 词 | 一句话 |
|---|---|---|---|---|---|
| [shangchaohu718/supermimic-pera](https://github.com/shangchaohu718/supermimic-pera) | 0 | 19 | 19 | world model | G1 SuperMimic-PERA，已跑通滑板技能独立验收（39.87–42.13m 滑行）|
| [eshaan2418/Recall](https://github.com/eshaan2418/Recall) | 0 | 19 | 19 | egocentric | 端侧情景视觉记忆，「钥匙放哪了」不出设备，Android+Kotlin+CI |
| [ZaidKamil1574/Robot-Teleoperation](https://github.com/ZaidKamil1574/Robot-Teleoperation) | 0 | 16 | 16 | teleoperation | Unity 6 + Meta Quest 数据中心遥操 + Da Vinci 手术臂仿真 |
| [SetsunaFSeiei21/Circuit-OP-JEPA](https://github.com/SetsunaFSeiei21/Circuit-OP-JEPA) | 0 | 9 | 9 | jepa | JEPA 拿去做模拟电路工作点预测 —— **JEPA 已溢出到 EDA** |
| [syaok1/wm-outcome-pilot](https://github.com/syaok1/wm-outcome-pilot) | 0 | 5 | 5 | world model | ⚠️ **纯静态站**（index.html+.nojekyll），世界模型结局预测研究页 |

### 🔴 本轮最大发现：词表对 `SuperMimic` 几乎全盲

18 词只捞到 55 仓簇里的 **2 个**。直接反查 `"SuperMimic" in:name,description`（10-19 起）= **55 仓**，逐仓核验 **25 个 7d≥5 提交**：

| 仓库 | ★ | 30d | 7d |
|---|---|---|---|
| [sxh-kk/SuperMimic_Recurrence](https://github.com/sxh-kk/SuperMimic_Recurrence) | 0 | **85** | **85** |
| [QinnyuLan/SuperMimicCarnival](https://github.com/QinnyuLan/SuperMimicCarnival) | 0 | 33 | 33（索引仓）|
| [CesarLiu/smimic](https://github.com/CesarLiu/smimic) | 0 | 31 | 31 |
| [LaoYang1994/SuperMimic-Rep](https://github.com/LaoYang1994/SuperMimic-Rep) | 0 | 27 | 27 |
| [Motphys/Uni-SuperMimic](https://github.com/Motphys/Uni-SuperMimic) | 137 | 22 | 22 |

**全扫的 7 天最高值只有 19，簇内最高是 85。** 原因：这批仓名/描述只写 `SuperMimic`，不写 `world model`/`sim2real`。**新专名（不只是缩写）是「有人在写代码」最强的信号，而按机制词组织的词表结构上抓不到。**

**star 再次反向**：`zita-ch/supermimic_vibed` ★553 只有 4 提交（自称 "vibe coded within 1h"），而 ★0 的 `sxh-kk` 有 85。

### 词表四分类

- **查询失败**：0
- **真零（7d total=0）**：`verifiable inference`（30d=6/60d=7）· `proof of useful work`（30d=6/60d=13）→ **窗口太短，不是词废**；`maximal extractable value`（60d=2）→ 真稀
- **全已见（饱和，别删）**：`data availability`(23) · `vision language action`(18) · `world action model`(11) · `embodied data`(5) · `robot dataset`(5) · `restaking`(2) · `robotics data engine`(1)
- **有新增**：`world model`(216/9) · `teleoperation`(57/6) · `robot manipulation`(34/3) · `egocentric`(27/3) · `jepa`(120/2) · `sim2real`(29/1) · `sim-to-real`(28/1) · `intent-based`(16/1)

### 过滤器审计

- **carrier 假误杀**：只排 carrier 一条时，120 个被丢仓里 43 个是报告级 —— 但**重放整条管线后净增只有 1 个**。EXCL 挡 11、short_desc 挡 27、后缀挡 7、仍离题 73。**单条规则审计会得出 43 倍的虚高误杀。**
- **carrier 真缺陷**：只看 description 不看 topics。`UCSC-VLAA/ALPS`（topics: embodied-ai/robot-learning/libero）被误判离题。同类 13 个，多数是 awesome 列表 —— 单改 carrier 会多放 12 个列表仓。
- **站点后缀规则验证通过**：丢 17 个，含 357MB 的 `mundo-world-model.github.io`。若留着「体量小」条件，这三个会全进报告级。**但留一个洞**：`syaok1/wm-outcome-pilot` 无后缀、不同名，靠人工才看出是静态站。
- **NEG 有效**：`jepa` 丢 15 个印尼语污染（`Belajar-Jepang` / 地名 `Jepara`）。

### 加密侧

**零报告级。** `intent-based` 唯一新仓 `Zahraxy09/intent-centric-web3-2026` 只有 LICENSE+README、无 language。`data availability`/`restaking` 全饱和，`vearl` 未回捞。

### 方法学

- **7 天窗会把稀有词读成假零**：判词表死活必须量 7/30/60 三个 total_count（见 `terms10.json`）。
- **dry-run 下「真新增 26」不可当增量**：上轮 created≤7d 的 31 个已全部推出窗口，本轮 26 是换窗口的算术结果。
- **下轮非 dry-run 时这 26 个会全部重复回捞**（第九轮已验证的 3.6× 噪音机制）。

[source: api.github.com/search/repositories · 18 词 × 3 窗 · created:2026-10-19..2026-10-26 · fork:false · stars:>=0 · 快照 `output/ghradar/out10.json` · 簇探测 `cluster10.json` · 跨窗词表 `terms10.json`]
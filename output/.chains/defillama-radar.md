ℹ️ defillama-radar 更正（2/2）：桥类批次不属同类目

**defillama-radar 更正（第二处，最后一条）**

上一条更正里「与 10-07 那批 22 条桥同型」仍不准确，改两点：

- **10-07 那批桥不是同类目**：横跨 `Cross Chain Bridge`(15)/`Canonical Bridge`(5)/`Bridge Aggregator`(1)/`Bridge`(1) 四个类目字符串，属「类目也混」的另一类。
- **不是「第三次」**：全量 31 组同秒簇分三类 -- 同 parent 5 组、同类目跨 parent 4 组、类目与 parent 都混 22 组。本轮加密卡属第二类，前有 2022-06-18 Lending、2024-03-12 Dexs。

**净结论不变**：6 条加密卡是常规的同类目跨 parent 同秒回填，不新、不必细看；可报仍是 `Paboxo` + `zkAPI` 两条，已标记。

根因一条：拿本轮差集当全量去断言「首次/第 N 次」。已记进 lessons。
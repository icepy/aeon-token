那个监视器是无效的 —— 它的循环条件 `pgrep -f pagekill5.py` 会匹配到监视器**自己**的命令行（命令字符串里就含 `pagekill5.py`），所以永远不退出。而 `pagekill5.py` 本体早已跑完，结果我也读了：

```
21 个被 pages 族规则丢弃的仓 → 4 个是真代码仓且 ≥5 提交/30d
  UniWAM/UniWAM              Python 3300KB  c30=20
  dextacwam/DexTacWAM        Python 3075KB  c30=26
  Agentic-WAM/agentic-wam.github.io  CSS 594477KB c30=20
  Prism-WAM/prism-wam.github.io      JS  75842KB  c30=14
```

这条结论已经写进报告和 `memory/topics/lessons.md`。**无需重跑任何东西。**

第五轮终态不变：扫描完成（原始 2,427 / 幸存 1,207 / 报告级 89 / 净 82）、三组验证完成、`memory/` 四处已更新、dry-run 确认未写 seen 与 candidates、未发通知。

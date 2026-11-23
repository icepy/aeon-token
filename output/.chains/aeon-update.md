ℹ️ aeon-update

*aeon-update - 2026-11-23*

**同步 13 条上游提交 → PR #28**，但净变更为零。

上游 `aeonfun/aeon` 从 `7b20c95` 到 `f94f39e` 有 13 条提交。三个可自动合并的文件（`aeon.yml` 的 MCP deny-list、`messages.yml` 的 1200s 超时、dashboard 技能图标）**本地早已与上游 HEAD 逐字节相同** -- 上一轮之后手工同步已超前，3-way 合并没有产生任何差异。这个 PR 的唯一实质作用是**把 baseline 推进到 `f94f39e`**，让下一轮只拉真正的新东西。

上游这 13 条里值得知道的两条：新增 `icp-mcp` 技能（托管 ICP MCP，默认停用）；`skill-scan.sh` 改为扫描整个技能目录而不只看 `SKILL.md`（本地已同步）。

**需要你决定的只有一件事：** 5 条冲突全是文档里的「92 → 93 skills」计数漂移，跟上一轮 PR #27 一模一样。要么把这 5 个路径写进 `keep_local`，要么接受上游的数字 -- 二选一，否则每轮都会挂在这里。清单在 PR 正文里。

PR: https://github.com/icepy/aeon-token/pull/28

`pending_conflicts` 6 条（含沿用的 `.gitignore`）。
# Knowledge — topics index

Durable knowledge notes live under `memory/topics/`, one concept per markdown file.

# Reference

- [Base RPC access from the runner](/topics/base-rpc-access.md) — the one keyless endpoint that works, its 1,000-block `eth_getLogs` cap, and how to tell a quiet window from a broken query.
- [Scheduler & notification plumbing](/topics/ops-plumbing.md) — how to prove scheduled dispatch actually fires, why to write plain Markdown in `./notify`, and which state-file writes (`cp`, `jq -f`) the permission layer silently blocks.
- [price-alert state file contract](/topics/price-alert-state.md) — what each field in `price-alert-state.json` means and why targets must be pre-seeded.
- [Lessons learned — archive](/topics/lessons.md) — the full detail behind each one-line lesson in MEMORY.md (wallet watch topic filters, keyless RPC, calldata vs chain facts, and when a missing `h1` or a zero-volume hour is *unmeasured* rather than calm).
- [World Action Models (WAM)](/topics/world-action-models.md) — the 2026 WAM term on GitHub: weekly convergence curve, the paper-repo → engineering-repo split, and why star order is not activity order (★1106 with 11 commits vs ★48 with 10).
- [github-radar — 实现缺陷与判据](/topics/github-radar.md) — 九轮实证的过滤器陷阱：`PER_TERM_CAP` 抽样低估 3.85×、`pages` 两侧误判、缩写→全称只在类别通名上成立（`vla` 赢 / `jepa` 亏 94.6%）、以及「已合并 ≠ 已生效」。

## Tokens

- [Note Systems (NOTE)](tokens/note-systems.md) — Robinhood Chain 4663 结构化票据代币；timelock 持 25.42%，48h 延迟解锁，owner 为单个 EOA。含两轮砸盘手法、`0xfdd9` 整块风险修正
- [DEUS / xDEUS watch addresses](/topics/deus-escrow.md) — token, escrow, and xDEUS NFT addresses; why xDEUS being an ERC-721 needs no config change; stake/unstake pairing; counterparty map.
- [DEUS 事件流水](/topics/deus-events.md) — 10-23 → 10-24 逐小时明细归档：四次 claim-and-dump、跨场所拆分、复活/静默、escrow 逐 wei 闭合。MEMORY.md 只留当前状态，历史看这里。


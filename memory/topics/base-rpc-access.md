---
title: Base RPC access from the GitHub Actions runner
description: Which Base endpoints actually work keyless from this runner, and the eth_getLogs window cap that shapes every on-chain scan.
tags:
  - crypto
  - base
  - rpc
  - runbook
resource: https://base.gateway.tenderly.co
timestamp: 2026-10-24T09:35:00Z
---

# Base RPC access from this runner

Verified 2026-10-21. Keys `ALCHEMY_API_KEY`, `ETHERSCAN_API_KEY`, `COINGECKO_API_KEY` were all
**unset** in the run environment, so every on-chain read is keyless. This file records what that
costs, so future runs don't re-run the endpoint hunt from scratch.

## What works

| Endpoint | Status |
|---|---|
| `https://base.gateway.tenderly.co` | ✅ works — `eth_blockNumber`, `eth_getLogs`, `eth_call` |
| `https://mainnet.base.org` | ❌ 403 from this runner |
| `https://base.drpc.org` | ❌ 403 |
| `https://base-rpc.publicnode.com` | ❌ 403 (archive token required) |
| `https://base.llamarpc.com` | ❌ 403 |

Etherscan v2 free tier refuses `chainid=8453` keyless, so the intended Path B is unavailable too.
Net: **Tenderly public gateway is the only live path** without keys.

## ⚠️ 2026-10-22：`$BASE_RPC_URL` / `$RH_RPC_URL` 已变成 Infura 免费档（10 块上限）

两个 workflow env 变量现在都指向 Alchemy/Infura 免费档端点，`eth_getLogs` **最大只允许 10 个块**：

```
Under the Free tier plan, you can make eth_getLogs requests with up to a 10 block range.
Based on your parameters, this block range should work: [0x5a3a000, 0x5a3a009].
```

后果：任何分窗扫描脚本（含 `memory/rpc.sh`，它优先读这两个 env）会不断把窗口减半，最后在
10–500 块之间反复失败，看起来像"卡住"或"零日志"，**实际是端点拒绝**。

判定：错误体里出现 `Free tier plan` + `10 block range`。
处置：**显式绕过 env**，直接打公共端点：

| 链 | 端点 | 实际窗口 |
|---|---|---|
| Base | `https://base.gateway.tenderly.co` | 1,000 块 |
| Robinhood | `https://rpc.mainnet.chain.robinhood.com` | 24,000 块 |

2026-10-22 21:05Z 这轮按上述端点跑：Base 22 calls / 0 retries、RH 每 job 18 calls / 0 retries，全部 200。

⚠️ 零日志窗口仍要按老规矩验证（控制窗口 + `eth_call` 余额），别把端点拒绝当成"平静"。

## The 1,000-block cap

Tenderly's public access rejects wide ranges:

```
Block range too large for public access: maximum 1000 blocks.
```

So walk any range in 1,000-block windows. At Base's ~2s blocks that is ~33 min per window, and a
24h backfill is ~43 windows per direction — cheap in time, but the reason scans must be looped
rather than issued as one call.

## Always pass an `address` filter — the 20,000-result cap

Observed 2026-10-21T10:12Z: a **203-block** range on the unfiltered xDEUS leg failed with

```
query exceeds max results 20000, retry with the range 52893845-52893896
```

A three-minute window was too wide once every Transfer on Base was in scope. Fix: put the contract
address in the query (`"address": "0x…"`) rather than only in the topics, and scan that token's logs
alone. Filtered queries returned cleanly for the same range. Base Transfer volume means an
**unfiltered** `eth_getLogs` is no longer viable at any range — never scan "all Transfers on the
chain" just because the topic filter would sort it out afterwards.

Also note the error message suggests a *narrower* range; that works but is far slower than adding
the address filter, which fixes the cause rather than the symptom.

## Topic filters work — don't misread a quiet window as a broken query

`topics: [Transfer, null, <addr>]` and `topics: [Transfer, <addr>, null]` both behave correctly
here. A sampled window returning 0 logs is **not** evidence the filter was dropped; verify with a
control query against a window with known activity before concluding anything.

That control step matters: on this run the new window returned zero across all three streams,
which looks identical to a silent fetch failure. Re-querying the prior 24h produced 10 escrow DEUS
logs and 21 xDEUS logs, matching the previous run exactly — and the escrow DEUS balance was
byte-identical before and after. Only then was "zero activity" a trustworthy claim.

## Cheap independent confirmations

- **Token balance via `eth_call`** `0x70a08231` + padded holder address against the token contract.
  For a staking escrow this is the strongest single fact available: if it is unchanged to the wei,
  nothing moved, regardless of what the log query returned.
- **`eth_chainId`** should be `0x2105` for Base — confirms you're on the right chain before trusting
  any address lookup.
- **`18160ddd`** = `totalSupply()`, for expressing escrow size as a share of supply.

See [DEUS escrow watch](/topics/deus-escrow.md) for what these watchers are for.

# Citations

- Base RPC endpoint list + public-access range limit observed live from `https://base.gateway.tenderly.co`, 2026-10-21.

## ⚠️ 2026-10-24：三个会静默毁掉一轮扫描的坑

均在本轮 `onchain-monitor` 实测，每一种都长得像「链上平静」。

### 1. Robinhood RPC 对 urllib 默认 User-Agent 返 403

```
HTTP Error 403: Forbidden
```

`curl` 同一 URL 立刻 200。**判定**：JSON-RPC 层没回错误体，是 HTTP 层被 WAF 拒 —— 扫描脚本若只捕获异常字符串，会把它记成「该窗口无事件」。**处置**：显式带 `User-Agent: curl/8.5.0`（或任意非 `Python-urllib/x.y`）。

```python
urllib.request.Request(url, data=body, headers={
    'Content-Type': 'application/json',
    'User-Agent': 'curl/8.5.0',
})
```

这轮因此浪费约 40 分钟、17 个窗口全假空，直到对已知活跃块做 control 才暴露。

### 2. Robinhood 公共 RPC 不支持历史 `eth_call`

```
historical state 3b8fa680... is not available
```

只有 `'latest'` 能读。**后果**：不能靠回查旧块 `balanceOf` 验证余额变化，历史余额必须由 **log 差额**推（本轮的 vesting 余额就是这么算的：`old − sum(out) + sum(in)`）。Base 的 Tenderly 网关则**支持**任意历史块 `eth_call`（本轮用 12 个时点回溯 `ownerOf` 证明一个 NFT 的持仓时长），两条链的能力不对称，别互推。

### 3. Uniswap v4 的 `pairAddress` 是 poolId，不是合约地址

DexScreener / GeckoTerminal 对 v4 池返回的 `pairAddress` 是 **32 字节的 poolId**（如 NOTE 主池 `0x378b1023…7f9f91`）。把它当合约 `eth_call`，`token0()` / `token1()` / `getReserves()` / `slot0()` / `liquidity()` / `fee()` **全部返回 `0x`**，看起来像池子不存在。

**处置**：v4 池的价格/储备走聚合器（GeckoTerminal pool 端点，或 DexScreener token 端点），或直接读 PoolManager（`0x8366a39c…e40951`）的 `extsload`。**判据：六个标准 getter 全返 `0x` 而代币确实在成交 → 先怀疑是 v4，别怀疑代币死了。**

## Long scans must checkpoint

A single enumeration over ~400k blocks at 24k/window will be killed by the harness timeout with **zero output** if it only writes at the end. Write the progress file after every window (`json.dump` to `.tmp` then `os.replace`) and resume from a cursor — this run survived two kills that way.

---
title: DEUS / xDEUS watch addresses
description: The DEUS token contract plus the staking escrow and xDEUS NFT addresses every on-chain watcher reads, and what each one proves.
tags:
  - crypto
  - deus
  - base
  - runbook
  - onchain
resource: https://basescan.org/address/0xA85A38796B951CE87B378538b32B3E6Ee3C4C373
timestamp: 2026-10-25T08:09:17Z
---

# DEUS / xDEUS watch addresses

Chain: **Base** (`eth_chainId` = `0x2105`). Verified 2026-10-21 against live `eth_call` / `eth_getLogs`.

## Addresses

| Role | Address | Type | Threshold |
|---|---|---|---|
| DEUS token (ERC-20) | `0x940A319B75861014A220D9c6c144d108552B089B` | token, 18 decimals | — |
| Staking escrow | `0xA85A38796B951CE87B378538b32B3E6Ee3C4C373` | wallet (holds staked DEUS) | $200 |
| xDEUS | `0xe6d5f7439Bc236C40054e2275f765f59343D4431` | ERC-721 (soulbound) | $250 |

Configured in `memory/on-chain-watches.yml`; thresholds are per-watch USD.

## xDEUS is an NFT, not a token — and that is fine

`decimals()` **reverts** on xDEUS: it is ERC-721, and `Transfer` carries the `tokenId` in
`topics[3]` (four topics) rather than a value in `data`. This does *not* require changing the watch
config: the ERC-20 `Transfer` topic0 hash
(`0xddf252ad…23b3ef`) is the *same signature*, so the existing `event_topics` entry matches
mints, burns, and moves correctly. Only the decoding differs — don't read a value out of `data`.

## First recorded unstake → full dump (2026-10-24)

The 5-day xDEUS cooldown has now been observed being **paid and converted into market selling**
for the first time in the record. This is the clearest live proof of the STRATEGY premise: the
cooldown is the real cost of the multiplier, and somebody did pay it to exit.

- **23:09:15Z** — escrow `0xA85A…C373` burned **xDEUS NFT #1492** and released
  **319,562.226531 DEUS** to `0xbb0f7533` (plain EOA, `code 0x`, nonce 105).
  Tx `0xb62d28fafa1454fb26d84ee5146483319941fb96eb2baabe8c969321b5c54dfd`, block 53,002,812.
- **00:24:17Z** (75 min later) — the same address sold the **entire** 319,562.226531 DEUS into the
  deepest pool for 8,618.5315 VIRTUAL (~$5,488). Tx
  `0x156d9316ab040c0dd4c73ac02eafcfb9df2c58a930518dc8e476c5d9cbbaa762`, block 53,006,055.
  Post-sale DEUS balance: **0.000000** — full exit, nothing retained.
- This is **3.49×** the previous largest single dump on record (91,566 DEUS, 2026-10-23 00:32Z).

**Do not over-read the damage.** Measured off the pool reserves (constant-product mark
VIRTUAL/DEUS `0.02769675 → 0.02714852`), the true depth cost was only **−1.98%**. The USD tape
printed −4.37%, inflated by VIRTUAL's own move and a stale prior print. Recalibrated absorption:
**~$2.8k of notional per 1%** ($5,488 / 1.979%), not the ~$1.7k/1% inferred from the 91.5k dump — the book is deeper
than previously estimated. A record-sized unstake does **not** collapse this pool.

**Why it did not cascade:** six buys printed in the *same block* totalling 125,867.74 DEUS
($1,771) — largest `0x6011b76b` 62,825 DEUS, then `0x6abea499` 29,739 DEUS — plus a seventh
(11,529.69 DEUS) in the next block. Absorption 137,397.44 DEUS; net DEUS left in the pool after the
event **178,969.17** (after the 3,195.62 fee to `0x205db642`).

**Open forward signal — the trigger for the next dump:** this wallet **still holds one more xDEUS
NFT, tokenId #1396 (0x574)**, confirmed via `tokenOfOwnerByIndex(owner, 0)`. Since 1396 < 1492 it
was staked *earlier*, so this is a multi-position staker unwinding in tranches, not a one-off. The
size of #1396 is **not yet measured** — do not assume it matches 319,562. Watch escrow `Burn`
(topic0 `0xe08737ac`) for tokenId 1396.

**Not an exodus:** xDEUS `totalSupply` (`0x18160ddd`) went 1724 (−24h) → 1727 pre-burn → 1726
immediately post-burn → 1727 now. A new position was minted right after the burn; net 24h is **+3
NFTs**. Staking is still net additive. [source: logs/2026-10-24#price-alert]

## Reading stake vs unstake

Every stake or unstake pairs **one DEUS ERC-20 transfer** with **one xDEUS mint (stake) or burn
(unstake)** by the escrow. So:

- escrow DEUS balance **down** + xDEUS burn = someone unstaked.
- escrow DEUS balance **up** + xDEUS mint = new stake.

Seeing one without the other in the same tx means something unusual is going on. The strongest
single check is the escrow's DEUS balance via `eth_call` `0x70a08231` — if it is unchanged to the
wei, nothing moved regardless of what the log query returned.

**Wallet-type watches must be scanned as a topic filter on the token contract**, never as
`eth_getLogs{address: <wallet>}` — an EOA emits no logs, so that shape returns zero forever. This
bit the escrow, owner EOA, staging, and vesting watches simultaneously on 2026-10-21.

## The 5%/day research trigger

The operator's intel threshold is escrow DEUS **net outflow > 5% in one day**. On 2026-10-21 the
escrow held 29,362,657.94 DEUS, so that gate sat at **1,468,133 DEUS** in a day. Observed outflow
across the whole day was 43,512.49 DEUS = **0.148%** — two orders of magnitude short.

When the gate *does* trip, the question to answer is not "how much" but "who": one whale pulling
out reads as an internal/team move, a crowd of small holders reads as a sentiment shift. Check
whether counterparties are contracts (likely a staking wrapper or vault) or plain EOAs.

## Counterparty map (as of 2026-10-21)

- `0x7901…0185` — **contract**, staked 25,000 DEUS twice in the same day, holds 25,000 DEUS + 5 xDEUS.
  Largest single accumulator seen. Contract code with a tiny footprint (`0xef01…` prefix) suggests a
  smart-account/wallet-contract rather than a shared protocol.
- `0x6e5f…cba5` — **contract**, round-tripper: 13,385 DEUS in, 7,560 + 5,020 out, retains 12 xDEUS.
  Operates like an active staking position being resized, not an exit.
- `0xf196…437b` — **contract**, unstaked 18,512.68 DEUS and now holds 0 DEUS, 0 xDEUS. Fully exited.
- `0xd5ff…c724` — **EOA**, unstaked 12,419.81 DEUS and still holds **52,837 DEUS liquid**. This is the
  address that matters: the one real holder with both size and a demonstrated willingness to sell.
  Worth watching as a future addition to `on-chain-watches.yml`.

## Sizing reality

Daily volume is thin (~$11.5k on the deep VIRTUAL pair, ~$4.6k on USDC). The escrow's own 24h
activity was 10 transfers, median $179, max $447. Nothing here approaches the $200/$250 alert
thresholds on a normal day — thresholds are calibrated to catch exceptions, not routine staking.

## Scale reference (2026-10-21)

- Escrow holds ~29.36M DEUS ≈ 3.35% of 876,222,316 total supply.
- xDEUS supply 1,711; escrow holds 57.
- A 24h window carries ~10 escrow DEUS logs and ~21 xDEUS logs. An order-of-magnitude drop from
  that is a signal; an exact zero warrants a control query first (see
  [Base RPC access](/topics/base-rpc-access.md)).

## Why the escrow is the tell

Spot DEUS liquidity is thin and the staked position carries a 5-day unstake cooldown. Escrow
outflow is therefore the *leading* indicator that someone decided the cooldown was worth paying —
which is exactly the decision the sentinel exists to surface.

## The CLAIM vault — 38.8% of supply, dripping ~$6.4k/day (2026-10-23)

This is the largest structural fact about DEUS supply and it is **not** the escrow. Address
`0x5cbf5dfaa5336ce0456e24217e7911365100879a` — `name()`/`symbol()` both return `DEUS` — is a
vesting/distributor vault holding **340,146,039.82 DEUS = 38.82% of the 876,206,780.45 total
supply**.

It pays out at a strikingly constant rate:

| Window | DEUS out | Per day |
|---|---|---|
| last 24h | 350,214.42 | 350,214.42 |
| last 7d | 1,981,979.13 | 283,139.88 |
| last 30d | 9,988,856.31 | 332,961.88 |

That is ~0.040% of supply/day ≈ **$6.4k/day at $0.01820 — 40.8% of the deepest pool's entire 24h
volume ($15,635)**. The drip is steady, not accelerating, so it reads as routine emissions rather
than a regime change. **The risk is not the rate; it is that recipients dump.**

### Claim-and-dump is measurable — use the ratio, not the payout

Proof, 2026-10-23 00:32Z: plain EOA `0xbf328713670d3407e94c3ab60ff1c36f95748e70` (nonce 538)
received 30,546.279 DEUS from distributor `0x20d29c8e…6fc5` at 00:32:21Z, another 61,019.563 from
the CLAIM vault at 00:32:33Z, and sold **all 91,565.842 DEUS into the deepest pool at 00:32:53Z** —
**32 seconds from first receipt to full exit**. It ended at `balanceOf` exactly 0 with 0.00756 ETH.
Tx `0xe2edb1b0e96e9a2d336b80b931f172fc21ee5c7281068dd9ddc3c1d7b716e9ad`, block 52963113.

**Price impact: −0.933% in that one block.** Reserves moved DEUS 19,303,121 → 19,393,771 and
VIRTUAL 515,912 → 513,501. So **~$1.7k of notional moves this pool 1%**.

That ratio converts a vague "overhang" into distance-to-trigger arithmetic:

- The operator's **$0.012** floor is **−34%** away. At constant liquidity that needs ~**2.5M DEUS**
  sold at market — seven full days of the entire claim drip dumped at once. **Routine emissions
  cannot grind the price to $0.012.** It requires a deliberate large seller.
- Conversely **$0.041** (the unstake line, +125%) cannot arrive from emissions either; it needs
  genuine external buying.

Other distributors in the same cluster: `0x0ae95bd7…c4a7` (`CLAIM W2`), `0xd4c450ac…9409`
(`CLAIM`), plus `0x20d29c8e…6fc5` and `0xea247ce9…e6ae` (unnamed, both contracts, both holding
~9.2M DEUS and having transferred **0** DEUS into the deep pool in 7d).

### Emissions get re-staked too

Same window, the opposite behaviour: EOA `0x5a46519659e3557112b90a8becb891873fe17406` (nonce 83)
staked **10,000 DEUS** into escrow at 20:06:29Z (tx `0xf126500c…ab24`, block 52998321), now holding
**24 xDEUS NFTs**. Funding chain ran claim → EIP-7702 router `0xcd920c78` → staker → escrow inside
~6 minutes. **Not external new money** — recycled emission — but constructive: someone chose the
5-day cooldown over selling. Escrow rose to 29,418,223.901 (+0.034%), still orders of magnitude
below the 5%/day (~1.47M DEUS) intel trigger.

### Supply is net inflationary — someone actively holds the mint

Prior notes read "slowly deflationary" off single-window `totalSupply` reads. That is wrong:
single reads often just miss a mint. Over the 7 days to 2026-10-23 there were **37 mints /
201,697.86 DEUS** against **18 burns / 136,317.22** → **net +65,380.63 DEUS**. The run caught it
directly: block 52,996,523, tx `0xce65a0e0371a564807fd20c8825578fc78cd44d1da76650445127b9c6ba19285`,
**+14,413.4894 DEUS** minted by `0x2cca08ae69e0c44b18a57ab2a87644234daebae4` to
`0xd8f8e00e9d9ab9600a910f133f8959737e143e84` (EIP-7702 delegated account). That recipient held
20,785.16 for 30 days, 21,719.61 at −1h, **36,133.10** now — an entity exercising mint authority,
not a passive contract.

**Implication for the strategy:** dilution is a slow headwind against the $0.041 break-even line.
Don't claim "deflationary" from a single unchanged read. [source: logs/2026-10-23#price-alert]

### 2026-10-25 08:09Z — 85,829 mint, the largest single mint on record, fanned out to 8 dormant EOAs

The 14,413 print above is no longer the record. **Block 53,061,481 (07:11:49Z)**: mint contract
`0x2cca08ae69e0c44b18a57ab2a87644234daebae4`, selector `0xcfc32570`, called by
`0x7ddb0773e979cd36ef0dc8b6e594a6ebc876e654`, minted **85,828.91 DEUS** (6.0× the prior record) to
`0x42a1647e8a77f8325a7c7bf06096cda477915d39` (EIP-7702, code `0xef0100…`). Tx
`0xa83d52f2e9d045ba52355e8b250243635aaa25c0e4a06fc4c91e22026804d68e`.

**It was fanned out within 4.5 minutes.** Nine `Transfer` txs between 07:14:35Z and 07:16:13Z split
the full 85,828.91 to eight plain EOAs, closing to the wei; the first hop kept only **98.09**.

| Recipient | minted in | balance before | balance now |
|---|---|---|---|
| `0x5318d687` | 14,621.91 | 64,430.06 | 79,051.97 |
| `0x393f8acc` | 12,951.38 | 46,449.34 | 59,400.72 |
| `0x3d1aa83e` | 12,694.08 | 30,369.10 | 43,063.18 |
| `0xfb422428` | 11,926.29 | 43,252.18 | 55,178.47 |
| `0xd50de171` | 10,459.29 | 23,573.50 | 34,032.79 |
| `0x4af20629` | 8,612.18 | 42,768.35 | 51,380.53 |
| `0x9be2134e` | 7,593.33 | 56,963.21 | 64,556.54 |
| `0x380ce63e` | 6,970.44 | 5,334.50 | 12,304.94 |
| **total** | **85,828.91** | **313,140.24** | **398,969.15** |

**Read the addresses, not the size.** All eight have `nonce == 1` and all eight already held DEUS
before the mint (313,140 combined) — these are **dormant incumbents being topped up, not new
wallets**. The cohort's rolling balance: 384,051 at −30d → 327,370 at −7d → 398,969 now. It was
**net selling for a month and has just been re-armed**. As of 08:09Z **not one of the eight has
moved a single wei out** — this is supply being staged, not a dump in progress.

**What it does and does not change.** If all 398,969 hit the deepest pool at once the constant-product
mark goes **−4.08%** ($6,685 out); the mint tranche alone is **−0.90%**. Neither reaches any gate,
and zero of it has moved yet — so it does **not** justify pre-emptive unstake. What it kills is the
"deflationary" framing: `totalSupply` sat byte-identical for 12 straight hours and then jumped
**+85,828.91 in a single block**. Repeated "unchanged" reads were the mint missing the observation
window, never the absence of a mint. Watch the eight addresses for the first outflow — that is the
trigger, not the mint itself. [source: logs/2026-10-25#price-alert]

## The 338k/day "drip" is mostly internal plumbing — 2026-10-25

**This is the single most important correction to the CLAIM narrative.** Enumerated all **2,244**
DEUS `Transfer` logs out of the main vault `0x5cbf5dfa` over the exact 86400s window and classified
every recipient by `eth_getCode`:

| Recipient | 24h in (DEUS) | Type | Balance now |
|---|---|---|---|
| `0x20d29c8e…6fc5` (CLAIM proxy) | 150,082.04 | CONTRACT | 9,225,852.53 |
| `0xea247ce9…e6ae` (conduit A) | 113,872.81 | CONTRACT | 9,344,220.19 |
| `0x0ae95bd7…c4a7b` (CLAIM W2) | 40,441.16 | CONTRACT | 4,711,376.93 |
| `0xd4c450ac…9409` (distributor D) | 22,941.62 | CONTRACT | 1,331,275.67 |
| `0x2347c364…500f` (dumped same day) | 7,293.56 | EOA | 0.00 |
| `0xe338adc6…e61d` (staked it) | 3,771.14 | EIP-7702 | 30,903.11 |
| small (<200 each, 101 txs/hour base drip) | 191.97 | mixed | — |

- **97.8% of the gross outflow goes to four contracts the issuer controls**, and their combined
  balance is **RISING**: +331,108.77 received, net **+186,618.99** (24,426,115.51 → 24,612,734.50).
- So only **145,227.81 DEUS** was actually re-distributed outward by those conduits in 24h — **42.9%
  of the headline number, not 100%**.
- Of that 145,227.81, **zero** went straight into a DEUS pool. It broke down as: 93,716 through
  three confirmed claim→dump EOAs (`0xbd6383c7` 52,736.88 / `0x2347c364` 24,451.11 /
  `0x8180513f` 16,528.05 — all at balance 0 today), **23,756 into xDEUS stakes**, and ~27k to
  small EOAs and other contracts.
- **Realistic daily market supply ≈ 75,977 DEUS** (the dump EOAs plus small EOAs), i.e. **0.0087% of
  the 876.2M supply**, ≈ **$1,318/day** at $0.01734.

**Operational conclusion:** at the measured depth (~$1.7k notional per 1% move), $1,318/day of real
supply is under **1% of one percent** of a price move. The emission drip **cannot** reach the
operator's $0.012 floor and **cannot** justify unstaking. Both extreme gates need a deliberate
whale — the drip is background noise, not a threat.

**How to re-verify quickly:** `balanceOf` on the four conduits at now vs −86400s. If the combined
balance is *rising*, the drip is being warehoused; if it is *falling* faster than the payouts, real
distribution is accelerating. [source: logs/2026-10-25#price-alert]

# Citations

- All balances, transfers and counterparty classification read live from Base via
  `https://base.gateway.tenderly.co` (`eth_getLogs`, `eth_call`, `eth_getCode`), 2026-10-21.- ERC-721 behaviour of xDEUS confirmed via `eth_call` (`decimals()` reverts), 2026-10-21.
- Prices from DexScreener token endpoint for `0x940A319B75861014A220D9c6c144d108552B089B`, 2026-10-21.
- CLAIM vault balance/emission, claim-and-dump tx, price impact and the 10,000-DEUS stake: live Base
  reads via `https://base.gateway.tenderly.co` (`eth_getLogs` chunked ≤1000 blocks, `eth_call`
  `balanceOf`/`totalSupply`/`name`/`symbol`, `eth_getTransactionReceipt`), head 53,000,418, 2026-10-23 21:16Z.
- Escrow/xDEUS addresses from `memory/on-chain-watches.yml`; DEUS token from the `MEMORY.md` tracked-token table.
- Unstake-and-dump (`0xbb0f7533`, NFT #1492, 319,562.226531 DEUS): escrow `Burn` topic0
  `0xe08737ac…4def35` on `0xA85A…C373`; xDEUS `Transfer` (burn to `0x0`) topic0 `0xddf252ad…b3ef`;
  pool reserves via `eth_call balanceOf` on DEUS and VIRTUAL `0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b`
  at blocks `0x328cee6` / `0x328cee7`; xDEUS `totalSupply` `0x18160ddd`; `tokenOfOwnerByIndex`
  `0x2f745c59`. Live Base reads via `https://base.gateway.tenderly.co`, head 53,014,594, 2026-10-24 05:08Z.
- Conduit attribution (2,244 `Transfer` logs out of `0x5cbf5dfa`, recipient classification by
  `eth_getCode`, four-conduit `balanceOf` delta): live Base reads via
  `https://base.gateway.tenderly.co`, `eth_getLogs` chunked at 999 blocks over the exact 86400s
  window blk 53,014,374 → 53,057,574, head 53,057,574 (2026-10-25T05:01:35Z).
  Depth calibration `~$1.7k notional per 1%` from three prints: 91.5k (−0.933%), 52.7k (−0.551%),
  319.6k (−1.979%, the $2.9k/1% outlier).

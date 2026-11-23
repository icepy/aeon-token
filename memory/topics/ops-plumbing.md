---
title: Scheduler and notification plumbing state
description: What actually fires this agent's schedules, what "enabled" in aeon.yml does and does not prove, how a gateway 403 differs from a skill regression and from a 402 balance exhaustion, **why a flapping code sequence (`402`→`max_output_tokens`→`403` in one slot) means the gateway state itself is unstable so no diagnosis can rest on the code alone — `duration_api_ms:0` tells you it never left the gateway, real turns tell you it died mid-session**, **and why two enabled skills failing inside the same 23:00–23:31Z half hour with a byte-identical signature makes the shared gateway the object and any per-skill cron/verbosity fix the wrong layer — plus why a growing `total_runs` denominator makes `chronic` self-reinforcing so "recovered once" never clears it**, why the max_output_tokens failure needs its own fix, the daily-log append-only rule, and the notification-format rules that supersede the old hand-formatting notes.
tags:
  - ops
  - runbook
  - scheduler
  - notify
timestamp: 2026-11-23T18:20:00Z
---

# Scheduler and notification plumbing state

## Schedules now fire — the earlier "never ran" finding is closed

An earlier entry recorded `scheduler.yml` as having 0 runs, with every repo run arriving as
`workflow_dispatch`/`push` — the classic fork symptom, where a forked repo's scheduled workflows
are disabled by default. That is **no longer true**: on 2026-10-21T10:09:10Z a `schedule`-event run
named `scheduler: cron` completed successfully. Scheduled dispatch is live.

Keep the distinction that made the original finding easy to misread:

- `enabled: true` in `aeon.yml` only means the skill is *eligible* to be dispatched. It says nothing
  about whether the scheduler has ever fired, and it does **not** create missing state files.
- A skill with `enabled: true` and no state file has simply never completed a run. `price-alert`
  was in exactly that spot until its state was seeded by hand.
- Diagnose with `gh run list --json name,event,conclusion` and filter `event == "schedule"`. A
  non-zero count there is the only proof the cron path works.
- Manual dispatch is always available: `gh workflow run scheduler.yml`.

## Fleet dispatch — the "never ran" finding is closed

`token-movers`, `defi-overview`, `unlock-monitor` were once recorded as never dispatched. That was
wrong: all three were only enabled in `aeon.yml` at 2026-10-23 09:01Z and their first slot had not
yet arrived. **Before judging a skill "never dispatched", check the `aeon.yml` change time for that
skill's line.** `token-movers` first ran 2026-10-23 12:00Z (single-token on NOTE).

## Catch-up bursts collapse the clock — "when did it run" is not "when is its cron"

`scheduler.yml` uses a slot-debt model (`cron-due.sh` + `CATCHUP_HOURS=12`), so a batch missed
overnight is replayed **all at once**. On 2026-10-28 three skills whose crons sit at 22:00 / 22:30 /
23:45 UTC all fired in the same second, `04:15:45Z` — roughly 5.5 h late but back-to-back.

- **Never read "skill X ran at HH:MM" as its cron time**, and never treat a cluster of same-second
  dispatches as an anomaly or a duplicate-spawn bug. Check `last_dispatch` in
  `memory/cron-state.json` and the `CATCHUP_HOURS` window before calling it a finding.
- A dispatch with no state write-back within ~45 min is `⏳ in flight`, not `failed` — the window is
  wide enough to absorb a 130 s scan plus retries.
- **Orphan entries in `cron-state.json` persist forever.** `arxvi-radar` (a one-off successful run on
  10-26, `total_runs: 1`) matches no skill in `aeon.yml` — a typo for `arxiv-radar` from some past
  dispatch. It never affects scheduling, but it keeps showing up as an unexplainable row whenever the
  status page cross-checks cron state against the skill list. Delete it when a write path is handy.

## Gateway 403 is a window, not an outage — and it self-heals

On 2026-11-06 `defi-overview` failed twice back-to-back (23:00:48Z and 23:30:49Z) with
`api_error_status: 403` and the identical signature `hivemindos: Failed to authenticate. API Error:
403 All target providers failed.` Both runs show **`num_turns: 1` + 0 tool calls + `duration_api_ms: 0`**
— that triple means the request never reached the model, so it is a **gateway-side auth rejection, not
a skill regression**. Do not go looking for a bug in the skill's own logic when you see it.

- **Localise it by window, not by scope**: in the same window `arxiv-radar` 22:06Z, `github-radar`
  22:35Z and `defillama-radar` 00:04Z all succeeded, so the gateway was healthy overall and the 403
  only hit the 23:00–23:31 pair. Acknowledge as WATCH (`cf=2`, below the `cf≥3` red line) and let the
  next dispatch decide.
- **It did self-heal**: the 00:15Z re-dispatch succeeded at 00:36Z and `consecutive_failures` went back
  to **0**. The correct action after two failures is to say the *impact* (here: `market-context.md`
  stayed one day stale, `timestamp` pinned at 11-05T23:20Z) and then wait for the next slot rather than
  escalate. [source: logs/2026-11-07#heartbeat]

### The 23:00–23:31Z slot repeats — treat it as a quota window, not random jitter

2026-11-08 failed at **exactly the same two slots** as 11-06 (23:00:47Z and 23:30:48Z) with the
byte-identical `403 All target providers failed.` signature. Two days, same minute positions, same
error → upgrade the hypothesis from "transient blip" to **a periodic auth/quota window at
23:00–23:31Z**. Adjacent skills in the same window all succeeded (`arxiv-radar` 22:06Z,
`github-radar` 22:33Z, `defillama-radar` 00:04Z), so the gateway is healthy overall — still not a
global outage.

- **Discipline:** when the 403 repeats at a known slot, look at the gateway/quota side, **not** the
  skill's own logic. Do not "fix" the skill for it.
- **It self-healed again**: the third re-dispatch (00:15:45Z) landed at 00:46:26Z, `consecutive_failures`
  back to 0, `success_rate` 0.65. Two independent self-heals now confirm the WATCH-not-escalate call.
- **Impact to record while it lasts**: `memory/topics/market-context.md` goes stale by exactly the
  number of missed days — check its `timestamp`, not the skill's `last_status`. [source: logs/2026-11-09#heartbeat]


### Three failures, two distinct signatures — and the self-heal assumption fell

On 2026-11-10 `defi-overview` reached `consecutive_failures: 3` (first time across the 🔴 line).
Reading each run log separately showed the three failures are **not one bug**:

| Slot | Run | Signature | Tell |
|---|---|---|---|
| 11-09T23:00Z | 42716872115 | `403 All target providers failed` | `num_turns:1`, but `duration_api_ms:824635` (13.7 min before the 403) |
| 11-09T23:30Z | 42721050413 | same 403 | `duration_api_ms:0` (instant reject) |
| 11-10T00:15Z | 42726955929 | **`api_error: max_output_tokens`** | `output_tokens:76298` / limit 128000, `num_turns:95`, `stop_reason:stop_sequence` |

So the 11-09 hypothesis ("the 00:15Z re-dispatch will self-heal") **failed** — the retry died a
different death. The 403 quota window (11-06 / 11-08 / 11-09, same 23:00–23:31Z slots) still holds,
but it is **not the only cause**; the two need separate fixes.

- **Cost is the real damage (first quantification):** the three failures burned ≈ **$10 for zero
  output** — $2.83 (`00:15` run `total_cost_usd`) + $3.79 (`23:00` run) + ~$3 (23:30 run, no exact
  figure). Output-limit failures are the expensive kind: 95 turns before hitting the cap.
- **Not every 23:00 fails** — 11-07's 23:00Z run succeeded. It is intermittent, not a hard block.
- **Fixes proposed, neither applied:** move `defi-overview`'s cron off `0 23`, or add a second
  gateway cascade; fix the output limit by *cutting per-round read/output volume*, not by raising
  `CLAUDE_CODE_MAX_OUTPUT_TOKENS` (that treats the symptom).
- **`duration_api_ms` is a discriminator worth keeping:** `0` = never left the gateway (auth
  rejection); thousands of ms + `num_turns:1` = the request ran and *then* failed. Same status code,
  different layer. [source: logs/2026-11-10#heartbeat]

### The circuit breaker closes the retry path — "wait for the retry to self-heal" stops working

On 2026-11-11 `defi-overview` reached `consecutive_failures: 4` and the self-heal assumption was
falsified **in a new way**: the retry channel itself was shut off.

- **2026-11-10T23:00Z** still `403 All target providers failed`, but now `duration_api_ms: 0` +
  `num_turns: 1` + `total_cost_usd: 0` + `output_tokens: 0` → the request never left the gateway.
- **The 30-minute retry never ran.** Scheduler log, verbatim: *"Circuit breaker OPEN: defi-overview
  (4 consecutive failures) - skip, next probe in 330m"* (11-10T23:30Z), then `next probe in 270m`
  (11-11T00:30Z). Reading `scripts/breaker.sh` + `.github/workflows/scheduler.yml:250-275`: once
  `consecutive_failures >= BREAKER_THRESHOLD` (default 3), **both** the retry and the cron match sit
  behind the gate; a run is released only when `MINUTES_SINCE >= COOLDOWN_MIN` (default 360m) **and**
  `slot_owed=1`. `RETRY_LIMIT = BREAKER_THRESHOLD`, so past the line even the 30-min retry is refused.
- **This retroactively explains every earlier self-heal.** Slot-by-slot history: 11-02 fail → 23:30
  success; 11-06 fail → next-day 00:15 success; 11-08 fail → next-day 00:15 success; **11-09 fail →
  23:30 fail → 00:15 fail (`max_output_tokens`)**; 11-10 fail → breaker skip, no retry at all.
  **The retry was the self-heal mechanism.** When 11-09's retry died on the output cap, `cf` climbed
  to 4, tripped the breaker, and closed the only path that had ever worked.
- **Shape upgrade:** the 23:00Z slot has failed 5 of 6 times since 11-06 (only 11-07 succeeded),
  down from a 100% success rate across 10-29–11-01. The current combination — tripped breaker
  allowing one probe a day, at the very slot that 403s most — is no longer intermittent jitter;
  **it is structurally stuck.**
- **Two separate fixes, neither applied:** ① move the cron off `0 23` (the only action that dodges
  the 403 window without depending on a retry); ② cut per-round read/output volume for the
  `max_output_tokens` failure (raising `CLAUDE_CODE_MAX_OUTPUT_TOKENS` treats the symptom).
- **The real cost is the stale artifact, not the wasted spend:** `memory/topics/market-context.md`
  `timestamp` is pinned at `2026-11-09T00:30:00Z` → the macro snapshot is 2 days old. Check the
  topic's own `timestamp`, never the skill's `last_status`.
- **Operational lesson (generalises past this skill):** a `cf`-based breaker that shares its
  threshold with the retry limit **converts a recoverable intermittent failure into a permanent one**.
  When you see "it used to self-heal, now it doesn't", check whether the breaker tripped before
  assuming the failure got worse. [source: logs/2026-11-11#heartbeat]

### Recovery ≠ fixed: `defi-overview` keeps coming back, and the mechanism is the ordinary retry

2026-11-12 heartbeat: `last_success` = 11-11T23:22:51Z, `consecutive_failures` 4 → 0. The skills
status page moved 🔴 DEGRADED → 🟡 WATCH, **not** 🟢 OK.

- **Correction (2026-11-13): the 11-11 recovery was NOT a 360m breaker probe.** The 11-12 night
  repeated the same 23:00 + 23:30 double failure, and the scheduler log at 00:00:58Z reads
  `Retrying failed skill: defi-overview (failed 30m ago)` → success at 00:11:57Z. That is the
  plain 30-minute retry, gated only by `CONSEC < RETRY_LIMIT`. **Always read the retirement
  decision out of that run's own scheduler log — do not inherit last round's explanation.** The
  two mechanisms mean opposite things: a probe implies the breaker already tripped; a retry
  implies it has not.
- The distinction is load-bearing because `RETRY_LIMIT = BREAKER_THRESHOLD = 3`. Any two
  consecutive nights of the 23:00+23:30 double failure push `cf` to 3, the retry path closes,
  and the skill is back to one probe a day inside the worst 403 band — the 11-08→11-10 trap.
- Both root causes are still in place after four nights of this: cron fixed at `0 23` (inside the
  403-heavy 23:00–23:31Z band) and per-round output volume still over the 128k cap. The only
  actionable item is the cron move, and it is an operator config decision.
- **Margin, as of 2026-11-13:** `defi-overview` success rate is **0.56 (19/34)** — one more long
  bad stretch crosses the `<0.5` chronic line (`total_runs >= 5` already satisfied). That is the
  score-level argument for moving the cron, not a new mechanism.
- **Generalise the status rule:** a skill recovering on its own does not clear the finding while
  the cause stands. Keep the artifact-staleness check (`market-context.md`'s own `timestamp`)
  until a fix lands.
- A health-scorer issue thread (`#13 health: defi-overview`) did **not** auto-close on recovery —
  its `updatedAt` tracks the latest failure, not the recovery. Thread state and `cron-state.json`
  are decoupled; closing belongs to `skill-health`, not to whatever skill notices the mismatch.
  [source: logs/2026-11-12#heartbeat, logs/2026-11-13#heartbeat]

### `403` → `402`: the error code changed family, and the self-heal no longer applies

2026-11-14 heartbeat: **both** `defi-overview` (cf=3) and `github-radar` (cf=3) are in breaker trip.
Scheduler run `43534664526`, verbatim: `Circuit breaker OPEN: defi-overview (3 consecutive failures)
- skip, next probe in 331m` / `Circuit breaker OPEN: github-radar (3 consecutive failures) - skip,
next probe in 301m`. Every prior round in this file was about `403`; this one is `402`.

| Run | Skill | Slot | Turns | Cost | Signature |
|---|---|---|---|---|---|
| `43519867759` | github-radar | 11-13T22:30Z | **6** | **$0.176** | `402 All target providers failed` |
| `43523845097` | github-radar | 11-13T23:00Z | 1 | $0 | same 402, `duration_api_ms:0` |
| `43527668402` | github-radar | 11-13T23:30Z | 1 | $0 | same 402, `duration_api_ms:0` |
| `43523835067` | defi-overview | 11-13T23:00Z | 1 | $0 | same 402 |
| `43527662024` | defi-overview | 11-13T23:30Z | 1 | $0 | same 402 |
| `43531239772` | defi-overview | 11-14T00:11Z | **119** | — | **`max_output_tokens`** (128k), 580s |

- **`403` is a window that self-heals; `402` is a balance that does not.** The 22:30 github-radar run
  burned 6 turns and $0.176 *before* returning 402 — credit ran out mid-session, not a door
  rejection. That is the discriminator: a 402 arriving **after** real turns = balance exhaustion;
  a 402 at `num_turns:1` / `duration_api_ms:0` = already empty when the request was composed.
- **Consequence for the breaker:** its ~5h auto-probe exists to catch windows that reopen. It cannot
  reopen a balance. Both skills will keep failing every probe until the gateway credit is topped up
  or `gateway.provider` is re-pinned. **"Wait for the probe" is the wrong reflex for a 402.**
- **`duration_api_ms: 0` still discriminates, and now across three codes** (403 auth reject, 402
  empty balance, and the non-gateway `max_output_tokens` which shows thousands of ms). Same read as
  the 11-10 note above; only the code label moved.
- **`defi-overview` failed for two independent reasons within 3h** — 402 at 23:00/23:30, then
  119 turns before hitting the 128k cap at 00:11. The 00:11 attempt proves the output-volume bug is
  real independently of the gateway: **even with credit, this skill's single-round output is over
  the cap.** Two fixes, neither applied: move cron off `0 23`, and cut per-round volume.
- **Margin:** `defi-overview` is **0.51 (19/37)**. Two more consecutive failures → 19/39 = 48.7%
  crosses `<0.5` (19/38 = 50.0% does not satisfy `<`).
- **Scorer threads stay open and pile up:** `#9` got three regression comments (22:33/23:01/23:31Z),
  `#13` three (23:01/23:31Z + 11-14T00:11Z), one per failed run — same decoupling noted above.
  [source: logs/2026-11-14#heartbeat]

#### Correction (11-15): the code itself flaps — do not diagnose from one code

The 11-14 conclusion ("`402` = balance, it will not self-heal") was too strong. Three-day sequence
for the **same** skill: `402` (11-13T23:00) → `402` (11-13T23:30) → `max_output_tokens` (11-14T00:11,
119 turns) → back to **`403`** (11-14T23:00, run `43651034939`: `api_error_status: 403`,
`duration_api_ms: 0`, `num_turns: 1`, 0 tool calls, `$0`).

- **Two different codes for one skill inside one 23:00Z slot, three nights running = the gateway's
  own routing/credit state is flapping.** The signature still discriminates *where* it failed
  (0 ms = request never left the gateway; real turns = died mid-session), but **the code does not
  identify a cause.** Stop inferring "top up the balance" from `402` alone.
- **The operator decision does not change** (top up credit, or re-pin `gateway.provider`) — only the
  confidence in "waiting is useless" does. Report the sequence, not the single code.
- **`github-radar` self-healed on its own** (11-14T22:30 run `43648482742` `success`, cf back to 0,
  81% = 39/48) — so the two-skill trip was not one shared outage.
- **`defi-overview` now sits at exactly 0.50 (19/38).** The chronic rule is `success_rate < 0.5`
  (strict) and `total_runs >= 5`, so 19/38 does not qualify; **one more failure → 19/39 = 48.7%
  crosses it.** One loss away, not two.
- **Staleness has a downstream cost:** `market/topics/market-context.md` is pinned at
  `2026-11-13T00:15:00Z` (48.3h), because every `defi-overview` round since has failed before the
  write. Any judgement citing it is quoting two-day-old macro readings. `github-radar` recovery did
  not touch it — only `defi-overview` refreshes it.
  [source: logs/2026-11-15#heartbeat]

#### Update (11-16): the flap converged, the chronic line was crossed

- **The code sequence stopped flapping and settled on `403`:** `402`→`402`→`max_output_tokens`→
  `403`→`403`. The 11-15 reading ("do not diagnose from a single code") still stands — convergence on
  one code is *not* a diagnosis. The last failure (`run 43772461867`, 11-15T23:01Z, job 26 s:
  `23:01:06→23:01:32`) carries `Gateway cascade failed (hivemindos): Failed to authenticate. API Error:
  403 All target providers failed` — authentication is named, but a cascade across all providers can
  still be quota, routing or key state. **Cause remains undetermined.**
- **`defi-overview` crossed the chronic line: 49% (19/39), `consecutive_failures=5`,** so
  `success_rate<0.5` ∧ `total_runs>=5` now holds. The 11-15 note said "one more failure crosses it";
  that failure happened.
- **Staleness compounds:** `market-context.md` is now 72h stale (`2026-11-13T00:15:00Z`). Because
  `defi-overview` is its only writer, the freeze grows by a day per failure — treat any citation of it
  as a three-day-old reading.
- **A queued PR can invalidate a skill's own numbers.** PR #25 (word-list downgrade) crossed the 24 h
  stalled line; while it is open, `arxiv-radar`'s 「低频探针 N=0」 is the status light for *an
  unmerged change*, not a reading about the corpus. See [lessons](/topics/lessons.md#arXiv-检索arxiv-radar).
  Do not self-merge a config decision; log it as WATCH.
  [source: logs/2026-11-16#heartbeat]

#### Update (11-17): it is one shared gateway, not two skill regressions

On the night of 2026-11-16 two *enabled* skills failed inside the same half hour with a byte-identical
signature (`hivemindos: Failed to authenticate. API Error: 403 All target providers failed`):
`defi-overview` at 23:01:11Z (cf 5→6, 19/40 = 48%) and `github-radar` at 23:31:22Z (cf→3, 40/52 = 77%,
last success 11-15T22:33:23Z — so its 第 28 轮 produced nothing at all, which is *not* a zero-hit round).

- **The discriminator is the same window, not the same skill.** In that window `arxiv-radar` (22:06Z),
  `memory-flush` (18:05Z) and `defillama-radar` (11-17T00:09Z) all succeeded → the gateway is
  **intermittently rejecting**, not down, and this is **not** a single-skill regression. Earlier rounds
  framed `defi-overview` as an individual case and proposed moving its cron or trimming its per-round
  output; with two skills hit at once, those are **low-level fixes on the wrong object**. The object is
  the shared HivemindOS gateway (quota / auth / routing — still undetermined which).
- **The design intent puts the fleet inside the failure band.** The 23:00–23:31Z slot is exactly where
  `defi-overview` (23:00) and `github-radar` (22:30 dispatch, 23:31 fail) run. Any future "batch the
  nightly skills after 23:00" plan re-creates the same collision.
- **A growing denominator makes `chronic` self-reinforcing.** `defi-overview` went 19/39 → 19/40
  because a failure increments `total_runs` while the numerator stays put — every further failure
  pushes `success_rate` further below 0.5. So "recovered once" does **not** clear it; only a run of
  successes lifts the rate back over the line. Read the pair `(num/den)` before calling a skill fixed.
- **Downstream state keeps aging:** `market-context.md` pinned at `2026-11-13T00:15:00Z` → ~96 h. Only
  `defi-overview` writes it, so the freeze grows a day per failure. Do not cite it as current.
- **PR queue is empty and the earlier WATCH items are closed:** PR #25 merged 2026-11-16T01:10:30Z
  (word-list downgrade — the 「低频探针 N=0」 status light went green, judgement closed) and PR #27
  (the 50-commit upstream sync, a watermark-only change) merged 2026-11-16T11:42:57Z.
  [source: logs/2026-11-17#heartbeat]

#### Update (11-18): the shared-gateway reading was half wrong — the other half is max_output_tokens

One full run log (`44195522715`, 2026-11-17) settles it for `defi-overview`: `num_turns: 138`,
`output_tokens: 147604` against `maxOutputTokens: 128000`, 1026 s, $4.88, cache_read 7.1 M,
`permission_denials: []`, `terminal_reason: api_error`, `api_error: max_output_tokens`.

- **The two diseases are distinguishable in one line each — do not merge them.** A gateway refusal is
  `num_turns: 1` with 0 tool calls and `duration_api_ms: 0` (request never left). A token-ceiling death
  is a *large* `num_turns` plus `output_tokens` at/over the limit — the session ran fine for 138 turns
  and died while writing. The 11-17 note framed the two skills as one shared-gateway object; that was
  **true for the 403 signature and false for this failure**, which is not a gateway refusal at all.
- **The "move the cron off 23:00–23:31Z" fix lost its object.** Last night's run started 23:01:01Z and
  ended 23:18:45Z — the whole session inside the allegedly bad band, gateway reachable throughout. The
  403 band did not reproduce. Any later "batch the nightly fleet after 23:00" concern is unfounded
  *for 11-17*; keep it as a hypothesis, not a standing rule.
- **`github-radar` self-healed:** success 11-17T22:36:40Z, cf 3→0, 41/53 = 77%, and its 第 28 轮 was
  actually produced on 11-17 (see [github-radar](/topics/github-radar.md)). So "two skills hit the same
  wall" no longer holds as a diagnosis. Health issue `#9` was never revisited after the recovery —
  **issue thread state and dispatch state are decoupled** (same lesson as 11-12, now with a second case).
- **The chronic counter is still sliding:** `defi-overview` cf 6→7, `total_runs` 41, 19/41 = **46%**
  (48% → 46%). Third consecutive round where only the denominator moved. `market-context.md` frozen at
  `2026-11-13T00:15:00Z` = ~120 h, single writer still `defi-overview`.
  [source: logs/2026-11-18#heartbeat]

#### Update (11-19): the output-budget fix worked on its first try — but the chronic counter is still red

- **`defi-overview` self-healed: `last_success=2026-11-18T23:14:04Z`, `last_dispatch=23:00:44Z`,
  `consecutive_failures` 7 → 0, `total_runs` 41 → 42.** The previous round died at `num_turns:138` /
  `output_tokens:147604` vs 128000; this round logged **48 tool calls**, all data pulling aggregated in
  python with only summary lines printed. Same-day diagnosis → same-day fix → success. **This is the
  positive control for the 11-18 entry: the "large `num_turns` + tokens at ceiling" disease is fixable
  by squeezing per-turn I/O; it does not require a provider change.**
- **`market-context.md` unfroze:** `2026-11-13T00:15:00Z` → `2026-11-18T23:10:00Z`, ending a ~120 h
  freeze. Third full lifecycle sample of "single writer dies ⇒ derived file freezes." **Recovery of
  writes ≠ recovery of success rate — record them separately.**
- **The success rate is still 20/42 = 48%, below the 50% chronic line, so it stays in the chronic
  bucket this round.** A 42-run mean cannot be moved by one green night. `STATUS_PAGE` moved
  🔴 DEGRADED → 🟡 WATCH, not 🟢. Rule unchanged from 11-14: several consecutive green runs before
  calling it a durable fix.
- **Remaining orphan: `arxvi-radar`'s cron-state row (22nd consecutive round).** `aeon.yml` has zero
  mentions of that skill, but `state` still holds a `total_runs:1` record from 10-26.
  [source: logs/2026-11-19#heartbeat]

#### Update (11-20): second consecutive green — the arithmetic now says one more success clears the line

- **`defi-overview` green again: `last_success=2026-11-19T23:10:25Z`, `last_dispatch=23:00:51Z`,
  `consecutive_failures` stays 0, `total_runs` 42 → 43.** Two consecutive green rounds since the 11-18
  fix — the 11-19 "several consecutive greens before calling it durable" bar is now two-thirds walked.
  `market-context.md` written again, so the ~120 h freeze has not recurred.
- **Success rate 20/42 = 48% → 21/43 = 49%.** The denominator gains +1 every round and the numerator only
  on success, so **one more green run takes it to 22/44 = 50.0% and out of the chronic bucket.** Until
  then it stays red; a green run that does not happen also keeps it under. **This is the only quantified
  forward movement this round.**
- **`consecutive_failures` does not decay when a skill is disabled.** Three rows sit at cf≥3 —
  `price-alert` cf=5, `onchain-monitor` cf=4, `token-movers` cf=3 — but all three are `enabled: false` in
  `aeon.yml` with last dispatch stuck at 10-25, and one shared error signature (`hivemindos 403 All
  target providers failed`, a gateway-layer refusal). **Read: the cf counter is a ledger, not a status
  light — it says the 10-25 gateway outage was never reconciled, not that anything is failing now.**
  [source: logs/2026-11-20#heartbeat]

#### Update (11-21): third consecutive green — the line is crossed, but only as a hairline

- **`defi-overview` 22/44 = 50.0%, out of the chronic bucket.** `last_success=2026-11-20T23:09:22Z`,
  `last_dispatch=23:00:52Z`, cf **0**, `total_runs` 43 → 44. The 11-18 "cut the single-round output"
  fix has now paid off three rounds running (11-18 / 11-19 / 11-20), and the arithmetic both earlier
  heartbeats predicted ("one more green ⇒ 22/44") landed.
- **50.0% is standing on the line, not clear of it.** The ladder tests `success_rate < 0.5`, so 50.0%
  passes by exactly zero. **The next failure is 22/45 = 48.9% (straight back to 🔴), the next success
  23/45 = 51.1%.** 22 of the 44 failures are almost all one 7-round losing streak (11-14 → 11-17), so
  the mean needs *weeks* to move away from the threshold. **Read `defi-overview` by cf and the last three
  rounds only — never by the 44-round mean.**
  [source: logs/2026-11-21#heartbeat]

#### Update (11-22): clear of the line at 51.1%, and the MEMORY-lag watch-item is retired

- **`defi-overview` is now genuinely off the chronic line: 23/45 = 51.1%**, cf **0**, four consecutive
  greens (11-18 → 11-21). The 11-21 rule applies as written — **cf 0 + last three rounds green = no
  fault; the 45-round mean is no longer a criterion.**
- **The "MEMORY 待盯 line is stale" watch-item is structural timing, not a bookkeeping miss.** The
  line is written only by the 18:00 `memory-flush`, while `defi-overview` runs at 23:00 — so the
  line is *necessarily* one day behind any new round. 11-21 flagged it 🟡 only because the recorded
  number (49%) had been contradicted; from 11-22 on, a number that was accurate at consolidation time
  and merely superseded later is normal. **It no longer counts as a P2 watch-item and no longer tints
  the status page.** Any future staleness of that line is expected and should not be re-reported.
- **`STATUS_PAGE` 🟡 WATCH → 🟢 OK** on this basis; the only P1 residue is nine scorer-generated
  `health: <skill>` issue threads with no labels and no urgent/critical/high severity (three point at
  disabled skills = dead threads, six at self-healed skills = unclosed threads). PR queue empty,
  twentieth consecutive day.
  [source: logs/2026-11-22#heartbeat]

## Reading `gh run view --log`: colour-escaped lines are the script body, not output

2026-11-14 heartbeat burned two attempts grepping `gh run view --log | grep -i error` and got
nothing but the workflow YAML echoing itself back (`^[[36;1m…` lines).

- **The discriminator:** any log line still carrying ANSI escapes (`^[[36;1m`, `^[[0;1;31m`) is the
  *script source* echoed for the run header — it is never program output. Filter it out first:
  `grep -v "36;1m"`, then look for `claude exited` / `api_error_status` / `Circuit breaker OPEN`.
  [source: logs/2026-11-14#heartbeat]

## WebSearch is unavailable in this fleet — do not treat "no headlines" as a null result

Confirmed 2026-11-13 (fifth consecutive round): in-run `WebSearch` calls return a
no-tool/no-browsing notice rather than results. `defi-overview` has logged `websearch=fail` every
round since 2026-11-09 and deletes its macro-catalysts section as a result.

- **Consequence:** any check that depends on independently verifying a third-party headline cannot
  be satisfied in-run. The `narrative-brief` scorer flag `unverifiable_claim` (score 2 on
  2026-11-09 and again on 2026-11-12, filed to `#18`) is not fixable inside this repo — that skill
  only sha256-dedups and forwards Grok-written text, and the verifying tool is absent.
- **Working substitute for causes, not for headlines:** RSS + `WebFetch` (CoinDesk
  `arc/outboundfeeds/rss/`) and DefiLlama `hallmarks` both worked where WebSearch did not.
  [source: logs/2026-11-13#heartbeat, logs/2026-11-05#defi-overview]

## A skill's frontmatter `var:` default is NOT injected into the run

Every skill declares a `var:` default in its frontmatter (e.g. `skills/github-radar/SKILL.md:7` →
`var: "days:7"`), and the body reads "default 7". **That value never reaches `$var` at runtime.**
An unset `var` arrives empty, so the skill falls through to *whatever the script hardcodes* —
`skills/github-radar/scan.py:184` sets `DAYS = 30`. `scan.py:193` only overrides it when `days:N` is
explicitly passed.

Consequence: the belief "github-radar runs daily on a 7-day window" was never true on the dispatch
path. The 7-day runs that got recorded were manual `days:7` invocations from inside a run. Round 9
(7d) and round 10 (30d) are therefore **not comparable** — the 2106 → 35 → 16 funnel in round 10 was
produced by a different window, not by a change in the topic.

- **Check the script's default, not the frontmatter's, when reasoning about what a scheduled run
  actually measured.** Frontmatter `var:` is documentation and a default for the *manual* path.
- Any cross-round comparison that changes window must state the window in the same breath as the
  numbers. A funnel delta across two windows is a window effect until proven otherwise.

## Nothing merges PRs — `auto-merge` is off, so a write-mode skill's output can stall indefinitely

`aeon.yml` has `auto-merge: { enabled: false }`. That skill is the only thing in the fleet that would
merge; with it disabled, **every PR a write-mode skill opens sits until a human merges it.** This is a
structural stall, not "wait a while".

Observed cost (2026-11-02): `defi-overview` opened #21 (10-31) and #22 (11-01); both went
`CONFLICTING`/`DIRTY` and neither merged, so `memory/topics/market-context.md` on `main` stayed at
`timestamp: 2026-10-30T23:05:00Z` — **~73 h stale** while two newer snapshots existed on branches.
Both were merged by hand on 11-02; the staleness was invisible from the skill itself, which reported
success each run.

- **Diagnose by reading the target file's `timestamp:` on `main`, not by reading run status.** A
  write-mode skill can be green every run and still have nothing reach `main`.
- **Before blaming a script bug for a conflicting PR, reproduce the merge locally** with full history
  (`git merge-tree --write-tree`) — GitHub's `CONFLICTING` flag and a local merge of `prNN` disagree
  in practice (#22 showed `CONFLICTING` on GitHub but merged clean locally).
- **A conflict on a `memory/` file is usually two writers, not two features.** #21's `lessons.md`
  hunk was superseded by the version `memory-flush` had already merged; the right call was to close
  it, not to resolve the hunk.

## `eyebrowlock.json` drifts from local `__pycache__` — clean it before `eyebrow scan`

`ci-skill-integrity` runs `eyebrow verify --ci`, which compares each skill's `files` list and
`contentHash` against the committed `eyebrowlock.json`. If the lockfile was regenerated on a machine
where the skills had been executed, `skills/*/__pycache__/*.pyc` exists on disk and `eyebrow scan`
writes those `.pyc` entries into the lockfile. A CI runner never has them, so **every later run
drifts** — the failure looks like skill content changed, but nothing in the skill did.

Observed 2026-11-03: `eyebrow scan` picked up 4 `.pyc` files into `files`; deleting the local
`__pycache__` directories and re-scanning produced a lockfile without them and `verify --ci` went OK.

- **Regenerate the lockfile only from a tree with no `__pycache__`** — `find skills -name __pycache__ -prune -exec rm -rf {} +` first, then `eyebrow scan`.
- **Do not "fix" this by making the manifest generator skip `.pyc`.** `bin/generate-skills-json` and the eyebrow tooling are upstream system files; patching them to compensate for a dirty working tree reverts on the next sync and hides the real cause. Same class of mistake as the `count_files` patch that was reverted the same day (`523bfe02`).
- A real `eyebrow verify` failure can also be legitimate content drift / capability expansion (new `api.` hosts in a skill). Read the reported entries before assuming the `.pyc` cause.

## Daily logs are append-only — `Write` on an existing `memory/logs/*.md` is destructive

`memory-flush` wiped a whole day of logs on 2026-11-03: it called `Write` on `memory/logs/2026-11-03.md`
to add its own entry, and the six sections already in that file (defillama-radar / heartbeat /
merge-conflict-cleanup / narrative-brief, plus their under-the-hood rows) were replaced by the single
new section. `git status` showed the file as `M` and `git show HEAD:` still had the original, so
`git checkout HEAD -- memory/logs/2026-11-03.md` restored all 63 lines; the flush entry was then
re-added with `Edit`.

- **Never call `Write` on a daily log that already exists.** Check with `Glob` first, then `Read` +
  `Edit` to append. `Write` is only safe for the *first* write of a given UTC day.
- **Recovery is `git checkout HEAD -- <path>`, then append again** — do not try to reconstruct the
  lost sections from the other skills' outputs.
- The log is the audit trail the health loop and every `[source: logs/…]` tag point at, so a silent
  overwrite breaks citations for runs you did not touch.

## Unstaging is `git restore --staged` — `git reset --hard` wipes work you already wrote

2026-11-11 `defi-overview`: after writing three memory files, the run wanted to undo a `git add`.
It ran `git reset --hard HEAD`, which discarded the working-tree contents of `market-context.md`,
`lessons.md` and that day's log. Recovery only worked because `.tmp/` still held 37 raw JSON payloads
and every calculation script, so all three files were rebuilt from cached data.

- **To unstage, use `git restore --staged <file>`.** `git reset --hard` is for discarding *content*,
  not staging — it rewrites the working tree and takes unrecoverable edits with it.
- `git reset` (mixed, no `--hard`) also unstages and leaves the tree alone; `--hard` is the only
  variant that destroys content.
- The blast radius is worst exactly where this fleet writes: memory files are the state store, and
  there are no PRs or branches protecting an uncommitted write. [source: logs/2026-11-11#defi-overview]

## Restarting a parked watch — seed the cursor first

Base reads go through `base.gateway.tenderly.co` (`eth_getLogs` capped at 1,000 blocks); the RH 4663
chain needs no key. Data-shape caveats live in [lessons](/topics/lessons.md#行情取数形状defillama--coingecko).

**A watch that is switched back on must first get a `memory/on-chain-state.json` entry with
`last_block` set to the current block** — otherwise the first run replays the entire historical log
range and every old event arrives as if it were new. The 10-25 parked DEUS/NOTE watches still have
the stale `memory/on-chain-state.json.new` leftover; deal with it before re-enabling anything, not
before.

## Watchlist rationale

Base watches sit at $200/$250. NOTE watches sit at $500 — deliberately low because NOTE events are
sparse and sensitivity matters more than noise control there. The NOTE timelock watch carries no
`event_topics` filter because all three event kinds (scheduled / executed / cancelled) are wanted.
Retired watches are left as commented blocks in `memory/on-chain-watches.yml`: the `NOTE` token
itself (too noisy) and `NOTE staging 0x69bb` (repeatedly zero-activity).

## Notifications: write plain Markdown, do not hand-format

`./notify` renders each channel itself (`scripts/notify_format.py` normalizes Markdown into
Telegram's safe HTML subset and auto-chunks at ~3900 chars with `[i/N]`). So the correct habit is
ordinary Markdown — `##` headings, `**bold**`, `-` bullets, `| tables |`, fenced code, `[label](url)`.

This supersedes any older hand-formatting rules for Telegram (the "no `#`, no tables, wrap nothing
in `>`" list). Those rules describe a legacy parse_mode problem that the formatter now solves; hand
formatting for the transport is wasted effort and loses structure.

Editorial choices still matter: keep it terse because the operator wants signal, not because of a
transport limit. Use `x.com/handle` instead of `@handle` so nobody gets pinged.

## Multi-line notifications

Use `./notify -f path.md`. Do **not** use `./notify "$(cat file.md)"` — long multi-line argv trips
the sandbox. Short bodies containing `test`/`ping`/`debug`/`trace` are suppressed as diagnostic
probes, so a "test" message is not a delivery check.

## Permission layer: state writes and file copies

Writing skill state from Bash is unreliable in this harness, and the failure looks like a skill bug
rather than a permission rule:

- **`jq -f` is refused** as a "dangerous flag". Use `jq empty` / `jq -e` for *validation* only; do
  the actual rewrite through `Write` or a `node` one-liner.
- **`cp` into the repo requires interactive approval**, so a `.bak` roll silently does not happen.
  `price-alert` went eight consecutive runs on 2026-10-22 with a stale backup (21:01–23:01Z all say
  "`.bak` still not refreshed"), and the 12:01Z run's denial left the backup a full run behind.
- Preferred pattern that does work: build the new JSON in `node`, write a tmpfile, re-parse it to
  validate, then `os.replace` / atomic rename. Confirm with `jq empty` afterwards and log
  `STATE_VALID`.
- Write the state file directly with `Write` rather than trying to shell-copy the old one first. A
  missing backup is survivable; a half-written state file is not.

## `aeon-update` can report `CLEAN-MERGE 4` and have changed nothing

2026-11-16: the plan counted 4 `CLEAN-MERGE` files (`.github/workflows/aeon.yml`,
`.github/workflows/messages.yml`, `AGENTS.md`, `apps/dashboard/lib/skill-icons.data.ts`), the 3-way
merge exited 0 for all four, and `apply` returned `AEON_UPDATE_APPLIED` — but `git diff --stat HEAD`
was **empty**. The whole 50-commit sync was the `baseline_sha` bump alone.

Why: PR #24 (the prior sync) was closed unmerged while its *content* reached `main` in a catalog
commit. So the local tree already carried upstream's HEAD content; a 3-way merge of identical
`local`/`head` produces no hunks, which the plan still records as `CLEAN-MERGE`.

**Reading rule:** a non-zero `CLEAN-MERGE`/`CLEAN-UPDATE` count is *not* evidence of synced content.
After `apply`, check `git diff --stat HEAD`; if it lists only `memory/topics/aeon-update-state.json`,
the run was a watermark advance — say so in the PR body instead of implying 4 fixes landed.

Two related traps found the same run:

- **A staged `D` on a generated file reads as `deleted-locally`.** The session opened with
  `AGENTS.md` deleted-and-staged, so the first `plan` classified it `CONFLICT deleted-locally`. After
  `git checkout -- AGENTS.md` the same plan returned `CLEAN-MERGE` and conflicts dropped 7→6. Run
  `git status` before trusting a `deleted-locally` verdict on a file upstream generates.
- **Perpetual doc conflicts are a `keep_local` miss, not drift to reconcile.** All 6 conflicts were
  the same upstream 87→92 skill-count edit against a fork that legitimately ships 96. Adding
  `"keep_local": ["docs/**", ".github/README.md"]` to the state file stops the list regrowing every
  run (`.gitignore` is worth keeping visible until upstream stops editing it).

## Update (11-23): the same zero-delta sync, and the skill-count conflicts are now counted

2026-11-23 sync `7b20c95..f94f39e` (13 upstream commits): plan `CLEAN-MERGE 3 / CONFLICT 5 / OPERATOR 6`,
and again `git diff HEAD --stat` was empty outside the state file — the three CLEAN-MERGE targets
(`.github/workflows/aeon.yml`, `.github/workflows/messages.yml`, `apps/dashboard/lib/skill-icons.data.ts`)
were already byte-identical locally, verified by sha256 against upstream's contents API. Same mechanism
as 11-16: local hand-syncing had run ahead of the baseline, so 3-way merge saw identical sides.

Two things this round clarifies:

- **The doc conflicts now track the catalogue count, not a fixed number.** All 5 conflicts are the
  92→93 skill count in `.github/README.md`, `docs/aeon-setup.md`, `docs/assets/hero-animated.svg`,
  `docs/examples/README.md`, `docs/skill-packs.md` — the delta is the newly added `icp-mcp` skill
  (Crypto & Markets 22→23). **The count moves every time upstream adds a skill, so the `keep_local`
  glob (`docs/**`, `.github/README.md`) is the only fix that stops it recurring**, not a one-off number edit.
- **`OPERATOR` entries are not conflicts and never land.** `aeon.yml`, `catalog/*.json`, `eyebrowlock.json`
  are held for the operator by design; their presence in the plan should not be read as pending work.

PR #28 opened at `f94f39e`, `pending_conflicts` 6 (the 5 doc files plus the long-carried `.gitignore`).
`AGENTS.md` was deleted-in-worktree before the run — pre-existing drift, not this skill's output.
The clone is `--depth=1` (`.git/shallow`), so all history judgements route through `gh api compare`.
[source: logs/2026-11-23#aeon-update]

# Citations

- `gh run list` showing `scheduler: cron` with `event: schedule`, `success`, 2026-10-21T10:09:10Z.
- `scripts/notify_format.py` module docstring (channel limits + Markdown→HTML normalization).
- `CLAUDE.md` § Tools / § Network & Secrets.
- `aeon.yml:18` (`auto-merge: enabled: false`) · `git merge-tree --write-tree` exit=1 on PR #21 (`CONFLICT (content): memory/topics/lessons.md`), exit=0 on PR #22 · `memory/topics/market-context.md` `timestamp: 2026-10-30T23:05:00Z` on main, 2026-11-02.
- `logs/2026-11-02#heartbeat` (both PRs merged by the operator 2026-11-02T09:26Z / 09:29Z).
- `logs/2026-11-03#merge-conflict-cleanup（手工会话）` — `eyebrow scan` wrote 4 `.pyc` into `eyebrowlock.json`; `eyebrow verify --ci` OK after removing local `__pycache__` · `bin/generate-skills-json` `count_files` patch reverted in `523bfe02`.

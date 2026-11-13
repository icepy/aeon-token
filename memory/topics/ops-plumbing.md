---
title: Scheduler and notification plumbing state
description: What actually fires this agent's schedules, what "enabled" in aeon.yml does and does not prove, how a gateway 403 differs from a skill regression (and why a 403 and a max_output_tokens failure need separate fixes), the daily-log append-only rule, and the notification-format rules that supersede the old hand-formatting notes.
tags:
  - ops
  - runbook
  - scheduler
  - notify
timestamp: 2026-11-13T00:45:00Z
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

# Citations

- `gh run list` showing `scheduler: cron` with `event: schedule`, `success`, 2026-10-21T10:09:10Z.
- `scripts/notify_format.py` module docstring (channel limits + Markdown→HTML normalization).
- `CLAUDE.md` § Tools / § Network & Secrets.
- `aeon.yml:18` (`auto-merge: enabled: false`) · `git merge-tree --write-tree` exit=1 on PR #21 (`CONFLICT (content): memory/topics/lessons.md`), exit=0 on PR #22 · `memory/topics/market-context.md` `timestamp: 2026-10-30T23:05:00Z` on main, 2026-11-02.
- `logs/2026-11-02#heartbeat` (both PRs merged by the operator 2026-11-02T09:26Z / 09:29Z).
- `logs/2026-11-03#merge-conflict-cleanup（手工会话）` — `eyebrow scan` wrote 4 `.pyc` into `eyebrowlock.json`; `eyebrow verify --ci` OK after removing local `__pycache__` · `bin/generate-skills-json` `count_files` patch reverted in `523bfe02`.

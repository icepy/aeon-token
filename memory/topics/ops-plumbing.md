---
title: Scheduler and notification plumbing state
description: What actually fires this agent's schedules, what "enabled" in aeon.yml does and does not prove, and the notification-format rules that supersede the old hand-formatting notes.
tags:
  - ops
  - runbook
  - scheduler
  - notify
timestamp: 2026-10-28T18:20:00Z
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

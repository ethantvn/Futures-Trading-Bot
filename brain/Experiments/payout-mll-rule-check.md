---
type: experiment
status: open
priority: P3
phase: 20
family: rules-verification
next-action: Ask Lucid support when convenient; log answer in Inbox then update lucid-25k-verified. DOWNGRADED 2026-07-13 — Phase 22 showed pass+FIRST-payout is independent of this rule; it only matters for multi-cycle income modeling.
verdict: null
updated: 2026-07-13
---

# Payout vs MLL rule check (blocker for funded sweep)

**One fact lookup that changes the funded model.**

## Question for Lucid support

> When a funded Flex 25K account takes a payout, does the withdrawn amount reduce the balance used for the trailing Max Loss Limit — i.e. does withdrawing $1,000 pull the account $1,000 closer to the MLL floor?

Also confirm while at it:
- Exact auto-flatten timing before 4:45 PM ET (config note says ~10 sec).
- Payout cycle cadence (can qualifying days for cycle N+1 start immediately after payout N?)

## Why it matters

Decides optimal payout timing in [[funded-phase-sizing]]: take $500 ASAP vs build to the $1,000 cap. If withdrawal erodes the MLL cushion, early small payouts materially raise blow-up risk on later cycles.

When answered: update [[lucid-25k-verified]] and `config/lucid_25k.yaml`, then run the funded sweep.

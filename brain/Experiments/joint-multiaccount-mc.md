---
type: experiment
status: closed
priority: P1
phase: 20
family: account-economics
next-action: none — run both accounts
verdict: RUN BOTH. Marginal 2nd account = +0.81 expected funded accounts for +$97 expected cost ($119/funded acct vs $102 for acct 1). Correlation real (0.725 conditional) but restart-until-funded makes it near-additive, not a duplicate-risk trap.
updated: 2026-07-13
---

# Joint multi-account Monte Carlo — CLOSED

**Shapes actual income more than any pass-rate work.** Full writeup: `data/reports/phase20_joint_mc.md`, script `scripts/run_phase20_joint_mc.py`.

Constraint: Lucid forbids identical copy-trading across accounts → account 2 runs a **unique bot** (NR7 ORB + skipMon, ~63% pass standalone, ~40 trades/yr — see `PHASE_7_REPORT`).

## What was found

- Day-PnL correlation: **0.187 unconditional** (NR7 dormant ~81% of days), **0.725 on the ~80 days both fire**. Real co-movement when both trade, but NR7 is mostly a *dormant* second bot, not a *duplicate* one.
- **The originally-planned kill criterion was based on the wrong metric.** "P(≥1 account passes) vs a sequential-restart baseline" sounds like the right comparison but isn't: restarting ONE account gets ~10 independent attempts in a 250-trading-day window (median ORB-W pass ≈24 days) vs one un-restarted attempt per account in the parallel case — so the sequential baseline wins on that framing almost by construction (98.4% vs 85.7%), regardless of correlation.
- **Correct metric:** expected funded-account count when BOTH accounts restart on failure. Account 1 alone → 0.986 expected funded accounts, $101 E[cost]. Adding account 2 → 1.797 expected funded accounts, $198 E[cost]. The 2nd account is **near-additive** (+0.81 accounts for +$97) despite the real correlation, because "restart until funded, no eval time limit" already drives each account's own probability near-certain independently.

## Verdict

**Open both accounts.** Cost per marginal funded account: $102 (acct 1) vs $119 (acct 2) — only ~17% worse, not a correlated-risk trap. Treat NR7 as a slow/low-maintenance second stream (250 *trading* days ≈ much more real calendar time at ~40 trades/yr), not a fast second income source.

## Not modeled (flag if pursued further)

Correlated drawdown risk during a genuinely bad shared regime (both accounts failing the same violent week) — block bootstrap partially captures clustering but a dedicated worst-rolling-90-day joint-stress read was out of scope this pass.

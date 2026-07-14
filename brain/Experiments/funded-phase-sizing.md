---
type: experiment
status: closed
priority: P1
phase: 22
family: eval-mechanics
next-action: none
verdict: REJECTED — keep 1 micro in the funded phase too. Every upshift policy loses 7-18pts of pass+payout; the $100 qualifying-day asymmetry is real but breach risk vs the $1,000 funded MLL swamps it.
updated: 2026-07-13
---

# Funded-phase sizing sweep — CLOSED (rejected)

Report: `data/reports/phase22_funded_sizing.md`. Script: `scripts/run_phase22_funded_sizing.py`. Policy hook added to `src/evaluation/funded.py` + `journey.py` (tests green).

## Unblocking insight

The open [[payout-mll-rule-check]] question only affects cycles AFTER the first payout — pass+**first**-payout (the goal metric) is independent of it. The sweep was never actually blocked.

## Result (screen: WF-OOS, block, seed 42, 10k MC, eval locked @ 1 micro)

| Funded policy | Pass+payout | vs fixed_1 |
| --- | --- | --- |
| **fixed_1 (keep)** | **51.6%** | — |
| qualcush600_2 (2 if unqualified & cushion≥$600) | 44.2% | −7.4pt |
| qual_rush_2 (2 until 5 qual days, then 1) | 43.4% | −8.2pt |
| fixed_2 | 41.2% | −10.4pt |
| cushion600_2 | 39.9% | −11.7pt |
| qualcush800_3 | 38.7% | −12.9pt |
| qual_rush_3 | 34.6% | −17.0pt |
| fixed_3 | 33.5% | −18.1pt |

No policy came within +1pt of control → full battery skipped per staged design. The hypothesis (18% of 1-micro win days miss the $100 qualifying bar; sizing 2 converts them) is refuted: median loss day is −$172/micro, so doubling size doubles the funded drawdown-fail mode against the same $1,000 trailing MLL — and funded failure costs the entire pass.

## Consequence

[[fixed-1-micro]] now covers **both phases**: 1 MNQ micro every session, eval and funded, no exceptions. Together with Phase 19, sizing research is fully closed — the eval game (P19) and the funded game (P22) both prefer minimum size for this edge's win/loss profile.

[[payout-mll-rule-check]] is downgraded: it no longer blocks anything; it only matters for multi-cycle income modeling after the first payout.

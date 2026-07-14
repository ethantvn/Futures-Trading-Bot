# Phase 22 — Funded-phase sizing sweep (pass + first payout)

Eval phase locked at 1 micro (Phase 19). Funded phase swept — it differs:
no consistency rule, $100 qualifying day (18% of 1-micro win days miss it),
scaling tiers allow 10-20 micros. First-payout metric is independent of the
open payout-vs-MLL rule question (that affects later cycles only).

Ledgers: incumbent re-backtest WF-OOS (473 trades) + 2026 holdout (52 trades). 10k MC per cell, no eval time limit.

## Stage 1 — screen (WF-OOS, block, seed 42)

| Funded policy | Pass % | Pass+payout % | vs fixed_1 |
| --- | --- | --- | --- |
| fixed_1 | 70.3% | 51.6% | +0.0pt |
| fixed_2 | 70.3% | 41.2% | -10.4pt |
| fixed_3 | 70.3% | 33.5% | -18.1pt |
| qual_rush_2 | 70.3% | 43.4% | -8.2pt |
| qual_rush_3 | 70.3% | 34.6% | -17.0pt |
| cushion600_2 | 70.3% | 39.9% | -11.7pt |
| qualcush600_2 | 70.3% | 44.2% | -7.4pt |
| qualcush800_3 | 70.3% | 38.7% | -13.0pt |

## Stage 2 — full battery (3 seeds x block/day x WF+holdout)

_No policy beat fixed_1 by +1pt on the screen — battery skipped._

## Verdict

**Keep 1 micro in the funded phase.** No policy clears the pre-registered bar (+2pts pass+payout over fixed_1 across all seeds, sample modes, and both ledgers).

Pre-registered in `brain/Experiments/funded-phase-sizing.md` before running.

---
type: experiment
status: closed
priority: P1
phase: 21
family: rescoring-audit
next-action: none — orb_tod added to Dec 2026 refresh watch list
verdict: INCUMBENT STANDS. Corrections lift everything ~4-10pts but nothing crosses 69.8/51.6. Three within-2pts flags — two are the control itself, one (orb_tod midday) is a tie-minus with a holdout-only win. "Anything missed in the old data" is now permanently closed.
updated: 2026-07-13
---

# Re-score frozen challenger ledgers under verified rules — CLOSED

Full report: `data/reports/phase21_rescore_audit.md`. Script: `scripts/run_phase21_rescore.py`. 17 frozen ledgers, cost-corrected $1.98→$1.00/RT (exact — slippage lives in fill prices), 10k MC seed 42, no eval time limit, verified funded journey.

## Result

**No promotion.** The rules corrections lifted every candidate roughly in parallel (+4 to +10pts pass); the ranking compressed but did not invert. Bar: 69.8% / 51.6%.

| Flagged (within 2pts + dense) | New pass / pap | Disposition |
| --- | --- | --- |
| p17_orb_w_control | 69.8 / 51.6 | **Is the incumbent** (same ledger) — flag is vacuous |
| p17_orb_inside_day | 69.3 / 50.4 | Tie-minus on both; P17's "≈ control, no lift" conclusion unchanged |
| p18_orb_tod (midday window) | 68.9 / 50.7 | Closest true challenger ever (was −5.1pts, now −0.9) but still **below on both**; holdout 92.8/84.4 is striking but [[picky-bar]] forbids promoting on holdout alone → **watch item at [[wf-reselection-2026-12]]** |

Sparsity gate correctly caught the two headline-lookers: p16_structure_gated_orb (70.1/51.4 but 3.1 t/mo, 8-trade holdout) and p17_orb_only_inside (98.3 on 12 trades).

## Side findings

1. **NR7 caveat → [[run-both-accounts]]:** NR7 re-scores 65.1/44.5 WF but its 2026 holdout is weak — 34.0% pass / 11.5% pap on a sparse 15-trade window (+$148). Noisy sample, but check NR7's Dec-refresh numbers before funding account 2's eval fee.
2. **Anomaly logged, not chased** (`brain/Inbox/anomaly-gated-holdouts.md`): several gated ORB variants post far stronger 2026 holdouts than control (orb_tod 92.8%, vix_on_stack 90.6% vs control 67.8%).
3. Cross-check passed: arithmetic correction of the old P9 ledger → 68.8/49.3, within ~1pt of the engine re-backtest (69.8/51.6); residual explained by the known 1.0R-vs-stitched-folds difference.

## Kill criteria applied as pre-registered

Flag rule was "within 2pts on BOTH + density = flagged **for discussion**" — discussed above; none beats the incumbent, so none promotes. This note closes permanently: the old data has now been scored under correct rules exactly once, and the answer is the same.

---
type: experiment
status: rejected
phase: 19
family: eval-mechanics
verdict: Upshift, downshift, post-lock aggression, cushion-skip, consistency-cap — all worse than fixed 1 micro.
updated: 2026-07-13
---

# Eval-phase sizing policies

10k MC × 3 seeds × 2 sample modes × max_days {60,90,120} × 2 ledgers, only contract policy varied. fixed_1 62.9% avg vs post_lock_2 58.7%, upshift+cap 54.8%, fixed_2 51.6%. Dynamic sizing adds variance without improving the eval game; upshift feeds the drawdown-fail mode. Report: [[PHASE_19_REPORT]]. Decision: [[fixed-1-micro]].

**Scope limit resolved:** this covered the EVAL phase; the funded phase was swept separately in Phase 22 ([[funded-phase-sizing]]) — same conclusion, fixed 1 micro everywhere.

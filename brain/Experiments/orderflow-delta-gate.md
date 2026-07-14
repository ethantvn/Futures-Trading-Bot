---
type: experiment
status: open
priority: P2
phase: 19C
family: order-flow
next-action: Get Databento cost quote (Stage 0)
verdict: null
updated: 2026-07-13
---

# Order-flow delta gate on ORB-W (Phase 19C)

**The one remaining alpha bet.** First test using information the strategy has never seen (aggressor-side trade flow), not the 443rd OHLCV combo. Expect it to die at Stage 1 — that's fine; it settles whether order-flow data is ever worth discussing again (incl. MBP-1).

## Hypothesis

ORB longs where opening-range (09:30–10:00) cumulative delta / imbalance agrees with the breakout have higher follow-through; disagreeing breakouts are losers the width filter can't see.

## Staged plan with kill gates

### Stage 0 — cost quote (free)
Quote Databento **GLBX.MDP3 `trades` schema** for **MNQ + NQ**, 2019-06 → present ([[databento-trades-quote]]).
**KILL if > ~$300** (that's MBP-1 pricing; not worth it pre-evidence).

### Stage 1 — univariate screen (before ANY strategy code)
On ORB-W's actual trade days: does OR delta sign / imbalance predict P(hit 1.0R before stop)?
**PASS bar:** monotonic, year-stable lift — top-vs-bottom tercile follow-through gap ≥ ~5pts in ≥5 of 7 years.
**KILL:** if the feature can't predict our own trades' outcomes, no gate built on it will clear 70%. Stop. Write verdict. Do not proceed to Stage 2 "to be sure."

### Stage 2 — gated strategy (only if Stage 1 passes)
Gate ORB-W, exact Phase 18 harness: UPI train scorer, WF 24m/6m, 10k MC (no time limit), frozen 2026 holdout, density ≥4 t/mo.
**PASS bar:** [[picky-bar]] — ≥ ~70% pass / ≥ ~52% pass+payout with density. Not a thinner-trades sparsity trap.

## Prior

18 phases of gates on ORB-W: every one matched or hurt ([[vix-on-regime-gates]], [[mes-divergence-gate]], [[orb-filter-variants]]). Budget: ~$200 + 2 days, once.

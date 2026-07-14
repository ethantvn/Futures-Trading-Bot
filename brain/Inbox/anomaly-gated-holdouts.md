---
type: inbox
captured: 2026-07-13
source: Phase 21 re-scoring audit (data/reports/phase21_rescore_audit.md)
---

# Anomaly (logged, not chased): gated ORB variants outperform control on 2026 holdout

Under verified rules, frozen 2026 H1 holdout ledgers:

| Variant | Holdout pass / pap | Trades | WF pass (below bar) |
| --- | --- | --- | --- |
| orb_tod (midday) | 92.8% / 84.4% | 44 | 68.9% |
| vix_on_stack | 90.6% / 81.2% | 50 | 64.5% |
| control / incumbent | 67.8% / 47.7% | 52 | 69.8% |

Two different gates, same direction, decent (not tiny) trade counts. Could be: (a) 2026 H1 regime favors filtered entries, (b) chance on ~50-trade windows, (c) nothing — the same pattern P17 already declined to chase.

**Standing rule applies:** never promote on holdout alone ([[picky-bar]]). Correct venue to look again is [[wf-reselection-2026-12]] with 5 more months of data — if these gates' WF numbers cross the incumbent there, that's a real signal; if not, this stays noise.

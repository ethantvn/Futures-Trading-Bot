---
type: decision
decided: 2026-07-12
status: locked
---

# No more OHLCV strategy grids

Phases 1–18 ≈ 1,000+ combos across every testable family on 1m/5m bars: breakouts, fades, trend, momentum, structure, profile, cross-asset gates, seasonality, scalps. Nothing beats [[orb-w-incumbent]]. [[PHASE_18_REPORT]] is the definitive sweep.

New edge hunting requires a **new information set** (order flow: [[orderflow-delta-gate]]) or a different product. A "new" indicator on the same bars is not a new information set. This includes re-gridding with a different objective function (journey-scoring) — same data, noisier objective, skip.

---
type: experiment
status: rejected
phase: 16
family: mean-reversion
verdict: The "96%" was a lookahead bug (same-day afternoon ETH in "overnight"). Causal = 13.9% WF pass.
updated: 2026-07-13
---

# Overnight fade — REVOKED (lookahead lesson)

An earlier draft **promoted** this on 96% headline numbers. Audit trigger: the TradingView export was far worse than the Python ledger. Bug: `overnight_levels()` folded 16:00–17:00 same-day ETH into "overnight" high/low — morning signals saw post-RTH extremes unknowable at 09:30. ~355/517 sample days changed under the fix. Causal re-run: **13.9% WF pass**.

This is why [[causal-only]] is a standing decision and TV-vs-Python divergence is treated as an audit trigger, not an annoyance. Report: [[PHASE_16_REPORT]]. Also killed: overnight break (P18: 0.7%).

---
type: experiment
status: rejected
phase: 15
family: scalping
verdict: Cost floor kills it. Dense families deeply negative; the pretty one (89.5%) was a 7-trade sparsity trap.
updated: 2026-07-13
---

# Scalping (FVG / VWAP band / volume spike, 1m)

500 combos, 10 families, MNQ + GC. Task 0 cost-floor math: MNQ needs ~15-pt stops for +EV at 55% WR; median 1m bar is 9 pts. Dense families: large negative expectancy, several >10% ambiguous bars, die under 2-tick slippage. `mnq_fvg_vol` 89.5% headline = 7 OOS trades, 11% fold+, holdout 37.9%. Report: [[PHASE_15_REPORT]].

**Structural, not parametric — do not revisit on bar data.**

**2026-07-13 re-check (user request, GCQ2026 TV export, 25 days 1m):** VWAP 1σ band fade by ET session — 441 signals, 29.7% reach VWAP before 1R stop, avg **−$36.60/trade net GC** (−$5.86 MGC). Best session (Asia) is gross +$14/trade vs the $28 RT cost floor. The one positive bucket (NY PM, +$189 avg) is 29 trades with a 3.4% target-hit rate — time-exit luck, textbook sparse mirage. Tombstone re-confirmed on fresh data.

---
type: experiment
status: open
priority: P3
phase: maintenance
family: maintenance
next-action: Scheduled ~2026-12 with data through 2026-11
verdict: null
updated: 2026-07-13
---

# WF re-selection — December 2026 (scheduled)

Routine 6-month parameter refresh for [[orb-w-incumbent]]. **Not** an edge hunt.

## Scope

1. Re-run WF pipeline on data through 2026-11.
2. Fold in the **full re-grid at $0.50/side** (deferred from 2026-07: frozen-param re-backtest showed incumbent improved under real costs — 69.8/51.6 — so re-gridding early risked re-tuning to noise; see `data/reports/rebacktest_commission050.md`).
3. Check band stability: historically min_ratio ∈ {0.25, 0.3}, max_ratio ∈ {0.55, 0.7} in all folds. The *region* matters, not the grid point — do not chase a marginally different band.
4. Re-run MC under verified rules; update [[orb-w-incumbent]] and Home numbers.

## Watch list (from Phase 21 re-scoring audit, 2026-07-13)

- **orb_tod (midday window)** — closest challenger ever under verified rules: 68.9/50.7 WF (−0.9pt) with a 92.8/84.4 holdout. If its WF numbers cross the incumbent with December data, that's real; see `brain/Inbox/anomaly-gated-holdouts.md`.
- **NR7 ORB** — 2026 H1 holdout was weak (34% pass, 15 sparse trades). Confirm before funding account 2's eval fee ([[run-both-accounts]]).

## Guardrail

If live trading is mid-eval in December, param changes apply to the **next** attempt, not mid-attempt.

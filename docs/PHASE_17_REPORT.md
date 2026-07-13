# Phase 17 Report — ORB-W Causal Enhancers (VIX / ON / Regime)

Date: 2026-07-12.

## TL;DR

**No enhancer beats the incumbent.** Keep **MNQ ORB-W long-only + skip Monday @ 1 micro
on Lucid 25K** (~64% pass / ~46% pass+payout).

Free VIX prior-close, causal overnight range (18:00–09:30), prior-day structure
regime, and inside-day filters were all tested as **gates on ORB-W** (not new
primaries). Dense candidates either match control or **hurt** pass rate. The one
98% headline (`only_inside`) is a sparsity trap (12 trades, 11% fold+).

| Candidate | WF Pass | Pass+payout | Fold+ | Trades | Verdict |
| --- | --- | --- | --- | --- | --- |
| **ORB-W control** | **64.5%** | **46.4%** | 89% | 473 | **KEEP** |
| skip inside-day | 64.2% | 45.8% | 89% | 423 | ≈ control; no lift |
| prior-day regime | 61.6% | 42.7% | 78% | 147 | weaker / thinner |
| VIX + ON stack | 58.3% | 38.9% | 89% | 356 | worse WF |
| ON context | 57.4% | 38.8% | 78% | 426 | worse |
| VIX band | 52.2% | 34.4% | 89% | 357 | worse |
| only inside-day | 98.1% | 95.1% | **11%** | **12** | **REJECT** (sparse) |

## What we tested (causal only)

| Gate | Rule |
| --- | --- |
| VIX | Prior calendar-day VIX close (CBOE history → `data/processed/vix_daily.parquet`) |
| Overnight | Range from ETH bars **18:00–09:30 only** vs prior RTH ATR (no afternoon ETH lookahead) |
| Prior regime | Prior completed RTH HH/HL vs LH/LL / range |
| Inside day | Prior RTH high/low inside day-before-prior |

Base: Phase 9 ORB-W (`range=30`, width ∈ (0.25, 0.70], long-only, skip Mon, 1.0R).

## Holdout (2026-01-01 → 2026-06-28, frozen WF params)

| Family | Trades | Net $ | Pass % | Pass+payout % |
| --- | --- | --- | --- | --- |
| orb_w_control | 52 | $2,785 | **66.4%** | 46.1% |
| orb_inside_day | 51 | $2,647 | 65.7% | 45.5% |
| orb_prior_regime | 24 | $396 | 53.3% | 30.1% |
| orb_vix_on_stack | 50 | $3,825 | 89.5% | 79.9% |

Stack’s holdout looks strong but **WF was only 58%** — do not promote on a
short 2026 window alone. Control remains the picky-bar winner.

## Portfolio

Daily-sum of incumbent + skip-inside-day: **55.5%** pass / **32%** pass+payout —
worse than either alone (highly overlapping days ≈ doubling size, not diversifying).

## Deliverables

- `src/strategies/orb_enhanced.py`, VIX join helpers
- `config/phase17_orb_enhance.yaml`, `scripts/run_phase17.py`
- `data/reports/phase17_leaderboard.md`, `phase17_holdout.md`, `phase17_walk_forward.md`
- Tests: `tests/test_phase17_orb_enhance.py`

## Decision

**Reject all Phase 17 enhancers as replacements or stacks.** Live recommendation
unchanged: `tradingview/lucid_orb_width_25k.pine`.

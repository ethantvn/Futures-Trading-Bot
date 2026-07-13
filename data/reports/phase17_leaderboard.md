# Phase 17 Leaderboard — ORB-W Causal Enhancers (MNQ 25K)

Gates use prior VIX close, causal overnight (18:00–09:30), prior-day regime. Incumbent ORB-W shown for comparison.

| Candidate | Combos | Trades | Pass % | Pass+payout % | Fold+ % | Net $ | 2025 $ | t/mo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **ORB-W long-only + skipMon (incumbent)** | 0 | 473 | 64.3% | 45.6% | — | $13,731 | $4,201 | 8.8 |
| P17 orb_only_inside | 1 | 12 | 98.1% | 95.1% | 11% | $1,372 | $1,344 | 1.4 |
| P17 orb_w_control | 1 | 473 | 64.5% | 46.4% | 89% | $12,037 | $4,015 | 8.8 |
| P17 orb_inside_day | 1 | 423 | 64.2% | 45.8% | 89% | $10,502 | $2,671 | 7.9 |
| P17 orb_prior_regime | 6 | 147 | 61.6% | 42.7% | 78% | $3,373 | $-346 | 2.7 |
| P17 orb_vix_on_stack | 64 | 356 | 58.3% | 38.9% | 89% | $8,192 | $3,495 | 6.6 |
| P17 orb_on_context | 9 | 426 | 57.4% | 38.8% | 78% | $9,160 | $4,015 | 7.9 |
| P17 orb_vix_band | 9 | 357 | 52.2% | 34.4% | 89% | $5,671 | $1,713 | 6.6 |

## Portfolio MC (daily sum)

Components: incumbent ORB-W + **orb_inside_day** (daily PnL sum).
- Pass: **55.5%**
- Pass+payout: **32.0%**
- Active days: {'orb_w': 473, 'orb_inside_day': 423}


## Slippage stress (2025, top 2)

## P17 orb_only_inside — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 11 | $1,365 | 3.41 | 7.14 | $124.11 |
| 1 | 11 | $1,357 | 3.39 | 7.09 | $123.34 |
| 2 | 11 | $1,348 | 3.36 | 7.04 | $122.57 |

## P17 orb_w_control — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 93 | $3,499 | 1.43 | 2.46 | $37.62 |
| 1 | 93 | $3,422 | 1.42 | 2.40 | $36.80 |
| 2 | 93 | $3,346 | 1.41 | 2.35 | $35.98 |


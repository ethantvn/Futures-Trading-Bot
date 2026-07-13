# Re-backtest — ORB-W @ Lucid $0.50/side + verified rules

Commission: **$0.50/side** (was $0.62 + $0.37 exchange). Slippage: 1 tick.

Frozen params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True}` + skip Monday.

Note: old Phase 9 WF OOS stitched **1.0R and 1.5R** across folds (grid had both).
This re-backtest uses **1.0R only** (matches live Pine) — net $ is not directly
comparable; MC pass/payout is the meaningful comparison.

## Ledger

| | Trades | Net $ | Costs $ | Sharpe |
| --- | --- | --- | --- | --- |
| Old ($0.99/side) | 473 | $13,731 | $937 | 2.16 |
| **New ($0.50/side)** | 473 | $12,501 | $473 | 2.17 |

## Lucid 25K Monte Carlo (1 micro, block bootstrap)

| Ledger | max_days | Pass % | Fail % | Timeout % | Pass+payout % | Med days |
| --- | --- | --- | --- | --- | --- | --- |
| Old WF OOS | 60 | 64.3% | 31.3% | 4.4% | 45.7% | 23 |
| Old WF OOS | none | 67.7% | 32.3% | 0.0% | 47.9% | 24 |
| **New WF OOS** | 60 | 65.8% | 28.4% | 5.8% | 48.2% | 25 |
| **New WF OOS** | **none** | **69.8%** | 30.2% | 0.0% | **51.6%** | 26 |
| New 2026 holdout | none | 67.8% | 32.1% | 0.0% | 47.7% | 12 |

## Holdout 2026

- Trades: 52, net $2,836

## Recommendation (updated)

**ORB-W long-only + skip Monday @ 1 micro** — unchanged.
Use **69.8%** pass / **51.6%** pass+payout (no eval time limit, verified Lucid rules).

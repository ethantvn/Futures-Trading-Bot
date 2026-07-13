# Phase 7 Leaderboard — consistency-focused candidates

WF OOS window: stitched test folds 2021-06 → 2025-11 (same folds as Phase 5). MC: 10000 attempts, block bootstrap, seed 42, Lucid 25K, @1 micro. Sorted by **pass rate**, then **UPI** (annualized P&L / ulcer index). `+skipMon` = same ledger, Mondays removed (post-hoc overlay, Phase 6b methodology).

| Candidate | Trades | Pass@1 | Med d | Net $ | Sharpe | UPI | MaxDD | R² | ConsecL | Last90 $ | Last252 $ | 2023-25 $ | Neg 6m | Worst 6m |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nr7_orb +skipMon | 181 | 63.5% | 18 | $6,095 | 2.48 | 12.93 | $-1,965 | 0.89 | 6 | $4,967 | $6,095 | $5,523 | 0% | $2,857 |
| orb_width +skipMon | 659 | 61.8% | 21 | $17,607 | 1.89 | 10.68 | $-2,533 | 0.92 | 9 | $1,836 | $10,948 | $13,203 | 0% | $1,061 |
| nr7_orb | 219 | 59.6% | 20 | $5,632 | 1.92 | 9.62 | $-2,090 | 0.90 | 9 | $2,928 | $5,632 | $4,887 | 0% | $2,736 |
| orb_width | 802 | 55.0% | 22 | $17,057 | 1.52 | 6.63 | $-2,350 | 0.94 | 9 | $1,458 | $5,305 | $12,153 | 0% | $173 |
| orb_target +skipMon | 913 | 53.8% | 21 | $24,400 | 1.64 | 6.10 | $-3,998 | 0.97 | 12 | $1,701 | $5,565 | $16,919 | 5% | $-1,614 |
| BASELINE orb +skipMon | 807 | 51.9% | 21 | $19,427 | 1.52 | 6.15 | $-3,003 | 0.96 | 7 | $1,273 | $3,759 | $11,430 | 0% | $227 |
| orb_timestop +skipMon | 913 | 49.4% | 22 | $14,711 | 1.13 | 3.80 | $-4,412 | 0.93 | 12 | $1,273 | $1,671 | $10,056 | 16% | $-3,069 |
| orb_target | 1128 | 46.7% | 22 | $22,640 | 1.27 | 3.72 | $-4,449 | 0.97 | 10 | $2,276 | $6,409 | $15,170 | 2% | $-1,959 |
| orb_timestop | 1128 | 44.9% | 24 | $16,947 | 1.04 | 3.99 | $-3,071 | 0.96 | 7 | $1,847 | $2,609 | $11,152 | 8% | $-1,442 |
| BASELINE orb (Phase 5 WF OOS) | 993 | 44.3% | 22 | $18,377 | 1.16 | 3.52 | $-3,458 | 0.93 | 6 | $1,847 | $5,432 | $11,132 | 17% | $-1,266 |
| afternoon_breakout +skipMon | 594 | 24.5% | 37 | $2,761 | 0.55 | 1.78 | $-1,654 | 0.73 | 9 | $-502 | $-1,011 | $236 | 26% | $-842 |
| afternoon_breakout | 728 | 23.0% | 35 | $2,216 | 0.36 | 0.82 | $-2,265 | 0.52 | 7 | $-1,419 | $-1,808 | $-920 | 34% | $-1,124 |

## Rejected families (consistency re-score, fixed params, full grid window)

Documented only — not candidates (failed Phase 3-5 expectancy/holdout).

| Candidate | Trades | Pass@1 | Med d | Net $ | Sharpe | UPI | MaxDD | R² | ConsecL | Last90 $ | Last252 $ | 2023-25 $ | Neg 6m | Worst 6m |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REJ ema_trend | 2950 | 29.9% | 26 | $5,081 | 0.31 | 0.34 | $-7,063 | 0.28 | 10 | $-220 | $6,084 | $3,426 | 48% | $-2,923 |
| REJ vwap_pullback | 1943 | 9.3% | 35 | $-9,382 | -0.94 | -0.28 | $-12,615 | 0.90 | 11 | $778 | $634 | $-3,108 | 78% | $-4,386 |
| REJ prev_day_hl_breakout | 1443 | 6.0% | 38 | $-6,732 | -0.67 | -0.22 | $-8,992 | 0.85 | 8 | $-52 | $1,765 | $-530 | 73% | $-2,667 |
| REJ bollinger_mean_reversion | 1715 | 3.9% | 41 | $-5,384 | -0.81 | -0.26 | $-6,942 | 0.84 | 10 | $620 | $243 | $193 | 80% | $-2,615 |

## Slippage stress (2025, final params)

## nr7_orb — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 62 | $1,687 | 1.34 | 1.88 | $27.21 |
| 1 | 62 | $1,635 | 1.33 | 1.82 | $26.37 |
| 2 | 62 | $1,583 | 1.31 | 1.76 | $25.54 |

## orb_width — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 189 | $4,909 | 1.27 | 1.67 | $25.98 |
| 1 | 189 | $4,756 | 1.26 | 1.61 | $25.16 |
| 2 | 189 | $4,602 | 1.25 | 1.56 | $24.35 |

## orb_target — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 251 | $4,581 | 1.17 | 1.02 | $18.25 |
| 1 | 251 | $4,370 | 1.16 | 0.97 | $17.41 |
| 2 | 251 | $4,159 | 1.15 | 0.92 | $16.57 |


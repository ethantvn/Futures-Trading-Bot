# Phase 9 Leaderboard — long-only, macro skip, portfolio research

Sorted by Lucid 25K pass rate @1 micro, then UPI. MC: 10000 block-bootstrap attempts. `Pass+Payout` = pass eval AND reach first $500-eligible payout (same attempt).

| Candidate | Trades | Pass@1 | Pass+Payout | Med d | Net $ | Sharpe | UPI | MaxDD | Last252 $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orb_longonly +skipMon | 473 | 64.3% | 45.6% | 23 | $13,731 | 2.16 | 10.7 | $-2,500 | $8,778 |
| orb_longonly_macro +skipMon | 395 | 63.6% | 46.4% | 26 | $9,883 | 2.06 | 11.8 | $-2,030 | $6,867 |
| PHASE7 nr7_orb +skipMon | 181 | 63.5% | 42.9% | 18 | $6,095 | 2.48 | 12.9 | $-1,965 | $6,095 |
| PHASE7 orb_width +skipMon | 659 | 61.8% | 41.7% | 21 | $17,607 | 1.89 | 10.7 | $-2,533 | $10,948 |
| orb_macro_skip +skipMon | 685 | 55.9% | 35.7% | 25 | $12,589 | 1.45 | 3.6 | $-5,345 | $9,347 |

## Macro-day P&L (Phase 7 winner, skipMon)

- Phase 7 winner on macro days (108 sessions): net $3,274 (avg $30) vs non-macro net $14,333 (avg $26)

## Slippage stress (2025, final params)

## orb_longonly — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 116 | $4,071 | 1.41 | 2.35 | $35.09 |
| 1 | 116 | $3,974 | 1.40 | 2.29 | $34.26 |
| 2 | 116 | $3,877 | 1.39 | 2.23 | $33.42 |

## orb_macro_skip — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 180 | $3,910 | 1.22 | 1.41 | $21.72 |
| 1 | 180 | $3,763 | 1.22 | 1.36 | $20.90 |
| 2 | 180 | $3,615 | 1.21 | 1.30 | $20.08 |

## orb_longonly_macro — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 98 | $3,823 | 1.46 | 2.56 | $39.01 |
| 1 | 98 | $3,742 | 1.45 | 2.50 | $38.18 |
| 2 | 98 | $3,661 | 1.44 | 2.45 | $37.36 |


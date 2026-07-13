# Phase 10 MES Leaderboard

MES micro @ 1 contract. Lucid Flex 25K MC (10k block-bootstrap). `Pass+Payout` = pass eval AND first $500-eligible payout. Sorted by pass rate, then UPI.

| Candidate | Trades | Pass@1 | Pass+Payout | Med d | Net $ | Sharpe | UPI | MaxDD | Last252 $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MNQ orb_longonly +skipMon (Phase 9) | 473 | 64.3% | 45.6% | 23 | $13,731 | 2.16 | 10.7 | $-2,500 | $8,778 |
| MES orb_longonly +skipMon | 431 | 19.4% | 7.6% | 38 | $973 | 0.28 | 0.9 | $-1,611 | $1,693 |
| MES orb_width +skipMon | 605 | 12.3% | 3.8% | 38 | $-994 | -0.21 | -0.4 | $-2,609 | $-458 |

## Slippage stress (2025, final params)

## MES orb_width — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 211 | $-607 | 0.95 | -0.30 | $-2.87 |
| 1 | 211 | $-1,030 | 0.92 | -0.51 | $-4.88 |
| 2 | 211 | $-1,454 | 0.90 | -0.72 | $-6.89 |

## MES orb_longonly — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 100 | $1,112 | 1.19 | 1.14 | $11.12 |
| 1 | 100 | $888 | 1.15 | 0.91 | $8.88 |
| 2 | 100 | $664 | 1.11 | 0.68 | $6.64 |


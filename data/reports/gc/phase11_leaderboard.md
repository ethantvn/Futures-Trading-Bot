# Phase 11 GC Leaderboard — Lucid Flex 50K @ 1 full-size contract

Sorted by 50K pass rate @1 GC, then UPI. MC: 10k block-bootstrap.
Sizing verdict: see `phase11_sizing.md`.

| Candidate | Trades | Pass@1 | Fail % | Med d | Net $ | Sharpe | UPI | MaxDD | Last252 $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GC macro_nfp_cpi | 97 | 53.9% | 46.0% | 11 | $12,124 | 2.70 | 15.1 | $-5,566 | $12,124 |
| GC ny_orb | 627 | 25.6% | 73.9% | 12 | $2,104 | 0.07 | 0.1 | $-17,918 | $-4,086 |
| GC comex_orb | 618 | 21.2% | 77.6% | 13 | $-3,554 | -0.13 | -0.1 | $-19,014 | $3,679 |
| GC nr_comex | 158 | 15.0% | 84.9% | 14 | $-8,294 | -1.39 | -1.6 | $-13,768 | $-8,294 |
| GC london_orb | 762 | 12.8% | 86.3% | 18 | $-35,756 | -1.41 | -0.8 | $-37,498 | $-24,896 |
| GC vwap_trend | 698 | 10.0% | 89.7% | 19 | $-35,806 | -2.51 | -1.2 | $-39,002 | $-30,655 |
| GC vwap_reversion | 1417 | 2.1% | 96.0% | 27 | $-58,535 | -3.33 | -0.6 | $-61,277 | $-21,481 |

## Slippage stress (2025, top 2 by pass rate)

## GC macro_nfp_cpi — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 33 | $-3,324 | 0.74 | -2.03 | $-100.73 |
| 1 | 33 | $-3,894 | 0.71 | -2.36 | $-118.00 |
| 2 | 33 | $-4,464 | 0.68 | -2.69 | $-135.27 |

## GC ny_orb — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 194 | $2,703 | 1.04 | 0.23 | $13.93 |
| 1 | 194 | $-817 | 0.99 | -0.07 | $-4.21 |
| 2 | 194 | $-4,337 | 0.94 | -0.36 | $-22.36 |


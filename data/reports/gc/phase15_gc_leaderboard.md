# Phase 15 Scalp Leaderboard — GC

Primary ranking: lucid_50k pass → fold stability → UPI. Ambiguity >10% flagged REJECT. Grids through 2025-12-31; 2026 holdout separate.

| Candidate | Combos | Trades | Pass 50K | Pass 100K | Amb % | Fold+ % | Net $ | UPI | MaxDD | 2025 $ | t/mo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gc gc_fvg_vol | 64 | 83 | 38.1% | 22.9% | 8.4% | 50% | $1,316 | 1.7 | $-6,058 | $728 | 2.4 |
| gc gc_fvg_1m | 96 | 255 | 23.9% | 7.3% | 5.9% | 50% | $-595 | -0.3 | $-6,138 | $-5,029 | 7.3 |
| gc gc_vol_spike | 96 | 2660 | 9.6% | 3.2% | 3.5% | 0% | $-72,840 | -0.7 | $-78,694 | $-39,286 | 74.0 |
| gc gc_vwap_rev ❌AMB | 48 | 1482 | 10.2% | 2.1% | 18.2% | 17% | $-29,683 | -0.7 | $-31,847 | $-3,341 | 41.3 |

## Slippage stress (2025, top eligible)

## P15 gc gc_fvg_vol — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 64 | $878 | 1.07 | 0.57 | $13.72 |
| 1 | 64 | $508 | 1.04 | 0.33 | $7.94 |
| 2 | 64 | $138 | 1.01 | 0.09 | $2.16 |

## P15 gc gc_fvg_1m — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 258 | $-8,784 | 0.85 | -1.76 | $-34.05 |
| 1 | 258 | $-10,424 | 0.83 | -2.07 | $-40.40 |
| 2 | 258 | $-12,064 | 0.81 | -2.37 | $-46.76 |

## P15 gc gc_vol_spike — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 1047 | $-14,116 | 0.92 | -1.18 | $-13.48 |
| 1 | 1019 | $-25,482 | 0.86 | -2.19 | $-25.01 |
| 2 | 1005 | $-38,420 | 0.80 | -3.38 | $-38.23 |


## Sparsity / wall-clock

| Family | Active days | Span days | Trades/mo | Ambiguity |
| --- | --- | --- | --- | --- |
| gc_fvg_vol | 62 | 1060 | 2.4 | 8.4% |
| gc_fvg_1m | 164 | 1066 | 7.3 | 5.9% |
| gc_vol_spike | 771 | 1094 | 74.0 | 3.5% |
| gc_vwap_rev | 547 | 1093 | 41.3 | 18.2% |

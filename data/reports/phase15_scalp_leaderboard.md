# Phase 15 Scalping Leaderboard (MNQ + GC)

See Task 0 sizing: `data/reports/phase15_scalp_sizing.md`.
Incumbent benchmark: MNQ ORB-W long-only + skipMon @ 25K ≈ **64%** pass.

# Phase 15 Scalp Leaderboard — MNQ

Primary ranking: lucid_25k pass → fold stability → UPI. Ambiguity >10% flagged REJECT. Grids through 2025-12-31; 2026 holdout separate.

| Candidate | Combos | Trades | Pass 25K | Amb % | Fold+ % | Net $ | UPI | MaxDD | 2025 $ | t/mo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mnq mnq_fvg_vol | 32 | 7 | 89.5% | 0.0% | 11% | $182 | 163.7 | $-85 | $182 | 1.4 |
| mnq mnq_vol_spike | 48 | 4015 | 5.3% | 7.7% | 33% | $-7,291 | -0.4 | $-7,314 | $-1,123 | 74.4 |
| mnq mnq_fvg_3m | 32 | 432 | 0.4% | 6.0% | 22% | $-1,652 | -1.5 | $-1,955 | $-566 | 8.4 |
| mnq mnq_vwap_rev ❌AMB | 24 | 4530 | 0.7% | 24.5% | 0% | $-10,653 | -0.5 | $-11,224 | $-4,689 | 84.0 |
| mnq mnq_fvg_1m ❌AMB | 48 | 314 | 0.1% | 21.0% | 33% | $-1,662 | -1.9 | $-2,099 | $-600 | 6.1 |
| mnq mnq_vwap_pb ❌AMB | 12 | 3774 | 0.0% | 17.0% | 0% | $-15,762 | -0.4 | $-16,118 | $-2,108 | 70.0 |

## Slippage stress (2025, top eligible)

## P15 mnq mnq_fvg_vol — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 31 | $195 | 1.30 | 1.93 | $6.30 |
| 1 | 31 | $188 | 1.29 | 1.85 | $6.08 |
| 2 | 31 | $181 | 1.27 | 1.77 | $5.85 |

## P15 mnq mnq_vol_spike — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 728 | $-346 | 0.98 | -0.18 | $-0.48 |
| 1 | 728 | $-916 | 0.95 | -0.49 | $-1.26 |
| 2 | 728 | $-1,486 | 0.92 | -0.79 | $-2.04 |

## P15 mnq mnq_fvg_3m — slippage stress (2025)

| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |
| --- | --- | --- | --- | --- | --- |
| 0 | 191 | $-812 | 0.86 | -1.71 | $-4.25 |
| 1 | 191 | $-863 | 0.85 | -1.81 | $-4.52 |
| 2 | 191 | $-913 | 0.84 | -1.91 | $-4.78 |


## Sparsity / wall-clock

| Family | Active days | Span days | Trades/mo | Ambiguity |
| --- | --- | --- | --- | --- |
| mnq_fvg_vol | 7 | 147 | 1.4 | 0.0% |
| mnq_vol_spike | 1130 | 1642 | 74.4 | 7.7% |
| mnq_fvg_3m | 290 | 1561 | 8.4 | 6.0% |
| mnq_vwap_rev | 1009 | 1642 | 84.0 | 24.5% |
| mnq_fvg_1m | 186 | 1561 | 6.1 | 21.0% |
| mnq_vwap_pb | 915 | 1642 | 70.0 | 17.0% |


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


## 2026 Holdout (one-shot)

### MNQ
See `data/reports/phase15_mnq_holdout.md`

| Family | Trades | Net $ | Amb % | Pass 25K |
| --- | --- | --- | --- | --- |
| mnq_fvg_vol | 31 | $423 | 12.9% | 37.9% |
| mnq_vol_spike | 323 | $-2,872 | 9.6% | 4.7% |
| mnq_fvg_3m | 127 | $-196 | 4.7% | 0.5% |

### GC
See `data/reports/gc/phase15_gc_holdout.md`

| Family | Trades | Net $ | Amb % | Pass 50K | Pass 100K |
| --- | --- | --- | --- | --- | --- |
| gc_fvg_vol | 105 | $-4,148 | 16.2% | 15.2% | 3.7% |
| gc_fvg_1m | 331 | $-24,958 | 18.1% | 6.7% | 1.3% |

**Verdict: REJECT all Phase 15 scalpers. Incumbent MNQ ORB-W (~64% 25K) unchanged.**

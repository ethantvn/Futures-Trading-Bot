# Phase 11 GC Walk-Forward

- Folds: 6 × (18m train / 6m test)
- Grid: 2021-06-11 → 2025-12-31

## comex_orb

- Final params: `{'anchor_minute': 500, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 1000000000.0, 'max_risk_points': 5.0}`
- OOS trades: 618, net $-3,554

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=500, range_minutes=60, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=5.0 | -0.03 | $-292 | $8,888 | 74 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=500, range_minutes=60, target_r=1.0, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=0.7, max_risk_points=5.0 | 1.58 | $16,244 | $-3,758 | 86 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=500, range_minutes=60, target_r=1.0, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=5.0 | 1.51 | $21,902 | $-7,700 | 120 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=500, range_minutes=60, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=4.0 | 1.07 | $16,348 | $4,284 | 127 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=500, range_minutes=60, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=4.0 | 0.39 | $6,211 | $-5,044 | 118 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=500, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=5.0 | 0.50 | $6,560 | $-224 | 93 |

## ny_orb

- Final params: `{'anchor_minute': 570, 'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 5.0}`
- OOS trades: 627, net $2,104

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=570, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=5.0 | 0.43 | $5,020 | $3,284 | 102 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=570, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=5.0 | 1.07 | $13,044 | $3,298 | 109 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=570, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=5.0 | 1.80 | $17,884 | $8,530 | 95 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=570, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=5.0 | 1.73 | $17,876 | $-7,138 | 111 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=570, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=5.0 | 0.69 | $10,208 | $-7,951 | 112 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=570, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=5.0 | 0.02 | $341 | $2,081 | 98 |

## london_orb

- Final params: `{'anchor_minute': 330, 'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.0, 'max_width_ratio': 1000000000.0, 'max_risk_points': 5.0}`
- OOS trades: 762, net $-35,756

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=330, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=4.0 | -0.71 | $-6,379 | $739 | 127 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=330, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=5.0 | -1.03 | $-10,275 | $-5,184 | 128 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=330, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=5.0 | -0.83 | $-7,631 | $-989 | 128 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=330, range_minutes=60, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=3.0 | -0.08 | $-862 | $-5,754 | 128 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=330, range_minutes=60, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=5.0 | 0.38 | $4,975 | $-13,807 | 124 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=330, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=5.0 | 0.04 | $518 | $-10,761 | 127 |

## globex_orb

- Final params: `{}`
- OOS trades: 0, net $0

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## nr_comex

- Final params: `{'anchor_minute': 500, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'nr_n': 7, 'mode': 'either', 'max_risk_points': 4.0}`
- OOS trades: 158, net $-8,294

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=500, range_minutes=30, target_r=1.0, expire_minutes=120, nr_n=5, mode=either, max_risk_points=4.0 | 1.07 | $3,170 | $-2,142 | 34 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=500, range_minutes=30, target_r=1.0, expire_minutes=120, nr_n=7, mode=either, max_risk_points=4.0 | 0.85 | $2,080 | $-3,488 | 21 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=500, range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=7, mode=either, max_risk_points=4.0 | 0.36 | $1,033 | $105 | 25 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=500, range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=7, mode=either, max_risk_points=4.0 | -0.09 | $-254 | $-2,361 | 32 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=500, range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=7, mode=either, max_risk_points=4.0 | -1.51 | $-4,504 | $-2,704 | 23 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=500, range_minutes=30, target_r=1.0, expire_minutes=120, nr_n=7, mode=either, max_risk_points=4.0 | -0.54 | $-1,660 | $2,296 | 23 |

## macro_nfp_cpi

- Final params: `{'macro_kind': 'nfp_cpi', 'release_minute': 510, 'pre_range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 90, 'max_risk_points': 5.0}`
- OOS trades: 97, net $12,124

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, target_r=1.0, expire_minutes=90, max_risk_points=5.0 | 3.42 | $6,870 | $6,080 | 15 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, target_r=1.0, expire_minutes=90, max_risk_points=5.0 | 7.93 | $15,788 | $532 | 16 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, target_r=1.0, expire_minutes=90, max_risk_points=5.0 | 7.78 | $15,638 | $6,592 | 16 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, target_r=1.0, expire_minutes=90, max_risk_points=5.0 | 6.87 | $13,204 | $1,414 | 17 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, target_r=1.0, expire_minutes=90, max_risk_points=5.0 | 4.02 | $8,538 | $-3,188 | 16 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, target_r=1.0, expire_minutes=90, max_risk_points=5.0 | 2.05 | $4,818 | $694 | 17 |

## macro_fomc

- Final params: `{}`
- OOS trades: 0, net $0

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## vwap_trend

- Final params: `{'stop_atr': 1.5, 'target_r': 1.5, 'expire_minutes': 60, 'entry_start_minute': 540, 'max_risk_points': 4.0}`
- OOS trades: 698, net $-35,806

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=4.0 | -0.09 | $-597 | $-4,344 | 116 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=4.0 | -0.48 | $-3,242 | $-865 | 133 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=4.0 | -0.66 | $-4,208 | $99 | 121 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=4.0 | -0.77 | $-5,110 | $-10,638 | 118 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=4.0 | -1.60 | $-11,404 | $-8,255 | 106 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=4.0 | -2.55 | $-18,793 | $-11,803 | 104 |

## vwap_reversion

- Final params: `{'extension_atr': 2.0, 'stop_atr': 1.0, 'target_r': 1.0, 'expire_minutes': 45, 'entry_start_minute': 540, 'max_risk_points': 3.0}`
- OOS trades: 1417, net $-58,535

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | extension_atr=1.5, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=3.0 | -2.20 | $-15,881 | $-11,059 | 230 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | extension_atr=1.5, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=3.0 | -3.11 | $-22,884 | $-9,054 | 240 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | extension_atr=1.5, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=3.0 | -3.69 | $-25,250 | $-7,466 | 241 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | extension_atr=2.0, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=4.0 | -2.55 | $-19,267 | $-9,342 | 243 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | extension_atr=2.0, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=4.0 | -2.62 | $-21,953 | $-7,424 | 227 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | extension_atr=2.0, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=3.0 | -1.71 | $-15,218 | $-14,190 | 236 |


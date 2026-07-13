# Phase 12 GC Deep-Parameter Walk-Forward

- Folds: 6 × (18m train / 6m test)
- Grid: 2021-06-11 → 2025-12-31

## macro_nfp_cpi

- Grid size: **1296** combos
- Final params: `{'macro_kind': 'nfp_cpi', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 0.75, 'expire_minutes': 60, 'max_risk_points': 5.0, 'min_range_points': 0.0, 'long_only': True}`
- OOS trades: 87, net $4,599
- Fold stability: 67% positive test folds (median test $950)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=5.0, min_range_points=0.0, long_only=True | 13.31 | $7,710 | $880 | 10 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=5.0, min_range_points=2.0, long_only=False | 9.24 | $16,222 | $950 | 15 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=5.0, min_range_points=2.0, long_only=False | 8.87 | $16,052 | $4,562 | 16 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=5.0, min_range_points=0.0, long_only=False | 6.87 | $13,204 | $1,414 | 17 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=5.0, min_range_points=0.0, long_only=False | 4.06 | $8,808 | $-2,748 | 16 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=0.75, expire_minutes=60, max_risk_points=5.0, min_range_points=0.0, long_only=True | 7.94 | $4,982 | $-459 | 13 |

## macro_nfp

- Grid size: **216** combos
- Final params: `{'macro_kind': 'nfp', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 1.0, 'expire_minutes': 90, 'max_risk_points': 5.0, 'long_only': True}`
- OOS trades: 35, net $4,430
- Fold stability: 67% positive test folds (median test $1,422)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=4.0, long_only=False | 8.14 | $3,734 | $3,070 | 5 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=4.0, long_only=False | 12.03 | $6,014 | $1,422 | 6 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=4.0, long_only=False | 12.89 | $6,534 | $3,382 | 6 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=nfp, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=4.0, long_only=False | 12.05 | $8,584 | $1,142 | 6 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=nfp, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=4.0, long_only=False | 7.64 | $6,726 | $-3,188 | 6 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=1.0, expire_minutes=90, max_risk_points=5.0, long_only=True | 5.26 | $1,404 | $-1,398 | 6 |

## macro_cpi

- Grid size: **216** combos
- Final params: `{'macro_kind': 'cpi', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 1.0, 'expire_minutes': 60, 'max_risk_points': 5.0, 'long_only': True}`
- OOS trades: 52, net $1,354
- Fold stability: 50% positive test folds (median test $106)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=5, target_r=1.0, expire_minutes=60, max_risk_points=5.0, long_only=True | 9.96 | $4,960 | $2,046 | 8 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=5, target_r=1.0, expire_minutes=90, max_risk_points=5.0, long_only=True | 12.71 | $6,724 | $-970 | 5 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=2.0, expire_minutes=60, max_risk_points=5.0, long_only=False | 7.84 | $12,384 | $2,900 | 10 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=1.5, expire_minutes=60, max_risk_points=5.0, long_only=False | 6.13 | $5,905 | $-673 | 11 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=0, target_r=1.5, expire_minutes=60, max_risk_points=5.0, long_only=False | 3.53 | $4,223 | $-2,055 | 10 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=1.0, expire_minutes=60, max_risk_points=5.0, long_only=True | 8.63 | $4,840 | $106 | 8 |

## macro_fomc

- Grid size: **324** combos
- Final params: `{'macro_kind': 'fomc', 'release_minute': 840, 'pre_range_minutes': 45, 'post_delay_minutes': 5, 'target_r': 1.0, 'expire_minutes': 60, 'max_risk_points': 5.0, 'long_only': False}`
- OOS trades: 19, net $-102
- Fold stability: 50% positive test folds (median test $78)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=15, target_r=1.5, expire_minutes=60, max_risk_points=4.0, long_only=True | 7.83 | $2,777 | $436 | 3 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=4.0, long_only=True | 13.22 | $2,652 | $-616 | 2 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=4.0, long_only=True | 7.82 | $1,428 | $78 | 4 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=fomc, release_minute=840, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=4.0, long_only=False | 7.55 | $2,514 | $766 | 3 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=fomc, release_minute=840, pre_range_minutes=15, post_delay_minutes=5, target_r=2.0, expire_minutes=60, max_risk_points=3.0, long_only=True | 9.30 | $1,498 | $-644 | 3 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=5, target_r=1.0, expire_minutes=60, max_risk_points=5.0, long_only=False | 34.85 | $3,454 | $-122 | 4 |

## ny_orb_deep

- Grid size: **1296** combos
- Final params: `{'anchor_minute': 570, 'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 60, 'min_width_ratio': 0.3, 'max_width_ratio': 0.7, 'max_risk_points': 5.0, 'long_only': True}`
- OOS trades: 309, net $-1,044
- Fold stability: 50% positive test folds (median test $544)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=570, range_minutes=15, target_r=0.75, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 1.69 | $6,249 | $-389 | 34 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=570, range_minutes=15, target_r=0.75, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 1.54 | $5,528 | $-2,122 | 44 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=570, range_minutes=15, target_r=1.5, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=0.7, max_risk_points=5.0, long_only=False | 1.93 | $12,927 | $1,995 | 55 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=570, range_minutes=15, target_r=1.0, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=0.7, max_risk_points=5.0, long_only=False | 2.07 | $12,518 | $-4,780 | 65 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=570, range_minutes=30, target_r=1.5, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 1.87 | $13,991 | $544 | 57 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=570, range_minutes=30, target_r=1.5, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=0.7, max_risk_points=5.0, long_only=True | 1.83 | $15,034 | $3,708 | 54 |

## comex_orb_deep

- Grid size: **1296** combos
- Final params: `{'anchor_minute': 500, 'range_minutes': 15, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 1000000000.0, 'max_risk_points': 5.0, 'long_only': True}`
- OOS trades: 323, net $13,936
- Fold stability: 67% positive test folds (median test $1,922)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=500, range_minutes=30, target_r=2.0, expire_minutes=60, min_width_ratio=0.2, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 0.49 | $4,044 | $-378 | 61 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.2, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 2.70 | $23,336 | $1,922 | 61 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.2, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 2.95 | $24,782 | $2,354 | 62 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 2.23 | $16,742 | $-2,220 | 50 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=500, range_minutes=15, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=5.0, long_only=True | 1.27 | $4,336 | $1,308 | 39 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=500, range_minutes=15, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=5.0, long_only=True | 1.41 | $9,190 | $10,950 | 50 |

## nr_comex_deep

- Grid size: **288** combos
- Final params: `{'anchor_minute': 500, 'range_minutes': 45, 'target_r': 1.5, 'expire_minutes': 120, 'nr_n': 10, 'mode': 'either', 'max_risk_points': 4.0, 'long_only': True}`
- OOS trades: 93, net $2,906
- Fold stability: 50% positive test folds (median test $32)

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=570, range_minutes=45, target_r=1.0, expire_minutes=120, nr_n=10, mode=either, max_risk_points=4.0, long_only=False | 2.34 | $5,042 | $2,516 | 18 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=570, range_minutes=45, target_r=1.0, expire_minutes=120, nr_n=7, mode=either, max_risk_points=4.0, long_only=True | 3.83 | $4,450 | $-1,314 | 8 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=570, range_minutes=45, target_r=1.0, expire_minutes=120, nr_n=10, mode=either, max_risk_points=4.0, long_only=True | 4.81 | $4,466 | $32 | 11 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=570, range_minutes=45, target_r=1.5, expire_minutes=120, nr_n=10, mode=either, max_risk_points=3.0, long_only=True | 6.20 | $6,180 | $-2,993 | 16 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=570, range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=either, max_risk_points=5.0, long_only=False | 1.50 | $6,448 | $-704 | 23 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=500, range_minutes=45, target_r=1.5, expire_minutes=120, nr_n=10, mode=either, max_risk_points=4.0, long_only=True | 2.73 | $6,526 | $5,369 | 17 |


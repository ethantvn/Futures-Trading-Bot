# Phase 13 MGC Walk-Forward

- Folds: 6 × (18m train / 6m test)
- Grid: 2021-06-11 → 2025-12-31

## macro_nfp

- Grid size: **324** combos
- Final params: `{'macro_kind': 'nfp', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 0.75, 'expire_minutes': 60, 'max_risk_points': 15.0, 'long_only': False}`
- OOS trades: 32, net $643
- Fold stability: 67% positive test folds (median test $149)
- OOS by year: {'2023': 44.0000000000241, '2024': 512.0000000000314, '2025': 86.50000000001637}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=nfp, release_minute=510, pre_range_minutes=30, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=15.0, long_only=True | 8.13 | $211 | $-28 | 2 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=0.75, expire_minutes=60, max_risk_points=15.0, long_only=False | 11.55 | $553 | $109 | 6 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.5, expire_minutes=60, max_risk_points=15.0, long_only=False | 16.60 | $832 | $315 | 6 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=nfp, release_minute=510, pre_range_minutes=45, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=15.0, long_only=False | 15.13 | $974 | $238 | 6 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=nfp, release_minute=510, pre_range_minutes=45, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=15.0, long_only=False | 10.67 | $933 | $149 | 6 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=nfp, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=0.75, expire_minutes=60, max_risk_points=15.0, long_only=False | 10.25 | $352 | $-140 | 6 |

## macro_nfp_cpi

- Grid size: **648** combos
- Final params: `{'macro_kind': 'nfp_cpi', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 0.75, 'expire_minutes': 60, 'max_risk_points': 15.0, 'min_range_points': 3.0, 'long_only': True}`
- OOS trades: 76, net $938
- Fold stability: 50% positive test folds (median test $283)
- OOS by year: {'2022': 5.000000000001819, '2023': -156.9999999999368, '2024': 814.0000000000719, '2025': 275.4999999999991}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=15.0, min_range_points=0.0, long_only=True | 7.43 | $579 | $-41 | 10 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=15.0, min_range_points=3.0, long_only=False | 10.33 | $1,470 | $-7 | 9 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=15.0, min_range_points=3.0, long_only=False | 10.81 | $1,548 | $475 | 12 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=90, max_risk_points=15.0, min_range_points=3.0, long_only=False | 7.95 | $1,186 | $339 | 16 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=15.0, min_range_points=0.0, long_only=False | 5.72 | $1,183 | $-112 | 16 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=nfp_cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=0.75, expire_minutes=60, max_risk_points=15.0, min_range_points=3.0, long_only=True | 8.42 | $429 | $283 | 13 |

## comex_orb_deep

- Grid size: **432** combos
- Final params: `{'anchor_minute': 500, 'range_minutes': 10, 'target_r': 1.5, 'expire_minutes': 60, 'min_width_ratio': 0.3, 'max_width_ratio': 1000000000.0, 'max_risk_points': 10.0, 'long_only': True, 'skip_weekdays': [], 'skip_macro_days': False}`
- OOS trades: 204, net $1,995
- Fold stability: 50% positive test folds (median test $686)
- OOS by year: {'2022': 277.00000000002365, '2023': 403.00000000025466, '2024': 983.5000000002306, '2025': 331.50000000001}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=500, range_minutes=60, target_r=2.0, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=10.0, long_only=True, skip_weekdays=[], skip_macro_days=False | 0.75 | $653 | $874 | 46 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=500, range_minutes=60, target_r=2.0, expire_minutes=60, min_width_ratio=0.2, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True, skip_weekdays=[1], skip_macro_days=False | 2.78 | $2,364 | $-26 | 48 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.2, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True, skip_weekdays=[1], skip_macro_days=False | 2.75 | $2,174 | $800 | 52 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True, skip_weekdays=[1], skip_macro_days=False | 2.47 | $1,781 | $-243 | 39 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=500, range_minutes=10, target_r=1.5, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=10.0, long_only=True, skip_weekdays=[], skip_macro_days=False | 6.86 | $934 | $686 | 11 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=500, range_minutes=10, target_r=1.5, expire_minutes=60, min_width_ratio=0.3, max_width_ratio=1000000000.0, max_risk_points=10.0, long_only=True, skip_weekdays=[], skip_macro_days=False | 10.53 | $1,331 | $-96 | 8 |

## comex_orb

- Grid size: **960** combos
- Final params: `{'anchor_minute': 500, 'range_minutes': 10, 'target_r': 1.0, 'expire_minutes': 60, 'min_width_ratio': 0.25, 'max_width_ratio': 1000000000.0, 'max_risk_points': 15.0, 'long_only': True}`
- OOS trades: 269, net $1,384
- Fold stability: 50% positive test folds (median test $485)
- OOS by year: {'2022': 160.00000000003547, '2023': 773.000000000337, '2024': 695.5000000003047, '2025': -244.99999999994998}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=500, range_minutes=60, target_r=2.0, expire_minutes=60, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=25.0, long_only=True | 0.50 | $485 | $1,326 | 60 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=500, range_minutes=60, target_r=2.0, expire_minutes=60, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 2.30 | $2,357 | $-75 | 58 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 1.94 | $1,674 | $630 | 52 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=500, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 1.75 | $1,673 | $-449 | 59 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=500, range_minutes=10, target_r=1.5, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 4.80 | $1,100 | $485 | 25 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=500, range_minutes=10, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 5.73 | $1,235 | $-533 | 15 |

## london_orb

- Grid size: **960** combos
- Final params: `{'anchor_minute': 330, 'range_minutes': 15, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 15.0, 'long_only': False}`
- OOS trades: 104, net $360
- Fold stability: 67% positive test folds (median test $44)
- OOS by year: {'2022': -46.99999999999636, '2023': 56.500000000025466, '2024': -161.99999999990814, '2025': 512.0000000001028}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=330, range_minutes=15, target_r=0.75, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=False | 3.81 | $247 | $44 | 8 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=330, range_minutes=15, target_r=0.75, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=False | 4.75 | $348 | $30 | 1 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=330, range_minutes=45, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 3.24 | $645 | $-263 | 18 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=330, range_minutes=30, target_r=2.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=True | 3.36 | $434 | $46 | 11 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=330, range_minutes=45, target_r=2.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=False | 1.94 | $768 | $865 | 59 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=330, range_minutes=15, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=False | 4.40 | $447 | $-363 | 7 |

## macro_cpi

- Grid size: **324** combos
- Final params: `{'macro_kind': 'cpi', 'release_minute': 510, 'pre_range_minutes': 15, 'post_delay_minutes': 5, 'target_r': 0.75, 'expire_minutes': 60, 'max_risk_points': 15.0, 'long_only': True}`
- OOS trades: 56, net $40
- Fold stability: 67% positive test folds (median test $114)
- OOS by year: {'2022': 30.00000000000182, '2023': -80.7499999999518, '2024': 301.0000000000646, '2025': -210.7500000000009}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=5, target_r=0.75, expire_minutes=90, max_risk_points=15.0, long_only=True | 8.17 | $465 | $114 | 8 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=15.0, long_only=False | 10.85 | $1,429 | $-110 | 10 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.0, expire_minutes=60, max_risk_points=15.0, long_only=False | 8.23 | $1,140 | $131 | 9 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=cpi, release_minute=510, pre_range_minutes=30, post_delay_minutes=0, target_r=1.5, expire_minutes=90, max_risk_points=15.0, long_only=False | 4.59 | $649 | $95 | 11 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=cpi, release_minute=510, pre_range_minutes=45, post_delay_minutes=0, target_r=1.5, expire_minutes=60, max_risk_points=15.0, long_only=False | 3.62 | $451 | $-510 | 10 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=cpi, release_minute=510, pre_range_minutes=15, post_delay_minutes=5, target_r=0.75, expire_minutes=60, max_risk_points=15.0, long_only=True | 5.65 | $268 | $319 | 8 |

## ny_orb

- Grid size: **960** combos
- Final params: `{'anchor_minute': 570, 'range_minutes': 45, 'target_r': 1.0, 'expire_minutes': 60, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 25.0, 'long_only': True}`
- OOS trades: 450, net $112
- Fold stability: 67% positive test folds (median test $307)
- OOS by year: {'2022': -16.49999999995771, '2023': -1967.4999999995066, '2024': 1037.750000000356, '2025': 1058.250000000141}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=570, range_minutes=15, target_r=0.75, expire_minutes=60, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=False | 0.39 | $414 | $-691 | 122 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=570, range_minutes=15, target_r=1.0, expire_minutes=60, min_width_ratio=0.0, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 0.73 | $590 | $-876 | 94 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=570, range_minutes=30, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=25.0, long_only=False | 0.43 | $546 | $73 | 94 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=570, range_minutes=60, target_r=2.0, expire_minutes=60, min_width_ratio=0.0, max_width_ratio=0.7, max_risk_points=15.0, long_only=True | 0.47 | $207 | $431 | 45 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=570, range_minutes=45, target_r=0.75, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=True | 1.00 | $483 | $307 | 43 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=570, range_minutes=45, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=25.0, long_only=True | 2.69 | $1,878 | $868 | 52 |

## overlap_orb

- Grid size: **256** combos
- Final params: `{'anchor_minute': 780, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 60, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 15.0, 'long_only': True}`
- OOS trades: 102, net $-801
- Fold stability: 33% positive test folds (median test $-46)
- OOS by year: {'2022': -40.99999999999727, '2023': -65.99999999989859, '2024': 351.50000000008595, '2025': -1045.9999999999827}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=780, range_minutes=30, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 1.58 | $147 | $-126 | 17 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=780, range_minutes=15, target_r=1.5, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=False | 4.24 | $334 | $-46 | 8 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=600, range_minutes=15, target_r=1.5, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=True | 0.53 | $267 | $343 | 38 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=780, range_minutes=15, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=1000000000.0, max_risk_points=15.0, long_only=False | 1.96 | $225 | $74 | 10 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=780, range_minutes=15, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=False | 2.13 | $242 | $-617 | 14 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=780, range_minutes=30, target_r=1.0, expire_minutes=60, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=15.0, long_only=True | 4.32 | $764 | $-429 | 15 |

## london_orb_deep

- Grid size: **648** combos
- Final params: `{'anchor_minute': 330, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.3, 'max_width_ratio': 0.5, 'max_risk_points': 10.0, 'long_only': False}`
- OOS trades: 60, net $-499
- Fold stability: 50% positive test folds (median test $67)
- OOS by year: {'2022': -43.99999999999909, '2023': 50.50000000002274, '2024': 157.75000000006185, '2025': -662.9999999999718}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=330, range_minutes=10, target_r=0.75, expire_minutes=90, min_width_ratio=0.2, max_width_ratio=0.7, max_risk_points=10.0, long_only=False | 4.73 | $305 | $-48 | 6 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=330, range_minutes=15, target_r=0.75, expire_minutes=90, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=10.0, long_only=False | 4.75 | $348 | $67 | 2 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=330, range_minutes=15, target_r=1.0, expire_minutes=90, min_width_ratio=0.2, max_width_ratio=0.7, max_risk_points=10.0, long_only=False | 3.02 | $315 | $-330 | 14 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=330, range_minutes=30, target_r=1.0, expire_minutes=90, min_width_ratio=0.25, max_width_ratio=0.5, max_risk_points=10.0, long_only=True | 2.06 | $166 | $313 | 11 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=330, range_minutes=30, target_r=0.75, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.5, max_risk_points=10.0, long_only=False | 8.94 | $551 | $309 | 15 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=330, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.5, max_risk_points=10.0, long_only=False | 6.47 | $948 | $-809 | 12 |

## nr_orb

- Grid size: **384** combos
- Final params: `{'anchor_minute': 570, 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 60, 'nr_n': 10, 'mode': 'nr', 'max_risk_points': 25.0, 'long_only': True}`
- OOS trades: 98, net $-624
- Fold stability: 33% positive test folds (median test $-70)
- OOS by year: {'2022': -52.99999999999545, '2023': -297.9999999999113, '2024': -575.9999999998881, '2025': 303.00000000002456}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | anchor_minute=570, range_minutes=15, target_r=1.5, expire_minutes=120, nr_n=10, mode=nr, max_risk_points=15.0, long_only=False | 1.80 | $250 | $-70 | 12 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | anchor_minute=570, range_minutes=15, target_r=1.5, expire_minutes=120, nr_n=7, mode=nr, max_risk_points=15.0, long_only=False | 1.55 | $318 | $-311 | 16 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | anchor_minute=570, range_minutes=15, target_r=1.0, expire_minutes=120, nr_n=5, mode=either, max_risk_points=15.0, long_only=True | 1.14 | $231 | $-145 | 25 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | anchor_minute=570, range_minutes=15, target_r=1.0, expire_minutes=60, nr_n=5, mode=either, max_risk_points=15.0, long_only=True | 0.82 | $185 | $-296 | 22 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | anchor_minute=570, range_minutes=15, target_r=1.0, expire_minutes=60, nr_n=10, mode=either, max_risk_points=15.0, long_only=True | 0.62 | $98 | $180 | 15 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | anchor_minute=570, range_minutes=30, target_r=1.0, expire_minutes=60, nr_n=10, mode=nr, max_risk_points=25.0, long_only=True | 4.62 | $663 | $18 | 8 |

## vwap_trend

- Grid size: **72** combos
- Final params: `{'stop_atr': 1.5, 'target_r': 1.5, 'expire_minutes': 120, 'entry_start_minute': 540, 'max_risk_points': 15.0}`
- OOS trades: 663, net $-5,261
- Fold stability: 0% positive test folds (median test $-853)
- OOS by year: {'2022': -22.054309086064677, '2023': -1293.2749512273485, '2024': -2120.5231937224753, '2025': -1824.760450479057}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | stop_atr=1.5, target_r=2.0, expire_minutes=120, entry_start_minute=570, max_risk_points=15.0 | -1.13 | $-781 | $-853 | 117 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | stop_atr=2.0, target_r=2.0, expire_minutes=60, entry_start_minute=570, max_risk_points=15.0 | -1.30 | $-1,172 | $-599 | 107 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | stop_atr=1.5, target_r=2.0, expire_minutes=60, entry_start_minute=570, max_risk_points=15.0 | -1.67 | $-1,085 | $-101 | 112 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | stop_atr=2.0, target_r=2.0, expire_minutes=60, entry_start_minute=540, max_risk_points=15.0 | -1.36 | $-1,365 | $-1,804 | 115 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | stop_atr=1.5, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=15.0 | -2.08 | $-1,765 | $-887 | 100 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | stop_atr=1.5, target_r=1.5, expire_minutes=120, entry_start_minute=540, max_risk_points=15.0 | -2.23 | $-1,986 | $-1,016 | 112 |

## macro_fomc

- Grid size: **324** combos
- Final params: `{'macro_kind': 'fomc', 'release_minute': 840, 'pre_range_minutes': 45, 'post_delay_minutes': 5, 'target_r': 0.75, 'expire_minutes': 90, 'max_risk_points': 15.0, 'long_only': True}`
- OOS trades: 16, net $-16
- Fold stability: 67% positive test folds (median test $33)
- OOS by year: {'2022': 30.00000000000182, '2023': -25.99999999999227, '2024': 62.000000000010004, '2025': -81.74999999998181}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=15.0, long_only=True | 5.26 | $200 | $75 | 3 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=15, target_r=1.0, expire_minutes=60, max_risk_points=15.0, long_only=True | 5.18 | $196 | $-68 | 2 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=15, target_r=0.75, expire_minutes=60, max_risk_points=15.0, long_only=True | 8.42 | $108 | $26 | 3 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | macro_kind=fomc, release_minute=840, pre_range_minutes=15, post_delay_minutes=0, target_r=1.5, expire_minutes=60, max_risk_points=15.0, long_only=True | 8.09 | $308 | $33 | 2 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | macro_kind=fomc, release_minute=840, pre_range_minutes=15, post_delay_minutes=5, target_r=1.5, expire_minutes=90, max_risk_points=15.0, long_only=True | 12.11 | $218 | $-117 | 3 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | macro_kind=fomc, release_minute=840, pre_range_minutes=45, post_delay_minutes=5, target_r=0.75, expire_minutes=90, max_risk_points=15.0, long_only=True | 31.98 | $231 | $35 | 3 |

## vwap_reversion

- Grid size: **48** combos
- Final params: `{'extension_atr': 2.0, 'stop_atr': 1.0, 'target_r': 1.0, 'expire_minutes': 45, 'entry_start_minute': 540, 'max_risk_points': 15.0}`
- OOS trades: 1407, net $-10,439
- Fold stability: 0% positive test folds (median test $-1,444)
- OOS by year: {'2022': -129.29168469696242, '2023': -2830.086134626689, '2024': -3327.351588816934, '2025': -4152.041536835865}

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-06-11→2022-11-30 | 2022-12-01→2023-05-31 | extension_atr=2.5, stop_atr=1.0, target_r=1.5, expire_minutes=60, entry_start_minute=540, max_risk_points=15.0 | -3.59 | $-2,998 | $-1,444 | 232 |
| 2 | 2021-12-01→2023-05-31 | 2023-06-01→2023-11-30 | extension_atr=2.5, stop_atr=1.0, target_r=1.5, expire_minutes=45, entry_start_minute=540, max_risk_points=15.0 | -3.57 | $-3,227 | $-1,411 | 241 |
| 3 | 2022-06-01→2023-11-30 | 2023-12-01→2024-05-31 | extension_atr=1.5, stop_atr=1.0, target_r=1.5, expire_minutes=45, entry_start_minute=540, max_risk_points=15.0 | -3.95 | $-3,408 | $-1,786 | 242 |
| 4 | 2022-12-01→2024-05-31 | 2024-06-01→2024-11-30 | extension_atr=2.0, stop_atr=1.0, target_r=1.5, expire_minutes=45, entry_start_minute=540, max_risk_points=15.0 | -3.89 | $-3,616 | $-1,297 | 238 |
| 5 | 2023-06-01→2024-11-30 | 2024-12-01→2025-05-31 | extension_atr=2.5, stop_atr=1.0, target_r=1.5, expire_minutes=45, entry_start_minute=540, max_risk_points=15.0 | -3.42 | $-3,612 | $-1,687 | 224 |
| 6 | 2023-12-01→2025-05-31 | 2025-06-01→2025-11-30 | extension_atr=2.0, stop_atr=1.0, target_r=1.0, expire_minutes=45, entry_start_minute=540, max_risk_points=15.0 | -2.92 | $-3,215 | $-2,813 | 230 |


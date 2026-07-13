# Phase 10 MES Walk-Forward

## orb_width

- Final params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.2, 'max_width_ratio': 1000000000.0}`
- OOS trades: 748, net $-2,653

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 0.44 | $671 | $-909 | 72 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 0.22 | $281 | $124 | 72 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 0.17 | $291 | $151 | 78 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | -0.15 | $-300 | $240 | 64 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 0.31 | $711 | $-447 | 76 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.2, max_width_ratio=0.55 | 0.04 | $135 | $-462 | 98 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.2, max_width_ratio=1000000000.0 | -0.09 | $-282 | $500 | 109 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.21 | $444 | $427 | 69 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.2, max_width_ratio=1000000000.0 | 0.82 | $2,573 | $-2,277 | 110 |

## orb_longonly

- Final params: `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True}`
- OOS trades: 526, net $96

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | 0.57 | $702 | $-246 | 60 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | 0.58 | $859 | $-580 | 56 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | -0.04 | $-60 | $-173 | 71 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | -0.35 | $-657 | $158 | 54 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | -0.15 | $-292 | $-310 | 68 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | -0.45 | $-905 | $-438 | 56 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | -0.45 | $-763 | $293 | 52 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | -0.21 | $-297 | $1,865 | 53 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True | 0.83 | $1,410 | $-473 | 56 |


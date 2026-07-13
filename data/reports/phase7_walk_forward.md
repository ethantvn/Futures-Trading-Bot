# Phase 7 Walk-Forward

## orb_width (orb_filtered)

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7}`
- Stitched OOS: 802 trades, net $17,057

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 1.23 | $3,893 | $2,067 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 1.94 | $5,451 | $-770 | 74 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 1.22 | $4,500 | $2,623 | 83 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 1.57 | $6,366 | $248 | 72 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 1.27 | $5,983 | $1,733 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 1.11 | $7,048 | $2,393 | 98 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 1.86 | $9,513 | $3,742 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 1.96 | $9,709 | $4,594 | 94 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 2.40 | $12,173 | $428 | 96 |

## orb_target (orb_filtered)

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.25, 'expire_minutes': 120}`
- Stitched OOS: 1128 trades, net $22,640

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=999.0, expire_minutes=120 | -0.39 | $-2,145 | $1,030 | 125 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=999.0, expire_minutes=120 | -0.15 | $-899 | $3,032 | 123 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=999.0, expire_minutes=120 | 0.84 | $6,417 | $2,374 | 125 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=999.0, expire_minutes=120 | 1.01 | $8,030 | $1,321 | 125 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=2.5, expire_minutes=120 | 1.03 | $8,000 | $3,157 | 127 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=2.5, expire_minutes=120 | 1.28 | $10,247 | $2,741 | 123 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=2.5, expire_minutes=120 | 1.66 | $10,783 | $2,718 | 129 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=2.5, expire_minutes=120 | 1.73 | $11,432 | $5,846 | 125 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.25, expire_minutes=120 | 1.92 | $13,777 | $420 | 126 |

## orb_timestop (orb_filtered)

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'exit_minute': None}`
- Stitched OOS: 1128 trades, net $16,947

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | -0.49 | $-2,539 | $1,459 | 125 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | -0.19 | $-1,055 | $686 | 123 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | 0.53 | $3,595 | $2,189 | 125 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | 0.78 | $5,536 | $1,583 | 125 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | 0.83 | $5,917 | $1,909 | 127 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | 0.88 | $6,367 | $3,007 | 123 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | 1.47 | $8,688 | $3,647 | 129 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=870 | 2.06 | $11,659 | $2,421 | 125 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, exit_minute=None | 1.88 | $14,386 | $46 | 126 |

## nr7_orb (nr7_orb)

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'nr_n': 5, 'mode': 'nr'}`
- Stitched OOS: 219 trades, net $5,632

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=inside | 0.80 | $471 | $-196 | 12 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 1.60 | $1,882 | $-510 | 25 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=either | 1.00 | $1,738 | $1,093 | 25 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 1.67 | $2,394 | $415 | 21 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 1.86 | $2,477 | $940 | 27 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 1.77 | $2,328 | $988 | 24 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 3.89 | $3,826 | $1,273 | 25 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 3.47 | $3,616 | $-330 | 30 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, nr_n=5, mode=nr | 2.18 | $2,871 | $1,958 | 30 |

## afternoon_breakout (afternoon_breakout)

- Final params (last fold): `{'range_start_minute': 780, 'range_minutes': 60, 'target_r': 1.0, 'expire_minutes': 60, 'with_trend_filter': True}`
- Stitched OOS: 728 trades, net $2,216

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 0.97 | $1,875 | $-663 | 68 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 0.88 | $1,731 | $1,845 | 93 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 1.46 | $3,753 | $1,597 | 79 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 1.57 | $4,119 | $322 | 85 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 1.16 | $3,100 | $1,014 | 74 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 1.73 | $4,777 | $-241 | 76 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_start_minute=780, range_minutes=60, target_r=1.5, expire_minutes=60, with_trend_filter=True | 1.35 | $2,692 | $-837 | 65 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_start_minute=780, range_minutes=60, target_r=1.0, expire_minutes=60, with_trend_filter=False | 0.25 | $650 | $532 | 110 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_start_minute=780, range_minutes=60, target_r=1.0, expire_minutes=60, with_trend_filter=True | 0.16 | $384 | $-1,352 | 78 |


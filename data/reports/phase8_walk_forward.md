# Phase 8 Walk-Forward (overlays)

## maxhold_60

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7}`
- Stitched OOS: 818 trades, net $3,086

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.0, max_width_ratio=0.7 | -0.10 | $-238 | $287 | 107 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 0.34 | $710 | $-1,597 | 95 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.16 | $394 | $440 | 98 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.31 | $816 | $-216 | 93 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.33 | $910 | $726 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.47 | $1,472 | $1,576 | 86 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 1.13 | $2,531 | $1,034 | 67 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 1.88 | $5,185 | $993 | 83 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 2.24 | $7,891 | $-159 | 96 |

## maxhold_90

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.3, 'max_width_ratio': 0.7}`
- Stitched OOS: 847 trades, net $7,877

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | -0.06 | $-130 | $977 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 0.41 | $991 | $-991 | 95 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.56 | $1,586 | $136 | 98 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.47 | $1,471 | $458 | 93 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.87 | $2,827 | $1,791 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 1.05 | $3,668 | $926 | 86 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 1.11 | $4,031 | $3,134 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.2, max_width_ratio=0.7 | 2.15 | $8,345 | $825 | 109 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 2.41 | $8,281 | $621 | 81 |

## maxhold_120

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7}`
- Stitched OOS: 857 trades, net $8,122

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 0.45 | $1,059 | $888 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55 | 0.77 | $1,643 | $-171 | 74 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 0.83 | $3,356 | $-266 | 114 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.61 | $2,055 | $1,281 | 93 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 1.05 | $3,669 | $1,680 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 1.09 | $4,093 | $637 | 86 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 1.19 | $4,698 | $3,507 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.2, max_width_ratio=0.7 | 2.27 | $9,564 | $297 | 109 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 2.09 | $8,775 | $269 | 96 |

## maxhold_180

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7}`
- Stitched OOS: 859 trades, net $11,531

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 0.68 | $1,784 | $1,773 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 1.09 | $3,212 | $-1,399 | 95 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7 | 0.55 | $2,197 | $390 | 99 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 0.38 | $1,889 | $1,700 | 104 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.78 | $3,056 | $1,348 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55 | 0.67 | $2,800 | $1,187 | 86 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 1.43 | $6,285 | $5,182 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 2.55 | $11,002 | $1,616 | 94 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7 | 2.29 | $10,388 | $-267 | 96 |

## stopcap_200pts

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 200.0}`
- Stitched OOS: 802 trades, net $14,643

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7, max_risk_points=200.0 | 1.23 | $3,909 | $2,067 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=200.0 | 1.94 | $5,452 | $-739 | 74 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=200.0 | 1.23 | $4,531 | $2,623 | 83 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=200.0 | 1.58 | $6,397 | $248 | 72 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55, max_risk_points=200.0 | 1.28 | $6,014 | $1,733 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=200.0 | 1.13 | $7,163 | $2,393 | 98 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=200.0 | 1.86 | $9,513 | $3,742 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=200.0 | 1.96 | $9,709 | $2,769 | 94 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=200.0 | 2.13 | $10,668 | $-192 | 96 |

## stopcap_250pts

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 250.0}`
- Stitched OOS: 802 trades, net $15,574

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7, max_risk_points=250.0 | 1.23 | $3,893 | $2,067 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=250.0 | 1.94 | $5,451 | $-770 | 74 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=250.0 | 1.22 | $4,500 | $2,623 | 83 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=250.0 | 1.57 | $6,366 | $248 | 72 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55, max_risk_points=250.0 | 1.27 | $5,983 | $1,733 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=250.0 | 1.11 | $7,048 | $2,393 | 98 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=250.0 | 1.86 | $9,513 | $3,742 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=250.0 | 1.96 | $9,709 | $3,111 | 94 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=250.0 | 2.20 | $11,048 | $428 | 96 |

## stopcap_300pts

- Final params (last fold): `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'max_risk_points': 300.0}`
- Stitched OOS: 802 trades, net $15,384

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.7, max_risk_points=300.0 | 1.23 | $3,893 | $2,067 | 90 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=300.0 | 1.94 | $5,451 | $-770 | 74 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=300.0 | 1.22 | $4,500 | $2,623 | 83 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.3, max_width_ratio=0.55, max_risk_points=300.0 | 1.57 | $6,366 | $248 | 72 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.55, max_risk_points=300.0 | 1.27 | $5,983 | $1,733 | 93 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=300.0 | 1.11 | $7,048 | $2,393 | 98 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=300.0 | 1.86 | $9,513 | $3,742 | 102 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=300.0 | 1.96 | $9,709 | $2,921 | 94 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, max_risk_points=300.0 | 2.15 | $10,858 | $428 | 96 |


# Phase 17 Walk-Forward

## orb_only_inside

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'skip_inside_day': False, 'only_inside_day': True, 'vix_min': 0.0, 'vix_max': '1.0e9', 'on_range_min_ratio': 0.0, 'on_range_max_ratio': '1.0e9', 'allow_regimes': ''}`
- Fold+: 11%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | — | — | $0 | $0 | 0 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | — | — | $0 | $0 | 0 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=False, only_inside_day=True, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 0.51 | $147 | $1,503 | 8 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=False, only_inside_day=True, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 4.61 | $1,806 | $-131 | 4 |

## orb_w_control

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'vix_min': 0.0, 'vix_max': '1.0e9', 'on_range_min_ratio': 0.0, 'on_range_max_ratio': '1.0e9', 'allow_regimes': '', 'skip_inside_day': False, 'only_inside_day': False}`
- Fold+: 89%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | -0.41 | $-660 | $1,012 | 59 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 0.23 | $438 | $-581 | 46 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 0.00 | $10 | $2,895 | 62 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 1.55 | $4,058 | $737 | 55 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 1.51 | $4,063 | $1,243 | 54 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 1.60 | $4,294 | $832 | 53 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 2.47 | $5,707 | $1,483 | 50 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 2.00 | $4,295 | $2,868 | 47 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes=, skip_inside_day=False, only_inside_day=False | 2.57 | $6,427 | $1,547 | 47 |

## orb_inside_day

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'skip_inside_day': True, 'only_inside_day': False, 'vix_min': 0.0, 'vix_max': '1.0e9', 'on_range_min_ratio': 0.0, 'on_range_max_ratio': '1.0e9', 'allow_regimes': ''}`
- Fold+: 89%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | -0.67 | $-1,035 | $1,162 | 52 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 0.12 | $214 | $-494 | 44 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | -0.05 | $-100 | $2,642 | 59 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 1.51 | $3,695 | $892 | 49 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 1.68 | $4,202 | $1,160 | 46 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 1.70 | $4,200 | $664 | 49 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 2.55 | $5,359 | $1,431 | 42 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 2.23 | $4,148 | $1,365 | 39 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_inside_day=True, only_inside_day=False, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 2.19 | $4,621 | $1,679 | 43 |

## orb_prior_regime

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'pivot_n': 5, 'allow_regimes': 'range', 'vix_min': 0.0, 'vix_max': '1.0e9', 'on_range_min_ratio': 0.0, 'on_range_max_ratio': '1.0e9'}`
- Fold+: 78%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 1.81 | $771 | $-361 | 19 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 0.43 | $219 | $865 | 13 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 0.93 | $554 | $800 | 23 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 1.74 | $1,349 | $904 | 18 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 2.59 | $2,208 | $537 | 13 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 3.83 | $3,106 | $847 | 19 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 4.13 | $3,088 | $128 | 15 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=up, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 3.64 | $2,416 | $-444 | 7 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=5, allow_regimes=range, vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9 | 2.42 | $2,822 | $98 | 20 |

## orb_vix_on_stack

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'vix_min': 12.0, 'vix_max': 30.0, 'on_range_min_ratio': 0.0, 'on_range_max_ratio': 2.0, 'allow_regimes': '', 'pivot_n': 3}`
- Fold+: 89%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=12.0, vix_max=25.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=up,range, pivot_n=3 | 0.49 | $360 | $1,148 | 41 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=25.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=, pivot_n=3 | 1.55 | $2,044 | $-1,189 | 21 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=25.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=up,range, pivot_n=3 | 1.46 | $1,650 | $1,344 | 20 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=25.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=up,range, pivot_n=3 | 2.22 | $2,825 | $614 | 43 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=25.0, on_range_min_ratio=0.0, on_range_max_ratio=1.2, allow_regimes=up,range, pivot_n=3 | 2.42 | $3,152 | $794 | 39 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=, pivot_n=3 | 2.10 | $5,383 | $317 | 53 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=, pivot_n=3 | 2.83 | $6,156 | $1,061 | 49 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=, pivot_n=3 | 1.85 | $4,441 | $2,556 | 43 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=12.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes=, pivot_n=3 | 2.54 | $5,798 | $1,547 | 47 |

## orb_on_context

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'vix_min': 0.0, 'vix_max': '1.0e9', 'on_range_min_ratio': 0.0, 'on_range_max_ratio': 2.0, 'allow_regimes': ''}`
- Fold+: 78%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes= | -0.30 | $-465 | $1,012 | 59 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.25, on_range_max_ratio=2.0, allow_regimes= | 0.35 | $637 | $-581 | 46 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.25, on_range_max_ratio=0.8, allow_regimes= | 0.32 | $483 | $1,279 | 49 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes= | 1.45 | $3,770 | $737 | 55 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=0.8, allow_regimes= | 1.76 | $3,477 | $881 | 41 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=0.8, allow_regimes= | 1.70 | $3,452 | $-68 | 32 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes= | 2.36 | $5,419 | $1,483 | 50 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes= | 2.00 | $4,295 | $2,868 | 47 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=1.0e9, on_range_min_ratio=0.0, on_range_max_ratio=2.0, allow_regimes= | 2.57 | $6,427 | $1,547 | 47 |

## orb_vix_band

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'vix_min': 12.0, 'vix_max': 30.0, 'on_range_min_ratio': 0.0, 'on_range_max_ratio': '1.0e9', 'allow_regimes': ''}`
- Fold+: 89%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=14.0, vix_max=20.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | -0.00 | $-0 | $621 | 49 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=14.0, vix_max=20.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 0.81 | $466 | $-1,420 | 8 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=25.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | -0.40 | $-590 | $1,649 | 25 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 1.64 | $3,630 | $737 | 55 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 1.72 | $3,950 | $1,243 | 54 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 1.82 | $4,181 | $832 | 53 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=20.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 3.12 | $3,922 | $190 | 39 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=0.0, vix_max=20.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 2.21 | $3,831 | $271 | 27 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], vix_min=12.0, vix_max=30.0, on_range_min_ratio=0.0, on_range_max_ratio=1.0e9, allow_regimes= | 2.54 | $5,798 | $1,547 | 47 |


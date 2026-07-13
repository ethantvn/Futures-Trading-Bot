# Phase 16 Walk-Forward

## overnight_fade

- Params: `{'mode': 'fade', 'stop_atr': 1.75, 'target_r': 1.5, 'expire_minutes': 120, 'require_pdh_confluence': False, 'tick': 0.25, 'entry_start_minute': 575, 'entry_end_minute': 720}`
- Fold+: 100%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=60, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 4.61 | $5,488 | $1,809 | 80 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=60, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 5.39 | $7,187 | $4,125 | 70 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=60, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 5.14 | $9,433 | $5,116 | 84 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=60, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 6.27 | $13,242 | $3,906 | 69 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=60, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 7.22 | $14,956 | $2,893 | 83 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=120, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 8.01 | $13,478 | $1,757 | 87 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=120, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 7.99 | $14,772 | $3,207 | 83 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=120, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 7.32 | $12,974 | $1,779 | 63 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=120, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | 4.75 | $10,869 | $3,514 | 78 |

## structure_gated_orb

- Params: `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'pivot_n': 2, 'allow_regimes': 'up'}`
- Fold+: 78%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=range | 0.90 | $715 | $686 | 30 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=range | 1.91 | $1,865 | $1,116 | 21 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=range | 2.45 | $2,980 | $-430 | 25 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=3, allow_regimes=up | 2.27 | $1,812 | $897 | 18 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=range | 2.23 | $3,072 | $-621 | 27 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=3, allow_regimes=up | 2.36 | $2,110 | $747 | 13 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=up | 5.98 | $3,473 | $1,923 | 15 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=up | 6.68 | $4,310 | $1,039 | 13 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], pivot_n=2, allow_regimes=up | 5.47 | $4,784 | $480 | 7 |

## mes_agree_orb

- Params: `{'mes_mode': 'agree', 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [], 'mes_path': 'data/processed/mes/continuous_5m.parquet'}`
- Fold+: 78%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mes_mode=agree, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.49 | $1,869 | $1,129 | 41 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mes_mode=agree, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[], mes_path=data/processed/mes/continuous_5m.parquet | 2.08 | $3,811 | $-893 | 35 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mes_mode=agree, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.13 | $1,963 | $2,259 | 41 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mes_mode=agree, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 2.19 | $4,323 | $1,049 | 31 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mes_mode=agree, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 2.02 | $3,903 | $602 | 42 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mes_mode=agree, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.71 | $3,376 | $-124 | 32 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mes_mode=agree, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 2.20 | $3,407 | $699 | 39 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mes_mode=agree, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.25 | $1,917 | $3,135 | 33 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mes_mode=agree, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[], mes_path=data/processed/mes/continuous_5m.parquet | 2.76 | $5,951 | $763 | 43 |

## mes_diverge_orb

- Params: `{'mes_mode': 'diverge', 'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'mes_path': 'data/processed/mes/continuous_5m.parquet'}`
- Fold+: 78%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mes_mode=diverge, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=False, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | -0.38 | $-463 | $1,606 | 34 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mes_mode=diverge, range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=False, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 0.70 | $952 | $1,178 | 39 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=False, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.34 | $2,087 | $-756 | 38 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=False, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 0.96 | $1,660 | $494 | 43 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.45 | $1,361 | $662 | 11 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 1.69 | $1,499 | $500 | 21 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 3.07 | $2,293 | $784 | 11 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 4.20 | $2,528 | $-267 | 14 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mes_mode=diverge, range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], mes_path=data/processed/mes/continuous_5m.parquet | 2.50 | $1,680 | $790 | 16 |

## round_break

- Params: `{'mode': 'break', 'round_step': 100.0, 'stop_atr': 1.75, 'target_r': 1.5, 'expire_minutes': 90, 'entry_end_minute': 660, 'tick': 0.25}`
- Fold+: 44%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=break, round_step=100.0, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | -0.41 | $-813 | $-146 | 188 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=break, round_step=100.0, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | -0.15 | $-349 | $-327 | 253 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=break, round_step=100.0, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | -0.15 | $-434 | $289 | 244 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=break, round_step=100.0, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | 0.16 | $512 | $-469 | 216 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=break, round_step=100.0, stop_atr=1.75, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | 0.24 | $1,126 | $354 | 213 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=break, round_step=100.0, stop_atr=1.75, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | 0.28 | $1,352 | $-54 | 204 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=break, round_step=50.0, stop_atr=1.75, target_r=1.0, expire_minutes=90, entry_end_minute=660, tick=0.25 | 0.31 | $1,026 | $1,954 | 258 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=break, round_step=50.0, stop_atr=1.75, target_r=1.0, expire_minutes=45, entry_end_minute=660, tick=0.25 | 0.56 | $1,918 | $-1,041 | 252 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=break, round_step=100.0, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_end_minute=660, tick=0.25 | 0.39 | $1,854 | $2,148 | 237 |

## round_fade

- Params: `{'mode': 'fade', 'round_step': 50.0, 'stop_atr': 1.5, 'target_r': 1.0, 'expire_minutes': 45, 'entry_end_minute': 660, 'tick': 0.25}`
- Fold+: 44%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | 1.07 | $1,136 | $-55 | 50 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.5, expire_minutes=45, entry_end_minute=660, tick=0.25 | 0.59 | $668 | $1,504 | 54 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=45, entry_end_minute=660, tick=0.25 | 1.66 | $1,781 | $-122 | 55 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=45, entry_end_minute=660, tick=0.25 | 1.85 | $2,146 | $-334 | 57 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=45, entry_end_minute=660, tick=0.25 | 1.19 | $1,343 | $-490 | 71 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=90, entry_end_minute=660, tick=0.25 | 0.57 | $688 | $608 | 68 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=90, entry_end_minute=660, tick=0.25 | -0.29 | $-320 | $679 | 49 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=90, entry_end_minute=660, tick=0.25 | 0.45 | $480 | $1,393 | 49 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=fade, round_step=50.0, stop_atr=1.5, target_r=1.0, expire_minutes=45, entry_end_minute=660, tick=0.25 | 1.96 | $2,242 | $-294 | 54 |

## structure_gated_vwap

- Params: `{'mode': 'pullback', 'pivot_n': 3, 'band_atr': 0.75, 'stop_atr': 1.75, 'target_r': 1.5, 'expire_minutes': 90, 'entry_start_minute': 600, 'entry_end_minute': 900}`
- Fold+: 56%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | 0.52 | $731 | $427 | 117 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | 0.82 | $1,267 | $-1,929 | 112 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.25, target_r=1.5, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | -0.07 | $-121 | $1,270 | 106 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.25, target_r=1.0, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | 0.15 | $242 | $-596 | 126 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | 0.14 | $365 | $1,501 | 130 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.75, target_r=1.5, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | 0.68 | $1,896 | $605 | 128 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=reversion, pivot_n=3, band_atr=0.75, stop_atr=1.75, target_r=1.0, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | 1.12 | $2,439 | $-883 | 122 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=pullback, pivot_n=3, band_atr=0.75, stop_atr=1.75, target_r=1.0, expire_minutes=45, entry_start_minute=600, entry_end_minute=900 | 1.36 | $1,062 | $584 | 46 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=pullback, pivot_n=3, band_atr=0.75, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | 2.20 | $2,768 | $-736 | 32 |

## prior_day_fade

- Params: `{'mode': 'fade', 'stop_atr': 1.75, 'target_r': 1.5, 'expire_minutes': 150, 'structure_gate': True, 'allow_regimes': 'range', 'tick': 0.25}`
- Fold+: 44%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=fade, stop_atr=1.25, target_r=1.5, expire_minutes=90, structure_gate=True, allow_regimes=range, tick=0.25 | 0.74 | $534 | $-236 | 78 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=90, structure_gate=True, allow_regimes=range, tick=0.25 | 0.13 | $127 | $-943 | 70 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=fade, stop_atr=1.25, target_r=1.5, expire_minutes=90, structure_gate=True, allow_regimes=range, tick=0.25 | 0.03 | $30 | $393 | 60 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=fade, stop_atr=1.25, target_r=1.5, expire_minutes=150, structure_gate=False, allow_regimes=range, tick=0.25 | 0.70 | $1,469 | $150 | 111 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=fade, stop_atr=1.25, target_r=1.5, expire_minutes=150, structure_gate=False, allow_regimes=range, tick=0.25 | 0.85 | $1,783 | $-522 | 117 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=fade, stop_atr=1.25, target_r=1.5, expire_minutes=150, structure_gate=False, allow_regimes=range, tick=0.25 | 0.80 | $1,688 | $-367 | 122 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=150, structure_gate=False, allow_regimes=range, tick=0.25 | 1.32 | $2,929 | $1,752 | 120 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=150, structure_gate=False, allow_regimes=range, tick=0.25 | 1.53 | $3,399 | $97 | 105 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=150, structure_gate=True, allow_regimes=range, tick=0.25 | 1.58 | $2,867 | $-404 | 68 |

## poc_reversion

- Params: `{'mode': 'reversion', 'bin_size': 5.0, 'stop_atr': 1.5, 'target_r': 1.0, 'expire_minutes': 120, 'entry_start_minute': 600, 'entry_end_minute': 900}`
- Fold+: 11%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=reversion, bin_size=10.0, stop_atr=1.5, target_r=1.0, expire_minutes=60, entry_start_minute=600, entry_end_minute=900 | -1.48 | $-3,636 | $-987 | 252 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=reversion, bin_size=10.0, stop_atr=1.5, target_r=1.0, expire_minutes=120, entry_start_minute=600, entry_end_minute=900 | -1.27 | $-3,473 | $-1,930 | 246 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=reversion, bin_size=5.0, stop_atr=1.0, target_r=1.0, expire_minutes=60, entry_start_minute=600, entry_end_minute=900 | -0.95 | $-2,491 | $-1,076 | 251 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=reversion, bin_size=20.0, stop_atr=1.0, target_r=1.0, expire_minutes=120, entry_start_minute=600, entry_end_minute=900 | -0.44 | $-1,152 | $-616 | 249 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=reversion, bin_size=20.0, stop_atr=1.0, target_r=1.0, expire_minutes=120, entry_start_minute=600, entry_end_minute=900 | -0.36 | $-957 | $-1,205 | 251 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=reversion, bin_size=5.0, stop_atr=1.0, target_r=1.0, expire_minutes=60, entry_start_minute=600, entry_end_minute=900 | -0.15 | $-418 | $-343 | 247 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=reversion, bin_size=5.0, stop_atr=1.5, target_r=1.0, expire_minutes=60, entry_start_minute=600, entry_end_minute=900 | -0.82 | $-2,529 | $-1,252 | 246 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=reversion, bin_size=5.0, stop_atr=1.5, target_r=1.0, expire_minutes=60, entry_start_minute=600, entry_end_minute=900 | -0.80 | $-2,444 | $584 | 243 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=reversion, bin_size=5.0, stop_atr=1.5, target_r=1.0, expire_minutes=120, entry_start_minute=600, entry_end_minute=900 | -0.27 | $-1,060 | $-720 | 249 |

## prior_day_break

- Params: `{'mode': 'break', 'stop_atr': 1.75, 'target_r': 2.0, 'expire_minutes': 120, 'structure_gate': True, 'allow_regimes': 'up,range', 'tick': 0.25}`
- Fold+: 33%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=180, structure_gate=False, allow_regimes=up,range, tick=0.25 | -0.35 | $-410 | $-343 | 108 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=180, structure_gate=False, allow_regimes=up,range, tick=0.25 | -0.39 | $-499 | $151 | 106 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=180, structure_gate=False, allow_regimes=up,range, tick=0.25 | 0.27 | $430 | $-1,136 | 106 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=120, structure_gate=False, allow_regimes=up,range, tick=0.25 | -0.84 | $-1,399 | $-204 | 100 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=120, structure_gate=False, allow_regimes=up,range, tick=0.25 | -0.84 | $-1,408 | $-1,007 | 100 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=180, structure_gate=True, allow_regimes=up,range, tick=0.25 | -1.05 | $-2,146 | $108 | 104 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=break, stop_atr=1.75, target_r=2.0, expire_minutes=180, structure_gate=False, allow_regimes=up,range, tick=0.25 | -0.81 | $-1,753 | $-1,236 | 100 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=break, stop_atr=1.75, target_r=2.0, expire_minutes=120, structure_gate=True, allow_regimes=up,range, tick=0.25 | -0.32 | $-721 | $628 | 105 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=break, stop_atr=1.75, target_r=2.0, expire_minutes=120, structure_gate=True, allow_regimes=up,range, tick=0.25 | 0.01 | $41 | $-1,102 | 105 |

## poc_breakout

- Params: `{'mode': 'breakout', 'bin_size': 20.0, 'stop_atr': 1.25, 'target_r': 1.0, 'expire_minutes': 90, 'entry_start_minute': 600, 'entry_end_minute': 900}`
- Fold+: 11%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=breakout, bin_size=20.0, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.98 | $-1,450 | $-674 | 131 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=breakout, bin_size=20.0, stop_atr=1.25, target_r=2.0, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -1.15 | $-2,488 | $841 | 126 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=breakout, bin_size=20.0, stop_atr=1.25, target_r=1.5, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.14 | $-318 | $-1,751 | 130 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=breakout, bin_size=10.0, stop_atr=1.25, target_r=1.5, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.54 | $-1,576 | $-523 | 127 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=breakout, bin_size=10.0, stop_atr=1.25, target_r=1.5, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.06 | $-177 | $-1,211 | 129 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=breakout, bin_size=20.0, stop_atr=1.25, target_r=1.5, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | 0.17 | $433 | $-461 | 127 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=breakout, bin_size=10.0, stop_atr=1.25, target_r=2.0, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.07 | $-181 | $-910 | 129 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=breakout, bin_size=20.0, stop_atr=1.25, target_r=2.0, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.34 | $-801 | $-1,534 | 126 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=breakout, bin_size=20.0, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_start_minute=600, entry_end_minute=900 | -0.43 | $-899 | $-943 | 130 |

## overnight_break

- Params: `{'mode': 'break', 'stop_atr': 1.25, 'target_r': 1.0, 'expire_minutes': 90, 'require_pdh_confluence': False, 'tick': 0.25, 'entry_start_minute': 575, 'entry_end_minute': 720}`
- Fold+: 11%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -4.22 | $-3,057 | $-1,196 | 68 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -4.96 | $-4,039 | $-2,375 | 58 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -5.61 | $-5,495 | $-2,045 | 67 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -6.11 | $-6,538 | $-1,086 | 57 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -6.30 | $-6,702 | $-893 | 61 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -5.99 | $-6,399 | $-556 | 57 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -4.81 | $-4,580 | $-543 | 66 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -3.30 | $-3,079 | $955 | 54 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, require_pdh_confluence=False, tick=0.25, entry_start_minute=575, entry_end_minute=720 | -0.96 | $-1,038 | $-1,713 | 70 |


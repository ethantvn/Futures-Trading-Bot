# Phase 18 Walk-Forward

## orb_w_control

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'skip_macro_days': False}`
- Fold+: 78%
- Pass: 63.8%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 0.28 | $438 | $-581 | 46 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | -1.72 | $10 | $2,895 | 62 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 3.69 | $4,058 | $737 | 55 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 3.53 | $4,063 | $1,243 | 54 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 3.88 | $4,294 | $832 | 53 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 18.07 | $5,707 | $1,483 | 50 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 12.72 | $4,295 | $2,868 | 47 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=False | 21.85 | $6,427 | $1,547 | 47 |

## orb_tod

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'trade_window': 'midday'}`
- Fold+: 78%
- Pass: 59.2%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=90, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=last90 | 2.63 | $458 | $247 | 45 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=90, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=last90 | 7.83 | $1,312 | $-245 | 39 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=90, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=midday | 10.27 | $2,794 | $2,126 | 51 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=midday | 18.67 | $5,528 | $1,924 | 45 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=midday | 23.72 | $6,552 | $928 | 52 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=midday | 19.20 | $5,698 | $-420 | 46 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=full | 20.49 | $6,174 | $1,205 | 50 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=midday | 15.72 | $3,318 | $3,043 | 46 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], trade_window=midday | 24.12 | $5,296 | $831 | 47 |

## mes_diverge_orb

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'mes_mode': 'diverge', 'long_only': True, 'skip_weekdays': [1]}`
- Fold+: 78%
- Pass: 58.4%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=agree, long_only=True, skip_weekdays=[1] | 5.64 | $1,622 | $488 | 41 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=agree, long_only=True, skip_weekdays=[1] | 8.93 | $2,896 | $-534 | 28 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=agree, long_only=True, skip_weekdays=[1] | 3.15 | $1,963 | $2,259 | 41 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=agree, long_only=True, skip_weekdays=[1] | 9.36 | $4,323 | $1,049 | 31 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=diverge, long_only=True, skip_weekdays=[1] | 10.76 | $1,361 | $662 | 11 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=diverge, long_only=True, skip_weekdays=[1] | 12.41 | $1,499 | $500 | 21 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=agree, long_only=True, skip_weekdays=[1] | 22.70 | $3,785 | $531 | 39 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=diverge, long_only=True, skip_weekdays=[1] | 37.13 | $2,528 | $-267 | 14 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, mes_mode=diverge, long_only=True, skip_weekdays=[1] | 27.72 | $1,680 | $790 | 16 |

## orb_risk_cap

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'max_risk_points': 150}`
- Fold+: 78%
- Pass: 58.3%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=150 | 0.37 | $503 | $-950 | 46 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=250 | -1.72 | $10 | $2,895 | 62 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=250 | 3.69 | $4,058 | $737 | 55 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=250 | 3.53 | $4,063 | $1,243 | 54 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=250 | 3.88 | $4,294 | $832 | 53 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=150 | 18.34 | $5,773 | $1,432 | 50 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=150 | 13.44 | $4,244 | $1,629 | 47 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], max_risk_points=150 | 18.09 | $5,137 | $1,028 | 47 |

## orb_macro_skip

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'expire_minutes': 120, 'min_width_ratio': 0.25, 'max_width_ratio': 0.7, 'long_only': True, 'skip_weekdays': [1], 'skip_macro_days': True, 'macro_events': 'nfp'}`
- Fold+: 78%
- Pass: 56.9%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=all | 0.43 | $245 | $1,275 | 51 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=nfp | 3.55 | $1,949 | $-1,127 | 44 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=all | 8.29 | $3,100 | $2,449 | 51 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=all | 15.99 | $5,535 | $1,588 | 49 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=all | 17.61 | $6,342 | $1,239 | 46 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=all | 17.84 | $6,306 | $213 | 44 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=all | 20.68 | $5,490 | $-70 | 40 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=cpi | 11.49 | $4,192 | $2,480 | 43 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, expire_minutes=120, min_width_ratio=0.25, max_width_ratio=0.7, long_only=True, skip_weekdays=[1], skip_macro_days=True, macro_events=nfp | 22.46 | $6,180 | $1,742 | 46 |

## ema_trend

- Params: `{'ema_fast': 8, 'ema_slow': 21, 'ema_filter': 50, 'stop_atr': 1.5, 'target_r': 1.5, 'entry_start_minute': 600}`
- Fold+: 78%
- Pass: 32.6%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=2.0, target_r=2.5, entry_start_minute=600 | -0.67 | $3,528 | $1,859 | 179 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=2.0, target_r=2.5, entry_start_minute=600 | 2.06 | $5,919 | $316 | 181 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=2.0, target_r=2.5, entry_start_minute=600 | 1.52 | $5,861 | $1,413 | 180 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=1.5, target_r=2.5, entry_start_minute=600 | -0.82 | $3,222 | $-862 | 171 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=1.5, target_r=2.5, entry_start_minute=600 | 0.67 | $2,651 | $485 | 195 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=1.5, target_r=2.5, entry_start_minute=600 | -0.46 | $1,233 | $1,019 | 193 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=1.5, target_r=2.5, entry_start_minute=600 | 1.05 | $2,194 | $-2,433 | 175 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=1.5, target_r=1.5, entry_start_minute=600 | 0.02 | $29 | $1,439 | 168 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | ema_fast=8, ema_slow=21, ema_filter=50, stop_atr=1.5, target_r=1.5, entry_start_minute=600 | 1.69 | $2,166 | $2,561 | 175 |

## roc_vol_mom

- Params: `{'roc_n': 10, 'roc_thresh': 0.2, 'vol_mult': 1.25, 'stop_atr': 1.25, 'target_r': 1.5, 'expire_minutes': 60, 'skip_weekdays': [1]}`
- Fold+: 56%
- Pass: 26.1%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | roc_n=10, roc_thresh=0.2, vol_mult=1.25, stop_atr=1.25, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 3.73 | $2,173 | $487 | 145 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | roc_n=10, roc_thresh=0.2, vol_mult=1.25, stop_atr=1.75, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 5.76 | $5,504 | $-1,225 | 169 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | roc_n=10, roc_thresh=0.2, vol_mult=1.25, stop_atr=1.25, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | -1.04 | $561 | $-217 | 178 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | roc_n=10, roc_thresh=0.2, vol_mult=1.25, stop_atr=1.75, target_r=1.0, expire_minutes=60, skip_weekdays=[1] | -1.48 | $2,009 | $1,048 | 180 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | roc_n=5, roc_thresh=0.1, vol_mult=1.75, stop_atr=1.75, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 2.18 | $2,479 | $-907 | 114 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | roc_n=5, roc_thresh=0.1, vol_mult=1.75, stop_atr=1.75, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 0.14 | $733 | $334 | 112 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | roc_n=5, roc_thresh=0.1, vol_mult=1.25, stop_atr=1.75, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 1.90 | $2,333 | $1,663 | 189 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | roc_n=10, roc_thresh=0.1, vol_mult=1.75, stop_atr=1.25, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 2.66 | $2,041 | $-1,149 | 109 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | roc_n=10, roc_thresh=0.2, vol_mult=1.25, stop_atr=1.25, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 1.68 | $2,016 | $1,411 | 147 |

## prior_day_fade

- Params: `{'mode': 'fade', 'stop_atr': 1.75, 'target_r': 1.5, 'expire_minutes': 90, 'entry_end_minute': 840, 'structure_gate': False}`
- Fold+: 56%
- Pass: 20.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=90, entry_end_minute=840, structure_gate=False | 3.57 | $1,087 | $22 | 75 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=90, entry_end_minute=840, structure_gate=False | 3.48 | $1,174 | $987 | 77 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=180, entry_end_minute=840, structure_gate=False | 4.32 | $1,758 | $1,317 | 72 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=180, entry_end_minute=840, structure_gate=False | 5.03 | $2,620 | $401 | 67 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=90, entry_end_minute=840, structure_gate=False | 4.20 | $2,912 | $-559 | 72 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=180, entry_end_minute=840, structure_gate=False | 4.47 | $3,073 | $-7 | 74 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_end_minute=840, structure_gate=False | 4.48 | $2,543 | $1,888 | 77 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_end_minute=840, structure_gate=False | 5.49 | $2,388 | $-340 | 65 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_end_minute=840, structure_gate=False | 3.30 | $1,690 | $-954 | 72 |

## macd_mom

- Params: `{'fast': 12, 'slow': 26, 'signal': 9, 'stop_atr': 1.75, 'target_r': 1.5, 'expire_minutes': 60, 'skip_weekdays': [1]}`
- Fold+: 11%
- Pass: 15.5%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | fast=12, slow=26, signal=9, stop_atr=1.75, target_r=2.0, expire_minutes=120, skip_weekdays=[1] | -1.10 | $2,139 | $-468 | 184 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | fast=12, slow=26, signal=9, stop_atr=1.75, target_r=2.0, expire_minutes=120, skip_weekdays=[1] | -4.09 | $1,841 | $-412 | 187 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | — | — | $0 | $0 | 0 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | fast=12, slow=26, signal=9, stop_atr=1.75, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 0.25 | $371 | $242 | 189 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | fast=12, slow=26, signal=9, stop_atr=1.75, target_r=1.5, expire_minutes=60, skip_weekdays=[1] | 0.61 | $1,033 | $-3,220 | 188 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## vwap_reversion

- Params: `{'band_k': 2.5, 'stop_atr': 1.5, 'target_r': 1.0, 'adx_max': 20.0, 'expire_minutes': 45, 'skip_weekdays': [1], 'long_only': False}`
- Fold+: 56%
- Pass: 15.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | band_k=2.5, stop_atr=1.0, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 2.46 | $850 | $-288 | 48 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | band_k=2.5, stop_atr=1.0, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 0.28 | $455 | $352 | 61 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | band_k=2.0, stop_atr=1.0, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 0.60 | $1,105 | $459 | 70 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | band_k=2.0, stop_atr=1.0, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 5.31 | $1,514 | $-576 | 79 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | band_k=2.0, stop_atr=1.5, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 1.77 | $1,015 | $264 | 88 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | band_k=2.0, stop_atr=1.5, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 3.76 | $2,051 | $20 | 83 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | band_k=2.0, stop_atr=1.5, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | -0.48 | $735 | $99 | 88 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | band_k=2.5, stop_atr=1.5, target_r=1.0, adx_max=20.0, expire_minutes=45, skip_weekdays=[1], long_only=False | 0.69 | $950 | $-855 | 61 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## stoch_fade

- Params: `{'use_stoch': True, 'stoch_k': 14, 'stoch_d': 3, 'stoch_ob': 80, 'stoch_os': 20, 'stop_atr': 1.25, 'target_r': 1.0, 'adx_max': 25.0, 'expire_minutes': 60, 'skip_weekdays': [1]}`
- Fold+: 22%
- Pass: 14.7%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | use_stoch=True, stoch_k=14, stoch_d=3, stoch_ob=80, stoch_os=20, stop_atr=1.75, target_r=1.5, adx_max=25.0, expire_minutes=60, skip_weekdays=[1] | 0.30 | $676 | $2,664 | 144 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | use_stoch=True, stoch_k=14, stoch_d=3, stoch_ob=80, stoch_os=20, stop_atr=1.75, target_r=1.5, adx_max=25.0, expire_minutes=60, skip_weekdays=[1] | 2.96 | $3,024 | $-2,763 | 140 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | use_stoch=True, stoch_k=14, stoch_d=3, stoch_ob=80, stoch_os=20, stop_atr=1.75, target_r=1.5, adx_max=25.0, expire_minutes=60, skip_weekdays=[1] | -4.36 | $40 | $475 | 128 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | use_stoch=True, stoch_k=14, stoch_d=3, stoch_ob=80, stoch_os=20, stop_atr=1.25, target_r=1.5, adx_max=25.0, expire_minutes=60, skip_weekdays=[1] | -3.00 | $152 | $-441 | 156 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | use_stoch=True, stoch_k=14, stoch_d=3, stoch_ob=80, stoch_os=20, stop_atr=1.25, target_r=1.5, adx_max=25.0, expire_minutes=60, skip_weekdays=[1] | -3.03 | $96 | $-1,125 | 163 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | use_stoch=True, stoch_k=14, stoch_d=3, stoch_ob=80, stoch_os=20, stop_atr=1.25, target_r=1.0, adx_max=25.0, expire_minutes=60, skip_weekdays=[1] | -3.19 | $57 | $-2,047 | 148 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## donchian

- Params: `{'channel_n': 40, 'stop_atr': 1.25, 'target_r': 1.0, 'adx_min': 0.0, 'expire_minutes': 120, 'skip_weekdays': [1], 'long_only': False}`
- Fold+: 22%
- Pass: 6.6%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | — | — | $0 | $0 | 0 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | channel_n=40, stop_atr=1.75, target_r=2.0, adx_min=0.0, expire_minutes=120, skip_weekdays=[1], long_only=True | 3.91 | $2,071 | $20 | 97 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | channel_n=20, stop_atr=1.75, target_r=2.0, adx_min=0.0, expire_minutes=120, skip_weekdays=[1], long_only=True | 4.07 | $3,324 | $267 | 145 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | channel_n=20, stop_atr=1.75, target_r=2.0, adx_min=20.0, expire_minutes=120, skip_weekdays=[1], long_only=False | 7.44 | $7,078 | $-1,499 | 172 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | channel_n=20, stop_atr=1.75, target_r=2.0, adx_min=20.0, expire_minutes=120, skip_weekdays=[1], long_only=True | 4.42 | $3,002 | $-630 | 116 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | channel_n=20, stop_atr=1.75, target_r=2.0, adx_min=20.0, expire_minutes=120, skip_weekdays=[1], long_only=True | 0.51 | $507 | $-1,174 | 104 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | channel_n=40, stop_atr=1.25, target_r=1.0, adx_min=0.0, expire_minutes=120, skip_weekdays=[1], long_only=False | 1.41 | $1,845 | $-3,338 | 187 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## overnight_fade

- Params: `{'mode': 'fade', 'stop_atr': 1.25, 'target_r': 1.0, 'expire_minutes': 90, 'entry_end_minute': 720}`
- Fold+: 67%
- Pass: 5.5%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | mode=fade, stop_atr=1.75, target_r=1.5, expire_minutes=90, entry_end_minute=720 | -0.04 | $324 | $837 | 87 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | mode=fade, stop_atr=1.75, target_r=1.0, expire_minutes=90, entry_end_minute=720 | 1.67 | $1,180 | $136 | 87 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=fade, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_end_minute=720 | 1.82 | $944 | $853 | 94 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | mode=fade, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_end_minute=720 | 5.41 | $2,356 | $127 | 74 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | mode=fade, stop_atr=1.25, target_r=1.0, expire_minutes=120, entry_end_minute=720 | 5.65 | $2,466 | $-125 | 87 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | mode=fade, stop_atr=1.25, target_r=1.0, expire_minutes=120, entry_end_minute=720 | 4.22 | $1,930 | $319 | 88 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | mode=fade, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_end_minute=720 | 3.56 | $1,243 | $826 | 81 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | mode=fade, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_end_minute=720 | 3.60 | $1,216 | $-2,735 | 74 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## bollinger_mr

- Params: `{'bb_n': 20, 'bb_k': 2.5, 'adx_max': 15.0, 'stop_atr': 1.0, 'entry_start_minute': 600}`
- Fold+: 11%
- Pass: 3.3%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | bb_n=20, bb_k=2.5, adx_max=15.0, stop_atr=2.0, entry_start_minute=600 | 2.77 | $81 | $-46 | 17 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | bb_n=20, bb_k=2.5, adx_max=15.0, stop_atr=2.0, entry_start_minute=600 | 1.78 | $55 | $-1,286 | 24 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | — | — | $0 | $0 | 0 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | bb_n=20, bb_k=2.0, adx_max=15.0, stop_atr=1.5, entry_start_minute=600 | 0.65 | $474 | $-110 | 47 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | bb_n=20, bb_k=2.5, adx_max=15.0, stop_atr=1.5, entry_start_minute=600 | 31.18 | $840 | $-474 | 12 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | bb_n=20, bb_k=2.0, adx_max=15.0, stop_atr=2.0, entry_start_minute=600 | 2.06 | $386 | $-49 | 48 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | bb_n=20, bb_k=2.5, adx_max=15.0, stop_atr=1.0, entry_start_minute=600 | 7.86 | $351 | $184 | 17 |

## rsi_fade

- Params: `{'rsi_n': 14, 'rsi_ob': 80, 'rsi_os': 30, 'stop_atr': 1.75, 'target_r': 1.5, 'adx_max': 30.0, 'expire_minutes': 60, 'use_stoch': False, 'skip_weekdays': [1]}`
- Fold+: 0%
- Pass: 1.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | rsi_n=14, rsi_ob=70, rsi_os=20, stop_atr=1.75, target_r=1.0, adx_max=30.0, expire_minutes=60, use_stoch=False, skip_weekdays=[1] | 1.23 | $88 | $-396 | 18 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | rsi_n=14, rsi_ob=80, rsi_os=30, stop_atr=1.25, target_r=1.5, adx_max=30.0, expire_minutes=60, use_stoch=False, skip_weekdays=[1] | 8.68 | $343 | $-399 | 16 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | rsi_n=14, rsi_ob=80, rsi_os=30, stop_atr=1.25, target_r=1.0, adx_max=30.0, expire_minutes=60, use_stoch=False, skip_weekdays=[1] | 1.20 | $62 | $-19 | 7 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | rsi_n=14, rsi_ob=70, rsi_os=20, stop_atr=1.25, target_r=1.5, adx_max=30.0, expire_minutes=60, use_stoch=False, skip_weekdays=[1] | 10.18 | $751 | $-240 | 29 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | rsi_n=14, rsi_ob=80, rsi_os=30, stop_atr=1.75, target_r=1.5, adx_max=30.0, expire_minutes=60, use_stoch=False, skip_weekdays=[1] | 37.00 | $1,681 | $-47 | 18 |

## overnight_break

- Params: `{'mode': 'break', 'stop_atr': 1.25, 'target_r': 1.0, 'expire_minutes': 90, 'entry_end_minute': 720}`
- Fold+: 11%
- Pass: 0.7%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | — | — | $0 | $0 | 0 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | — | — | $0 | $0 | 0 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | mode=break, stop_atr=1.25, target_r=1.0, expire_minutes=90, entry_end_minute=720 | -0.09 | $523 | $352 | 98 |

## orb_fade

- Params: `{'range_minutes': 30, 'target_r': 1.0, 'stop_buffer_ticks': 2, 'expire_minutes': 60, 'long_only': True, 'skip_weekdays': [1], 'entry_end_minute': 840}`
- Fold+: 22%
- Pass: 0.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=30, target_r=1.5, stop_buffer_ticks=2, expire_minutes=60, long_only=True, skip_weekdays=[1], entry_end_minute=840 | -7.16 | $-1,165 | $-397 | 54 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=30, target_r=1.5, stop_buffer_ticks=4, expire_minutes=60, long_only=True, skip_weekdays=[1], entry_end_minute=840 | -8.62 | $-1,395 | $-230 | 60 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=15, target_r=1.5, stop_buffer_ticks=4, expire_minutes=60, long_only=False, skip_weekdays=[1], entry_end_minute=840 | -7.29 | $-1,404 | $22 | 86 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=15, target_r=1.5, stop_buffer_ticks=4, expire_minutes=60, long_only=False, skip_weekdays=[1], entry_end_minute=840 | -6.99 | $-1,222 | $-115 | 89 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=15, target_r=1.5, stop_buffer_ticks=4, expire_minutes=60, long_only=False, skip_weekdays=[1], entry_end_minute=840 | -6.98 | $-778 | $-95 | 89 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=30, target_r=1.0, stop_buffer_ticks=2, expire_minutes=60, long_only=True, skip_weekdays=[1], entry_end_minute=840 | -6.66 | $-450 | $-203 | 58 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=1.0, stop_buffer_ticks=2, expire_minutes=60, long_only=False, skip_weekdays=[1], entry_end_minute=840 | -7.69 | $-1,137 | $-576 | 82 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.0, stop_buffer_ticks=2, expire_minutes=60, long_only=True, skip_weekdays=[1], entry_end_minute=840 | -8.11 | $-485 | $-424 | 50 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.0, stop_buffer_ticks=2, expire_minutes=60, long_only=True, skip_weekdays=[1], entry_end_minute=840 | -8.23 | $-859 | $107 | 59 |

## prior_day_break

- Params: `{'mode': 'break', 'stop_atr': 1.75, 'target_r': 1.0, 'expire_minutes': 180, 'entry_end_minute': 840, 'structure_gate': False}`
- Fold+: 0%
- Pass: 0.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | — | — | $0 | $0 | 0 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | mode=break, stop_atr=1.75, target_r=1.0, expire_minutes=180, entry_end_minute=840, structure_gate=False | -2.20 | $430 | $-1,136 | 106 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |

## atr_breakout

- Params: `{}`
- Fold+: 0%
- Pass: 0.0%

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | — | — | $0 | $0 | 0 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | — | — | $0 | $0 | 0 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | — | — | $0 | $0 | 0 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | — | — | $0 | $0 | 0 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | — | — | $0 | $0 | 0 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | — | — | $0 | $0 | 0 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | — | — | $0 | $0 | 0 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | — | — | $0 | $0 | 0 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | — | — | $0 | $0 | 0 |


# Walk-Forward Validation

- Grid period: 2019-06-01 → 2025-12-31
- Folds: 24m train / 6m test (9 windows)
- Train selection: daily Sharpe (min 40 trades)

## opening_range_breakout — walk-forward

- Final selected params (last fold train window): `range_minutes=30, target_r=1.5, expire_minutes=120`
- Stitched OOS period: 2021-06-01 → 2025-11-28
- Stitched OOS trades: 993

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | range_minutes=45, target_r=3.0, expire_minutes=60 | 0.37 | $1,790 | $1,808 | 104 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | range_minutes=45, target_r=3.0, expire_minutes=60 | 0.61 | $3,122 | $4,629 | 108 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | range_minutes=45, target_r=3.0, expire_minutes=60 | 1.39 | $9,156 | $651 | 106 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | range_minutes=60, target_r=2.0, expire_minutes=60 | 1.54 | $9,333 | $435 | 106 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | range_minutes=60, target_r=2.0, expire_minutes=60 | 1.56 | $9,588 | $3,061 | 101 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | range_minutes=60, target_r=2.0, expire_minutes=60 | 1.65 | $10,346 | $-255 | 91 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | range_minutes=30, target_r=2.5, expire_minutes=120 | 1.66 | $10,783 | $2,718 | 129 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | range_minutes=30, target_r=1.5, expire_minutes=60 | 1.76 | $9,974 | $5,286 | 122 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | range_minutes=30, target_r=1.5, expire_minutes=120 | 1.88 | $14,386 | $46 | 126 |

## opening_range_breakout (WF OOS)

| Metric | Value |
| --- | --- |
| n_trades | 993 |
| net_pnl | $18,377.36 |
| gross_pnl | $20,343.50 |
| total_costs | $1,966.14 |
| win_rate | 50.76% |
| avg_win | $214.65 |
| avg_loss | $-183.65 |
| expectancy | $18.51 |
| profit_factor | 1.20 |
| max_consecutive_losses | 6 |
| max_drawdown | $-3,457.56 |
| n_active_days | 993 |
| best_day | $1,868.02 |
| worst_day | $-661.48 |
| sharpe_daily | 1.16 |
| sortino_daily | 2.52 |
| trades_per_day | 1.00 |
| avg_hold_minutes | 251 |
| time_in_market_pct | 18.17% |
| pct_ambiguous_trades | 0.00% |
| exit_reasons | {'stop': 306, 'session_end': 29, 'eod': 572, 'target': 86} |


## ema_trend — walk-forward

- Final selected params (last fold train window): `ema_fast=9, ema_slow=21, stop_atr=1.5, target_r=3.0`
- Stitched OOS period: 2021-06-01 → 2025-11-27
- Stitched OOS trades: 1999

| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2019-06-01→2021-05-31 | 2021-06-01→2021-11-30 | ema_fast=9, ema_slow=21, stop_atr=2.5, target_r=2.0 | 0.96 | $3,847 | $1,434 | 230 |
| 2 | 2019-12-01→2021-11-30 | 2021-12-01→2022-05-31 | ema_fast=9, ema_slow=21, stop_atr=2.5, target_r=2.0 | 1.36 | $5,844 | $1,356 | 225 |
| 3 | 2020-06-01→2022-05-31 | 2022-06-01→2022-11-30 | ema_fast=9, ema_slow=21, stop_atr=1.5, target_r=3.0 | 1.37 | $6,401 | $1,738 | 223 |
| 4 | 2020-12-01→2022-11-30 | 2022-12-01→2023-05-31 | ema_fast=5, ema_slow=21, stop_atr=2.5, target_r=2.0 | 1.51 | $7,915 | $-1,435 | 245 |
| 5 | 2021-06-01→2023-05-31 | 2023-06-01→2023-11-30 | ema_fast=12, ema_slow=21, stop_atr=1.5, target_r=3.0 | 1.11 | $5,210 | $-690 | 242 |
| 6 | 2021-12-01→2023-11-30 | 2023-12-01→2024-05-31 | ema_fast=12, ema_slow=21, stop_atr=1.5, target_r=3.0 | 0.69 | $3,320 | $-579 | 229 |
| 7 | 2022-06-01→2024-05-31 | 2024-06-01→2024-11-30 | ema_fast=9, ema_slow=21, stop_atr=1.5, target_r=3.0 | 0.22 | $928 | $-3,449 | 214 |
| 8 | 2022-12-01→2024-11-30 | 2024-12-01→2025-05-31 | ema_fast=12, ema_slow=34, stop_atr=1.5, target_r=3.0 | -0.34 | $-1,425 | $1,901 | 184 |
| 9 | 2023-06-01→2025-05-31 | 2025-06-01→2025-11-30 | ema_fast=9, ema_slow=21, stop_atr=1.5, target_r=3.0 | 0.70 | $3,630 | $1,114 | 207 |

## ema_trend (WF OOS)

| Metric | Value |
| --- | --- |
| n_trades | 1999 |
| net_pnl | $1,390.79 |
| gross_pnl | $5,348.81 |
| total_costs | $3,958.02 |
| win_rate | 32.42% |
| avg_win | $146.22 |
| avg_loss | $-69.10 |
| expectancy | $0.70 |
| profit_factor | 1.01 |
| max_consecutive_losses | 19 |
| max_drawdown | $-7,514.53 |
| n_active_days | 941 |
| best_day | $1,087.81 |
| worst_day | $-675.93 |
| sharpe_daily | 0.12 |
| sortino_daily | 0.23 |
| trades_per_day | 2.12 |
| avg_hold_minutes | 75 |
| time_in_market_pct | 11.60% |
| pct_ambiguous_trades | 0.05% |
| exit_reasons | {'signal': 864, 'stop': 591, 'session_end': 18, 'target': 249, 'eod': 277} |


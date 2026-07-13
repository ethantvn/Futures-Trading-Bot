# Baseline Backtest Report

- Period: 2019-05-29 -> 2025-12-31 (1705 trading days)
- Costs: $0.99/side/contract, slippage 1 tick(s); qty 1 micro(s)
- Fills on 1-minute bars; pessimistic same-bar policy (stop before target).

## opening_range_breakout

| Metric | Value |
| --- | --- |
| n_trades | 1625 |
| net_pnl | $17,615.50 |
| gross_pnl | $20,833.00 |
| total_costs | $3,217.50 |
| win_rate | 47.51% |
| avg_win | $198.81 |
| avg_loss | $-159.28 |
| expectancy | $10.84 |
| profit_factor | 1.13 |
| max_consecutive_losses | 10 |
| max_drawdown | $-6,133.02 |
| n_active_days | 1625 |
| best_day | $1,427.52 |
| worst_day | $-661.48 |
| sharpe_daily | 0.77 |
| sortino_daily | 1.57 |
| trades_per_day | 0.95 |
| avg_hold_minutes | 233 |
| time_in_market_pct | 16.12% |
| pct_ambiguous_trades | 0.06% |
| exit_reasons | {'stop': 618, 'session_end': 38, 'target': 207, 'eod': 762} |

Overfit-prone parameters: range_minutes, target_r, expire_minutes

## prev_day_hl_breakout

| Metric | Value |
| --- | --- |
| n_trades | 1446 |
| net_pnl | $-6,760.02 |
| gross_pnl | $-3,896.94 |
| total_costs | $2,863.08 |
| win_rate | 45.44% |
| avg_win | $85.81 |
| avg_loss | $-80.02 |
| expectancy | $-4.67 |
| profit_factor | 0.89 |
| max_consecutive_losses | 8 |
| max_drawdown | $-9,018.30 |
| n_active_days | 1446 |
| best_day | $979.54 |
| worst_day | $-552.03 |
| sharpe_daily | -0.67 |
| sortino_daily | -1.17 |
| trades_per_day | 0.85 |
| avg_hold_minutes | 38 |
| time_in_market_pct | 2.33% |
| pct_ambiguous_trades | 1.87% |
| exit_reasons | {'eod': 47, 'session_end': 7, 'stop': 614, 'target': 778} |

Overfit-prone parameters: stop_atr, target_r, expire_minutes

## vwap_pullback

| Metric | Value |
| --- | --- |
| n_trades | 1951 |
| net_pnl | $-9,559.45 |
| gross_pnl | $-5,696.47 |
| total_costs | $3,862.98 |
| win_rate | 31.16% |
| avg_win | $127.72 |
| avg_loss | $-64.94 |
| expectancy | $-4.90 |
| profit_factor | 0.89 |
| max_consecutive_losses | 17 |
| max_drawdown | $-12,639.30 |
| n_active_days | 1138 |
| best_day | $573.19 |
| worst_day | $-789.83 |
| sharpe_daily | -0.96 |
| sortino_daily | -1.79 |
| trades_per_day | 1.14 |
| avg_hold_minutes | 61 |
| time_in_market_pct | 5.04% |
| pct_ambiguous_trades | 10.61% |
| exit_reasons | {'session_end': 12, 'eod': 191, 'target': 460, 'stop': 1288} |

Overfit-prone parameters: ema_fast, ema_slow, stop_atr, target_r, expire_minutes

## ema_trend

| Metric | Value |
| --- | --- |
| n_trades | 2959 |
| net_pnl | $4,822.26 |
| gross_pnl | $10,681.08 |
| total_costs | $5,858.82 |
| win_rate | 33.15% |
| avg_win | $137.49 |
| avg_loss | $-65.75 |
| expectancy | $1.63 |
| profit_factor | 1.04 |
| max_consecutive_losses | 19 |
| max_drawdown | $-7,063.32 |
| n_active_days | 1382 |
| best_day | $973.25 |
| worst_day | $-650.28 |
| sharpe_daily | 0.29 |
| sortino_daily | 0.53 |
| trades_per_day | 1.74 |
| avg_hold_minutes | 83 |
| time_in_market_pct | 10.38% |
| pct_ambiguous_trades | 0.03% |
| exit_reasons | {'target': 227, 'stop': 597, 'signal': 1606, 'session_end': 34, 'eod': 495} |

Overfit-prone parameters: ema_fast, ema_slow, ema_filter, stop_atr, target_r

## bollinger_mean_reversion

| Metric | Value |
| --- | --- |
| n_trades | 1722 |
| net_pnl | $-5,317.94 |
| gross_pnl | $-1,908.38 |
| total_costs | $3,409.56 |
| win_rate | 46.57% |
| avg_win | $67.38 |
| avg_loss | $-64.52 |
| expectancy | $-3.09 |
| profit_factor | 0.91 |
| max_consecutive_losses | 12 |
| max_drawdown | $-7,038.85 |
| n_active_days | 1074 |
| best_day | $550.97 |
| worst_day | $-319.27 |
| sharpe_daily | -0.80 |
| sortino_daily | -1.46 |
| trades_per_day | 1.01 |
| avg_hold_minutes | 35 |
| time_in_market_pct | 2.55% |
| pct_ambiguous_trades | 0.81% |
| exit_reasons | {'session_end': 5, 'stop': 810, 'target': 680, 'eod': 56, 'max_hold': 171} |

Overfit-prone parameters: bb_n, bb_k, adx_max, stop_atr

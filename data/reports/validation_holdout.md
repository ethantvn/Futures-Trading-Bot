# 2026 Holdout (single run)

**This holdout was run once. Do not re-run for tuning.**

## opening_range_breakout — 2026 holdout (single run)

- Params: `range_minutes=30, target_r=1.5, expire_minutes=120`
- Period: 2026-01-02 → 2026-06-26
- **This holdout was run once.** Do not re-run for tuning.

## opening_range_breakout (holdout 2026)

| Metric | Value |
| --- | --- |
| n_trades | 122 |
| net_pnl | $948.44 |
| gross_pnl | $1,190.00 |
| total_costs | $241.56 |
| win_rate | 52.46% |
| avg_win | $273.87 |
| avg_loss | $-285.85 |
| expectancy | $7.77 |
| profit_factor | 1.06 |
| max_consecutive_losses | 5 |
| max_drawdown | $-3,444.17 |
| n_active_days | 122 |
| best_day | $988.27 |
| worst_day | $-784.98 |
| sharpe_daily | 0.36 |
| sortino_daily | 0.71 |
| trades_per_day | 1.00 |
| avg_hold_minutes | 230 |
| time_in_market_pct | 16.66% |
| pct_ambiguous_trades | 0.00% |
| exit_reasons | {'stop': 39, 'session_end': 3, 'target': 18, 'eod': 62} |


## ema_trend — 2026 holdout (single run)

- Params: `ema_fast=9, ema_slow=21, stop_atr=1.5, target_r=3.0`
- Period: 2026-01-02 → 2026-06-26
- **This holdout was run once.** Do not re-run for tuning.

## ema_trend (holdout 2026)

| Metric | Value |
| --- | --- |
| n_trades | 220 |
| net_pnl | $-2,568.05 |
| gross_pnl | $-2,132.45 |
| total_costs | $435.60 |
| win_rate | 29.55% |
| avg_win | $209.66 |
| avg_loss | $-104.49 |
| expectancy | $-11.67 |
| profit_factor | 0.84 |
| max_consecutive_losses | 12 |
| max_drawdown | $-3,978.61 |
| n_active_days | 101 |
| best_day | $513.36 |
| worst_day | $-857.14 |
| sharpe_daily | -1.51 |
| sortino_daily | -2.53 |
| trades_per_day | 2.18 |
| avg_hold_minutes | 71 |
| time_in_market_pct | 11.26% |
| pct_ambiguous_trades | 0.45% |
| exit_reasons | {'eod': 30, 'stop': 88, 'signal': 81, 'session_end': 1, 'target': 20} |


## Monte Carlo — 2026 holdout

| Strategy | Account | Micros | Pass % | Fail % | Timeout % | Med days | P25-P75 | <=10d % | <=15d % | <=20d % | DD fails % | E[resets] | E[cost] | E[profit/attempt] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| opening_range_breakout (holdout 2026) | LucidFlex 25K | 1 | 37.3% | 62.5% | 0.2% | 12 | 8-19 | 14.6% | 23.2% | 29.1% | 100% | 1.7 | $201 | $111 |
| opening_range_breakout (holdout 2026) | LucidFlex 25K | 2 | 30.7% | 69.3% | 0.0% | 7 | 5-11 | 21.8% | 27.3% | 29.2% | 100% | 2.3 | $236 | $146 |
| ema_trend (holdout 2026) | LucidFlex 25K | 1 | 18.1% | 81.3% | 0.6% | 19 | 13-29 | 2.5% | 6.2% | 9.8% | 100% | 4.5 | $371 | $-397 |
| ema_trend (holdout 2026) | LucidFlex 25K | 2 | 20.7% | 79.3% | 0.0% | 8 | 6-13 | 13.0% | 17.8% | 19.6% | 100% | 3.8 | $330 | $-265 |

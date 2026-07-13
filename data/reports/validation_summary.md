# Phase 5 Validation Summary

Candidates: `opening_range_breakout`, `ema_trend`. Holdout 2026 is untouched unless `--holdout` was passed.

## opening_range_breakout

- Walk-forward OOS: 993 trades, net $18,377, Sharpe 1.16, PF 1.20
- Final params: `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 120}`
- 25K pass rate (WF OOS): 44.3% @1 micro, 35.8% @2 micros
- Slippage stress 2025: robust (profitable at 0/1/2 ticks)
- Top configs on 2023-2024 validation window:
  - `{'range_minutes': 30, 'target_r': 2.5, 'expire_minutes': 60}`: Sharpe 1.77, net $11,331
  - `{'range_minutes': 30, 'target_r': 2.5, 'expire_minutes': 120}`: Sharpe 1.76, net $11,721
  - `{'range_minutes': 30, 'target_r': 1.5, 'expire_minutes': 60}`: Sharpe 1.71, net $9,761

## ema_trend

- Walk-forward OOS: 1999 trades, net $1,391, Sharpe 0.12, PF 1.01
- Final params: `{'ema_fast': 9, 'ema_slow': 21, 'stop_atr': 1.5, 'target_r': 3.0}`
- 25K pass rate (WF OOS): 28.3% @1 micro, 30.0% @2 micros
- Slippage stress 2025: robust (profitable at 0/1/2 ticks)
- Top configs on 2023-2024 validation window:
  - `{'ema_fast': 5, 'ema_slow': 21, 'stop_atr': 2.5, 'target_r': 3.0}`: Sharpe -0.26, net $-1,247
  - `{'ema_fast': 5, 'ema_slow': 34, 'stop_atr': 2.5, 'target_r': 3.0}`: Sharpe -0.30, net $-1,424
  - `{'ema_fast': 5, 'ema_slow': 21, 'stop_atr': 2.0, 'target_r': 3.0}`: Sharpe -0.31, net $-1,407

## Monte Carlo — walk-forward OOS

| Strategy | Account | Micros | Pass % | Fail % | Timeout % | Med days | P25-P75 | <=10d % | <=15d % | <=20d % | DD fails % | E[resets] | E[cost] | E[profit/attempt] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| opening_range_breakout (WF OOS) | LucidFlex 25K | 1 | 44.3% | 51.9% | 3.9% | 22 | 14-32 | 6.1% | 13.4% | 20.4% | 100% | 1.3 | $176 | $413 |
| opening_range_breakout (WF OOS) | LucidFlex 25K | 2 | 35.8% | 63.8% | 0.4% | 10 | 7-16 | 18.3% | 26.5% | 30.8% | 100% | 1.8 | $208 | $355 |
| ema_trend (WF OOS) | LucidFlex 25K | 1 | 28.3% | 60.4% | 11.3% | 27 | 17-39 | 2.7% | 6.0% | 9.7% | 100% | 2.5 | $252 | $36 |
| ema_trend (WF OOS) | LucidFlex 25K | 2 | 30.0% | 69.2% | 0.8% | 11 | 7-18 | 13.9% | 20.1% | 24.2% | 100% | 2.3 | $240 | $0 |

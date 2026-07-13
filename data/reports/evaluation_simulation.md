# Lucid Evaluation Monte Carlo Report

- Attempts per row: 10,000; evaluation capped at 60 trading days; moving-block bootstrap (5-day blocks) of historical trading days.
- Ledgers are baseline backtests 2019-2025, pessimistic fills, all costs included.
- Rules: EOD trailing MLL with lock at starting balance, 50% consistency, 2 min trading days (sources cited in config).
- E[cost] = eval fee + E[resets] x reset fee, using discounted fees NOT applied (regular prices from config).

| Strategy | Account | Micros | Pass % | Fail % | Timeout % | Med days | P25-P75 | <=10d % | <=15d % | <=20d % | DD fails % | E[resets] | E[cost] | E[profit/attempt] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bollinger_mean_reversion | LucidFlex 25K | 1 | 4.0% | 37.0% | 59.0% | 40 | 30-51 | 0.0% | 0.2% | 0.4% | 100% | 23.8 | $1,525 | $-265 |
| bollinger_mean_reversion | LucidFlex 25K | 2 | 16.0% | 76.3% | 7.7% | 27 | 17-39 | 1.5% | 3.3% | 5.4% | 100% | 5.2 | $414 | $-293 |
| bollinger_mean_reversion | LucidFlex 25K | 3 | 17.9% | 80.4% | 1.6% | 17 | 10-26 | 4.8% | 8.1% | 11.3% | 100% | 4.6 | $374 | $-281 |
| bollinger_mean_reversion | LucidFlex 25K | 5 | 17.0% | 82.5% | 0.5% | 10 | 6-16 | 9.1% | 12.2% | 14.3% | 100% | 4.9 | $393 | $-285 |
| ema_trend | LucidFlex 25K | 1 | 30.2% | 59.2% | 10.6% | 26 | 16-39 | 4.0% | 7.4% | 11.2% | 100% | 2.3 | $239 | $71 |
| ema_trend | LucidFlex 25K | 2 | 30.2% | 69.3% | 0.4% | 12 | 7-18 | 13.5% | 19.9% | 23.9% | 100% | 2.3 | $238 | $55 |
| ema_trend | LucidFlex 25K | 3 | 26.7% | 73.1% | 0.2% | 9 | 5-14 | 16.2% | 21.2% | 24.0% | 100% | 2.7 | $264 | $60 |
| ema_trend | LucidFlex 25K | 5 | 21.7% | 78.2% | 0.1% | 7 | 4-11 | 15.7% | 18.7% | 20.2% | 100% | 3.6 | $316 | $74 |
| opening_range_breakout | LucidFlex 25K | 1 | 42.2% | 52.3% | 5.5% | 24 | 15-36 | 5.1% | 10.7% | 16.8% | 100% | 1.4 | $182 | $309 |
| opening_range_breakout | LucidFlex 25K | 2 | 37.0% | 62.6% | 0.4% | 11 | 7-17 | 18.1% | 25.9% | 30.6% | 100% | 1.7 | $202 | $273 |
| opening_range_breakout | LucidFlex 25K | 3 | 30.6% | 69.3% | 0.1% | 8 | 5-13 | 20.2% | 25.4% | 27.8% | 100% | 2.3 | $236 | $234 |
| opening_range_breakout | LucidFlex 25K | 5 | 24.4% | 75.5% | 0.1% | 6 | 4-10 | 18.6% | 21.4% | 22.8% | 100% | 3.1 | $286 | $233 |
| prev_day_hl_breakout | LucidFlex 25K | 1 | 6.0% | 44.4% | 49.6% | 38 | 27-50 | 0.2% | 0.4% | 0.9% | 100% | 15.6 | $1,038 | $-236 |
| prev_day_hl_breakout | LucidFlex 25K | 2 | 19.9% | 75.3% | 4.8% | 22 | 13-33 | 3.8% | 6.7% | 9.2% | 100% | 4.0 | $342 | $-247 |
| prev_day_hl_breakout | LucidFlex 25K | 3 | 21.7% | 77.3% | 1.0% | 14 | 8-22 | 7.6% | 12.2% | 15.4% | 100% | 3.6 | $317 | $-225 |
| prev_day_hl_breakout | LucidFlex 25K | 5 | 19.6% | 79.9% | 0.5% | 9 | 5-14 | 11.9% | 15.7% | 17.6% | 100% | 4.1 | $346 | $-237 |
| vwap_pullback | LucidFlex 25K | 1 | 9.3% | 64.1% | 26.6% | 36 | 25-47 | 0.2% | 0.7% | 1.4% | 100% | 9.8 | $686 | $-329 |
| vwap_pullback | LucidFlex 25K | 2 | 20.4% | 78.8% | 0.8% | 17 | 10-26 | 5.2% | 9.2% | 12.8% | 100% | 3.9 | $334 | $-275 |
| vwap_pullback | LucidFlex 25K | 3 | 20.3% | 79.5% | 0.2% | 11 | 7-17 | 10.0% | 14.4% | 17.2% | 100% | 3.9 | $335 | $-262 |
| vwap_pullback | LucidFlex 25K | 5 | 18.3% | 81.6% | 0.1% | 7 | 5-11 | 13.2% | 15.8% | 17.1% | 100% | 4.5 | $368 | $-279 |
| bollinger_mean_reversion | LucidFlex 50K | 1 | 0.0% | 1.9% | 98.0% | 49 | 49-49 | 0.0% | 0.0% | 0.0% | 100% | 9999.0 | $950,045 | $-302 |
| bollinger_mean_reversion | LucidFlex 50K | 2 | 1.7% | 37.0% | 61.3% | 42 | 32-50 | 0.0% | 0.0% | 0.1% | 100% | 57.1 | $5,568 | $-536 |
| bollinger_mean_reversion | LucidFlex 50K | 3 | 7.5% | 66.4% | 26.1% | 37 | 26-49 | 0.2% | 0.6% | 1.2% | 100% | 12.3 | $1,312 | $-612 |
| bollinger_mean_reversion | LucidFlex 50K | 5 | 14.7% | 82.0% | 3.3% | 24 | 16-35 | 1.7% | 3.7% | 5.8% | 100% | 5.8 | $691 | $-606 |
| ema_trend | LucidFlex 50K | 1 | 7.8% | 19.9% | 72.3% | 40 | 25-51 | 0.5% | 0.9% | 1.4% | 100% | 11.8 | $1,261 | $177 |
| ema_trend | LucidFlex 50K | 2 | 24.8% | 61.1% | 14.1% | 29 | 18-42 | 2.7% | 5.0% | 7.6% | 100% | 3.0 | $428 | $155 |
| ema_trend | LucidFlex 50K | 3 | 28.7% | 69.6% | 1.7% | 19 | 11-29 | 6.7% | 11.5% | 16.1% | 100% | 2.5 | $376 | $121 |
| ema_trend | LucidFlex 50K | 5 | 27.2% | 72.5% | 0.3% | 10 | 6-16 | 13.8% | 19.7% | 23.1% | 100% | 2.7 | $395 | $125 |
| opening_range_breakout | LucidFlex 50K | 1 | 11.9% | 21.6% | 66.5% | 45 | 35-53 | 0.1% | 0.3% | 0.6% | 100% | 7.4 | $843 | $595 |
| opening_range_breakout | LucidFlex 50K | 2 | 36.4% | 55.1% | 8.4% | 28 | 19-40 | 2.8% | 6.3% | 10.7% | 100% | 1.7 | $306 | $667 |
| opening_range_breakout | LucidFlex 50K | 3 | 36.9% | 62.1% | 1.0% | 17 | 11-25 | 9.2% | 16.7% | 22.9% | 100% | 1.7 | $302 | $561 |
| opening_range_breakout | LucidFlex 50K | 5 | 32.5% | 67.3% | 0.2% | 9 | 6-15 | 18.2% | 24.9% | 28.3% | 100% | 2.1 | $337 | $484 |
| prev_day_hl_breakout | LucidFlex 50K | 1 | 0.0% | 4.0% | 96.0% | 54 | 53-55 | 0.0% | 0.0% | 0.0% | 100% | 4999.0 | $475,045 | $-283 |
| prev_day_hl_breakout | LucidFlex 50K | 2 | 3.4% | 44.5% | 52.1% | 42 | 32-51 | 0.1% | 0.1% | 0.3% | 100% | 28.5 | $2,847 | $-477 |
| prev_day_hl_breakout | LucidFlex 50K | 3 | 10.5% | 69.3% | 20.2% | 32 | 21-44 | 0.8% | 1.5% | 2.6% | 100% | 8.5 | $950 | $-523 |
| prev_day_hl_breakout | LucidFlex 50K | 5 | 18.4% | 79.3% | 2.3% | 19 | 11-29 | 4.3% | 7.2% | 9.8% | 100% | 4.4 | $560 | $-488 |
| vwap_pullback | LucidFlex 50K | 1 | 0.1% | 16.4% | 83.6% | 58 | 45-59 | 0.0% | 0.0% | 0.0% | 100% | 1665.7 | $158,378 | $-486 |
| vwap_pullback | LucidFlex 50K | 2 | 5.3% | 64.7% | 30.0% | 40 | 29-51 | 0.0% | 0.1% | 0.4% | 100% | 18.0 | $1,851 | $-681 |
| vwap_pullback | LucidFlex 50K | 3 | 13.2% | 80.2% | 6.6% | 28 | 19-41 | 0.7% | 2.0% | 3.9% | 100% | 6.6 | $763 | $-659 |
| vwap_pullback | LucidFlex 50K | 5 | 18.2% | 81.4% | 0.4% | 15 | 9-22 | 5.7% | 9.6% | 12.9% | 100% | 4.5 | $566 | $-550 |

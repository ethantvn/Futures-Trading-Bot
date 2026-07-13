# TradingView Comparison Report

- TradingView bars: 21,864 (2025-07-31 22:00:00+00:00 -> 2026-07-06 20:45:00+00:00)
- Databento bars:   166,697 (2019-05-29 00:00:00+00:00 -> 2026-06-28 23:45:00+00:00)
- Overlapping bars (timestamp join): 21,336
- TradingView-only bars (missing in Databento series): 528
- Databento-only bars (missing in TradingView export): 145,361

- Candles fully matching (all OHLC within half a tick): 98.20%
- Suspected roll-date mismatch days (TV front contract differs): 2025-09-16, 2025-12-16, 2026-03-17, 2026-06-15
- Candles fully matching EXCLUDING those days: 99.92%

## Per-field differences

| Field | Max abs diff | Mean abs diff | % within half tick |
| --- | --- | --- | --- |
| open | 306.25 | 4.3248 | 98.25% |
| high | 308.25 | 4.3298 | 98.27% |
| low | 306.50 | 4.3187 | 98.27% |
| close | 306.25 | 4.3221 | 98.24% |

Volume was not compared (no volume column in the TradingView export).

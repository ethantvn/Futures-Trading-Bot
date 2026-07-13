# TradingView Comparison Report

- TradingView bars: 21,600 (2026-06-14 22:00:00+00:00 -> 2026-07-06 20:59:00+00:00)
- Databento bars:   2,496,400 (2019-05-29 00:00:00+00:00 -> 2026-06-28 23:59:00+00:00)
- Overlapping bars (timestamp join): 13,680
- TradingView-only bars (missing in Databento series): 7,920
- Databento-only bars (missing in TradingView export): 2,482,720

- Candles fully matching (all OHLC within half a tick): 89.88%
- Suspected roll-date mismatch days (TV front contract differs): 2026-06-15
- Candles fully matching EXCLUDING those days: 99.96%

## Per-field differences

| Field | Max abs diff | Mean abs diff | % within half tick |
| --- | --- | --- | --- |
| open | 306.25 | 30.3452 | 89.89% |
| high | 310.75 | 30.3645 | 89.90% |
| low | 308.25 | 30.3223 | 89.91% |
| close | 307.75 | 30.3500 | 89.90% |
| volume | 10774.00 | 82.4327 |  |

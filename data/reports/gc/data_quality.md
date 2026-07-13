# Data Quality Report

- Rows (outright 1m bars): 3,483,222
- Contracts: 89
- Range (UTC, bar-open): 2021-06-11 00:00:00+00:00 -> 2026-07-10 16:09:00+00:00
- Trading days (lead contract): 1312
- Median 1m bars per trading day: 1379 (full Globex day = 1380)

## Integrity checks

- Duplicate (ts, symbol) rows: 0
- OHLC relationship violations: 0
- Non-positive prices: 0
- Prices off the 0.25 tick grid: 0
- Bars with volume <= 0: 0

## Short days (< threshold minutes on lead contract): 14

Known-legitimate causes: holidays/half-days, COVID 2020 limit halts, export boundary.

- 2025-11-28 (GCG6): 602 minutes
- 2026-07-10 (GCQ6): 1081 minutes
- 2021-11-25 (GCZ1): 1133 minutes
- 2021-07-05 (GCQ1): 1135 minutes
- 2021-09-06 (GCZ1): 1135 minutes
- 2026-07-03 (GCQ6): 1135 minutes
- 2025-07-04 (GCQ5): 1138 minutes
- 2026-06-19 (GCQ6): 1140 minutes
- 2022-11-25 (GCZ2): 1176 minutes
- 2023-11-24 (GCZ3): 1182 minutes
- 2024-12-24 (GCG5): 1182 minutes
- 2021-11-26 (GCG2): 1184 minutes
- 2025-12-24 (GCG6): 1185 minutes
- 2023-09-04 (GCZ3): 1199 minutes

## Databento condition flags

- Day counts: {'available': 1590, 'degraded': 9, 'missing': 13}
- Degraded dates: 2021-12-05, 2022-01-02, 2025-09-17, 2025-09-24, 2025-11-28, 2026-03-15, 2026-03-16, 2026-04-10, 2026-05-24
- Missing dates (all verified Saturdays, market closed): 2026-02-14, 2026-02-21, 2026-02-28, 2026-03-07, 2026-03-14, 2026-03-21, 2026-03-28, 2026-04-04, 2026-04-11, 2026-04-18, 2026-04-25, 2026-05-02, 2026-05-09

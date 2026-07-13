# Data Quality Report

- Rows (outright 1m bars): 3,005,052
- Contracts: 42
- Range (UTC, bar-open): 2021-06-11 00:00:00+00:00 -> 2026-07-10 20:59:00+00:00
- Trading days (lead contract): 1312
- Median 1m bars per trading day: 1373 (full Globex day = 1380)

## Integrity checks

- Duplicate (ts, symbol) rows: 0
- OHLC relationship violations: 0
- Non-positive prices: 0
- Prices off the 0.1 tick grid: 0
- Bars with volume <= 0: 0

## Short days (< threshold minutes on lead contract): 27

Known-legitimate causes: holidays/half-days, COVID 2020 limit halts, export boundary.

- 2025-11-28 (MGCG6): 604 minutes
- 2021-09-06 (MGCZ1): 1048 minutes
- 2021-07-05 (MGCQ1): 1101 minutes
- 2023-09-04 (MGCZ3): 1105 minutes
- 2021-11-25 (MGCZ1): 1113 minutes
- 2022-01-17 (MGCG2): 1133 minutes
- 2025-07-04 (MGCQ5): 1140 minutes
- 2026-06-19 (MGCQ6): 1140 minutes
- 2026-07-03 (MGCQ6): 1140 minutes
- 2023-11-24 (MGCZ3): 1151 minutes
- 2022-09-05 (MGCZ2): 1153 minutes
- 2022-07-04 (MGCQ2): 1159 minutes
- 2022-11-25 (MGCZ2): 1159 minutes
- 2023-07-04 (MGCQ3): 1165 minutes
- 2021-11-26 (MGCZ1): 1166 minutes
- 2023-05-29 (MGCQ3): 1171 minutes
- 2022-05-30 (MGCQ2): 1173 minutes
- 2023-11-23 (MGCZ3): 1176 minutes
- 2022-06-20 (MGCQ2): 1179 minutes
- 2024-12-24 (MGCG5): 1183 minutes
- 2025-12-24 (MGCG6): 1185 minutes
- 2022-11-24 (MGCZ2): 1188 minutes
- 2024-02-19 (MGCJ4): 1189 minutes
- 2023-02-20 (MGCJ3): 1192 minutes
- 2023-01-16 (MGCG3): 1198 minutes

## Databento condition flags

- Day counts: {'available': 1590, 'degraded': 9, 'missing': 13}
- Degraded dates: 2021-12-05, 2022-01-02, 2025-09-17, 2025-09-24, 2025-11-28, 2026-03-15, 2026-03-16, 2026-04-10, 2026-05-24
- Missing dates (all verified Saturdays, market closed): 2026-02-14, 2026-02-21, 2026-02-28, 2026-03-07, 2026-03-14, 2026-03-21, 2026-03-28, 2026-04-04, 2026-04-11, 2026-04-18, 2026-04-25, 2026-05-02, 2026-05-09

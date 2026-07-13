# Data Quality Report

- Rows (outright 1m bars): 3,528,331
- Contracts: 33
- Range (UTC, bar-open): 2019-05-29 00:00:00+00:00 -> 2026-06-29 20:59:00+00:00
- Trading days (lead contract): 1832
- Median 1m bars per trading day: 1380 (full Globex day = 1380)

## Integrity checks

- Duplicate (ts, symbol) rows: 0
- OHLC relationship violations: 0
- Non-positive prices: 0
- Prices off the 0.25 tick grid: 0
- Bars with volume <= 0: 0

## Short days (< threshold minutes on lead contract): 72

Known-legitimate causes: holidays/half-days, COVID 2020 limit halts, export boundary.

- 2025-11-28 (MESZ5): 510 minutes
- 2020-03-16 (MESM0): 584 minutes
- 2021-04-02 (MESM1): 882 minutes
- 2023-04-07 (MESM3): 898 minutes
- 2019-12-24 (MESH0): 914 minutes
- 2026-04-03 (MESM6): 915 minutes
- 2025-01-09 (MESH5): 930 minutes
- 2020-03-09 (MESH0): 969 minutes
- 2020-06-30 (MESU0): 971 minutes
- 2020-03-18 (MESM0): 975 minutes
- 2019-07-04 (MESU9): 1007 minutes
- 2020-02-28 (MESH0): 1019 minutes
- 2020-01-20 (MESH0): 1047 minutes
- 2019-11-28 (MESZ9): 1057 minutes
- 2020-02-17 (MESH0): 1096 minutes
- 2019-11-29 (MESZ9): 1105 minutes
- 2023-07-04 (MESU3): 1119 minutes
- 2019-07-03 (MESU9): 1120 minutes
- 2019-12-26 (MESH0): 1120 minutes
- 2023-11-23 (MESZ3): 1129 minutes
- 2024-07-04 (MESU4): 1129 minutes
- 2021-07-05 (MESU1): 1130 minutes
- 2024-06-19 (MESU4): 1131 minutes
- 2024-11-28 (MESZ4): 1132 minutes
- 2024-05-27 (MESM4): 1133 minutes

## Databento condition flags

- Day counts: {'available': 2213, 'degraded': 13, 'missing': 13}
- Degraded dates: 2020-02-27, 2020-02-28, 2020-06-30, 2020-07-01, 2021-12-05, 2022-01-02, 2025-09-17, 2025-09-24, 2025-11-28, 2026-03-15, 2026-03-16, 2026-04-10, 2026-05-24
- Missing dates (all verified Saturdays, market closed): 2026-02-14, 2026-02-21, 2026-02-28, 2026-03-07, 2026-03-14, 2026-03-21, 2026-03-28, 2026-04-04, 2026-04-11, 2026-04-18, 2026-04-25, 2026-05-02, 2026-05-09

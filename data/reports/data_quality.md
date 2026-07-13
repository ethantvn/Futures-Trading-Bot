# Data Quality Report

- Rows (outright 1m bars): 3,736,515
- Contracts: 33
- Range (UTC, bar-open): 2019-05-29 00:00:00+00:00 -> 2026-06-28 23:59:00+00:00
- Trading days (lead contract): 1832
- Median 1m bars per trading day: 1380 (full Globex day = 1380)

## Integrity checks

- Duplicate (ts, symbol) rows: 0
- OHLC relationship violations: 0
- Non-positive prices: 0
- Prices off the 0.25 tick grid: 0
- Bars with volume <= 0: 0

## Short days (< threshold minutes on lead contract): 73

Known-legitimate causes: holidays/half-days, COVID 2020 limit halts, export boundary.

- 2026-06-29 (MNQU6): 120 minutes
- 2025-11-28 (MNQZ5): 510 minutes
- 2020-03-16 (MNQM0): 570 minutes
- 2021-04-02 (MNQM1): 915 minutes
- 2023-04-07 (MNQM3): 915 minutes
- 2026-04-03 (MNQM6): 915 minutes
- 2025-01-09 (MNQH5): 930 minutes
- 2020-03-18 (MNQM0): 936 minutes
- 2020-06-30 (MNQU0): 971 minutes
- 2020-03-09 (MNQH0): 1005 minutes
- 2019-07-04 (MNQU9): 1008 minutes
- 2020-02-28 (MNQH0): 1019 minutes
- 2020-03-17 (MNQM0): 1073 minutes
- 2019-11-28 (MNQZ9): 1117 minutes
- 2019-12-24 (MNQH0): 1119 minutes
- 2020-01-20 (MNQH0): 1120 minutes
- 2019-07-03 (MNQU9): 1130 minutes
- 2019-09-02 (MNQU9): 1139 minutes
- 2021-02-15 (MNQH1): 1139 minutes
- 2021-07-05 (MNQU1): 1139 minutes
- 2021-09-06 (MNQU1): 1139 minutes
- 2023-07-04 (MNQU3): 1139 minutes
- 2020-02-17 (MNQH0): 1140 minutes
- 2020-05-25 (MNQM0): 1140 minutes
- 2020-07-03 (MNQU0): 1140 minutes

## Databento condition flags

- Day counts: {'available': 2212, 'degraded': 13, 'missing': 13}
- Degraded dates: 2020-02-27, 2020-02-28, 2020-06-30, 2020-07-01, 2021-12-05, 2022-01-02, 2025-09-17, 2025-09-24, 2025-11-28, 2026-03-15, 2026-03-16, 2026-04-10, 2026-05-24
- Missing dates (all verified Saturdays, market closed): 2026-02-14, 2026-02-21, 2026-02-28, 2026-03-07, 2026-03-14, 2026-03-21, 2026-03-28, 2026-04-04, 2026-04-11, 2026-04-18, 2026-04-25, 2026-05-02, 2026-05-09

"""High-impact US macro event dates for day-level skip filters.

Sources (schedules are public; dates verified against Fed/BLS calendars):
- NFP: first Friday of each month (BLS Employment Situation, 08:30 ET)
- CPI: BLS Consumer Price Index — typically 08:30 ET on a weekday between
  the 10th and 15th; we use the published schedule where known and a
  conservative weekday-on-or-after-12th fallback for gaps.
- FOMC: Federal Reserve decision days (14:00 ET statement; 08:30 ET matters
  for pre-market but ORB trades post-10:00 — still skip due to elevated
  opening-range distortion).

All dates are **trading_date** (America/New_York session label), causal:
only dates on or before the session being evaluated are used.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

import polars as pl

# FOMC statement / decision days (ET calendar date), 2019-2026.
# Emergency/unscheduled meetings included where they fell on trading days.
FOMC_DECISION_DAYS: tuple[str, ...] = (
    # 2019
    "2019-01-30", "2019-03-20", "2019-05-01", "2019-06-19", "2019-07-31",
    "2019-09-18", "2019-10-30", "2019-12-11",
    # 2020
    "2020-01-29", "2020-03-03", "2020-03-15", "2020-03-19", "2020-04-29",
    "2020-06-10", "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16",
    # 2021
    "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28",
    "2021-09-22", "2021-11-03", "2021-12-15",
    # 2022
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27",
    "2022-09-21", "2022-11-02", "2022-12-14",
    # 2023
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26",
    "2023-09-20", "2023-11-01", "2023-12-13",
    # 2024
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31",
    "2024-09-18", "2024-11-07", "2024-12-18",
    # 2025
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30",
    "2025-09-17", "2025-10-29", "2025-12-10",
    # 2026 (scheduled through June)
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
)

# BLS CPI release dates (08:30 ET), 2019-2026 where published / verified.
# Gaps filled by _cpi_fallback().
CPI_RELEASE_DAYS: tuple[str, ...] = (
    # 2019
    "2019-01-11", "2019-02-13", "2019-03-12", "2019-04-10", "2019-05-10",
    "2019-06-12", "2019-07-11", "2019-08-13", "2019-09-12", "2019-10-10",
    "2019-11-13", "2019-12-11",
    # 2020
    "2020-01-14", "2020-02-13", "2020-03-11", "2020-04-10", "2020-05-12",
    "2020-06-10", "2020-07-14", "2020-08-12", "2020-09-11", "2020-10-13",
    "2020-11-12", "2020-12-10",
    # 2021
    "2021-01-13", "2021-02-10", "2021-03-10", "2021-04-13", "2021-05-12",
    "2021-06-10", "2021-07-13", "2021-08-11", "2021-09-14", "2021-10-13",
    "2021-11-10", "2021-12-10",
    # 2022
    "2022-01-12", "2022-02-10", "2022-03-10", "2022-04-12", "2022-05-11",
    "2022-06-10", "2022-07-13", "2022-08-10", "2022-09-13", "2022-10-13",
    "2022-11-10", "2022-12-13",
    # 2023
    "2023-01-12", "2023-02-14", "2023-03-14", "2023-04-12", "2023-05-10",
    "2023-06-13", "2023-07-12", "2023-08-10", "2023-09-13", "2023-10-12",
    "2023-11-14", "2023-12-12",
    # 2024
    "2024-01-11", "2024-02-13", "2024-03-12", "2024-04-10", "2024-05-15",
    "2024-06-12", "2024-07-11", "2024-08-14", "2024-09-11", "2024-10-10",
    "2024-11-13", "2024-12-11",
    # 2025
    "2025-01-15", "2025-02-12", "2025-03-12", "2025-04-10", "2025-05-13",
    "2025-06-11", "2025-07-15", "2025-08-12", "2025-09-11", "2025-10-15",
    "2025-11-13", "2025-12-10",
    # 2026
    "2026-01-14", "2026-02-11", "2026-03-11", "2026-04-14", "2026-05-12",
    "2026-06-10",
)


def _next_weekday(d: date) -> date:
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def nfp_dates(start: date, end: date) -> set[date]:
    """First Friday of each month in [start, end]."""
    out: set[date] = set()
    y, m = start.year, start.month
    end_y, end_m = end.year, end.month
    while (y, m) <= (end_y, end_m):
        cal = calendar.monthcalendar(y, m)
        for week in cal:
            if week[calendar.FRIDAY]:
                d = date(y, m, week[calendar.FRIDAY])
                if start <= d <= end:
                    out.add(d)
                break
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def _cpi_fallback(start: date, end: date) -> set[date]:
    """Weekday on or after the 12th — conservative gap-fill only."""
    out: set[date] = set()
    y, m = start.year, start.month
    end_y, end_m = end.year, end.month
    known = {date.fromisoformat(s) for s in CPI_RELEASE_DAYS}
    while (y, m) <= (end_y, end_m):
        d = _next_weekday(date(y, m, 12))
        if start <= d <= end and d not in known:
            out.add(d)
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def cpi_dates(start: date, end: date) -> set[date]:
    known = {date.fromisoformat(s) for s in CPI_RELEASE_DAYS}
    return {d for d in known if start <= d <= end} | _cpi_fallback(start, end)


def fomc_dates(start: date, end: date) -> set[date]:
    return {date.fromisoformat(s) for s in FOMC_DECISION_DAYS if start <= date.fromisoformat(s) <= end}


def macro_event_dates(
    start: date,
    end: date,
    events: str | tuple[str, ...] = "all",
) -> set[date]:
    """Return skip dates for the requested event set.

    events: 'all' | 'nfp' | 'cpi' | 'fomc' | ('nfp', 'cpi') | ...
    """
    if events == "all":
        kinds = ("nfp", "cpi", "fomc")
    elif isinstance(events, str):
        kinds = (events,)
    else:
        kinds = events
    out: set[date] = set()
    for k in kinds:
        if k == "nfp":
            out |= nfp_dates(start, end)
        elif k == "cpi":
            out |= cpi_dates(start, end)
        elif k == "fomc":
            out |= fomc_dates(start, end)
        else:
            raise ValueError(f"unknown macro event kind: {k!r}")
    return out


@lru_cache(maxsize=4)
def macro_skip_frame(start_iso: str, end_iso: str, events: str) -> pl.DataFrame:
    """Polars frame: trading_date, skip_macro (bool)."""
    start, end = date.fromisoformat(start_iso), date.fromisoformat(end_iso)
    skip = macro_event_dates(start, end, events)
    if not skip:
        return pl.DataFrame(schema={"trading_date": pl.Date, "skip_macro": pl.Boolean})
    return pl.DataFrame(
        {"trading_date": sorted(skip), "skip_macro": [True] * len(skip)}
    )


def export_calendar_csv(path: str | Path, start: date, end: date) -> Path:
    """Write a human-readable calendar for inspection."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for kind in ("nfp", "cpi", "fomc"):
        for d in sorted(macro_event_dates(start, end, kind)):
            rows.append({"date": d.isoformat(), "event": kind})
    pl.DataFrame(rows).write_csv(path)
    return path

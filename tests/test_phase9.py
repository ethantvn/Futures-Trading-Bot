from __future__ import annotations

from datetime import date

import polars as pl

from src.data.macro_calendar import cpi_dates, fomc_dates, macro_event_dates, nfp_dates
from src.strategies.orb_filtered import FilteredOrb
from tests.test_strategies import actionable_view
from tests.test_indicators import synthetic_5m


def test_nfp_first_friday():
    # Jan 2024: first Friday = 5th
    days = nfp_dates(date(2024, 1, 1), date(2024, 1, 31))
    assert date(2024, 1, 5) in days


def test_macro_all_union():
    all_days = macro_event_dates(date(2024, 1, 1), date(2024, 12, 31), "all")
    assert date(2024, 1, 5) in all_days  # NFP
    assert date(2024, 1, 31) in all_days  # FOMC


def test_filtered_orb_long_only():
    df = synthetic_5m(days=4, seed=11)
    p = FilteredOrb({"long_only": True}).prepare(df)
    assert p.filter(pl.col("enter_short")).height == 0


def test_filtered_orb_skip_macro_blocks_nfp_day():
    """Gate off on a known NFP Friday embedded in synthetic data."""
    df = synthetic_5m(days=5, seed=7)  # Mon 2024-01-15 ..
    # Re-label day 0 to first Friday of Feb 2024 (NFP)
    nfp_day = date(2024, 2, 2)
    df = df.with_columns(
        pl.when(pl.col("trading_date") == df["trading_date"][0])
        .then(pl.lit(nfp_day))
        .otherwise(pl.col("trading_date"))
        .alias("trading_date")
    )
    p = FilteredOrb({"skip_macro_days": True, "macro_events": "nfp"}).prepare(df)
    on_day = p.filter(pl.col("trading_date") == nfp_day)
    assert on_day.filter(pl.col("enter_long") | pl.col("enter_short")).height == 0


def test_long_only_no_look_ahead():
    df = synthetic_5m(days=4, seed=11)
    strat = FilteredOrb({"long_only": True})
    full = actionable_view(strat.prepare(df))
    k = len(df) // 2
    trunc = actionable_view(strat.prepare(df.head(k)))
    assert trunc.equals(full.head(k))

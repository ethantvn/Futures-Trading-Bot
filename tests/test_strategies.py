from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import numpy as np
import polars as pl
import pytest

from src.strategies.breakout import PrevDayLevelBreakout
from src.strategies.mean_reversion import BollingerMeanReversion
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.trend import EmaTrend
from src.strategies.vwap import VwapPullback
from tests.test_indicators import synthetic_5m

ALL_STRATEGIES = [
    OpeningRangeBreakout,
    PrevDayLevelBreakout,
    VwapPullback,
    EmaTrend,
    BollingerMeanReversion,
]

FLAG_COLS = ["enter_long", "enter_short", "exit_long", "exit_short"]
PRICE_COLS = [
    "entry_price_long_adj", "entry_price_short_adj",
    "stop_long_adj", "stop_short_adj",
    "target_long_adj", "target_short_adj",
]


def actionable_view(df: pl.DataFrame) -> pl.DataFrame:
    """Signal columns as the ENGINE consumes them: prices only matter on bars
    where an enter flag fires."""
    active = pl.col("enter_long") | pl.col("enter_short")
    return df.select(
        *FLAG_COLS,
        *[pl.when(active).then(pl.col(c)).otherwise(None).alias(c) for c in PRICE_COLS],
        pl.when(active).then(pl.col("expire_minutes")).otherwise(None).alias("expire_minutes"),
    )


def synthetic_frame(strategy_cls) -> pl.DataFrame:
    df = synthetic_5m(days=4, seed=11)
    if strategy_cls is PrevDayLevelBreakout:
        # 15m frame for the PDHL strategy
        df = (
            df.with_columns((pl.col("ts_utc").cast(pl.Int64) // (15 * 60_000_000_000)).alias("b"))
            .group_by("b", maintain_order=True)
            .agg(
                pl.col("ts_utc").first(), pl.col("ts_ny").first(),
                pl.col("trading_date").first(), pl.col("session").first(),
                pl.col("open_adj").first(), pl.col("high_adj").max(),
                pl.col("low_adj").min(), pl.col("close_adj").last(),
                pl.col("volume").sum(),
            )
            .drop("b")
        )
    return df


@pytest.mark.parametrize("cls", ALL_STRATEGIES, ids=lambda c: c.name)
def test_no_look_ahead(cls):
    """prepare() on truncated data must equal prepare() on full data for every
    already-elapsed bar (actionable columns)."""
    df = synthetic_frame(cls)
    strat = cls()
    full = actionable_view(strat.prepare(df))
    for k in (len(df) // 3, len(df) // 2, len(df) - 5):
        trunc = actionable_view(strat.prepare(df.head(k)))
        assert trunc.equals(full.head(k)), f"{cls.name} leaks future data at row {k}"


def test_orb_emits_at_range_completion_with_correct_levels():
    df = synthetic_5m(days=1, seed=3)
    prepared = OpeningRangeBreakout({"range_minutes": 30}).prepare(df)
    emits = prepared.filter(pl.col("enter_long"))
    assert emits.height == 1
    row = emits.to_dicts()[0]
    # emit on the 09:55 bar (completes at 10:00)
    assert row["ts_ny"].hour == 9 and row["ts_ny"].minute == 55
    window = df.head(6)  # 09:30..09:55 bars = first 30 minutes
    assert row["entry_price_long_adj"] == window["high_adj"].max() + 0.25
    assert row["entry_price_short_adj"] == window["low_adj"].min() - 0.25
    assert row["stop_long_adj"] == row["entry_price_short_adj"]


def test_pdhl_levels_are_previous_day_extremes():
    df = synthetic_frame(PrevDayLevelBreakout)
    prepared = PrevDayLevelBreakout().prepare(df)
    d2 = date(2024, 1, 16)
    d1_bars = df.filter(pl.col("trading_date") == date(2024, 1, 15))
    emit = prepared.filter((pl.col("trading_date") == d2) & pl.col("enter_long"))
    assert emit.height == 1
    row = emit.to_dicts()[0]
    assert row["entry_price_long_adj"] == d1_bars["high_adj"].max() + 0.25
    assert row["entry_price_short_adj"] == d1_bars["low_adj"].min() - 0.25


def test_ema_trend_signals_are_edges():
    df = synthetic_5m(days=3, seed=5)
    prepared = EmaTrend().prepare(df)
    # no two consecutive identical entry signals (cross = edge by construction)
    for c in ("enter_long", "enter_short"):
        flags = prepared[c].to_list()
        assert not any(a and b for a, b in zip(flags, flags[1:])), c


def test_bollinger_requires_low_adx_regime():
    df = synthetic_5m(days=3, seed=9)
    strat = BollingerMeanReversion({"adx_max": 0.0})  # impossible regime
    prepared = strat.prepare(df)
    assert prepared.filter(pl.col("enter_long") | pl.col("enter_short")).height == 0

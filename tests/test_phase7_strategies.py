from __future__ import annotations

from datetime import date

import polars as pl
import pytest

from src.strategies.afternoon import AfternoonRangeBreakout
from src.strategies.indicators import prev_day_context
from src.strategies.nr_compression import NrCompressionOrb
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.orb_filtered import FilteredOrb
from tests.test_indicators import synthetic_5m
from tests.test_strategies import actionable_view

NEW_STRATEGIES = [FilteredOrb, NrCompressionOrb, AfternoonRangeBreakout]


@pytest.mark.parametrize("cls", NEW_STRATEGIES, ids=lambda c: c.name)
def test_no_look_ahead(cls):
    df = synthetic_5m(days=4, seed=11)
    strat = cls()
    full = actionable_view(strat.prepare(df))
    for k in (len(df) // 3, len(df) // 2, len(df) - 5):
        trunc = actionable_view(strat.prepare(df.head(k)))
        assert trunc.equals(full.head(k)), f"{cls.name} leaks future data at row {k}"


# ---------------------------------------------------------------- FilteredOrb

def test_filtered_orb_defaults_match_base_orb():
    """All gates off -> identical actionable signals to the validated ORB."""
    df = synthetic_5m(days=4, seed=11)
    base = actionable_view(OpeningRangeBreakout().prepare(df))
    filt = actionable_view(FilteredOrb().prepare(df))
    # base ORB trades from day 1; FilteredOrb needs one day of vol_ref warmup
    d1 = df["trading_date"][0]
    warm = df.with_row_index().filter(pl.col("trading_date") != d1)["index"].min()
    assert filt.slice(warm).equals(base.slice(warm))
    # warmup day must not trade (vol_ref unknown), never trade MORE than base
    assert filt["enter_long"].sum() <= base["enter_long"].sum()


def test_filtered_orb_impossible_band_blocks_all_entries():
    df = synthetic_5m(days=4, seed=11)
    p = FilteredOrb({"min_width_ratio": 5.0, "max_width_ratio": 5.1}).prepare(df)
    assert p.filter(pl.col("enter_long") | pl.col("enter_short")).height == 0


def test_filtered_orb_skip_weekdays():
    df = synthetic_5m(days=3, seed=7)  # Mon 2024-01-15 .. Wed 2024-01-17
    p = FilteredOrb({"skip_weekdays": (2,)}).prepare(df)  # skip Tuesday
    tue = p.filter(pl.col("trading_date") == date(2024, 1, 16))
    assert tue.filter(pl.col("enter_long") | pl.col("enter_short")).height == 0
    wed = p.filter(pl.col("trading_date") == date(2024, 1, 17))
    assert wed.filter(pl.col("enter_long")).height == 1


def test_filtered_orb_exit_minute_sets_exit_flags():
    df = synthetic_5m(days=2, seed=7)
    p = FilteredOrb({"exit_minute": 13 * 60}).prepare(df)  # flat at 13:00
    flagged = p.filter(pl.col("exit_long"))
    mods = (
        flagged["ts_ny"].dt.hour().cast(pl.Int32) * 60
        + flagged["ts_ny"].dt.minute().cast(pl.Int32)
    )
    # first flagged bar opens at 12:55 (completes 13:00); all later bars too
    assert mods.min() == 13 * 60 - 5
    per_day = p.filter(
        (pl.col("ts_ny").dt.hour() >= 13) & pl.col("exit_long").not_()
    )
    assert per_day.height == 0


def test_filtered_orb_width_gate_uses_prev_day_vol():
    """Widening yesterday's range should flip today's gate for a tight band."""
    df = synthetic_5m(days=2, seed=3)
    d1 = df["trading_date"][0]
    ctx = prev_day_context(df)
    ref = ctx.filter(pl.col("vol_ref").is_not_null())["vol_ref"][0]
    orb = OpeningRangeBreakout().prepare(df)
    emit = orb.filter(pl.col("enter_long") & (pl.col("trading_date") != d1))
    width = float(emit["or_high"][0] - emit["or_low"][0])
    ratio = width / ref
    tight = FilteredOrb(
        {"min_width_ratio": ratio - 0.01, "max_width_ratio": ratio + 0.01}
    ).prepare(df)
    assert tight.filter(pl.col("enter_long")).height == 1
    shifted = FilteredOrb(
        {"min_width_ratio": ratio + 0.01, "max_width_ratio": ratio + 0.02}
    ).prepare(df)
    assert shifted.filter(pl.col("enter_long")).height == 0


# ------------------------------------------------------------ NrCompressionOrb

def test_prev_day_context_flags():
    df = synthetic_5m(days=4, seed=11)
    ctx = prev_day_context(df, vol_ref_days=3, nr_n=2)
    assert ctx.height == 4
    # day 1 has no prior data
    assert ctx["vol_ref"][0] is None and ctx["nr_flag"][0] is None
    # hand-check nr_flag on day 3: prev day (day 2) narrowest of days 1-2?
    ranges = (
        df.group_by("trading_date")
        .agg((pl.col("high_adj").max() - pl.col("low_adj").min()).alias("r"))
        .sort("trading_date")["r"]
        .to_list()
    )
    assert ctx["nr_flag"][2] == (ranges[1] <= min(ranges[0], ranges[1]))


def test_nr7_orb_gates_on_compression():
    df = synthetic_5m(days=4, seed=11)
    base = OpeningRangeBreakout().prepare(df)
    gated = NrCompressionOrb({"nr_n": 2, "mode": "nr"}).prepare(df)
    ctx = prev_day_context(df, nr_n=2)
    allowed = set(
        ctx.filter(pl.col("nr_flag").fill_null(False))["trading_date"].to_list()
    )
    got = set(gated.filter(pl.col("enter_long"))["trading_date"].to_list())
    want = set(
        base.filter(pl.col("enter_long"))["trading_date"].to_list()
    ) & allowed
    assert got == want


def test_nr7_orb_unknown_mode_raises():
    with pytest.raises(ValueError):
        NrCompressionOrb({"mode": "bogus"}).prepare(synthetic_5m(days=2))


# ------------------------------------------------------- AfternoonRangeBreakout

def test_afternoon_emits_at_range_completion_with_correct_levels():
    df = synthetic_5m(days=1, seed=3)
    p = AfternoonRangeBreakout({"with_trend_filter": False}).prepare(df)
    emits = p.filter(pl.col("enter_long"))
    assert emits.height == 1
    row = emits.to_dicts()[0]
    assert row["ts_ny"].hour == 13 and row["ts_ny"].minute == 55
    window = df.filter(
        (pl.col("ts_ny").dt.hour() == 13)
    )
    assert row["entry_price_long_adj"] == window["high_adj"].max() + 0.25
    assert row["entry_price_short_adj"] == window["low_adj"].min() - 0.25
    assert row["stop_long_adj"] == row["entry_price_short_adj"]
    risk = window["high_adj"].max() - window["low_adj"].min()
    assert row["target_long_adj"] == pytest.approx(
        row["entry_price_long_adj"] + 1.5 * risk
    )


def test_afternoon_trend_filter_takes_one_side_only():
    df = synthetic_5m(days=3, seed=5)
    p = AfternoonRangeBreakout({"with_trend_filter": True}).prepare(df)
    emits = p.filter(pl.col("enter_long") | pl.col("enter_short"))
    for row in emits.to_dicts():
        assert not (row["enter_long"] and row["enter_short"])
        if row["enter_long"]:
            assert row["close_adj"] > row["_vwap"]
        else:
            assert row["close_adj"] < row["_vwap"]

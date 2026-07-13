from __future__ import annotations

import math
from datetime import date, timedelta

import polars as pl
import pytest

from src.evaluation.consistency import consistency_metrics
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.orb_filtered import FilteredOrb
from tests.test_consistency import make_daily
from tests.test_indicators import synthetic_5m
from tests.test_strategies import actionable_view


# ------------------------------------------------- tail metrics (consistency)

def test_p95_daily_loss_is_5th_percentile():
    # 21 days: interpolation index (21-1)*0.05 = 1.0 -> exactly sorted[1]
    m = consistency_metrics(make_daily([-200.0, -100.0] + [10.0] * 19))
    assert m["p95_daily_loss"] == pytest.approx(-100.0, abs=1e-6)


def test_worst_20d_window_hand_check():
    # 30 days of +50 then 20 days of -100: worst 20-day window = -2000
    m = consistency_metrics(make_daily([50.0] * 30 + [-100.0] * 20))
    assert m["worst_20d_window"] == pytest.approx(-2000.0)
    # all-positive series: worst window is still positive
    m2 = consistency_metrics(make_daily([50.0] * 40))
    assert m2["worst_20d_window"] == pytest.approx(20 * 50.0)


def test_worst_20d_window_short_series_falls_back_to_total():
    m = consistency_metrics(make_daily([10.0, -5.0, 3.0, 8.0, -1.0]))
    assert m["worst_20d_window"] == pytest.approx(15.0)


# ------------------------------------------------------- stop cap (FilteredOrb)

def test_max_risk_points_tightens_wide_stops_only():
    df = synthetic_5m(days=3, seed=11)
    base = FilteredOrb().prepare(df)
    capped = FilteredOrb({"max_risk_points": 5.0}).prepare(df)
    b = base.filter(pl.col("enter_long"))
    c = capped.filter(pl.col("enter_long"))
    assert b.height == c.height and b.height > 0
    for rb, rc in zip(b.to_dicts(), c.to_dicts()):
        width_risk = rb["entry_price_long_adj"] - rb["stop_long_adj"]
        assert rc["entry_price_long_adj"] == rb["entry_price_long_adj"]
        # capped stop distance never exceeds 5 points and never loosens
        assert rc["entry_price_long_adj"] - rc["stop_long_adj"] <= 5.0 + 1e-9
        assert rc["stop_long_adj"] >= rb["stop_long_adj"] - 1e-9
        if width_risk <= 5.0:
            assert rc["stop_long_adj"] == pytest.approx(rb["stop_long_adj"])
        # short side mirrors
        assert rc["stop_short_adj"] - rc["entry_price_short_adj"] <= 5.0 + 1e-9
        # targets unchanged (anchored to range risk, not capped risk)
        assert rc["target_long_adj"] == pytest.approx(rb["target_long_adj"])
        assert rc["target_short_adj"] == pytest.approx(rb["target_short_adj"])


def test_max_risk_points_none_is_noop():
    df = synthetic_5m(days=3, seed=7)
    a = actionable_view(FilteredOrb().prepare(df))
    b = actionable_view(FilteredOrb({"max_risk_points": None}).prepare(df))
    assert a.equals(b)


def test_max_risk_points_no_lookahead():
    df = synthetic_5m(days=4, seed=11)
    strat = FilteredOrb({"max_risk_points": 4.0})
    full = actionable_view(strat.prepare(df))
    for k in (len(df) // 2, len(df) - 5):
        trunc = actionable_view(strat.prepare(df.head(k)))
        assert trunc.equals(full.head(k))

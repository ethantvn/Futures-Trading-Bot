from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest

from src.evaluation.consistency import (
    consistency_metrics,
    daily_pnl,
    recency_metrics,
    rolling_window_stats,
    year_pnls,
)


def make_daily(pnls: list[float], start: date = date(2024, 1, 1)) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "trading_date": [start + timedelta(days=i) for i in range(len(pnls))],
            "pnl": [float(p) for p in pnls],
        }
    )


def test_daily_pnl_groups_and_sorts():
    trades = pl.DataFrame(
        {
            "trading_date": [date(2024, 1, 2), date(2024, 1, 1), date(2024, 1, 2)],
            "net_pnl": [50.0, -20.0, 10.0],
        }
    )
    d = daily_pnl(trades)
    assert d["trading_date"].to_list() == [date(2024, 1, 1), date(2024, 1, 2)]
    assert d["pnl"].to_list() == [-20.0, 60.0]


def test_daily_pnl_empty_ledger():
    empty = pl.DataFrame(schema={"trading_date": pl.Date, "net_pnl": pl.Float64})
    assert daily_pnl(empty).height == 0


def test_consistency_metrics_too_few_days():
    assert consistency_metrics(make_daily([1, 2, 3])) == {}


def test_perfectly_linear_equity_has_r2_one_and_zero_drawdown():
    m = consistency_metrics(make_daily([100.0] * 30))
    assert m["equity_r2"] == pytest.approx(1.0)
    assert m["max_drawdown"] == 0.0
    assert m["ulcer_index"] == 0.0
    assert math.isnan(m["upi"])  # no drawdown -> UPI undefined
    assert m["max_consec_losing_days"] == 0
    assert m["win_day_rate"] == 1.0


def test_metrics_hand_check_small_series():
    # pnl: +100, -50, -50, +200 -> equity 100, 50, 0, 200
    m = consistency_metrics(make_daily([100, -50, -50, 200, 0]))
    assert m["net_pnl"] == 200.0
    assert m["max_drawdown"] == -100.0          # peak 100 -> trough 0
    assert m["max_consec_losing_days"] == 2
    assert m["worst_day"] == -50.0
    assert m["best_day"] == 200.0
    # ulcer: dd series = 0, -50, -100, 0, 0 -> rms = sqrt((2500+10000)/5)
    assert m["ulcer_index"] == pytest.approx(math.sqrt(12500 / 5))


def test_smoother_series_scores_higher_upi_and_r2():
    rng = np.random.default_rng(1)
    smooth = make_daily(list(rng.normal(30, 40, 252)))
    spiky_vals = list(rng.normal(30, 40, 252))
    # same mean, but inject deep loss clusters
    for i in range(0, 252, 40):
        spiky_vals[i] = -600.0
    spiky = make_daily([v + (600 + 30) / 40 for v in spiky_vals])  # keep mean similar
    ms, mp = consistency_metrics(smooth), consistency_metrics(spiky)
    assert ms["upi"] > mp["upi"]
    assert ms["ulcer_index"] < mp["ulcer_index"]


def test_recency_metrics_windows_subset_full():
    d = make_daily(list(np.linspace(-10, 50, 300)))
    r = recency_metrics(d)
    assert r["full"]["active_days"] == 300
    assert r["last_90d"]["active_days"] == 90
    assert r["last_252d"]["active_days"] == 252
    # last_756d falls back to all 300 available days
    assert r["last_756d"]["active_days"] == 300


def test_rolling_window_stats_flags_bad_era():
    # 126 good days, then 126 bad days
    d = make_daily([50.0] * 126 + [-50.0] * 126)
    s = rolling_window_stats(d, window=126, step=21)
    assert s["n_windows"] == 7
    assert 0.0 < s["negative_share"] <= 0.5
    assert s["worst_window"] == pytest.approx(-126 * 50.0)
    all_good = rolling_window_stats(make_daily([50.0] * 252), window=126, step=21)
    assert all_good["negative_share"] == 0.0


def test_rolling_window_stats_short_series():
    s = rolling_window_stats(make_daily([1.0] * 10), window=126)
    assert s["n_windows"] == 0 and math.isnan(s["negative_share"])


def test_year_pnls():
    d = pl.DataFrame(
        {
            "trading_date": [date(2023, 5, 1), date(2023, 6, 1), date(2024, 1, 5)],
            "pnl": [100.0, -40.0, 25.0],
        }
    )
    assert year_pnls(d) == {2023: 60.0, 2024: 25.0}

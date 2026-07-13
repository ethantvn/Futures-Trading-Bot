from __future__ import annotations

from datetime import date, datetime, timezone

import polars as pl

from src.validation.walk_forward import (
    Fold,
    GridRun,
    make_folds,
    param_grid,
    sensitivity_table,
    slice_trades,
    walk_forward,
)

SCHEMA = {
    "trading_date": pl.Date,
    "entry_ts": pl.Datetime("ns", "UTC"),
    "exit_ts": pl.Datetime("ns", "UTC"),
    "net_pnl": pl.Float64,
    "gross_pnl": pl.Float64,
    "costs": pl.Float64,
    "ambiguous": pl.Boolean,
    "exit_reason": pl.Utf8,
}


def ledger(day_pnls: dict[date, float]) -> pl.DataFrame:
    rows = []
    for d, pnl in day_pnls.items():
        ts = datetime(d.year, d.month, d.day, 15, tzinfo=timezone.utc)
        rows.append(
            {
                "trading_date": d, "entry_ts": ts, "exit_ts": ts,
                "net_pnl": pnl, "gross_pnl": pnl, "costs": 0.0,
                "ambiguous": False, "exit_reason": "target",
            }
        )
    return pl.DataFrame(rows, schema=SCHEMA)


def daily_range(start: date, end: date, pnl: float) -> dict[date, float]:
    """Weekday PnLs with small jitter (constant series has zero daily std,
    which the Sharpe scorer correctly rejects as degenerate)."""
    from datetime import timedelta

    out, d, i = {}, start, 0
    while d <= end:
        if d.weekday() < 5:
            out[d] = pnl * (1.0 + 0.02 * (i % 3))
            i += 1
        d += timedelta(days=1)
    return out


def test_param_grid_cartesian():
    g = param_grid({"a": [1, 2], "b": ["x", "y", "z"]})
    assert len(g) == 6
    assert {"a": 2, "b": "y"} in g


def test_make_folds_tiling():
    folds = make_folds(date(2019, 6, 1), date(2025, 12, 31), 24, 6)
    assert folds[0].train_start == date(2019, 6, 1)
    assert folds[0].train_end == date(2021, 5, 31)
    assert folds[0].test_start == date(2021, 6, 1)
    assert folds[0].test_end == date(2021, 11, 30)
    # consecutive test windows tile with no gap/overlap
    for a, b in zip(folds, folds[1:]):
        assert b.test_start == a.test_end.replace(day=1).replace(
            month=a.test_end.month % 12 + 1,
            year=a.test_end.year + (a.test_end.month == 12),
        )
    assert folds[-1].test_end <= date(2025, 12, 31)


def test_selection_uses_train_only():
    """Combo A wins the train window but loses in test; combo B is flat in
    train and great in test. Look-ahead-free walk-forward must choose A and
    therefore post A's (bad) test result."""
    train_days = daily_range(date(2021, 1, 1), date(2022, 12, 31), 100.0)
    test_days = daily_range(date(2023, 1, 1), date(2023, 6, 30), -50.0)

    a = ledger({**train_days, **test_days})
    b = ledger(
        {
            **{d: -v / 100.0 for d, v in train_days.items()},  # slightly losing in train
            **{d: -10.0 * v for d, v in test_days.items()},    # +500/day in test
        }
    )

    folds = [Fold(date(2021, 1, 1), date(2022, 12, 31), date(2023, 1, 1), date(2023, 6, 30))]
    res = walk_forward(
        [GridRun({"p": "A"}, a), GridRun({"p": "B"}, b)], folds
    )
    assert res.folds[0].chosen_params == {"p": "A"}
    assert res.folds[0].test_net < 0
    assert res.oos_trades["net_pnl"].sum() < 0


def test_oos_ledger_covers_only_test_windows():
    days = daily_range(date(2021, 1, 1), date(2023, 6, 30), 10.0)
    gr = GridRun({"p": 1}, ledger(days))
    folds = [Fold(date(2021, 1, 1), date(2022, 12, 31), date(2023, 1, 1), date(2023, 6, 30))]
    res = walk_forward([gr], folds)
    assert res.oos_trades["trading_date"].min() >= date(2023, 1, 1)
    assert res.oos_trades["trading_date"].max() <= date(2023, 6, 30)
    assert res.final_params == {"p": 1}


def test_insufficient_train_trades_skips_fold():
    sparse = ledger({date(2021, 3, 1): 100.0})  # far below min_trades gate
    folds = [Fold(date(2021, 1, 1), date(2022, 12, 31), date(2023, 1, 1), date(2023, 6, 30))]
    res = walk_forward([GridRun({"p": 1}, sparse)], folds)
    assert res.folds[0].chosen_params is None
    assert res.oos_trades.height == 0


def test_sensitivity_one_at_a_time():
    days = daily_range(date(2021, 1, 1), date(2021, 12, 31), 5.0)
    runs = [
        GridRun({"a": 1, "b": 10}, ledger(days)),
        GridRun({"a": 2, "b": 10}, ledger({d: v * 2 for d, v in days.items()})),
        GridRun({"a": 1, "b": 20}, ledger({d: -v for d, v in days.items()})),
        GridRun({"a": 2, "b": 20}, ledger(days)),  # off-baseline for both sweeps
    ]
    tab = sensitivity_table(runs, {"a": 1, "b": 10}, date(2021, 1, 1), date(2021, 12, 31))
    assert [r["value"] for r in tab["a"]] == [1, 2]        # b fixed at 10
    assert [r["value"] for r in tab["b"]] == [10, 20]      # a fixed at 1
    assert tab["b"][1]["net_pnl"] < 0


def test_slice_trades_inclusive():
    days = daily_range(date(2021, 1, 1), date(2021, 1, 31), 1.0)
    t = slice_trades(ledger(days), date(2021, 1, 4), date(2021, 1, 8))
    assert t.height == 5  # Mon-Fri

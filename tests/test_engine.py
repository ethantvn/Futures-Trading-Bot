from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import polars as pl

from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.strategies.base import SIGNAL_DEFAULTS, with_signal_defaults

COST = CostModel(
    commission_per_side=0.62,
    exchange_fees_per_side=0.37,
    slippage_ticks=1,
    tick_size=0.25,
    point_value=2.0,
)
D = date(2024, 1, 16)


def exec_bars(ohlc: list[tuple[float, float, float, float]]) -> pl.DataFrame:
    """1m bars starting 09:30 NY (14:30 UTC, winter) on one trading day."""
    n = len(ohlc)
    ts = [
        datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=i)
        for i in range(n)
    ]
    return pl.DataFrame(
        {
            "ts_utc": ts,
            "open": [b[0] for b in ohlc],
            "high": [b[1] for b in ohlc],
            "low": [b[2] for b in ohlc],
            "close": [b[3] for b in ohlc],
            "volume": [10] * n,
            "trading_date": [D] * n,
            "symbol": ["MNQH4"] * n,
            "session": ["rth"] * n,
            "adj_offset": [0.0] * n,
        },
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date},
    ).with_columns(pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny"))


def signal_frame(rows: list[dict]) -> pl.DataFrame:
    base = pl.DataFrame(
        {"ts_utc": [r["ts"] for r in rows], "trading_date": [D] * len(rows)},
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date},
    )
    df = with_signal_defaults(base)
    for c in SIGNAL_DEFAULTS:
        vals = [r.get(c) for r in rows]
        if any(v is not None for v in vals):
            dtype = df[c].dtype
            df = df.with_columns(pl.Series(c, vals, dtype=dtype))
    return df


FLAT = tuple([100.0] * 4)


def test_stop_entry_target_exit_hand_verified():
    bars = exec_bars(
        [
            FLAT, FLAT, FLAT, FLAT, FLAT,                     # 09:30-09:34 signal bucket
            (100.5, 101.5, 100.4, 101.4),                     # 09:35: stop 101 triggers -> 101.25
            (101.4, 102.0, 101.2, 101.9),
            (101.9, 102.8, 101.8, 102.7),
            (102.7, 103.5, 102.6, 103.0),                     # 09:38: target 103 trades through -> 103.0
            (103.0, 103.2, 102.9, 103.1),
        ]
    )
    sig = signal_frame(
        [
            {
                "ts": datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc),
                "enter_long": True,
                "entry_kind": "stop",
                "entry_price_long_adj": 101.0,
                "stop_long_adj": 99.0,
                "target_long_adj": 103.0,
            }
        ]
    )
    res = run_backtest(bars, sig, 5, COST, EngineConfig(qty=1), "t")
    assert res.trades.height == 1
    t = res.trades.to_dicts()[0]
    assert t["entry_px"] == 101.25          # stop 101 + 1 tick slippage
    assert t["exit_px"] == 103.0            # target limit, no slippage
    assert t["exit_reason"] == "target"
    assert t["entry_ts"] == datetime(2024, 1, 16, 14, 35, tzinfo=timezone.utc)
    assert t["exit_ts"] == datetime(2024, 1, 16, 14, 38, tzinfo=timezone.utc)
    assert t["gross_pnl"] == (103.0 - 101.25) * 2.0    # $3.50
    assert t["costs"] == 2 * (0.62 + 0.37)             # $1.98
    assert abs(t["net_pnl"] - 1.52) < 1e-9


def test_signal_before_completion_cannot_fill_early():
    """A 5m signal bar opening 09:30 completes at 09:35; the 09:34 breakout
    minute must NOT fill the order (look-ahead guard)."""
    bars = exec_bars(
        [
            FLAT, FLAT, FLAT,
            (100.0, 105.0, 100.0, 104.0),   # 09:33: breaks the 101 stop level
            (104.0, 104.0, 104.0, 104.0),   # 09:34
            (104.0, 104.1, 103.9, 104.0),   # 09:35: first eligible bar -> gap fill at open
        ]
    )
    sig = signal_frame(
        [
            {
                "ts": datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc),
                "enter_long": True,
                "entry_kind": "stop",
                "entry_price_long_adj": 101.0,
                "stop_long_adj": 99.0,
            }
        ]
    )
    res = run_backtest(bars, sig, 5, COST, EngineConfig(qty=1), "t")
    assert res.trades.height == 1
    t = res.trades.to_dicts()[0]
    # filled at 09:35 open (gap through stop) + slip, never on the 09:33 bar
    assert t["entry_ts"] == datetime(2024, 1, 16, 14, 35, tzinfo=timezone.utc)
    assert t["entry_px"] == 104.25


def test_flat_time_forces_exit():
    bars = exec_bars([FLAT] * 5 + [(100.0, 100.5, 99.8, 100.2)] * 30)
    sig = signal_frame(
        [
            {
                "ts": datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc),
                "enter_long": True,
                "entry_kind": "market",
                "stop_long_adj": 90.0,
            }
        ]
    )
    # flat at 09:50 NY
    res = run_backtest(bars, sig, 5, COST, EngineConfig(qty=1, flat_time="09:50"), "t")
    assert res.trades.height == 1
    t = res.trades.to_dicts()[0]
    assert t["exit_reason"] == "eod"
    assert t["exit_ts"] == datetime(2024, 1, 16, 14, 50, tzinfo=timezone.utc)
    assert t["exit_px"] == 100.0 - 0.25  # market out at open - slippage


def test_max_trades_per_day_blocks_reentry():
    bars = exec_bars([FLAT] * 5 + [(100.0, 100.1, 98.0, 98.2)] * 3 + [FLAT] * 12)
    mk = {
        "enter_long": True,
        "entry_kind": "market",
        "stop_long_adj": 99.0,   # stopped out quickly
    }
    sig = signal_frame(
        [
            {"ts": datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc), **mk},
            {"ts": datetime(2024, 1, 16, 14, 40, tzinfo=timezone.utc), **mk},
        ]
    )
    res = run_backtest(bars, sig, 5, COST, EngineConfig(qty=1, max_trades_per_day=1), "t")
    assert res.trades.height == 1  # second signal blocked


def test_oco_pair_first_fill_cancels_sibling():
    bars = exec_bars(
        [
            FLAT, FLAT, FLAT, FLAT, FLAT,
            (100.0, 100.2, 98.7, 98.8),     # 09:35: short stop 99 triggers
            (98.8, 101.5, 98.7, 101.4),     # would trigger the long stop if alive
            (101.4, 101.5, 101.3, 101.4),
        ]
    )
    sig = signal_frame(
        [
            {
                "ts": datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc),
                "enter_long": True,
                "enter_short": True,
                "entry_kind": "stop",
                "entry_price_long_adj": 101.0,
                "entry_price_short_adj": 99.0,
                "stop_long_adj": 99.0,
                "stop_short_adj": 101.0,
            }
        ]
    )
    res = run_backtest(bars, sig, 5, COST, EngineConfig(qty=1), "t")
    assert res.trades.height == 1
    t = res.trades.to_dicts()[0]
    assert t["side"] == -1
    assert t["entry_px"] == 99.0 - 0.25
    # the long sibling died on the short fill; the 09:36 spike exits via stop
    assert t["exit_reason"] == "stop"
    assert t["exit_ts"] == datetime(2024, 1, 16, 14, 36, tzinfo=timezone.utc)


def test_adjusted_to_raw_conversion():
    """Signals in adjusted space must fill at raw prices via adj_offset."""
    bars = exec_bars(
        [FLAT] * 5 + [(100.5, 101.5, 100.4, 101.4)] + [(101.4, 103.6, 101.3, 103.5)] * 4
    ).with_columns(pl.lit(50.0).alias("adj_offset"))  # adjusted = raw + 50
    sig = signal_frame(
        [
            {
                "ts": datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc),
                "enter_long": True,
                "entry_kind": "stop",
                "entry_price_long_adj": 151.0,   # raw 101
                "stop_long_adj": 149.0,          # raw 99
                "target_long_adj": 153.0,        # raw 103
            }
        ]
    )
    res = run_backtest(bars, sig, 5, COST, EngineConfig(qty=1), "t")
    t = res.trades.to_dicts()[0]
    assert t["entry_px"] == 101.25   # raw fill
    assert t["exit_px"] == 103.0

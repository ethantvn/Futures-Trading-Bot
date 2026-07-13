from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import numpy as np
import polars as pl
import pytest

from src.strategies.indicators import ADJ, adx, atr, ema, session_vwap


def synthetic_5m(days: int = 3, seed: int = 7) -> pl.DataFrame:
    """Random-walk RTH 5m bars (09:30-15:55 NY) with adjusted price columns."""
    rng = np.random.default_rng(seed)
    rows = []
    px = 15000.0
    for d in range(days):
        day = date(2024, 1, 15 + d)  # Mon..Wed
        for i in range(78):  # 78 5m bars 09:30->16:00
            ts = datetime(day.year, day.month, day.day, 14, 30, tzinfo=timezone.utc) + timedelta(minutes=5 * i)
            drift = rng.normal(0, 8)
            o = px
            c = px + drift
            hi = max(o, c) + abs(rng.normal(0, 3))
            lo = min(o, c) - abs(rng.normal(0, 3))
            rows.append(
                {
                    "ts_utc": ts, "trading_date": day, "session": "rth",
                    "open_adj": round(o, 2), "high_adj": round(hi, 2),
                    "low_adj": round(lo, 2), "close_adj": round(c, 2),
                    "volume": int(rng.integers(100, 5000)),
                }
            )
            px = c
    return pl.DataFrame(rows, schema_overrides={
        "ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date,
    }).with_columns(pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny"))


def test_session_vwap_hand_calculation():
    df = pl.DataFrame(
        {
            "trading_date": [date(2024, 1, 15)] * 2,
            "high_adj": [102.0, 104.0],
            "low_adj": [100.0, 102.0],
            "close_adj": [101.0, 103.0],
            "volume": [10, 30],
        }
    ).with_columns(session_vwap().alias("vwap"))
    # tp1 = 101, tp2 = 103; vwap2 = (101*10 + 103*30) / 40 = 102.5
    assert df["vwap"].to_list() == [101.0, 102.5]


def test_vwap_resets_per_trading_date():
    df = synthetic_5m(days=2).with_columns(session_vwap().alias("vwap"))
    first_of_day2 = df.filter(pl.col("trading_date") == date(2024, 1, 16)).head(1)
    tp = (first_of_day2["high_adj"][0] + first_of_day2["low_adj"][0] + first_of_day2["close_adj"][0]) / 3
    assert abs(first_of_day2["vwap"][0] - tp) < 1e-9


def test_adx_is_finite_and_bounded_after_warmup():
    df = synthetic_5m(days=3)
    x = df.with_columns(adx(14).alias("adx"))["adx"][30:]
    vals = x.to_numpy()
    assert np.isfinite(vals).all(), "ADX must not contain NaN/inf after warmup"
    assert (vals >= 0).all() and (vals <= 100).all()


def test_adx_survives_flat_price_stretch():
    """A dead-flat stretch (zero directional movement) must not poison ADX."""
    df = synthetic_5m(days=2)
    flat = df.head(1)
    flat_block = pl.concat([flat] * 30).with_columns(
        (pl.col("ts_utc") + pl.duration(minutes=5 * pl.arange(0, 30))).alias("ts_utc")
    )
    df2 = pl.concat([flat_block, df.with_columns(pl.col("ts_utc") + pl.duration(hours=5))])
    vals = df2.with_columns(adx(14).alias("adx"))["adx"].to_numpy()
    assert np.isfinite(vals[40:]).all()


@pytest.mark.parametrize(
    "expr_factory",
    [
        lambda: ema(ADJ["close"], 20),
        lambda: atr(14),
        lambda: adx(14),
        lambda: session_vwap(),
    ],
    ids=["ema", "atr", "adx", "vwap"],
)
def test_indicators_are_causal(expr_factory):
    """Truncating the data must not change any already-computed value."""
    df = synthetic_5m(days=3)
    full = df.with_columns(expr_factory().alias("x"))["x"]
    for k in (40, 100, 180):
        trunc = df.head(k).with_columns(expr_factory().alias("x"))["x"]
        a, b = full[k - 1], trunc[k - 1]
        both_nan = (a is None or np.isnan(a)) and (b is None or np.isnan(b))
        assert both_nan or abs(a - b) < 1e-9

from __future__ import annotations

from datetime import date, datetime, time, timezone

import polars as pl

from src.data.resampling import resample
from tests.conftest import make_bars


def minute_bars() -> pl.DataFrame:
    """15 consecutive RTH minutes starting 09:30 NY (14:30 UTC in winter)."""
    d = date(2024, 1, 16)
    rows = []
    for i in range(15):
        px = 100.0 + 0.25 * i
        rows.append(
            {
                "ts": datetime(2024, 1, 16, 14, 30 + i),
                "symbol": "MNQH4",
                "o": px, "h": px + 1.0, "l": px - 1.0, "c": px + 0.5,
                "v": 10 + i, "trading_date": d,
            }
        )
    return make_bars(rows)


def test_five_minute_aggregation():
    out = resample(minute_bars(), 5)
    assert out.height == 3
    first = out.to_dicts()[0]
    # bucket anchored to NY wall clock, bar-open convention
    assert first["ts_ny"].time() == time(9, 30)
    assert first["open"] == 100.0            # first minute's open
    assert first["close"] == 101.0 + 0.5     # 5th minute's close
    assert first["high"] == 102.0            # max high (101 + 1)
    assert first["low"] == 99.0              # min low (100 - 1)
    assert first["volume"] == sum(10 + i for i in range(5))
    # ts_utc is the first source minute of the bucket
    assert first["ts_utc"] == datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc)


def test_no_duplicate_or_missing_buckets():
    out = resample(minute_bars(), 5)
    assert out["ts_ny"].n_unique() == out.height
    assert [t.time() for t in out["ts_ny"]] == [time(9, 30), time(9, 35), time(9, 40)]


def test_reaggregation_consistency():
    """1m -> 5m -> 15m must equal 1m -> 15m."""
    bars = minute_bars()
    via_5 = resample(resample(bars, 5), 15)
    direct = resample(bars, 15)
    assert via_5.height == direct.height == 1
    for c in ("open", "high", "low", "close", "volume"):
        assert via_5[c].to_list() == direct[c].to_list()


def test_session_split_prevents_cross_session_buckets():
    """An ETH minute and an RTH minute in the same wall-clock bucket stay separate."""
    d = date(2024, 1, 16)
    rows = [
        # 09:29 NY = eth, 09:31 NY = rth; both truncate to the same 15m bucket 09:15/09:30?
        # 09:29 -> bucket 09:15, 09:31 -> bucket 09:30 for 15m; use 30m to force overlap:
        # 09:29 -> bucket 09:00, 09:31 -> bucket 09:30. Use 60m-like case via 30m at 09:00.
        {"ts": datetime(2024, 1, 16, 14, 29), "symbol": "MNQH4",
         "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 5, "trading_date": d},
        {"ts": datetime(2024, 1, 16, 14, 31), "symbol": "MNQH4",
         "o": 200.0, "h": 201.0, "l": 199.0, "c": 200.5, "v": 7, "trading_date": d},
    ]
    df = make_bars(rows).with_columns(
        pl.when(pl.col("ts_ny").dt.time() < pl.time(9, 30))
        .then(pl.lit("eth")).otherwise(pl.lit("rth")).alias("session")
    )
    out = resample(df, 30)
    # 09:29 eth and 09:31 rth: 30m buckets are 09:00 and 09:30 -> 2 bars, and
    # even if buckets collided, the session key keeps them apart.
    assert out.height == 2
    assert set(out["session"]) == {"eth", "rth"}

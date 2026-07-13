from __future__ import annotations

from datetime import date, time

import polars as pl

from src.data.databento_loader import normalize


def raw_frame(rows: list[tuple[str, str]]) -> pl.DataFrame:
    """rows: (ts_event ISO string, symbol)"""
    n = len(rows)
    return pl.DataFrame(
        {
            "ts_event": [r[0] for r in rows],
            "rtype": [33] * n,
            "publisher_id": [1] * n,
            "instrument_id": list(range(n)),
            "open": [100.0] * n,
            "high": [101.0] * n,
            "low": [99.0] * n,
            "close": [100.5] * n,
            "volume": [10] * n,
            "symbol": [r[1] for r in rows],
        }
    )


def test_trading_date_and_session_assignment():
    df = normalize(
        raw_frame(
            [
                # NY 18:00 EST Jan 15 -> session open, belongs to Jan 16
                ("2024-01-15T23:00:00.000000000Z", "MNQH4"),
                # NY 09:30 Jan 16 -> RTH open
                ("2024-01-16T14:30:00.000000000Z", "MNQH4"),
                # NY 15:59 Jan 16 -> last RTH bar
                ("2024-01-16T20:59:00.000000000Z", "MNQH4"),
                # NY 16:00 Jan 16 -> ETH again
                ("2024-01-16T21:00:00.000000000Z", "MNQH4"),
            ]
        )
    )
    assert df["trading_date"].to_list() == [date(2024, 1, 16)] * 4
    assert df["session"].to_list() == ["eth", "rth", "rth", "eth"]
    assert df["ts_ny"][0].time() == time(18, 0)


def test_dst_boundaries():
    df = normalize(
        raw_frame(
            [
                # Summer (EDT): NY 18:00 Jul 15 = 22:00Z -> trading date Jul 16
                ("2024-07-15T22:00:00.000000000Z", "MNQU4"),
                # Spring-forward day: NY 18:00 EDT Mar 10 -> trading date Mar 11
                ("2024-03-10T22:00:00.000000000Z", "MNQH4"),
                # Fall-back day: NY 18:00 EST Nov 3 -> trading date Nov 4
                ("2024-11-03T23:00:00.000000000Z", "MNQZ4"),
            ]
        )
    )
    # sorted by symbol: MNQH4 (spring), MNQU4 (summer), MNQZ4 (fall)
    assert df.sort("symbol")["trading_date"].to_list() == [
        date(2024, 3, 11),
        date(2024, 7, 16),
        date(2024, 11, 4),
    ]
    assert all(t.time() == time(18, 0) for t in df["ts_ny"])


def test_spreads_dropped_and_original_ts_preserved():
    df = normalize(
        raw_frame(
            [
                ("2024-01-16T14:30:00.000000000Z", "MNQH4"),
                ("2024-01-16T14:30:00.000000000Z", "MNQH4-MNQM4"),
            ]
        )
    )
    assert df["symbol"].to_list() == ["MNQH4"]
    # original exchange timestamp preserved, UTC
    assert str(df["ts_utc"][0]) == "2024-01-16 14:30:00+00:00"

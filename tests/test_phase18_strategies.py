"""Phase 18 strategy smoke tests."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import polars as pl
import pytest

from src.strategies.atr_breakout import AtrBreakout
from src.strategies.donchian_breakout import DonchianBreakout
from src.strategies.macd_momentum import MacdMomentum
from src.strategies.orb_fade import OpeningRangeFade
from src.strategies.roc_momentum import RocMomentum
from src.strategies.rsi_fade import RsiFade
from src.strategies.session_tod import SessionTodOrb
from src.strategies.vwap_reversion import VwapReversion
from tests.test_indicators import synthetic_5m

PHASE18 = [
    OpeningRangeFade,
    VwapReversion,
    DonchianBreakout,
    RsiFade,
    AtrBreakout,
    MacdMomentum,
    RocMomentum,
    SessionTodOrb,
]


@pytest.mark.parametrize("cls", PHASE18, ids=lambda c: c.name)
def test_phase18_prepare_smoke(cls):
    df = synthetic_5m(days=3, seed=18)
    prepared = cls().prepare(df)
    assert prepared.height == df.height
    for col in ("enter_long", "enter_short"):
        assert prepared.schema[col] == pl.Boolean
        assert prepared[col].fill_null(False).null_count() == 0


def test_orb_fade_emits_short_on_failed_or_high_break():
    d = date(2024, 1, 16)  # Tuesday
    base = datetime(2024, 1, 16, 14, 30, tzinfo=timezone.utc)  # 09:30 ET
    rows = []

    def add(i: int, o: float, h: float, l: float, c: float, v: int = 1000) -> None:
        rows.append(
            {
                "ts_utc": base + timedelta(minutes=5 * i),
                "trading_date": d,
                "session": "rth",
                "open_adj": o,
                "high_adj": h,
                "low_adj": l,
                "close_adj": c,
                "volume": v,
            }
        )

    # Opening range bars (09:30-09:55): OR high=101, OR low=99
    add(0, 100.0, 100.5, 99.5, 100.0)
    add(1, 100.0, 101.0, 99.8, 100.4)
    add(2, 100.4, 100.9, 99.9, 100.2)
    add(3, 100.2, 100.8, 99.2, 99.8)
    add(4, 99.8, 100.6, 99.0, 99.7)
    add(5, 99.7, 100.2, 99.1, 99.9)
    # 10:00 bar: breaks above OR high intrabar, closes back below -> short fade signal
    add(6, 99.9, 101.8, 99.6, 100.5)
    add(7, 100.5, 100.7, 99.7, 100.0)
    for i in range(8, 30):
        add(i, 100.0, 100.3, 99.7, 100.0, 500)

    df = pl.DataFrame(
        rows,
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date},
    ).with_columns(pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny"))

    prepared = OpeningRangeFade().prepare(df)
    assert prepared.filter(pl.col("enter_short")).height >= 1

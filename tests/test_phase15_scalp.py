"""Phase 15 scalp strategies — no-lookahead + basic emission checks."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import numpy as np
import polars as pl
import pytest

from src.strategies.fvg_scalp import FvgScalp
from src.strategies.fvg_volume_scalp import FvgVolumeScalp
from src.strategies.vwap_band_scalp import VwapBandScalp
from src.strategies.volume_spike_scalp import VolumeSpikeScalp
from tests.test_strategies import FLAG_COLS, PRICE_COLS, actionable_view

SCALP_STRATEGIES = [FvgScalp, VwapBandScalp, VolumeSpikeScalp, FvgVolumeScalp]


def synthetic_1m(days: int = 3, seed: int = 21) -> pl.DataFrame:
    """Random-walk RTH 1m bars (09:30–15:59 NY)."""
    rng = np.random.default_rng(seed)
    rows = []
    px = 15000.0
    for d in range(days):
        day = date(2024, 1, 15 + d)
        for i in range(390):  # 09:30 → 16:00
            ts = datetime(day.year, day.month, day.day, 14, 30, tzinfo=timezone.utc) + timedelta(
                minutes=i
            )
            drift = rng.normal(0, 4)
            o = px
            c = px + drift
            hi = max(o, c) + abs(rng.normal(0, 2))
            lo = min(o, c) - abs(rng.normal(0, 2))
            rows.append(
                {
                    "ts_utc": ts,
                    "trading_date": day,
                    "session": "rth",
                    "open_adj": round(o, 2),
                    "high_adj": round(hi, 2),
                    "low_adj": round(lo, 2),
                    "close_adj": round(c, 2),
                    "volume": int(rng.integers(50, 3000)),
                }
            )
            px = c
    return pl.DataFrame(
        rows,
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date},
    ).with_columns(
        pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny")
    )


@pytest.mark.parametrize("cls", SCALP_STRATEGIES, ids=lambda c: c.name)
def test_no_look_ahead(cls):
    df = synthetic_1m(days=4, seed=11)
    # Loosen floors so synthetic noise can emit
    params = {"min_gap_points": 1.0, "min_stop_points": 1.0, "z_threshold": 0.5}
    strat = cls(params)
    full = actionable_view(strat.prepare(df))
    for k in (len(df) // 3, len(df) // 2, len(df) - 5):
        trunc = actionable_view(strat.prepare(df.head(k)))
        assert trunc.equals(full.head(k)), f"{cls.name} leaks future data at row {k}"


def test_fvg_detects_hand_crafted_bull_gap():
    """Three bars: bar0 high=100, bar2 low=110 → 10pt bullish FVG."""
    day = date(2024, 1, 15)
    base = datetime(2024, 1, 15, 15, 0, tzinfo=timezone.utc)  # 10:00 ET

    def bar(i, o, h, l, c, vol=1000):
        ts = base + timedelta(minutes=i)
        return {
            "ts_utc": ts,
            "trading_date": day,
            "session": "rth",
            "open_adj": o,
            "high_adj": h,
            "low_adj": l,
            "close_adj": c,
            "volume": vol,
        }

    rows = [
        bar(0, 99, 100, 98, 99.5),
        bar(1, 100, 108, 99.5, 107),  # displacement
        bar(2, 108, 112, 110, 111),  # gap: low 110 > prior high 100
    ]
    # pad with flat bars so session window + rolling ok
    for i in range(3, 40):
        rows.append(bar(i, 111, 111.5, 110.5, 111, 200))
    df = pl.DataFrame(
        rows,
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date},
    ).with_columns(
        pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny")
    )
    prep = FvgScalp(
        {
            "min_gap_points": 5.0,
            "min_stop_points": 5.0,
            "entry_start_minute": 9 * 60,
            "entry_end_minute": 16 * 60,
            "tick": 0.25,
        }
    ).prepare(df)
    emits = prep.filter(pl.col("enter_long"))
    assert emits.height >= 1
    row = emits.head(1).to_dicts()[0]
    assert abs(row["entry_price_long_adj"] - 105.0) < 1e-6  # mid of 100–110
    assert row["stop_long_adj"] <= 100.0


def test_volume_spike_emits_on_z_spike():
    df = synthetic_1m(days=2, seed=5)
    # Force a huge volume bar mid-session
    df = df.with_columns(
        pl.when(pl.arange(0, pl.len()) == 100)
        .then(pl.lit(50_000))
        .otherwise(pl.col("volume"))
        .alias("volume")
    )
    prep = VolumeSpikeScalp(
        {"z_threshold": 2.0, "vol_lookback": 20, "min_stop_points": 5.0, "range_mult": 0.0}
    ).prepare(df)
    assert prep.filter(pl.col("enter_long") | pl.col("enter_short")).height >= 1


def test_vwap_band_prepare_columns():
    df = synthetic_1m(days=2)
    prep = VwapBandScalp({"min_stop_points": 5.0, "band_k": 1.0}).prepare(df)
    for c in FLAG_COLS + PRICE_COLS + ["expire_minutes", "entry_kind"]:
        assert c in prep.columns

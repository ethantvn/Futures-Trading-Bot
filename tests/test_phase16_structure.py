"""Phase 16 indicators + strategy no-lookahead tests."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import numpy as np
import polars as pl
import pytest

from src.strategies.indicators import (
    ADJ,
    align_mes_bars,
    overnight_levels,
    prior_settle_proxy,
    session_volume_profile,
    structure_regime,
)
from src.strategies.mes_divergence_orb import MesDivergenceOrb
from src.strategies.overnight_levels import OvernightLevels
from src.strategies.poc_value_area import PocValueArea
from src.strategies.prior_day_levels import PriorDayLevels
from src.strategies.round_number_magnet import RoundNumberMagnet
from src.strategies.structure_gated_orb import StructureGatedOrb
from src.strategies.structure_gated_vwap import StructureGatedVwap
from tests.test_indicators import synthetic_5m
from tests.test_strategies import actionable_view

P16_STRATEGIES = [
    StructureGatedOrb,
    StructureGatedVwap,
    OvernightLevels,
    PriorDayLevels,
    PocValueArea,
    RoundNumberMagnet,
]


def synthetic_with_eth(days: int = 3, seed: int = 9) -> pl.DataFrame:
    """RTH 5m + prior ETH hour so overnight levels exist."""
    rth = synthetic_5m(days=days, seed=seed)
    rng = np.random.default_rng(seed + 1)
    rows = []
    px = 15000.0
    for d in range(days):
        day = date(2024, 1, 15 + d)
        # ETH stub: 08:00–09:25 ET (= 13:00–14:25 UTC) on same trading_date
        for i in range(18):
            ts = datetime(day.year, day.month, day.day, 13, 0, tzinfo=timezone.utc) + timedelta(
                minutes=5 * i
            )
            drift = rng.normal(0, 6)
            o, c = px, px + drift
            hi, lo = max(o, c) + 2, min(o, c) - 2
            rows.append(
                {
                    "ts_utc": ts,
                    "trading_date": day,
                    "session": "eth",
                    "open_adj": round(o, 2),
                    "high_adj": round(hi, 2),
                    "low_adj": round(lo, 2),
                    "close_adj": round(c, 2),
                    "volume": int(rng.integers(50, 800)),
                }
            )
            px = c
    eth = pl.DataFrame(
        rows,
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC"), "trading_date": pl.Date},
    ).with_columns(
        pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny")
    )
    return pl.concat([eth, rth], how="diagonal_relaxed").sort("ts_utc")


@pytest.mark.parametrize("cls", P16_STRATEGIES, ids=lambda c: c.name)
def test_no_look_ahead(cls):
    df = synthetic_with_eth(days=4, seed=11)
    params = {}
    if cls is StructureGatedOrb:
        params = {"min_width_ratio": 0.0, "max_width_ratio": 1e9, "skip_weekdays": ()}
    strat = cls(params)
    full = actionable_view(strat.prepare(df))
    for k in (len(df) // 3, len(df) // 2, len(df) - 5):
        trunc = actionable_view(strat.prepare(df.head(k)))
        assert trunc.equals(full.head(k)), f"{cls.name} leaks at row {k}"


def test_structure_regime_causal():
    df = synthetic_5m(days=3)
    full = structure_regime(df, pivot_n=2)
    trunc = structure_regime(df.head(100), pivot_n=2)
    a = full.head(100)["structure_regime"]
    b = trunc["structure_regime"]
    # None vs None ok; string equality otherwise
    for x, y in zip(a.to_list(), b.to_list()):
        assert x == y


def test_overnight_levels_present():
    df = synthetic_with_eth(days=2)
    on = overnight_levels(df)
    assert on.height >= 1
    assert on["on_high"].null_count() == 0


def test_prior_settle_shifted():
    df = synthetic_5m(days=3)
    s = prior_settle_proxy(df)
    assert s.filter(pl.col("trading_date") == date(2024, 1, 15))["prior_settle"][0] is None
    assert s.filter(pl.col("trading_date") == date(2024, 1, 16))["prior_settle"][0] is not None


def test_session_volume_profile_columns():
    df = synthetic_5m(days=2)
    out = session_volume_profile(df, bin_size=10.0)
    rth = out.filter(pl.col("session") == "rth")
    assert rth["poc"].drop_nulls().len() > 0
    assert (rth["vah"] >= rth["val"]).drop_nulls().all()


def test_align_mes_bars():
    mnq = synthetic_5m(days=1, seed=1)
    mes = mnq.with_columns(
        (pl.col(ADJ["close"]) * 0.3).alias(ADJ["close"]),
        (pl.col(ADJ["high"]) * 0.3).alias(ADJ["high"]),
        (pl.col(ADJ["low"]) * 0.3).alias(ADJ["low"]),
        (pl.col(ADJ["open"]) * 0.3).alias(ADJ["open"]),
    )
    joined = align_mes_bars(mnq, mes)
    assert "mes_close_adj" in joined.columns
    assert joined.height == mnq.height


def test_mes_divergence_with_injected_mes():
    df = synthetic_with_eth(days=3, seed=4)
    # Inject MES columns so prepare skips file load
    df = df.with_columns(
        pl.col(ADJ["high"]).alias("mes_high_adj"),
        pl.col(ADJ["low"]).alias("mes_low_adj"),
        pl.col(ADJ["close"]).alias("mes_close_adj"),
        pl.col(ADJ["open"]).alias("mes_open_adj"),
    )
    prep = MesDivergenceOrb(
        {
            "min_width_ratio": 0.0,
            "max_width_ratio": 1e9,
            "skip_weekdays": (),
            "mes_mode": "agree",
        }
    ).prepare(df)
    assert "enter_long" in prep.columns

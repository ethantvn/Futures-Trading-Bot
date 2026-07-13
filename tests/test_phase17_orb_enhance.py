"""Phase 17 orb_enhanced — no-lookahead smoke tests."""
from __future__ import annotations

import polars as pl
import pytest

from src.strategies.orb_enhanced import OrbEnhanced, load_vix_prior_close
from tests.test_phase16_structure import synthetic_with_eth
from tests.test_strategies import actionable_view


def test_vix_prior_is_shifted():
    v = load_vix_prior_close("data/processed/vix_daily.parquet")
    assert "vix_prior" in v.columns
    # first row after sort should be null prior
    assert v.sort("trading_date")["vix_prior"][0] is None


def test_orb_enhanced_no_lookahead():
    df = synthetic_with_eth(days=5, seed=3)
    # Inject fake VIX join dates via skipping vix gate (defaults wide)
    strat = OrbEnhanced(
        {
            "min_width_ratio": 0.0,
            "max_width_ratio": 1e9,
            "skip_weekdays": (),
            "vix_min": 0.0,
            "vix_max": 1e9,
            "on_range_min_ratio": 0.0,
            "on_range_max_ratio": 1e9,
            "allow_regimes": "up,range",
        }
    )
    full = actionable_view(strat.prepare(df))
    for k in (len(df) // 2, len(df) - 5):
        trunc = actionable_view(strat.prepare(df.head(k)))
        assert trunc.equals(full.head(k))

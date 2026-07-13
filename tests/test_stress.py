from __future__ import annotations

from datetime import date

import polars as pl
import pytest

from src.backtest.engine import EngineConfig
from src.backtest.fees import CostModel
from src.strategies.opening_range import OpeningRangeBreakout
from src.validation.stress import slippage_sweep


@pytest.fixture
def tiny_bars():
    """Two trading days of synthetic 1m + 5m bars (minimal smoke test)."""
    from datetime import datetime, timezone

    rows_1m = []
    rows_5m = []
    for d in (date(2024, 6, 3), date(2024, 6, 4)):
        base = datetime(d.year, d.month, d.day, 14, 30, tzinfo=timezone.utc)
        for i in range(60):
            ts = base.replace(minute=30 + i % 30, hour=14 + i // 30)
            px = 18000.0 + i * 0.25
            rows_1m.append(
                {
                    "ts_utc": ts, "ts_ny": ts, "trading_date": d, "session": "rth",
                    "symbol": "MNQU4", "open": px, "high": px + 1, "low": px - 1,
                    "close": px, "volume": 100,
                    "open_adj": px, "high_adj": px + 1, "low_adj": px - 1,
                    "close_adj": px, "adj_offset": 0.0,
                }
            )
        for i in range(12):
            ts = base.replace(minute=i * 5)
            px = 18000.0 + i
            rows_5m.append(
                {
                    "ts_utc": ts, "ts_ny": ts, "trading_date": d, "session": "rth",
                    "symbol": "MNQU4", "open": px, "high": px + 2, "low": px - 2,
                    "close": px + 0.5, "volume": 500,
                    "open_adj": px, "high_adj": px + 2, "low_adj": px - 2,
                    "close_adj": px + 0.5, "adj_offset": 0.0,
                }
            )
    return pl.DataFrame(rows_1m), pl.DataFrame(rows_5m)


def test_slippage_sweep_monotonic_cost(tiny_bars):
    exec_bars, sig_bars = tiny_bars
    cost = CostModel(0.62, 0.37, 1, 0.25, 2.0)
    ecfg = EngineConfig(qty=1, max_trades_per_day=1)
    rows = slippage_sweep(
        OpeningRangeBreakout, {"range_minutes": 30, "target_r": 2.0, "expire_minutes": 90},
        exec_bars, sig_bars, cost, [0, 1, 2], ecfg,
        date(2024, 6, 3), date(2024, 6, 4),
    )
    assert len(rows) == 3
    assert rows[0].slippage_ticks == 0
    # higher slippage should not improve net pnl vs zero slippage
    if rows[0].n_trades > 0 and rows[2].n_trades > 0:
        assert rows[2].net_pnl <= rows[0].net_pnl

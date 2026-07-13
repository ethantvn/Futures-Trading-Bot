from __future__ import annotations

from datetime import date, datetime, timezone

import polars as pl

from src.backtest.metrics import compute_metrics


def ledger() -> pl.DataFrame:
    """Hand-checkable fixture: net pnls +100, -50, -50, +200 over 3 days."""
    def ts(day: int, hour: int) -> datetime:
        return datetime(2024, 1, day, hour, 0, tzinfo=timezone.utc)

    return pl.DataFrame(
        {
            "strategy": ["t"] * 4,
            "trading_date": [date(2024, 1, 2), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)],
            "side": [1, -1, 1, 1],
            "qty": [1] * 4,
            "entry_ts": [ts(2, 15), ts(2, 17), ts(3, 15), ts(4, 15)],
            "exit_ts": [ts(2, 16), ts(2, 18), ts(3, 16), ts(4, 17)],
            "entry_px": [100.0] * 4,
            "exit_px": [150.0, 125.0, 75.0, 200.0],
            "gross_pnl": [102.0, -48.0, -48.0, 202.0],
            "costs": [2.0] * 4,
            "net_pnl": [100.0, -50.0, -50.0, 200.0],
            "exit_reason": ["target", "stop", "stop", "target"],
            "ambiguous": [False, False, True, False],
            "tag": [""] * 4,
        }
    )


def test_metrics_hand_calculated():
    m = compute_metrics(ledger(), total_trading_days=4)
    assert m["n_trades"] == 4
    assert m["net_pnl"] == 200.0
    assert m["total_costs"] == 8.0
    assert m["win_rate"] == 0.5
    assert m["avg_win"] == 150.0
    assert m["avg_loss"] == -50.0
    assert m["expectancy"] == 50.0
    assert m["profit_factor"] == 300.0 / 100.0
    assert m["max_consecutive_losses"] == 2
    # equity: 100, 50, 0, 200 ; peak: 100,100,100,200 -> max dd = -100
    assert m["max_drawdown"] == -100.0
    # daily: +50, -50, +200
    assert m["best_day"] == 200.0
    assert m["worst_day"] == -50.0
    assert m["n_active_days"] == 3
    assert m["trades_per_day"] == 1.0
    # holding: 60 + 60 + 60 + 120 = 300 min over 4 trades
    assert m["avg_hold_minutes"] == 75.0
    assert m["pct_ambiguous_trades"] == 25.0
    assert m["exit_reasons"] == {"target": 2, "stop": 2}


def test_empty_ledger():
    m = compute_metrics(ledger().head(0))
    assert m == {"n_trades": 0}

"""Strategy base: a strategy is a causal transformation of a signal-bar frame.

`prepare()` must add the engine's signal columns (see src/backtest/engine.py).
`base_signal_columns()` provides inert defaults so a strategy only overrides
what it uses. All price columns are in BACK-ADJUSTED space.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import polars as pl

SIGNAL_DEFAULTS: dict[str, pl.Expr] = {
    "enter_long": pl.lit(False),
    "enter_short": pl.lit(False),
    "entry_kind": pl.lit("market"),
    "entry_price_long_adj": pl.lit(None, dtype=pl.Float64),
    "entry_price_short_adj": pl.lit(None, dtype=pl.Float64),
    "stop_long_adj": pl.lit(None, dtype=pl.Float64),
    "stop_short_adj": pl.lit(None, dtype=pl.Float64),
    "target_long_adj": pl.lit(None, dtype=pl.Float64),
    "target_short_adj": pl.lit(None, dtype=pl.Float64),
    "exit_long": pl.lit(False),
    "exit_short": pl.lit(False),
    "expire_minutes": pl.lit(None, dtype=pl.Int64),
}


def with_signal_defaults(df: pl.DataFrame) -> pl.DataFrame:
    missing = [e.alias(c) for c, e in SIGNAL_DEFAULTS.items() if c not in df.columns]
    return df.with_columns(missing) if missing else df


def rising_edge(cond: pl.Expr) -> pl.Expr:
    """True only on the first bar a condition becomes true (per trading date)."""
    return cond & ~cond.shift(1, fill_value=False).over("trading_date")


class Strategy(ABC):
    """Subclasses define `name`, `timeframe_minutes`, `default_params`."""

    name: str = ""
    timeframe_minutes: int = 5
    default_params: dict[str, Any] = {}

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params = {**self.default_params, **(params or {})}

    @abstractmethod
    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        """Add signal columns. MUST be causal (no future data in any row)."""

    def overfit_prone_params(self) -> list[str]:
        """Parameters most likely to be overfit; reported with results."""
        return list(self.params)

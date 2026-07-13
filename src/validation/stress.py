"""Execution-cost stress tests (slippage sweeps, etc.)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import polars as pl

from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.backtest.metrics import compute_metrics
from src.strategies.base import Strategy


@dataclass
class StressRow:
    slippage_ticks: int
    n_trades: int
    net_pnl: float
    profit_factor: float
    sharpe_daily: float
    expectancy: float


def filter_bars(df: pl.DataFrame, start: date, end: date) -> pl.DataFrame:
    return df.filter(
        (pl.col("trading_date") >= start) & (pl.col("trading_date") <= end)
    )


def slippage_sweep(
    strategy_cls: type[Strategy],
    params: dict[str, Any],
    exec_bars: pl.DataFrame,
    signal_bars: pl.DataFrame,
    base_cost: CostModel,
    slippage_ticks: list[int],
    engine_cfg: EngineConfig,
    start: date,
    end: date,
) -> list[StressRow]:
    exec_w = filter_bars(exec_bars, start, end)
    sig_w = filter_bars(signal_bars, start, end)
    strat = strategy_cls(params)
    prepared = strat.prepare(sig_w)
    rows: list[StressRow] = []
    for ticks in slippage_ticks:
        cost = CostModel(
            commission_per_side=base_cost.commission_per_side,
            exchange_fees_per_side=base_cost.exchange_fees_per_side,
            slippage_ticks=ticks,
            tick_size=base_cost.tick_size,
            point_value=base_cost.point_value,
        )
        res = run_backtest(
            exec_w, prepared, strat.timeframe_minutes, cost, engine_cfg,
            strategy_name=strat.name,
        )
        m = compute_metrics(res.trades)
        rows.append(
            StressRow(
                slippage_ticks=ticks,
                n_trades=res.trades.height,
                net_pnl=m.get("net_pnl", 0.0),
                profit_factor=m.get("profit_factor", float("nan")),
                sharpe_daily=m.get("sharpe_daily", float("nan")),
                expectancy=m.get("expectancy", 0.0),
            )
        )
    return rows

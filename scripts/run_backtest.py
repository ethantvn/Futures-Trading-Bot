"""Run baseline backtests for one or all strategies.

Usage:
  .venv/bin/python scripts/run_backtest.py                 # all strategies
  .venv/bin/python scripts/run_backtest.py ema_trend       # one strategy
  .venv/bin/python scripts/run_backtest.py --start 2020-01-01 --end 2024-12-31

Writes data/processed/trades_<name>.parquet and data/reports/backtest_baseline.md.
"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

import polars as pl
import yaml

from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.backtest.metrics import compute_metrics, render_metrics_markdown
from src.logging_setup import setup_logging
from src.strategies.base import Strategy
from src.strategies.breakout import PrevDayLevelBreakout
from src.strategies.mean_reversion import BollingerMeanReversion
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.trend import EmaTrend
from src.strategies.vwap import VwapPullback

log = logging.getLogger("run_backtest")

STRATEGIES: dict[str, type[Strategy]] = {
    s.name: s
    for s in (
        OpeningRangeBreakout,
        PrevDayLevelBreakout,
        VwapPullback,
        EmaTrend,
        BollingerMeanReversion,
    )
}


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("strategy", nargs="?", help="strategy name (default: all)")
    ap.add_argument("--start", type=date.fromisoformat, default=None)
    ap.add_argument("--end", type=date.fromisoformat, default=None)
    args = ap.parse_args()

    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )

    exec_bars = pl.read_parquet(processed / "continuous_1m.parquet")
    if args.start:
        exec_bars = exec_bars.filter(pl.col("trading_date") >= args.start)
    if args.end:
        exec_bars = exec_bars.filter(pl.col("trading_date") <= args.end)
    total_days = exec_bars["trading_date"].n_unique()

    names = [args.strategy] if args.strategy else list(STRATEGIES)
    sections = [
        "# Baseline Backtest Report",
        "",
        f"- Period: {exec_bars['trading_date'].min()} -> {exec_bars['trading_date'].max()}"
        f" ({total_days} trading days)",
        f"- Costs: ${cost.commission_per_side + cost.exchange_fees_per_side:.2f}/side/contract,"
        f" slippage {cost.slippage_ticks} tick(s); qty {eng['qty']} micro(s)",
        "- Fills on 1-minute bars; pessimistic same-bar policy (stop before target).",
        "",
    ]
    for name in names:
        scfg = strat_cfg["strategies"][name]
        strat = STRATEGIES[name](scfg.get("params"))
        tf = strat.timeframe_minutes
        signal_bars = pl.read_parquet(processed / f"continuous_{tf}m.parquet")
        if args.start:
            signal_bars = signal_bars.filter(pl.col("trading_date") >= args.start)
        if args.end:
            signal_bars = signal_bars.filter(pl.col("trading_date") <= args.end)

        prepared = strat.prepare(signal_bars)
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=scfg.get("max_trades_per_day"),
            max_hold_minutes=scfg.get("max_hold_minutes"),
        )
        res = run_backtest(exec_bars, prepared, tf, cost, ecfg, strategy_name=name)
        res.trades.write_parquet(processed / f"trades_{name}.parquet")

        m = compute_metrics(res.trades, total_trading_days=total_days)
        m["forced_session_end_exits"] = res.forced_session_end_exits
        sections.append(render_metrics_markdown(name, m))
        sections.append(
            f"Overfit-prone parameters: {', '.join(strat.overfit_prone_params())}\n"
        )

    out = reports / "backtest_baseline.md"
    out.write_text("\n".join(sections))
    log.info("wrote %s", out)
    print("\n".join(sections))


if __name__ == "__main__":
    main()

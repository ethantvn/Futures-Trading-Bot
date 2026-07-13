"""Walk-forward validation.

Approach: because the engine holds no cross-day state (every position is flat
by the session cutoff and daily counters reset), a trade ledger produced by ONE
full-period run can be sliced by trading_date to obtain the exact trades any
sub-window run would produce. Indicators are computed on full history, which
matches live trading (a real trader's EMA has years of warmup). So we:

1. run every parameter combo once over the full in-sample period,
2. for each rolling fold, pick the combo with the best TRAIN-window score,
3. collect that combo's trades in the following unseen TEST window,
4. stitch all test windows into one out-of-sample ledger.

The stitched ledger is what honest live performance would have looked like,
including the parameter re-selection every `test_months`.
"""
from __future__ import annotations

import itertools
import logging
import math
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable

import polars as pl

from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.backtest.metrics import compute_metrics
from src.strategies.base import Strategy

log = logging.getLogger(__name__)


def param_grid(space: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(space)
    return [dict(zip(keys, combo)) for combo in itertools.product(*space.values())]


@dataclass(frozen=True)
class Fold:
    train_start: date
    train_end: date     # inclusive
    test_start: date
    test_end: date      # inclusive


def _add_months(d: date, months: int) -> date:
    y, m = divmod((d.year * 12 + d.month - 1) + months, 12)
    return date(y, m + 1, 1)


def make_folds(
    first_train_start: date,
    last_test_end: date,
    train_months: int = 24,
    test_months: int = 6,
) -> list[Fold]:
    """Rolling folds stepping by test_months; test windows tile [.., last_test_end]."""
    folds = []
    t0 = first_train_start
    while True:
        test_start = _add_months(t0, train_months)
        test_end_excl = _add_months(t0, train_months + test_months)
        if _add_months(test_start, test_months) > _add_months(last_test_end, 1):
            break
        folds.append(
            Fold(
                train_start=t0,
                train_end=_prev_day(test_start),
                test_start=test_start,
                test_end=_prev_day(test_end_excl),
            )
        )
        t0 = _add_months(t0, test_months)
    return folds


def _prev_day(d: date) -> date:
    from datetime import timedelta

    return d - timedelta(days=1)


def slice_trades(trades: pl.DataFrame, start: date, end: date) -> pl.DataFrame:
    return trades.filter(
        (pl.col("trading_date") >= start) & (pl.col("trading_date") <= end)
    )


def score_sharpe(trades: pl.DataFrame, min_trades: int = 40) -> float:
    """Train-window selection score: daily Sharpe, gated on a minimum trade
    count so thin/degenerate combos can't win on noise."""
    if trades.height < min_trades:
        return -math.inf
    m = compute_metrics(trades)
    s = m.get("sharpe_daily", math.nan)
    return s if not math.isnan(s) else -math.inf


def score_upi(trades: pl.DataFrame, min_trades: int = 40) -> float:
    """Train score biased toward Lucid survival: Ulcer Performance Index.

    Prefers smooth positive equity (low drawdown path) over raw Sharpe, which
    correlates better with eval pass / pass+payout in prior phases.
    """
    if trades.height < min_trades:
        return -math.inf
    from src.evaluation.consistency import consistency_metrics, daily_pnl

    c = consistency_metrics(daily_pnl(trades))
    if not c:
        return -math.inf
    upi = c.get("upi", math.nan)
    if upi is None or (isinstance(upi, float) and math.isnan(upi)):
        return -math.inf
    # Soft preference for positive train net (do not hard-reject — empty OOS)
    net_bonus = 0.0 if c.get("net_pnl", 0) > 0 else -5.0
    # Soft penalty for Lucid-hostile single days / streaks (25K MLL path)
    worst = float(c.get("worst_day", 0) or 0)
    streak = int(c.get("max_consec_losing_days", 0) or 0)
    dd = float(c.get("max_drawdown", 0) or 0)
    penalty = 0.0
    if worst < -600:
        penalty += abs(worst + 600) / 200.0
    if streak > 6:
        penalty += (streak - 6) * 0.5
    if dd < -2000:
        penalty += abs(dd + 2000) / 500.0
    return float(upi) + net_bonus - penalty


@dataclass
class GridRun:
    params: dict[str, Any]
    trades: pl.DataFrame


def run_full_period_grid(
    strategy_cls: type[Strategy],
    space: dict[str, list[Any]],
    exec_bars: pl.DataFrame,
    signal_bars: pl.DataFrame,
    cost: CostModel,
    engine_cfg: EngineConfig,
) -> list[GridRun]:
    combos = param_grid(space)
    out: list[GridRun] = []
    for k, params in enumerate(combos, 1):
        strat = strategy_cls(params)
        prepared = strat.prepare(signal_bars)
        res = run_backtest(
            exec_bars, prepared, strat.timeframe_minutes, cost, engine_cfg,
            strategy_name=strat.name,
        )
        out.append(GridRun(params=params, trades=res.trades))
        log.info(
            "grid %d/%d %s -> %d trades, net $%.0f",
            k, len(combos), params, res.trades.height,
            res.trades["net_pnl"].sum() if res.trades.height else 0.0,
        )
    return out


@dataclass
class FoldResult:
    fold: Fold
    chosen_params: dict[str, Any] | None
    train_score: float
    train_net: float
    test_net: float
    test_trades: int


@dataclass
class WalkForwardResult:
    oos_trades: pl.DataFrame
    folds: list[FoldResult]
    final_params: dict[str, Any] | None   # selection of the LAST fold (most recent train)


def walk_forward(
    grid_runs: list[GridRun],
    folds: list[Fold],
    scorer: Callable[[pl.DataFrame], float] = score_sharpe,
) -> WalkForwardResult:
    fold_results: list[FoldResult] = []
    oos_parts: list[pl.DataFrame] = []
    final_params: dict[str, Any] | None = None

    for fold in folds:
        best: GridRun | None = None
        best_score = -math.inf
        for gr in grid_runs:
            s = scorer(slice_trades(gr.trades, fold.train_start, fold.train_end))
            if s > best_score:
                best_score, best = s, gr

        if best is None or best_score == -math.inf:
            fold_results.append(
                FoldResult(fold, None, best_score, 0.0, 0.0, 0)
            )
            continue

        train = slice_trades(best.trades, fold.train_start, fold.train_end)
        test = slice_trades(best.trades, fold.test_start, fold.test_end)
        oos_parts.append(test)
        final_params = best.params
        fold_results.append(
            FoldResult(
                fold=fold,
                chosen_params=best.params,
                train_score=best_score,
                train_net=float(train["net_pnl"].sum()) if train.height else 0.0,
                test_net=float(test["net_pnl"].sum()) if test.height else 0.0,
                test_trades=test.height,
            )
        )

    oos = (
        pl.concat(oos_parts).sort("entry_ts")
        if oos_parts
        else grid_runs[0].trades.clear()
    )
    return WalkForwardResult(oos_trades=oos, folds=fold_results, final_params=final_params)


def sensitivity_table(
    grid_runs: list[GridRun],
    baseline: dict[str, Any],
    start: date,
    end: date,
) -> dict[str, list[dict[str, Any]]]:
    """One-at-a-time sweeps around `baseline` using the existing grid runs."""
    out: dict[str, list[dict[str, Any]]] = {}
    for param in baseline:
        rows = []
        for gr in grid_runs:
            if any(gr.params.get(k) != v for k, v in baseline.items() if k != param):
                continue
            t = slice_trades(gr.trades, start, end)
            m = compute_metrics(t) if t.height else {}
            rows.append(
                {
                    "value": gr.params[param],
                    "n_trades": t.height,
                    "net_pnl": m.get("net_pnl", 0.0),
                    "profit_factor": m.get("profit_factor", math.nan),
                    "sharpe_daily": m.get("sharpe_daily", math.nan),
                }
            )
        rows.sort(key=lambda r: r["value"])
        if len(rows) > 1:
            out[param] = rows
    return out

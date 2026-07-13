"""Equity-curve consistency metrics (Phase 7).

All metrics operate on a per-trading-day P&L frame derived from a trade
ledger. "Days" below always means ACTIVE trading days (days with >= 1 trade);
strategies that skip days are compared on the days they actually trade, which
matches the Lucid eval (no calendar deadline — only traded days count).

Ranking convention for Phase 7: Lucid pass rate is PRIMARY and computed
elsewhere (src/evaluation/monte_carlo.py); the smoothness tie-breaker here is
the Ulcer Performance Index (annualized $ P&L / ulcer index), with the full
metric set reported so no single scalar hides a pathology.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import polars as pl

TRADING_DAYS_PER_YEAR = 252

#: recency windows in ACTIVE trading days, reported per candidate
RECENCY_WINDOWS = (90, 252, 756)


def daily_pnl(trades: pl.DataFrame) -> pl.DataFrame:
    """Per-trading-day net P&L, sorted by date. Columns: trading_date, pnl."""
    if trades.height == 0:
        return pl.DataFrame(
            schema={"trading_date": pl.Date, "pnl": pl.Float64}
        )
    return (
        trades.group_by("trading_date")
        .agg(pl.col("net_pnl").sum().alias("pnl"))
        .sort("trading_date")
    )


def consistency_metrics(daily: pl.DataFrame) -> dict[str, Any]:
    """Smoothness/consistency metrics on a daily-pnl frame.

    Returns an empty dict when there are fewer than 5 active days (not enough
    shape to measure).
    """
    if daily.height < 5:
        return {}
    pnl = daily["pnl"].to_numpy()
    eq = np.cumsum(pnl)
    peak = np.maximum.accumulate(eq)
    dd = eq - peak

    mean = float(pnl.mean())
    std = float(pnl.std(ddof=1))
    sharpe = mean / std * math.sqrt(TRADING_DAYS_PER_YEAR) if std > 0 else math.nan
    neg = pnl[pnl < 0]
    dstd = float(neg.std(ddof=1)) if len(neg) > 1 else math.nan
    sortino = (
        mean / dstd * math.sqrt(TRADING_DAYS_PER_YEAR)
        if dstd and not math.isnan(dstd) and dstd > 0
        else math.nan
    )

    # Ulcer index in dollars: RMS of the drawdown series. UPI = annualized
    # P&L / ulcer — the primary smoothness scalar (higher is better).
    ulcer = float(np.sqrt(np.mean(dd**2)))
    ann_pnl = mean * TRADING_DAYS_PER_YEAR
    upi = ann_pnl / ulcer if ulcer > 0 else math.nan

    # R^2 of the equity curve vs a straight line: 1.0 = perfectly steady.
    t = np.arange(len(eq), dtype=float)
    ss_tot = float(((eq - eq.mean()) ** 2).sum())
    if ss_tot > 0:
        coef = np.polyfit(t, eq, 1)
        resid = eq - np.polyval(coef, t)
        r2 = 1.0 - float((resid**2).sum()) / ss_tot
    else:
        r2 = math.nan

    streak = worst_streak = 0
    for v in pnl:
        streak = streak + 1 if v < 0 else 0
        worst_streak = max(worst_streak, streak)

    # tail metrics (Phase 8): 5th percentile of daily P&L ("95th pct daily
    # loss") and the worst rolling 20-active-day P&L window
    p95_loss = float(np.percentile(pnl, 5))
    if len(pnl) >= 20:
        c = np.concatenate(([0.0], eq))
        worst_20d = float((c[20:] - c[:-20]).min())
    else:
        worst_20d = float(eq[-1])

    return {
        "active_days": len(pnl),
        "net_pnl": float(eq[-1]),
        "sharpe_daily": sharpe,
        "sortino_daily": sortino,
        "max_drawdown": float(dd.min()),
        "ulcer_index": ulcer,
        "upi": upi,
        "equity_r2": r2,
        "max_consec_losing_days": worst_streak,
        "win_day_rate": float((pnl > 0).mean()),
        "worst_day": float(pnl.min()),
        "best_day": float(pnl.max()),
        "p95_daily_loss": p95_loss,
        "worst_20d_window": worst_20d,
    }


def recency_metrics(daily: pl.DataFrame) -> dict[str, dict[str, Any]]:
    """Consistency metrics over the trailing RECENCY_WINDOWS active days plus
    the full period. Keys: 'full', 'last_90d', 'last_252d', 'last_756d'."""
    out = {"full": consistency_metrics(daily)}
    for n in RECENCY_WINDOWS:
        out[f"last_{n}d"] = consistency_metrics(daily.tail(n))
    return out


def rolling_window_stats(
    daily: pl.DataFrame, window: int = 126, step: int = 21
) -> dict[str, Any]:
    """Regime stability: net P&L over rolling `window`-day slices stepped by
    `step` days. Reports the share of negative windows and the worst window —
    a strategy that only worked in one era shows a high negative share."""
    pnl = daily["pnl"].to_numpy()
    if len(pnl) < window:
        return {"n_windows": 0, "negative_share": math.nan, "worst_window": math.nan}
    sums = [
        float(pnl[s : s + window].sum()) for s in range(0, len(pnl) - window + 1, step)
    ]
    return {
        "n_windows": len(sums),
        "negative_share": float(np.mean([s < 0 for s in sums])),
        "worst_window": min(sums),
        "median_window": float(np.median(sums)),
    }


def year_pnls(daily: pl.DataFrame) -> dict[int, float]:
    """Net P&L per calendar year."""
    if daily.height == 0:
        return {}
    g = (
        daily.with_columns(pl.col("trading_date").dt.year().alias("yr"))
        .group_by("yr")
        .agg(pl.col("pnl").sum())
        .sort("yr")
    )
    return {int(y): float(p) for y, p in g.iter_rows()}

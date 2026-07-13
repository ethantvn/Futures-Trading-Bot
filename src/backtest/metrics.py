"""Performance metrics computed from a trade ledger."""
from __future__ import annotations

import math
from typing import Any

import polars as pl

TRADING_DAYS_PER_YEAR = 252


def compute_metrics(trades: pl.DataFrame, total_trading_days: int | None = None) -> dict[str, Any]:
    """All metrics from the spec that are derivable from a closed-trade ledger."""
    m: dict[str, Any] = {"n_trades": trades.height}
    if trades.height == 0:
        return m

    pnl = trades["net_pnl"]
    wins = trades.filter(pl.col("net_pnl") > 0)
    losses = trades.filter(pl.col("net_pnl") < 0)

    m["net_pnl"] = float(pnl.sum())
    m["gross_pnl"] = float(trades["gross_pnl"].sum())
    m["total_costs"] = float(trades["costs"].sum())
    m["win_rate"] = wins.height / trades.height
    m["avg_win"] = float(wins["net_pnl"].mean()) if wins.height else 0.0
    m["avg_loss"] = float(losses["net_pnl"].mean()) if losses.height else 0.0
    m["expectancy"] = float(pnl.mean())
    gross_win = float(wins["net_pnl"].sum()) if wins.height else 0.0
    gross_loss = abs(float(losses["net_pnl"].sum())) if losses.height else 0.0
    m["profit_factor"] = gross_win / gross_loss if gross_loss > 0 else math.inf

    # max consecutive losses
    streak = worst = 0
    for v in pnl:
        streak = streak + 1 if v < 0 else 0
        worst = max(worst, streak)
    m["max_consecutive_losses"] = worst

    # drawdown on the closed-trade equity curve (dollars)
    equity = pnl.cum_sum()
    peak = equity.cum_max()
    m["max_drawdown"] = float((equity - peak).min())

    # daily statistics
    daily = trades.group_by("trading_date").agg(pl.col("net_pnl").sum()).sort("trading_date")
    d = daily["net_pnl"]
    m["n_active_days"] = daily.height
    m["best_day"] = float(d.max())
    m["worst_day"] = float(d.min())
    mean_d, std_d = float(d.mean()), float(d.std()) if daily.height > 1 else 0.0
    m["sharpe_daily"] = (
        mean_d / std_d * math.sqrt(TRADING_DAYS_PER_YEAR) if std_d else math.nan
    )
    downside = daily.filter(pl.col("net_pnl") < 0)["net_pnl"]
    dd_std = float(downside.std()) if downside.len() > 1 else math.nan
    m["sortino_daily"] = (
        mean_d / dd_std * math.sqrt(TRADING_DAYS_PER_YEAR)
        if dd_std and not math.isnan(dd_std)
        else math.nan
    )

    days = total_trading_days or daily.height
    m["trades_per_day"] = trades.height / days if days else math.nan

    # time in market: holding minutes vs 1380-minute sessions
    held_min = (
        trades.select(
            ((pl.col("exit_ts") - pl.col("entry_ts")).dt.total_seconds() / 60).sum()
        ).item()
    )
    m["avg_hold_minutes"] = held_min / trades.height
    m["time_in_market_pct"] = 100.0 * held_min / (days * 1380) if days else math.nan

    m["pct_ambiguous_trades"] = 100.0 * trades["ambiguous"].sum() / trades.height
    m["exit_reasons"] = dict(
        trades.group_by("exit_reason").len().iter_rows()
    )
    return m


def render_metrics_markdown(name: str, m: dict[str, Any]) -> str:
    if m.get("n_trades", 0) == 0:
        return f"## {name}\n\nNo trades.\n"
    fmt = {
        "n_trades": "{:d}", "net_pnl": "${:,.2f}", "gross_pnl": "${:,.2f}",
        "total_costs": "${:,.2f}", "win_rate": "{:.2%}", "avg_win": "${:,.2f}",
        "avg_loss": "${:,.2f}", "expectancy": "${:,.2f}", "profit_factor": "{:.2f}",
        "max_consecutive_losses": "{:d}", "max_drawdown": "${:,.2f}",
        "n_active_days": "{:d}", "best_day": "${:,.2f}", "worst_day": "${:,.2f}",
        "sharpe_daily": "{:.2f}", "sortino_daily": "{:.2f}",
        "trades_per_day": "{:.2f}", "avg_hold_minutes": "{:.0f}",
        "time_in_market_pct": "{:.2f}%", "pct_ambiguous_trades": "{:.2f}%",
    }
    lines = [f"## {name}", "", "| Metric | Value |", "| --- | --- |"]
    for k, f in fmt.items():
        if k in m:
            try:
                lines.append(f"| {k} | {f.format(m[k])} |")
            except (ValueError, TypeError):
                lines.append(f"| {k} | {m[k]} |")
    lines.append(f"| exit_reasons | {m.get('exit_reasons', {})} |")
    lines.append("")
    return "\n".join(lines)

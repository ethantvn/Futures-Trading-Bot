"""Markdown report helpers for Phase 5 validation."""
from __future__ import annotations

import math
from typing import Any

from src.backtest.metrics import compute_metrics, render_metrics_markdown
from src.evaluation.monte_carlo import MonteCarloResult, render_mc_markdown
from src.validation.stress import StressRow
from src.validation.walk_forward import FoldResult, GridRun, WalkForwardResult


def render_fold_table(folds: list[FoldResult]) -> str:
    lines = [
        "| Fold | Train | Test | Chosen params | Train Sharpe | Train $ | Test $ | Test trades |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, fr in enumerate(folds, 1):
        f = fr.fold
        params = ", ".join(f"{k}={v}" for k, v in (fr.chosen_params or {}).items()) or "—"
        sharpe = f"{fr.train_score:.2f}" if fr.train_score != -math.inf else "—"
        lines.append(
            f"| {i} | {f.train_start}→{f.train_end} | {f.test_start}→{f.test_end} "
            f"| {params} | {sharpe} | ${fr.train_net:,.0f} | ${fr.test_net:,.0f} | {fr.test_trades} |"
        )
    return "\n".join(lines)


def render_walk_forward_section(name: str, wf: WalkForwardResult) -> list[str]:
    oos = wf.oos_trades
    m = compute_metrics(oos)
    params = wf.final_params or {}
    param_str = ", ".join(f"{k}={v}" for k, v in params.items()) or "baseline"
    return [
        f"## {name} — walk-forward",
        "",
        f"- Final selected params (last fold train window): `{param_str}`",
        f"- Stitched OOS period: {oos['trading_date'].min() if oos.height else '—'}"
        f" → {oos['trading_date'].max() if oos.height else '—'}",
        f"- Stitched OOS trades: {oos.height}",
        "",
        render_fold_table(wf.folds),
        "",
        render_metrics_markdown(f"{name} (WF OOS)", m),
        "",
    ]


def render_sensitivity_section(name: str, table: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines = [f"## {name} — parameter sensitivity (validation window)", ""]
    if not table:
        lines.append("_No one-at-a-time sweeps available._\n")
        return lines
    for param, rows in table.items():
        lines.append(f"### `{param}`")
        lines.append("")
        lines.append("| Value | Trades | Net $ | PF | Sharpe |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in rows:
            pf = r["profit_factor"]
            sh = r["sharpe_daily"]
            lines.append(
                f"| {r['value']} | {r['n_trades']} | ${r['net_pnl']:,.0f} "
                f"| {_fmt(pf)} | {_fmt(sh)} |"
            )
        lines.append("")
    return lines


def _fmt(x: float) -> str:
    return f"{x:.2f}" if not math.isnan(x) else "—"


def render_stress_section(name: str, rows: list[StressRow]) -> list[str]:
    lines = [f"## {name} — slippage stress (2025)", "", "| Slippage (ticks) | Trades | Net $ | PF | Sharpe | Expectancy |", "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(
            f"| {r.slippage_ticks} | {r.n_trades} | ${r.net_pnl:,.0f} "
            f"| {_fmt(r.profit_factor)} | {_fmt(r.sharpe_daily)} | ${r.expectancy:.2f} |"
        )
    lines.append("")
    return lines


def render_holdout_section(name: str, trades, params: dict[str, Any]) -> list[str]:
    m = compute_metrics(trades)
    param_str = ", ".join(f"{k}={v}" for k, v in params.items())
    return [
        f"## {name} — 2026 holdout (single run)",
        "",
        f"- Params: `{param_str}`",
        f"- Period: {trades['trading_date'].min() if trades.height else '—'}"
        f" → {trades['trading_date'].max() if trades.height else '—'}",
        f"- **This holdout was run once.** Do not re-run for tuning.",
        "",
        render_metrics_markdown(f"{name} (holdout 2026)", m),
        "",
    ]


def render_mc_section(title: str, results: list[MonteCarloResult]) -> list[str]:
    return [f"## {title}", "", render_mc_markdown(results), ""]


def top_grid_on_window(
    grid_runs: list[GridRun], start, end, top_n: int = 5
) -> list[dict[str, Any]]:
    from src.validation.walk_forward import slice_trades

    ranked = []
    for gr in grid_runs:
        t = slice_trades(gr.trades, start, end)
        if t.height == 0:
            continue
        m = compute_metrics(t)
        ranked.append({"params": gr.params, **m})
    ranked.sort(key=lambda r: r.get("sharpe_daily", -math.inf), reverse=True)
    return ranked[:top_n]

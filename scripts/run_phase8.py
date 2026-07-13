"""Phase 8: tail-risk exit overlays + outlier analysis on the Phase 7 winner.

Usage:
  .venv/bin/python scripts/run_phase8.py

Writes:
  data/reports/phase8_leaderboard.md
  data/reports/phase8_walk_forward.md
  data/reports/phase8_metrics.json
  data/processed/trades_phase8_<overlay>_wf_oos.parquet

Overlays (each = full Phase 7 orb_width grid + WF re-run with the overlay
fixed): max_hold_minutes via EngineConfig, max_risk_points via strategy
param. Baseline row = the untouched Phase 7 ledger. friday_flat is a no-op
in the engine (flat 15:55 daily) — asserted here, fixed on the TV side only.
No 2026 holdout in this phase (already consumed by Phases 5 and 7).
"""
from __future__ import annotations

import json
import logging
import math
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import yaml

from src.backtest.engine import EngineConfig
from src.backtest.metrics import compute_metrics
from src.evaluation.consistency import (
    consistency_metrics,
    daily_pnl,
    recency_metrics,
    rolling_window_stats,
    year_pnls,
)
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import run_monte_carlo
from src.logging_setup import setup_logging
from src.strategies.orb_filtered import FilteredOrb
from src.validation.reporting import render_fold_table
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase8")


def _as_date(v: date | str) -> date:
    return v if isinstance(v, date) else date.fromisoformat(v)


def _filter(df: pl.DataFrame, start: date, end: date) -> pl.DataFrame:
    return df.filter(
        (pl.col("trading_date") >= start) & (pl.col("trading_date") <= end)
    )


def skip_monday(trades: pl.DataFrame) -> pl.DataFrame:
    return trades.filter(pl.col("trading_date").dt.weekday() != 1)


def _sanitize(o: Any) -> Any:
    if isinstance(o, dict):
        return {str(k): _sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_sanitize(v) for v in o]
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, date):
        return o.isoformat()
    return o


def evaluate(
    name: str, trades: pl.DataFrame, rules: LucidRules, mc_cfg: dict, costs: dict
) -> dict[str, Any]:
    d = daily_pnl(trades)
    mc = run_monte_carlo(
        trades, rules, contracts=1,
        n_attempts=mc_cfg["n_attempts"], max_days=mc_cfg["max_days"],
        seed=mc_cfg["seed"],
        evaluation_cost=costs["evaluation_cost"], reset_cost=costs["reset_cost"],
        strategy=name,
    )
    return {
        "name": name,
        "trade_metrics": compute_metrics(trades),
        "consistency": recency_metrics(d),
        "rolling_6m": rolling_window_stats(d),
        "year_pnls": year_pnls(d),
        "mc": {
            "pass_rate": mc.pass_rate,
            "fail_rate": mc.fail_rate,
            "timeout_rate": mc.timeout_rate,
            "median_days": mc.median_days_to_pass,
            "expected_cost": mc.expected_total_cost_before_pass,
        },
    }


LB_HEADER = (
    "| Candidate | Trades | Pass@1 | Med d | Net $ | UPI | MaxDD | Worst day "
    "| p95 loss | Worst 20d | Last252 $ | E[cost] |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
)


def _row(r: dict[str, Any]) -> str:
    c = r["consistency"]["full"]
    c252 = r["consistency"]["last_252d"]
    mc = r["mc"]

    def _f(v, fmt="{:.2f}"):
        return "—" if v is None or (isinstance(v, float) and math.isnan(v)) else fmt.format(v)

    return (
        f"| {r['name']} | {r['trade_metrics'].get('n_trades', 0)} "
        f"| {100 * mc['pass_rate']:.1f}% | {_f(mc['median_days'], '{:.0f}')} "
        f"| ${c.get('net_pnl', 0):,.0f} | {_f(c.get('upi'))} "
        f"| ${c.get('max_drawdown', 0):,.0f} | ${c.get('worst_day', 0):,.0f} "
        f"| ${c.get('p95_daily_loss', 0):,.0f} | ${c.get('worst_20d_window', 0):,.0f} "
        f"| ${c252.get('net_pnl', 0):,.0f} | {_f(mc['expected_cost'], '${:,.0f}')} |"
    )


def tail_analysis(
    trades: pl.DataFrame, rules: LucidRules, mc_cfg: dict, costs: dict, label: str
) -> list[str]:
    """Part C: lottery dependence, worst days vs MLL, exit-reason attribution."""
    d = daily_pnl(trades).sort("trading_date")
    pnl = d["pnl"].to_numpy()
    lines = [f"### {label}", ""]

    # lottery dependence: drop top 5% winning days, re-run MC
    n_top = max(1, int(round(0.05 * len(pnl))))
    cutoff = float(np.sort(pnl)[-n_top])
    top_days = d.filter(pl.col("pnl") >= cutoff)["trading_date"].to_list()
    kept = trades.filter(~pl.col("trading_date").is_in(top_days))
    base_mc = run_monte_carlo(
        trades, rules, contracts=1, n_attempts=mc_cfg["n_attempts"],
        max_days=mc_cfg["max_days"], seed=mc_cfg["seed"],
        evaluation_cost=costs["evaluation_cost"], reset_cost=costs["reset_cost"],
    )
    trimmed_mc = run_monte_carlo(
        kept, rules, contracts=1, n_attempts=mc_cfg["n_attempts"],
        max_days=mc_cfg["max_days"], seed=mc_cfg["seed"],
        evaluation_cost=costs["evaluation_cost"], reset_cost=costs["reset_cost"],
    )
    top_sum = float(d.filter(pl.col("trading_date").is_in(top_days))["pnl"].sum())
    lines += [
        f"- Top 5% winning days: {len(top_days)} days (>= ${cutoff:,.0f}) contribute "
        f"**${top_sum:,.0f}** of ${float(pnl.sum()):,.0f} net "
        f"({100 * top_sum / float(pnl.sum()):.0f}%).",
        f"- Lucid pass rate with those days REMOVED: "
        f"**{100 * trimmed_mc.pass_rate:.1f}%** (vs {100 * base_mc.pass_rate:.1f}% full) — "
        f"median {trimmed_mc.median_days_to_pass:.0f} vs {base_mc.median_days_to_pass:.0f} days.",
        "",
        "Worst 10 days (fresh-$25k MLL = $1,000; single-day breach needs <= -$1,000):",
        "",
        "| Date | Day P&L | % of MLL |",
        "| --- | --- | --- |",
    ]
    worst = d.sort("pnl").head(10)
    breaches = 0
    for dt, p in worst.iter_rows():
        if p <= -rules.max_drawdown:
            breaches += 1
        lines.append(f"| {dt} | ${p:,.0f} | {100 * abs(p) / rules.max_drawdown:.0f}% |")
    lines += [
        "",
        f"- Single-day MLL breaches from fresh start: **{breaches}** of {len(pnl)} days.",
    ]
    # worst k-day cumulative vs MLL
    for k in (2, 5):
        if len(pnl) >= k:
            c = np.concatenate(([0.0], np.cumsum(pnl)))
            wk = float((c[k:] - c[:-k]).min())
            lines.append(
                f"- Worst {k}-consecutive-active-day run: ${wk:,.0f} "
                f"({100 * abs(wk) / rules.max_drawdown:.0f}% of MLL)."
            )
    # exit reason attribution
    er = (
        trades.group_by("exit_reason")
        .agg(
            pl.len().alias("n"),
            pl.col("net_pnl").sum().round(0).alias("net"),
            pl.col("net_pnl").mean().round(1).alias("avg"),
            (pl.col("net_pnl") > 0).mean().round(3).alias("win_rate"),
        )
        .sort("net", descending=True)
    )
    lines += ["", "| Exit | N | Net $ | Avg $ | Win rate |", "| --- | --- | --- | --- | --- |"]
    for row in er.iter_rows(named=True):
        lines.append(
            f"| {row['exit_reason']} | {row['n']} | ${row['net']:,.0f} "
            f"| ${row['avg']:,.1f} | {100 * row['win_rate']:.0f}% |"
        )
    lines.append("")
    return lines


def main() -> None:
    setup_logging()
    cfg = yaml.safe_load(Path("config/phase8.yaml").read_text())
    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    eng = strat_cfg["engine"]

    from src.backtest.fees import CostModel

    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    mc_cfg = cfg["monte_carlo"]
    lucid_path = Path("config") / f"{mc_cfg['account']}.yaml"
    rules = LucidRules.from_yaml(lucid_path)
    lucid_costs = yaml.safe_load(lucid_path.read_text())["costs"]

    splits = cfg["splits"]
    gs, ge = _as_date(splits["grid_start"]), _as_date(splits["grid_end"])
    exec_grid = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), gs, ge)
    sig_grid = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), gs, ge)
    wf_cfg = cfg["walk_forward"]
    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]), _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"], wf_cfg["test_months"],
    )
    scorer = lambda t: score_sharpe(t, min_trades=wf_cfg["min_trades_train"])
    space = cfg["base_family"]["param_grid"]

    def ecfg(max_hold: int | None = None) -> EngineConfig:
        return EngineConfig(
            qty=eng["qty"], flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=cfg["base_family"]["max_trades_per_day"],
            max_hold_minutes=max_hold,
        )

    # ---- baseline: Phase 7 ledger, engine invariant asserted ---------------
    baseline = pl.read_parquet(processed / cfg["baseline_ledger"])
    ny_exit = pl.col("exit_ts").dt.convert_time_zone("America/New_York")
    ny_entry = pl.col("entry_ts").dt.convert_time_zone("America/New_York")
    multiday = baseline.filter(ny_exit.dt.date() != ny_entry.dt.date()).height
    assert multiday == 0, "engine ledger must never hold overnight"
    log.info("baseline ledger: %d trades, 0 multi-day holds (friday_flat is a no-op)", baseline.height)

    results: list[dict[str, Any]] = [
        evaluate("BASELINE orb_width (Phase 7)", baseline, rules, mc_cfg, lucid_costs),
        evaluate("BASELINE orb_width +skipMon", skip_monday(baseline), rules, mc_cfg, lucid_costs),
    ]

    wf_report = ["# Phase 8 Walk-Forward (overlays)", ""]

    def run_overlay(tag: str, grid_space: dict, engine_cfg: EngineConfig) -> None:
        grid_runs = run_full_period_grid(
            FilteredOrb, grid_space, exec_grid, sig_grid, cost, engine_cfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase8_{tag}_wf_oos.parquet")
        wf_report.extend([
            f"## {tag}",
            "",
            f"- Final params (last fold): `{wf.final_params}`",
            f"- Stitched OOS: {oos.height} trades, net ${oos['net_pnl'].sum() if oos.height else 0:,.0f}",
            "",
            render_fold_table(wf.folds),
            "",
        ])
        if oos.height:
            results.append(evaluate(tag, oos, rules, mc_cfg, lucid_costs))
            results.append(
                evaluate(f"{tag} +skipMon", skip_monday(oos), rules, mc_cfg, lucid_costs)
            )

    for hold in cfg["overlays"]["max_hold_minutes"]:
        log.info("=== overlay max_hold=%s ===", hold)
        run_overlay(f"maxhold_{hold}", space, ecfg(max_hold=hold))

    for cap in cfg["overlays"]["max_risk_points"]:
        log.info("=== overlay stop cap=%s pts ===", cap)
        run_overlay(
            f"stopcap_{int(cap)}pts",
            {**space, "max_risk_points": [cap]},
            ecfg(),
        )

    # ---- leaderboard --------------------------------------------------------
    def key(r: dict) -> tuple:
        u = r["consistency"]["full"].get("upi")
        return (r["mc"]["pass_rate"], -1e9 if u is None or math.isnan(u) else u)

    results.sort(key=key, reverse=True)
    lb = [
        "# Phase 8 Leaderboard — tail-risk exit overlays on orb_width",
        "",
        f"Each overlay re-runs the full Phase 7 orb_width grid + walk-forward "
        f"(same 9 folds) with the overlay fixed; ledgers are stitched WF OOS "
        f"2021-06 → 2025-11. MC {mc_cfg['n_attempts']} attempts @1 micro, seed "
        f"{mc_cfg['seed']}. Stop caps in points: 200/250/300 pts = $400/$500/$600 "
        f"max gross loss per trade (= per day at 1 trade/day). "
        f"`friday_flat` is a **no-op in the engine** (flat 15:55 every day; "
        f"0 multi-day holds across all ledgers) — it was a TradingView bug, "
        f"fixed in the Pine scripts.",
        "",
        LB_HEADER,
    ]
    lb += [_row(r) for r in results]

    # ---- part C: tail analysis on the current winner -------------------------
    lb += [
        "",
        "## Tail / outlier analysis (Phase 7 winner ledgers)",
        "",
    ]
    lb += tail_analysis(baseline, rules, mc_cfg, lucid_costs, "orb_width (WF OOS, all days)")
    lb += tail_analysis(
        skip_monday(baseline), rules, mc_cfg, lucid_costs, "orb_width +skipMon (live config)"
    )

    (reports / "phase8_leaderboard.md").write_text("\n".join(lb) + "\n")
    (reports / "phase8_walk_forward.md").write_text("\n".join(wf_report) + "\n")
    (reports / "phase8_metrics.json").write_text(
        json.dumps(_sanitize({"results": results}), indent=1)
    )
    log.info("Phase 8 reports written to %s", reports)


if __name__ == "__main__":
    main()

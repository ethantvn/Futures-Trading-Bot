"""Phase 7: consistency-focused candidate search.

Usage:
  .venv/bin/python scripts/run_phase7.py                  # grids + WF + MC + leaderboard
  .venv/bin/python scripts/run_phase7.py --holdout F ...  # ONE 2026 run for finalists

Writes:
  data/reports/phase7_leaderboard.md
  data/reports/phase7_walk_forward.md
  data/reports/phase7_metrics.json          (full metric dump for the report)
  data/reports/phase7_holdout.md            (--holdout only)
  data/processed/trades_phase7_<family>_wf_oos.parquet
  data/processed/phase7_params_<family>.yaml

Ranking: Lucid 25K pass rate @1 micro PRIMARY, Ulcer Performance Index (UPI)
tie-breaker. Baselines: Phase 5 ORB WF OOS ledger and its skip-Monday overlay.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
from datetime import date
from pathlib import Path
from typing import Any

import polars as pl
import yaml

from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
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
from src.strategies.afternoon import AfternoonRangeBreakout
from src.strategies.mean_reversion import BollingerMeanReversion
from src.strategies.nr_compression import NrCompressionOrb
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.orb_filtered import FilteredOrb
from src.strategies.breakout import PrevDayLevelBreakout
from src.strategies.trend import EmaTrend
from src.strategies.vwap import VwapPullback
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase7")

STRATEGY_CLASSES = {
    "opening_range_breakout": OpeningRangeBreakout,
    "orb_filtered": FilteredOrb,
    "nr7_orb": NrCompressionOrb,
    "afternoon_breakout": AfternoonRangeBreakout,
    "ema_trend": EmaTrend,
    "vwap_pullback": VwapPullback,
    "prev_day_hl_breakout": PrevDayLevelBreakout,
    "bollinger_mean_reversion": BollingerMeanReversion,
}

ORB_BASELINE_LEDGER = "trades_opening_range_breakout_wf_oos.parquet"


def _as_date(v: date | str) -> date:
    return v if isinstance(v, date) else date.fromisoformat(v)


def _filter(df: pl.DataFrame, start: date, end: date) -> pl.DataFrame:
    return df.filter(
        (pl.col("trading_date") >= start) & (pl.col("trading_date") <= end)
    )


def skip_monday(trades: pl.DataFrame) -> pl.DataFrame:
    return trades.filter(pl.col("trading_date").dt.weekday() != 1)


def _sanitize(o: Any) -> Any:
    """JSON-safe: NaN/inf -> None, dates -> iso, numpy scalars -> python."""
    if isinstance(o, dict):
        return {str(k): _sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_sanitize(v) for v in o]
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, date):
        return o.isoformat()
    return o


def evaluate_ledger(
    name: str,
    trades: pl.DataFrame,
    rules: LucidRules,
    mc_cfg: dict,
    costs: dict,
) -> dict[str, Any]:
    """All Phase 7 numbers for one candidate ledger."""
    d = daily_pnl(trades)
    out: dict[str, Any] = {
        "name": name,
        "trade_metrics": compute_metrics(trades),
        "consistency": recency_metrics(d),
        "rolling_6m": rolling_window_stats(d),
        "year_pnls": year_pnls(d),
        "mc": {},
    }
    for k in mc_cfg["contracts"]:
        mc = run_monte_carlo(
            trades, rules, contracts=k,
            n_attempts=mc_cfg["n_attempts"], max_days=mc_cfg["max_days"],
            seed=mc_cfg["seed"],
            evaluation_cost=costs["evaluation_cost"], reset_cost=costs["reset_cost"],
            strategy=name,
        )
        out["mc"][k] = {
            "pass_rate": mc.pass_rate,
            "fail_rate": mc.fail_rate,
            "timeout_rate": mc.timeout_rate,
            "median_days": mc.median_days_to_pass,
            "expected_resets": mc.expected_resets_before_pass,
            "expected_cost": mc.expected_total_cost_before_pass,
            "expected_profit_per_attempt": mc.expected_profit_per_attempt,
        }
    return out


def _lb_row(r: dict[str, Any]) -> str:
    c = r["consistency"]["full"]
    c90 = r["consistency"]["last_90d"]
    c252 = r["consistency"]["last_252d"]
    roll = r["rolling_6m"]
    yp = r["year_pnls"]
    mc1 = r["mc"][1]
    last3 = sum(v for k, v in yp.items() if k in (2023, 2024, 2025))

    def _f(v, fmt="{:.2f}", dash_if_none=True):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return "—"
        return fmt.format(v)

    med = _f(mc1["median_days"], "{:.0f}")
    return (
        f"| {r['name']} | {r['trade_metrics'].get('n_trades', 0)} "
        f"| {100 * mc1['pass_rate']:.1f}% | {med} "
        f"| ${c.get('net_pnl', 0):,.0f} | {_f(c.get('sharpe_daily'))} "
        f"| {_f(c.get('upi'))} | ${c.get('max_drawdown', 0):,.0f} "
        f"| {_f(c.get('equity_r2'))} | {c.get('max_consec_losing_days', '—')} "
        f"| ${c90.get('net_pnl', 0):,.0f} | ${c252.get('net_pnl', 0):,.0f} "
        f"| ${last3:,.0f} "
        f"| {_f(roll.get('negative_share'), '{:.0%}')} "
        f"| ${roll.get('worst_window') or 0:,.0f} |"
    )


LB_HEADER = (
    "| Candidate | Trades | Pass@1 | Med d | Net $ | Sharpe | UPI | MaxDD | R² "
    "| ConsecL | Last90 $ | Last252 $ | 2023-25 $ | Neg 6m | Worst 6m |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- "
    "| --- | --- | --- |"
)


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--holdout", nargs="*", default=None, metavar="FAMILY",
        help="Run the 2026 holdout ONCE for these families (uses saved final params).",
    )
    args = ap.parse_args()

    cfg = yaml.safe_load(Path("config/phase7.yaml").read_text())
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
    mc_cfg = cfg["monte_carlo"]
    lucid_path = Path("config") / f"{mc_cfg['account']}.yaml"
    rules = LucidRules.from_yaml(lucid_path)
    lucid_costs = yaml.safe_load(lucid_path.read_text())["costs"]

    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")

    if args.holdout is not None:
        run_holdout(
            args.holdout, cfg, strat_cfg, processed, reports, exec_full, cost,
            rules, mc_cfg, lucid_costs,
        )
        return

    splits = cfg["splits"]
    grid_start, grid_end = _as_date(splits["grid_start"]), _as_date(splits["grid_end"])
    exec_grid = _filter(exec_full, grid_start, grid_end)
    wf_cfg = cfg["walk_forward"]
    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]), _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"], wf_cfg["test_months"],
    )
    scorer = lambda t: score_sharpe(t, min_trades=wf_cfg["min_trades_train"])

    sig_cache: dict[int, pl.DataFrame] = {}

    def sig_bars(tf: int) -> pl.DataFrame:
        if tf not in sig_cache:
            sig_cache[tf] = _filter(
                pl.read_parquet(processed / f"continuous_{tf}m.parquet"),
                grid_start, grid_end,
            )
        return sig_cache[tf]

    # ---- baselines -------------------------------------------------------
    results: list[dict[str, Any]] = []
    orb_oos = pl.read_parquet(processed / ORB_BASELINE_LEDGER)
    results.append(
        evaluate_ledger("BASELINE orb (Phase 5 WF OOS)", orb_oos, rules, mc_cfg, lucid_costs)
    )
    results.append(
        evaluate_ledger(
            "BASELINE orb +skipMon", skip_monday(orb_oos), rules, mc_cfg, lucid_costs
        )
    )

    # ---- candidate families: grid + walk-forward --------------------------
    wf_report: list[str] = ["# Phase 7 Walk-Forward", ""]
    final_params: dict[str, dict] = {}
    stress_targets: list[tuple[str, str, dict]] = []  # (family, strategy, params)

    for fam, fcfg in cfg["families"].items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        ecfg = EngineConfig(
            qty=eng["qty"], flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        space = fcfg["param_grid"]
        n_combos = 1
        for v in space.values():
            n_combos *= len(v)
        log.info("=== family %s (%s): %d combos ===", fam, cls.name, n_combos)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(cls.timeframe_minutes), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase7_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        final_params[fam] = chosen
        (processed / f"phase7_params_{fam}.yaml").write_text(yaml.dump(chosen))

        wf_report += [
            f"## {fam} ({cls.name})",
            "",
            f"- Final params (last fold): `{chosen}`",
            f"- Stitched OOS: {oos.height} trades, net ${oos['net_pnl'].sum() if oos.height else 0:,.0f}",
            "",
            render_fold_table(wf.folds),
            "",
        ]
        if oos.height:
            results.append(evaluate_ledger(fam, oos, rules, mc_cfg, lucid_costs))
            gates_weekdays = bool(chosen.get("skip_weekdays"))
            if not gates_weekdays:
                results.append(
                    evaluate_ledger(
                        f"{fam} +skipMon", skip_monday(oos), rules, mc_cfg, lucid_costs
                    )
                )
            stress_targets.append((fam, fcfg["strategy"], chosen))

    # ---- rejected families: consistency re-score only ---------------------
    rejected_rows: list[dict[str, Any]] = []
    for name in cfg.get("rescore_rejected", []):
        cls = STRATEGY_CLASSES[name]
        scfg = strat_cfg["strategies"][name]
        ecfg = EngineConfig(
            qty=eng["qty"], flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=scfg.get("max_trades_per_day"),
            max_hold_minutes=scfg.get("max_hold_minutes"),
        )
        strat = cls(scfg.get("params", {}))
        res = run_backtest(
            exec_grid, strat.prepare(sig_bars(cls.timeframe_minutes)),
            cls.timeframe_minutes, cost, ecfg, strategy_name=name,
        )
        if res.trades.height:
            rejected_rows.append(
                evaluate_ledger(f"REJ {name}", res.trades, rules, mc_cfg, lucid_costs)
            )

    # ---- leaderboard -------------------------------------------------------
    def sort_key(r: dict) -> tuple:
        upi = r["consistency"]["full"].get("upi")
        return (
            r["mc"][1]["pass_rate"],
            -1e9 if upi is None or math.isnan(upi) else upi,
        )

    results.sort(key=sort_key, reverse=True)

    lb = [
        "# Phase 7 Leaderboard — consistency-focused candidates",
        "",
        f"WF OOS window: stitched test folds 2021-06 → 2025-11 (same folds as Phase 5). "
        f"MC: {mc_cfg['n_attempts']} attempts, block bootstrap, seed {mc_cfg['seed']}, "
        f"Lucid 25K, @1 micro. Sorted by **pass rate**, then **UPI** "
        f"(annualized P&L / ulcer index). `+skipMon` = same ledger, Mondays removed "
        f"(post-hoc overlay, Phase 6b methodology).",
        "",
        LB_HEADER,
    ]
    lb += [_lb_row(r) for r in results]
    lb += [
        "",
        "## Rejected families (consistency re-score, fixed params, full grid window)",
        "",
        "Documented only — not candidates (failed Phase 3-5 expectancy/holdout).",
        "",
        LB_HEADER,
    ]
    lb += [_lb_row(r) for r in rejected_rows]

    # ---- slippage stress for the top families ------------------------------
    stress_lines: list[str] = ["", "## Slippage stress (2025, final params)", ""]
    ranked_fams = [
        r["name"] for r in results if r["name"] in {f for f, _, _ in stress_targets}
    ]
    st_cfg = cfg["stress"]
    for fam in ranked_fams[:3]:
        strategy_name = cfg["families"][fam]["strategy"]
        cls = STRATEGY_CLASSES[strategy_name]
        ecfg = EngineConfig(
            qty=eng["qty"], flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=cfg["families"][fam].get("max_trades_per_day"),
        )
        rows = slippage_sweep(
            cls, final_params[fam], exec_full,
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            cost, st_cfg["slippage_ticks"], ecfg,
            _as_date(st_cfg["period_start"]), _as_date(st_cfg["period_end"]),
        )
        stress_lines += render_stress_section(fam, rows)
    lb += stress_lines

    (reports / "phase7_leaderboard.md").write_text("\n".join(lb) + "\n")
    (reports / "phase7_walk_forward.md").write_text("\n".join(wf_report) + "\n")
    (reports / "phase7_metrics.json").write_text(
        json.dumps(
            _sanitize({"candidates": results, "rejected": rejected_rows,
                       "final_params": final_params}),
            indent=1,
        )
    )
    log.info("Phase 7 reports written to %s", reports)


def run_holdout(
    families: list[str],
    cfg: dict,
    strat_cfg: dict,
    processed: Path,
    reports: Path,
    exec_full: pl.DataFrame,
    cost: CostModel,
    rules: LucidRules,
    mc_cfg: dict,
    lucid_costs: dict,
) -> None:
    """ONE 2026 comparison for the named finalists. Do not iterate on this."""
    splits = cfg["splits"]
    h_start, h_end = _as_date(splits["holdout_start"]), _as_date(splits["holdout_end"])
    eng = strat_cfg["engine"]
    lines = [
        "# Phase 7 — 2026 Holdout (single run)",
        "",
        "**Run once for the Phase 7 finalists. Do not re-run for tuning.**",
        "",
        LB_HEADER,
    ]
    rows: list[dict[str, Any]] = []
    for fam in families:
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        params = yaml.safe_load(
            (processed / f"phase7_params_{fam}.yaml").read_text()
        )
        ecfg = EngineConfig(
            qty=eng["qty"], flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        # Prepare on a warmup margin so day-level context (vol_ref etc.) is
        # live from holdout day 1, then slice the PREPARED frame to the
        # holdout window: prepare() is causal, and slicing afterwards keeps
        # stale pre-holdout signal bars away from the engine.
        warm_start = date(2025, 11, 1)
        sig = _filter(
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            warm_start, h_end,
        )
        strat = cls(params)
        prepared = _filter(strat.prepare(sig), h_start, h_end)
        res = run_backtest(
            _filter(exec_full, h_start, h_end), prepared,
            cls.timeframe_minutes, cost, ecfg, strategy_name=fam,
        )
        trades = _filter(res.trades, h_start, h_end)
        trades.write_parquet(processed / f"trades_phase7_{fam}_holdout.parquet")
        r = evaluate_ledger(f"{fam} (holdout)", trades, rules, mc_cfg, lucid_costs)
        r["params"] = params
        rows.append(r)
        lines.append(_lb_row(r))
        # predeclared skip-Monday overlay (Phase 6b methodology), same run
        if trades.height and not params.get("skip_weekdays"):
            ro = evaluate_ledger(
                f"{fam} +skipMon (holdout)", skip_monday(trades), rules, mc_cfg,
                lucid_costs,
            )
            ro["params"] = {**params, "skip_weekdays": [1]}
            rows.append(ro)
            lines.append(_lb_row(ro))

    lines += ["", "Final params per family:", ""]
    for r in rows:
        lines.append(f"- `{r['name']}`: `{r['params']}`")
    (reports / "phase7_holdout.md").write_text("\n".join(lines) + "\n")
    (reports / "phase7_holdout_metrics.json").write_text(
        json.dumps(_sanitize({"holdout": rows}), indent=1)
    )
    log.info("Phase 7 holdout written to %s", reports)


if __name__ == "__main__":
    main()

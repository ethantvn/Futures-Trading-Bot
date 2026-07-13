"""Phase 5 validation: walk-forward, sensitivity, stress, holdout.

Usage:
  .venv/bin/python scripts/run_validation.py              # WF + sensitivity + stress
  .venv/bin/python scripts/run_validation.py --holdout  # also run 2026 holdout ONCE

Writes:
  data/reports/validation_walk_forward.md
  data/reports/validation_sensitivity.md
  data/reports/validation_stress.md
  data/reports/validation_holdout.md          (--holdout only)
  data/reports/validation_summary.md
  data/processed/trades_<strategy>_wf_oos.parquet
  data/processed/wf_params_<strategy>.yaml
"""
from __future__ import annotations

import argparse
import logging
import math
from datetime import date
from pathlib import Path

import polars as pl
import yaml

from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.backtest.metrics import compute_metrics
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import run_monte_carlo
from src.logging_setup import setup_logging
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.trend import EmaTrend
from src.validation.reporting import (
    render_holdout_section,
    render_mc_section,
    render_sensitivity_section,
    render_stress_section,
    render_walk_forward_section,
    top_grid_on_window,
)
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    sensitivity_table,
    walk_forward,
)

log = logging.getLogger("run_validation")

STRATEGIES = {
    OpeningRangeBreakout.name: OpeningRangeBreakout,
    EmaTrend.name: EmaTrend,
}

PHASE5 = tuple(STRATEGIES)


def _load_configs() -> tuple[dict, dict, dict]:
    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    val_cfg = yaml.safe_load(Path("config/validation.yaml").read_text())
    return data_cfg, strat_cfg, val_cfg


def _engine_cfg(strat_cfg: dict, scfg: dict) -> EngineConfig:
    eng = strat_cfg["engine"]
    return EngineConfig(
        qty=eng["qty"],
        flat_time=eng["flat_time"],
        no_entry_after=eng["no_entry_after"],
        max_trades_per_day=scfg.get("max_trades_per_day"),
        max_hold_minutes=scfg.get("max_hold_minutes"),
    )


def _base_cost(strat_cfg: dict, data_cfg: dict) -> CostModel:
    eng = strat_cfg["engine"]
    return CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )


def _as_date(v: date | str) -> date:
    return v if isinstance(v, date) else date.fromisoformat(v)


def _filter(df: pl.DataFrame, start: date, end: date) -> pl.DataFrame:
    return df.filter(
        (pl.col("trading_date") >= start) & (pl.col("trading_date") <= end)
    )


def _run_backtest(
    name: str,
    params: dict,
    exec_bars: pl.DataFrame,
    signal_bars: pl.DataFrame,
    cost: CostModel,
    ecfg: EngineConfig,
) -> pl.DataFrame:
    strat = STRATEGIES[name](params)
    prepared = strat.prepare(signal_bars)
    return run_backtest(
        exec_bars, prepared, strat.timeframe_minutes, cost, ecfg, strategy_name=name
    ).trades


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--holdout",
        action="store_true",
        help="Run the 2026 holdout once (do not re-run after tuning).",
    )
    ap.add_argument("--strategies", nargs="+", default=list(PHASE5))
    args = ap.parse_args()

    data_cfg, strat_cfg, val_cfg = _load_configs()
    splits = val_cfg["splits"]
    wf_cfg = val_cfg["walk_forward"]
    stress_cfg = val_cfg["stress"]
    mc_cfg = val_cfg["monte_carlo"]

    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    base_cost = _base_cost(strat_cfg, data_cfg)
    lucid_path = Path("config") / f"{mc_cfg['account']}.yaml"
    rules = LucidRules.from_yaml(lucid_path)
    costs = yaml.safe_load(lucid_path.read_text())["costs"]

    grid_start = _as_date(splits["grid_start"])
    grid_end = _as_date(splits["grid_end"])
    val_start = _as_date(splits["validation_start"])
    val_end = _as_date(splits["validation_end"])

    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    exec_grid = _filter(exec_full, grid_start, grid_end)

    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]),
        _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"],
        wf_cfg["test_months"],
    )
    min_trades = wf_cfg["min_trades_train"]
    scorer = lambda t: score_sharpe(t, min_trades=min_trades)

    wf_sections: list[str] = [
        "# Walk-Forward Validation",
        "",
        f"- Grid period: {grid_start} → {grid_end}",
        f"- Folds: {wf_cfg['train_months']}m train / {wf_cfg['test_months']}m test "
        f"({len(folds)} windows)",
        f"- Train selection: daily Sharpe (min {min_trades} trades)",
        "",
    ]
    sens_sections: list[str] = ["# Parameter Sensitivity", ""]
    stress_sections: list[str] = ["# Slippage Stress (2025)", ""]
    summary: list[str] = [
        "# Phase 5 Validation Summary",
        "",
        "Candidates: `opening_range_breakout`, `ema_trend`. "
        "Holdout 2026 is untouched unless `--holdout` was passed.",
        "",
    ]
    mc_oos_results = []
    mc_holdout_results = []
    final_params: dict[str, dict] = {}

    for name in args.strategies:
        if name not in STRATEGIES:
            log.warning("unknown strategy %s", name)
            continue

        scfg = strat_cfg["strategies"][name]
        baseline = scfg.get("params", {})
        space = val_cfg["strategies"][name]["param_grid"]
        tf = STRATEGIES[name].timeframe_minutes
        ecfg = _engine_cfg(strat_cfg, scfg)
        sig_grid = _filter(
            pl.read_parquet(processed / f"continuous_{tf}m.parquet"), grid_start, grid_end
        )

        n_combos = 1
        for v in space.values():
            n_combos *= len(v)
        log.info("=== %s: %d combos ===", name, n_combos)

        grid_runs = run_full_period_grid(
            STRATEGIES[name], space, exec_grid, sig_grid, base_cost, ecfg,
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        chosen = wf.final_params or baseline
        final_params[name] = chosen

        wf.oos_trades.write_parquet(processed / f"trades_{name}_wf_oos.parquet")
        (processed / f"wf_params_{name}.yaml").write_text(yaml.dump(chosen))
        wf_sections.extend(render_walk_forward_section(name, wf))

        sig_all = pl.read_parquet(processed / f"continuous_{tf}m.parquet")
        sens_sections.extend(
            render_sensitivity_section(
                name, sensitivity_table(grid_runs, chosen, val_start, val_end)
            )
        )

        stress_rows = slippage_sweep(
            STRATEGIES[name], chosen, exec_full, sig_all, base_cost,
            stress_cfg["slippage_ticks"], ecfg,
            _as_date(stress_cfg["period_start"]),
            _as_date(stress_cfg["period_end"]),
        )
        stress_sections.extend(render_stress_section(name, stress_rows))

        oos_m = compute_metrics(wf.oos_trades)
        pass_1m = pass_2m = float("nan")
        for k in mc_cfg["contracts"]:
            mc = run_monte_carlo(
                wf.oos_trades, rules, contracts=k,
                n_attempts=mc_cfg["n_attempts"],
                max_days=mc_cfg["max_days"],
                seed=mc_cfg["seed"],
                evaluation_cost=costs["evaluation_cost"],
                reset_cost=costs["reset_cost"],
                strategy=f"{name} (WF OOS)",
            )
            mc_oos_results.append(mc)
            if k == 1:
                pass_1m = mc.pass_rate
            elif k == 2:
                pass_2m = mc.pass_rate

        top = top_grid_on_window(grid_runs, val_start, val_end, top_n=3)
        slip_ok = all(r.net_pnl > 0 for r in stress_rows)

        def _f(x: float) -> str:
            return f"{x:.2f}" if not math.isnan(x) else "—"

        summary.append(f"## {name}")
        summary.append("")
        summary.append(
            f"- Walk-forward OOS: {oos_m.get('n_trades', 0)} trades, "
            f"net ${oos_m.get('net_pnl', 0):,.0f}, "
            f"Sharpe {_f(oos_m.get('sharpe_daily', float('nan')))}, "
            f"PF {_f(oos_m.get('profit_factor', float('nan')))}"
        )
        summary.append(f"- Final params: `{chosen}`")
        summary.append(
            f"- 25K pass rate (WF OOS): {100 * pass_1m:.1f}% @1 micro, "
            f"{100 * pass_2m:.1f}% @2 micros"
        )
        summary.append(
            f"- Slippage stress 2025: "
            + ("robust (profitable at 0/1/2 ticks)" if slip_ok else "fragile")
        )
        if top:
            summary.append("- Top configs on 2023-2024 validation window:")
            for t in top:
                ts = t.get("sharpe_daily", float("nan"))
                summary.append(
                    f"  - `{t['params']}`: Sharpe {ts:.2f}, net ${t.get('net_pnl', 0):,.0f}"
                )
        summary.append("")

    holdout_sections: list[str] = []
    if args.holdout:
        h_start = _as_date(splits["holdout_start"])
        h_end = _as_date(splits["holdout_end"])
        holdout_sections = [
            "# 2026 Holdout (single run)",
            "",
            "**This holdout was run once. Do not re-run for tuning.**",
            "",
        ]
        for name in args.strategies:
            if name not in final_params:
                continue
            scfg = strat_cfg["strategies"][name]
            ecfg = _engine_cfg(strat_cfg, scfg)
            chosen = final_params[name]
            tf = STRATEGIES[name].timeframe_minutes
            trades = _run_backtest(
                name, chosen,
                _filter(exec_full, h_start, h_end),
                _filter(pl.read_parquet(processed / f"continuous_{tf}m.parquet"), h_start, h_end),
                base_cost, ecfg,
            )
            trades.write_parquet(processed / f"trades_{name}_holdout.parquet")
            holdout_sections.extend(render_holdout_section(name, trades, chosen))
            for k in mc_cfg["contracts"]:
                mc_holdout_results.append(
                    run_monte_carlo(
                        trades, rules, contracts=k,
                        n_attempts=mc_cfg["n_attempts"],
                        max_days=mc_cfg["max_days"],
                        seed=mc_cfg["seed"],
                        evaluation_cost=costs["evaluation_cost"],
                        reset_cost=costs["reset_cost"],
                        strategy=f"{name} (holdout 2026)",
                    )
                )

    (reports / "validation_walk_forward.md").write_text("\n".join(wf_sections))
    (reports / "validation_sensitivity.md").write_text("\n".join(sens_sections))
    (reports / "validation_stress.md").write_text("\n".join(stress_sections))
    summary.extend(render_mc_section("Monte Carlo — walk-forward OOS", mc_oos_results))
    (reports / "validation_summary.md").write_text("\n".join(summary))

    if holdout_sections:
        holdout_sections.extend(
            render_mc_section("Monte Carlo — 2026 holdout", mc_holdout_results)
        )
        (reports / "validation_holdout.md").write_text("\n".join(holdout_sections))

    log.info("Phase 5 reports written to %s", reports)


if __name__ == "__main__":
    main()

"""Phase 12: Deep GC parameter search for Lucid Flex 50K.

Usage:
  .venv/bin/python scripts/run_phase12.py
  .venv/bin/python scripts/run_phase12.py --holdout macro_nfp_cpi ny_orb_deep

Selection discipline:
  - Params chosen on pre-2026 walk-forward only
  - Rank by 50K pass rate, then fold-stability (% positive OOS folds), then UPI
  - Holdout 2026 run once for top finalists — no re-tune after looking
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl
import yaml

from scripts.run_phase7 import _as_date, _filter, _sanitize, evaluate_ledger
from scripts.run_phase11 import STRATEGY_CLASSES
from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.evaluation.lucid_rules import LucidRules
from src.logging_setup import setup_logging
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    param_grid,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase12")


def fold_stability(wf) -> dict[str, float]:
    """Share of test folds with positive net PnL + median test $."""
    nets = []
    for f in wf.folds:
        t = f.test_trades if hasattr(f, "test_trades") else None
        # FoldResult structure from walk_forward
        net = getattr(f, "test_net", None)
        if net is None and hasattr(f, "test_metrics"):
            net = f.test_metrics.get("net_pnl") if f.test_metrics else None
        if net is None:
            # fall back: parse from fold object fields used in render
            net = getattr(f, "oos_pnl", None)
        if net is not None:
            nets.append(float(net))
    if not nets:
        # walk_forward FoldResult — check attributes
        return {"pos_fold_share": 0.0, "median_test_pnl": 0.0, "n_folds": 0}
    pos = sum(1 for n in nets if n > 0) / len(nets)
    return {
        "pos_fold_share": pos,
        "median_test_pnl": float(sorted(nets)[len(nets) // 2]),
        "n_folds": len(nets),
    }


def _fold_nets_from_wf(wf) -> list[float]:
    return [float(fr.test_net) for fr in wf.folds]


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", nargs="*", metavar="FAMILY")
    ap.add_argument(
        "--families",
        nargs="*",
        help="Run only these family keys (default: all).",
    )
    args = ap.parse_args()

    cfg = yaml.safe_load(Path("config/gc_phase12.yaml").read_text())
    data_cfg = yaml.safe_load(Path("config/data_gc.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies_gc.yaml").read_text())
    eng = strat_cfg["engine"]

    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    mc_cfg = cfg["monte_carlo"]
    rules = LucidRules.from_yaml(Path("config") / f"{mc_cfg['account']}.yaml")
    lucid_costs = yaml.safe_load(Path("config/lucid_50k.yaml").read_text())["costs"]

    splits = cfg["splits"]
    grid_start, grid_end = _as_date(splits["grid_start"]), _as_date(splits["grid_end"])
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    exec_grid = _filter(exec_full, grid_start, grid_end)
    wf_cfg = cfg["walk_forward"]
    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]),
        _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"],
        wf_cfg["test_months"],
    )

    if args.holdout is not None:
        _run_holdout(args.holdout, cfg, processed, exec_full, cost, eng, rules, splits, mc_cfg, lucid_costs)
        return

    sig_cache: dict[int, pl.DataFrame] = {}

    def sig_bars(tf: int) -> pl.DataFrame:
        if tf not in sig_cache:
            sig_cache[tf] = _filter(
                pl.read_parquet(processed / f"continuous_{tf}m.parquet"),
                grid_start,
                grid_end,
            )
        return sig_cache[tf]

    families = cfg["families"]
    if args.families:
        families = {k: families[k] for k in args.families if k in families}

    results: list[dict[str, Any]] = []
    wf_report = [
        "# Phase 12 GC Deep-Parameter Walk-Forward",
        "",
        f"- Folds: {len(folds)} × (18m train / 6m test)",
        f"- Grid: {grid_start} → {grid_end}",
        "",
    ]
    final_params: dict[str, dict] = {}
    grid_sizes: dict[str, int] = {}

    for fam, fcfg in families.items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        space = fcfg["param_grid"]
        n_combo = len(param_grid(space))
        grid_sizes[fam] = n_combo
        min_tr = int(fcfg.get("min_trades_train", wf_cfg["min_trades_train"]))
        scorer = lambda t, mt=min_tr: score_sharpe(t, min_trades=mt)
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        log.info("=== Phase 12 %s (%d combos) ===", fam, n_combo)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(cls.timeframe_minutes), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase12_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        final_params[fam] = chosen
        (processed / f"phase12_params_{fam}.yaml").write_text(yaml.dump(chosen))

        nets = _fold_nets_from_wf(wf)
        pos_share = (sum(1 for n in nets if n > 0) / len(nets)) if nets else 0.0
        med_test = float(sorted(nets)[len(nets) // 2]) if nets else 0.0

        wf_report += [
            f"## {fam}",
            "",
            f"- Grid size: **{n_combo}** combos",
            f"- Final params: `{chosen}`",
            f"- OOS trades: {oos.height}, net ${oos['net_pnl'].sum() if oos.height else 0:,.0f}",
            f"- Fold stability: {100 * pos_share:.0f}% positive test folds "
            f"(median test ${med_test:,.0f})",
            "",
            render_fold_table(wf.folds),
            "",
        ]
        if not oos.height:
            continue

        # Year breakdown for regime check
        yp = (
            oos.group_by(pl.col("trading_date").dt.year().alias("y"))
            .agg(pl.len().alias("n"), pl.col("net_pnl").sum().alias("net"))
            .sort("y")
        )
        year_pnls = {str(r["y"]): float(r["net"]) for r in yp.to_dicts()}

        r = evaluate_ledger(f"GC12 {fam}", oos, rules, mc_cfg, lucid_costs)
        r["params"] = chosen
        r["family"] = fam
        r["grid_size"] = n_combo
        r["pos_fold_share"] = pos_share
        r["median_test_pnl"] = med_test
        r["year_pnls_oos"] = year_pnls
        results.append(r)

    def sort_key(r: dict) -> tuple:
        upi = r["consistency"]["full"].get("upi")
        return (
            r["mc"][1]["pass_rate"],
            r.get("pos_fold_share", 0),
            -1e9 if upi is None or math.isnan(upi) else upi,
        )

    results.sort(key=sort_key, reverse=True)

    lb = [
        "# Phase 12 GC Deep-Parameter Leaderboard — Lucid Flex 50K",
        "",
        "Sorted by pass rate → fold stability → UPI. "
        "Deep grids; selection still walk-forward (no 2026 in training).",
        "",
        "| Candidate | Combos | Trades | Pass@1 | Fail % | Fold+ % | Med d | Net $ | UPI | MaxDD | 2025 $ |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        mc = r["mc"][1]
        c = r["consistency"]["full"]
        med = mc.get("median_days")
        med_s = f"{med:.0f}" if med else "—"
        y2025 = r.get("year_pnls_oos", {}).get("2025", 0)
        lb.append(
            f"| {r['name']} | {r.get('grid_size', 0)} "
            f"| {r['trade_metrics'].get('n_trades', 0)} "
            f"| {100 * mc['pass_rate']:.1f}% "
            f"| {100 * mc['fail_rate']:.1f}% "
            f"| {100 * r.get('pos_fold_share', 0):.0f}% "
            f"| {med_s} "
            f"| ${c.get('net_pnl', 0):,.0f} "
            f"| {c.get('upi', 0):.1f} "
            f"| ${c.get('max_drawdown', 0):,.0f} "
            f"| ${y2025:,.0f} |"
        )

    # Stress top 2
    st_cfg = cfg["stress"]
    stress_lines = ["", "## Slippage stress (2025, top 2)", ""]
    for r in results[:2]:
        fam = r["family"]
        fcfg = families[fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        params = r.get("params") or {}
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        rows = slippage_sweep(
            cls, params, exec_full,
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            cost, st_cfg["slippage_ticks"], ecfg,
            _as_date(st_cfg["period_start"]), _as_date(st_cfg["period_end"]),
        )
        stress_lines += render_stress_section(f"GC12 {fam}", rows)
    lb += stress_lines

    (reports / "phase12_leaderboard.md").write_text("\n".join(lb) + "\n")
    (reports / "phase12_walk_forward.md").write_text("\n".join(wf_report) + "\n")
    (reports / "phase12_metrics.json").write_text(
        json.dumps(
            _sanitize({
                "candidates": results,
                "final_params": final_params,
                "grid_sizes": grid_sizes,
                "folds": len(folds),
            }),
            indent=1,
        )
    )
    _write_report(results, final_params, grid_sizes, len(folds), reports)
    log.info("Phase 12 complete → %s", reports)


def _run_holdout(
    families: list[str],
    cfg: dict,
    processed: Path,
    exec_full: pl.DataFrame,
    cost: CostModel,
    eng: dict,
    rules: LucidRules,
    splits: dict,
    mc_cfg: dict,
    lucid_costs: dict,
) -> None:
    hs, he = _as_date(splits["holdout_start"]), _as_date(splits["holdout_end"])
    exec_h = _filter(exec_full, hs, he)
    lines = [
        "# Phase 12 GC Holdout (2026)",
        "",
        f"Single run {hs} → {he}. Frozen Phase 12 params — no re-tune.",
        "",
        "| Family | Trades | Net $ | Pass MC % |",
        "| --- | --- | --- | --- |",
    ]
    for fam in families:
        ppath = processed / f"phase12_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | params missing | — |")
            continue
        params = yaml.safe_load(ppath.read_text()) or {}
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        sig = _filter(
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            hs, he,
        )
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        prepared = cls(params).prepare(sig)
        res = run_backtest(exec_h, prepared, cls.timeframe_minutes, cost, ecfg, cls.name)
        trades = res.trades
        trades.write_parquet(processed / f"trades_phase12_{fam}_holdout.parquet")
        if trades.height == 0:
            lines.append(f"| {fam} | 0 | $0 | — |")
            continue
        mc = evaluate_ledger(fam, trades, rules, mc_cfg, lucid_costs)
        net = float(trades["net_pnl"].sum())
        lines.append(
            f"| {fam} | {trades.height} | ${net:,.0f} "
            f"| {100 * mc['mc'][1]['pass_rate']:.1f}% |"
        )
    Path("data/reports/gc/phase12_holdout.md").write_text("\n".join(lines) + "\n")
    log.info("Holdout → data/reports/gc/phase12_holdout.md")


def _write_report(
    results: list[dict],
    final_params: dict,
    grid_sizes: dict,
    n_folds: int,
    reports: Path,
) -> None:
    winner = results[0] if results else {}
    w_pass = 100 * winner["mc"][1]["pass_rate"] if winner else 0
    holdout_path = reports / "phase12_holdout.md"
    holdout_txt = holdout_path.read_text() if holdout_path.exists() else ""

    lines = [
        "# Phase 12 Report — GC Deep Parameter Search (Lucid Flex 50K)",
        "",
        "Date: 2026-07-10. Expanded grids on Phase 11 survivors; fold-stability ranking.",
        "",
        "## TL;DR",
        "",
    ]
    if winner:
        lines.append(
            f"Best deep-search candidate: `{winner['name']}` — "
            f"**{w_pass:.1f}%** 50K pass, "
            f"{100 * winner.get('pos_fold_share', 0):.0f}% positive WF folds, "
            f"grid size {winner.get('grid_size', 0)}. "
            "Compare to Phase 11 macro_nfp_cpi (53.9% pass, holdout failed)."
        )
    else:
        lines.append("No candidates produced OOS trades.")

    lines += [
        "",
        "## Method",
        "",
        f"- {n_folds} folds, 18m/6m, grid through 2025-12-31",
        "- Expanded axes: pre-range, post-delay, target R, expire, risk cap, "
        "min-range filter, long-only; NFP/CPI/FOMC split",
        "- Rank: Lucid 50K pass → fold stability → UPI",
        "- 2026 holdout: single run after selection (no re-tune)",
        "",
        f"- Total combos searched: **{sum(grid_sizes.values())}**",
        "",
        "## Leaderboard (top)",
        "",
        "| Candidate | Pass % | Fold+ % | Net $ | UPI | 2025 $ |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in results[:8]:
        mc = r["mc"][1]
        c = r["consistency"]["full"]
        y25 = r.get("year_pnls_oos", {}).get("2025", 0)
        lines.append(
            f"| {r['name']} | {100 * mc['pass_rate']:.1f}% "
            f"| {100 * r.get('pos_fold_share', 0):.0f}% "
            f"| ${c.get('net_pnl', 0):,.0f} | {c.get('upi', 0):.1f} "
            f"| ${y25:,.0f} |"
        )

    if final_params:
        lines += ["", "## Selected params (last WF fold)", ""]
        for fam, p in final_params.items():
            lines.append(f"- **{fam}** ({grid_sizes.get(fam, 0)} combos): `{p}`")

    if holdout_txt:
        lines += ["", "## 2026 holdout", "", holdout_txt.strip(), ""]

    lines += [
        "",
        "## Recommendation",
        "",
        "Deep search cannot invent a durable edge if 2025–2026 regimes broke the "
        "macro release pattern. Prefer candidates with **high fold stability AND "
        "non-negative 2025**, then confirm holdout once. If none survive, stay on "
        "MNQ ORB-W; consider MGC micro for gold sizing.",
        "",
        "## Artifacts",
        "",
        "| File | Content |",
        "| --- | --- |",
        "| `data/reports/gc/phase12_leaderboard.md` | Ranking |",
        "| `data/reports/gc/phase12_walk_forward.md` | Fold tables |",
        "| `config/gc_phase12.yaml` | Grids |",
    ]
    Path("docs/PHASE_12_REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

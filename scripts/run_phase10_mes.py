"""Phase 10: MES ORB-W walk-forward + Lucid 25K MC.

Usage:
  .venv/bin/python scripts/run_phase10_mes.py

Prerequisites:
  .venv/bin/python scripts/build_bars.py --config config/data_mes.yaml

Writes:
  data/reports/mes/phase10_leaderboard.md
  data/reports/mes/phase10_walk_forward.md
  data/reports/mes/phase10_metrics.json
  docs/PHASE_10_REPORT.md
  data/processed/mes/trades_phase10_<family>_wf_oos.parquet
"""
from __future__ import annotations

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

from scripts.run_phase7 import (
    LB_HEADER,
    STRATEGY_CLASSES,
    _as_date,
    _filter,
    _lb_row,
    _sanitize,
    evaluate_ledger,
    skip_monday,
)
from scripts.run_phase9 import _pass_and_payout_mc
from src.backtest.engine import EngineConfig
from src.backtest.fees import CostModel
from src.evaluation.lucid_rules import LucidRules
from src.logging_setup import setup_logging
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase10_mes")


def main() -> None:
    setup_logging()
    cfg = yaml.safe_load(Path("config/phase10.yaml").read_text())
    data_cfg = yaml.safe_load(Path("config/data_mes.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    eng = strat_cfg["engine"]

    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    processed.mkdir(parents=True, exist_ok=True)
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
    lucid_costs = yaml.safe_load(Path("config/lucid_25k.yaml").read_text())["costs"]

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
    scorer = lambda t: score_sharpe(t, min_trades=wf_cfg["min_trades_train"])

    sig_cache: dict[int, pl.DataFrame] = {}

    def sig_bars(tf: int) -> pl.DataFrame:
        if tf not in sig_cache:
            sig_cache[tf] = _filter(
                pl.read_parquet(processed / f"continuous_{tf}m.parquet"),
                grid_start,
                grid_end,
            )
        return sig_cache[tf]

    results: list[dict[str, Any]] = []
    wf_report: list[str] = ["# Phase 10 MES Walk-Forward", ""]
    final_params: dict[str, dict] = {}
    stress_targets: list[tuple[str, str, dict]] = []

    # MNQ baseline for comparison (same Lucid MC, different instrument ledger).
    bl = cfg.get("mnq_baseline", {})
    bl_path = Path(bl.get("ledger", ""))
    if bl_path.exists():
        t = skip_monday(pl.read_parquet(bl_path))
        r = evaluate_ledger(bl["name"], t, rules, mc_cfg, lucid_costs)
        r["journey"] = _pass_and_payout_mc(t, rules)
        r["instrument"] = "MNQ"
        results.append(r)

    for fam, fcfg in cfg["families"].items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        space = fcfg["param_grid"]
        log.info("=== Phase 10 MES family %s ===", fam)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(cls.timeframe_minutes), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase10_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        final_params[fam] = chosen
        (processed / f"phase10_params_{fam}.yaml").write_text(yaml.dump(chosen))

        wf_report += [
            f"## {fam}",
            "",
            f"- Final params: `{chosen}`",
            f"- OOS trades: {oos.height}, net ${oos['net_pnl'].sum() if oos.height else 0:,.0f}",
            "",
            render_fold_table(wf.folds),
            "",
        ]
        if not oos.height:
            continue

        name = f"MES {fam}"
        ledger = oos
        if cfg.get("post_overlays", {}).get("skip_monday") and not chosen.get(
            "skip_weekdays"
        ):
            name = f"MES {fam} +skipMon"
            ledger = skip_monday(oos)

        r = evaluate_ledger(name, ledger, rules, mc_cfg, lucid_costs)
        r["journey"] = _pass_and_payout_mc(ledger, rules)
        r["params"] = chosen
        r["instrument"] = "MES"
        results.append(r)
        stress_targets.append((fam, fcfg["strategy"], chosen))

    def sort_key(r: dict) -> tuple:
        upi = r["consistency"]["full"].get("upi")
        return (
            r["mc"][1]["pass_rate"],
            -1e9 if upi is None or math.isnan(upi) else upi,
        )

    results.sort(key=sort_key, reverse=True)

    lb = [
        "# Phase 10 MES Leaderboard",
        "",
        "MES micro @ 1 contract. Lucid Flex 25K MC (10k block-bootstrap). "
        "`Pass+Payout` = pass eval AND first $500-eligible payout. "
        "Sorted by pass rate, then UPI.",
        "",
        "| Candidate | Trades | Pass@1 | Pass+Payout | Med d | Net $ | Sharpe | UPI | MaxDD | Last252 $ |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        mc = r["mc"][1]
        c = r["consistency"]["full"]
        j = r.get("journey", {})
        med = mc.get("median_days")
        med_s = f"{med:.0f}" if med else "—"
        lb.append(
            f"| {r['name']} | {r['trade_metrics'].get('n_trades', 0)} "
            f"| {100 * mc['pass_rate']:.1f}% "
            f"| {100 * j.get('pass_and_payout', 0):.1f}% "
            f"| {med_s} "
            f"| ${c.get('net_pnl', 0):,.0f} "
            f"| {c.get('sharpe_daily', 0):.2f} "
            f"| {c.get('upi', 0):.1f} "
            f"| ${c.get('max_drawdown', 0):,.0f} "
            f"| ${r['consistency']['last_252d'].get('net_pnl', 0):,.0f} |"
        )

    st_cfg = cfg["stress"]
    stress_lines = ["", "## Slippage stress (2025, final params)", ""]
    for fam, strategy_name, params in stress_targets[:2]:
        cls = STRATEGY_CLASSES[strategy_name]
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=cfg["families"][fam].get("max_trades_per_day"),
        )
        rows = slippage_sweep(
            cls,
            params,
            exec_full,
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            cost,
            st_cfg["slippage_ticks"],
            ecfg,
            _as_date(st_cfg["period_start"]),
            _as_date(st_cfg["period_end"]),
        )
        stress_lines += render_stress_section(f"MES {fam}", rows)
    lb += stress_lines

    (reports / "phase10_leaderboard.md").write_text("\n".join(lb) + "\n")
    (reports / "phase10_walk_forward.md").write_text("\n".join(wf_report) + "\n")
    (reports / "phase10_metrics.json").write_text(
        json.dumps(_sanitize({"candidates": results, "final_params": final_params}), indent=1)
    )
    _write_report(results, final_params, reports)
    log.info("Phase 10 MES complete → %s", reports)


def _write_report(
    results: list[dict], final_params: dict[str, dict], reports: Path
) -> None:
    mes_results = [r for r in results if r.get("instrument") == "MES"]
    mnq = next((r for r in results if r.get("instrument") == "MNQ"), None)
    winner = mes_results[0] if mes_results else {}

    lines = [
        "# Phase 10 Report — MES ORB-W Validation",
        "",
        "Date: 2026-07-08. Second-instrument validation for Lucid Flex 25K @ 1 MES micro.",
        "",
        "## TL;DR",
        "",
    ]
    if winner and mnq:
        w_pass = 100 * winner["mc"][1]["pass_rate"]
        m_pass = 100 * mnq["mc"][1]["pass_rate"]
        if winner["mc"][1]["pass_rate"] >= mnq["mc"][1]["pass_rate"]:
            lines.append(
                f"**MES `{winner['name']}` matches or beats MNQ Phase 9 baseline "
                f"({w_pass:.1f}% vs {m_pass:.1f}% pass @1 micro).** "
                "Viable as a second unique Lucid bot on MES1!."
            )
        else:
            lines.append(
                f"**MNQ remains primary.** Best MES `{winner['name']}` "
                f"({w_pass:.1f}% pass) trails MNQ Phase 9 ({m_pass:.1f}%). "
                "Use MES only if you need a compliant second account and accept lower pass rate."
            )
    elif winner:
        lines.append(f"Best MES candidate: `{winner['name']}`.")
    else:
        lines.append("No MES candidates produced trades.")

    lines += [
        "",
        "## Method",
        "",
        "- Data: Databento GLBX.MDP3 `MES.FUT` ohlcv-1m, 2019-05-29 → 2026-06-29",
        "- Point value: $5/pt (MES micro), same ORB engine as MNQ",
        "- Walk-forward: 24m train / 6m test, grid_end 2025-12-31",
        "- MC: 10k Lucid 25K eval attempts @ 1 micro, block bootstrap",
        "",
        "## Results (@1 micro, skipMon overlay)",
        "",
        "| Candidate | Pass % | Pass+Payout % | Net $ | UPI |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results[:6]:
        mc = r["mc"][1]
        j = r.get("journey", {})
        c = r["consistency"]["full"]
        lines.append(
            f"| {r['name']} | {100 * mc['pass_rate']:.1f}% "
            f"| {100 * j.get('pass_and_payout', 0):.1f}% "
            f"| ${c.get('net_pnl', 0):,.0f} | {c.get('upi', 0):.1f} |"
        )

    if final_params:
        lines += ["", "## Selected params (last WF fold)", ""]
        for fam, p in final_params.items():
            lines.append(f"- **{fam}**: `{p}`")

    lines += [
        "",
        "## Live setup (if MES approved)",
        "",
        "1. TradingView chart: **MES1!**, **5m**, America/New_York, 1 micro",
        "2. Port `lucid_orb_width_25k.pine` with MES-specific width band from params above",
        "3. Separate Lucid account + TradersPost subscription (unique bot vs MNQ)",
        "4. Validate TV export vs Python ledger before funded trading",
        "",
        "## Artifacts",
        "",
        "| File | Content |",
        "| --- | --- |",
        "| `data/reports/mes/phase10_leaderboard.md` | Full ranking |",
        "| `data/reports/mes/phase10_walk_forward.md` | Fold tables |",
        "| `data/processed/mes/trades_phase10_*.parquet` | OOS ledgers |",
        "| `config/data_mes.yaml`, `config/phase10.yaml` | Reproducible config |",
    ]
    Path("docs/PHASE_10_REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

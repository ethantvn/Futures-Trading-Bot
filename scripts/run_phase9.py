"""Phase 9: long-only ORB, macro-day skip, portfolio / automation research.

Usage:
  .venv/bin/python scripts/run_phase9.py

Writes:
  data/reports/phase9_leaderboard.md
  data/reports/phase9_walk_forward.md
  data/reports/phase9_metrics.json
  data/calendar/macro_events.csv
  docs/PHASE_9_REPORT.md
  data/processed/trades_phase9_<family>_wf_oos.parquet
"""
from __future__ import annotations

import json
import logging
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Allow `python scripts/run_phase9.py` from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl
import yaml

from scripts.run_phase7 import (
    LB_HEADER,
    ORB_BASELINE_LEDGER,
    STRATEGY_CLASSES,
    _as_date,
    _filter,
    _lb_row,
    _sanitize,
    evaluate_ledger,
    skip_monday,
)
from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.data.macro_calendar import export_calendar_csv, macro_event_dates
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import ledger_to_days, run_monte_carlo
from src.evaluation.simulator import run_evaluation
from src.logging_setup import setup_logging
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase9")


def _pass_and_payout_mc(
    trades: pl.DataFrame,
    rules: LucidRules,
    n: int = 10000,
    seed: int = 42,
) -> dict[str, float]:
    """End-to-end: pass eval then reach first $500-eligible payout."""
    import numpy as np
    from src.evaluation.lucid_rules import EvalAccount
    from src.evaluation.monte_carlo import _sample_days

    days = ledger_to_days(trades.filter(pl.col("trading_date").dt.weekday() != 1), 1)
    if not days:
        return {"pass_and_payout": 0.0, "pass_rate": 0.0}

    rng = np.random.default_rng(seed)
    pass_n = payout_n = 0

    def funded_phase(seq, start_idx):
        balance, mll, qual, withdrawn, n_pay = 25000.0, 24000.0, 0, 0.0, 0
        for day in seq[start_idx : start_idx + 120]:
            dp = sum(day)
            balance += dp
            if balance <= mll:
                return False
            if balance - 1000 > mll:
                mll = balance - 1000
            if dp >= 100:
                qual += 1
            if qual >= 5 and balance - 25000 >= 1000 and n_pay < 6:
                req = min(1000, (balance - 25000) * 0.5)
                if req >= 500:
                    return True
        return False

    for _ in range(n):
        seq = _sample_days(days, 180, rng, "block", 5)
        acct = EvalAccount(rules)
        idx = 0
        passed = False
        for day in seq[:60]:
            idx += 1
            for pnl in day:
                acct.on_trade(pnl)
                if acct.status == "failed":
                    break
            acct.on_session_close()
            if acct.status == "passed":
                passed = True
                break
            if acct.status == "failed":
                break
        if passed:
            pass_n += 1
            if funded_phase(seq, idx):
                payout_n += 1
    return {
        "pass_rate": pass_n / n,
        "pass_and_payout": payout_n / n,
    }


def _tail_on_macro_days(trades: pl.DataFrame, start: date, end: date) -> dict:
    macro = macro_event_dates(start, end, "all")
    daily = (
        trades.group_by("trading_date")
        .agg(pl.col("net_pnl").sum())
        .sort("trading_date")
    )
    on = daily.filter(pl.col("trading_date").is_in(sorted(macro)))
    off = daily.filter(~pl.col("trading_date").is_in(sorted(macro)))
    return {
        "macro_days": on.height,
        "macro_net": float(on["net_pnl"].sum()) if on.height else 0.0,
        "macro_avg": float(on["net_pnl"].mean()) if on.height else 0.0,
        "non_macro_net": float(off["net_pnl"].sum()) if off.height else 0.0,
        "non_macro_avg": float(off["net_pnl"].mean()) if off.height else 0.0,
    }


def main() -> None:
    setup_logging()
    cfg = yaml.safe_load(Path("config/phase9.yaml").read_text())
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
    rules = LucidRules.from_yaml(Path("config") / f"{mc_cfg['account']}.yaml")
    lucid_costs = yaml.safe_load(Path("config/lucid_25k.yaml").read_text())["costs"]

    splits = cfg["splits"]
    grid_start, grid_end = _as_date(splits["grid_start"]), _as_date(splits["grid_end"])
    export_calendar_csv(
        Path("data/calendar/macro_events.csv"), grid_start, grid_end
    )

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
    tail_rows: list[str] = []
    wf_report: list[str] = ["# Phase 9 Walk-Forward", ""]
    final_params: dict[str, dict] = {}

    # Phase 7 baselines
    for bl in cfg.get("baselines", []):
        path = processed / bl["ledger"]
        if not path.exists():
            log.warning("baseline ledger missing: %s", path)
            continue
        t = pl.read_parquet(path)
        if bl.get("post_skip_monday"):
            t = skip_monday(t)
        r = evaluate_ledger(bl["name"], t, rules, mc_cfg, lucid_costs)
        r["journey"] = _pass_and_payout_mc(t, rules)
        results.append(r)

    # Phase 7 winner for macro tail analysis
    p7 = processed / "trades_phase7_orb_width_wf_oos.parquet"
    if p7.exists():
        tail = _tail_on_macro_days(skip_monday(pl.read_parquet(p7)), grid_start, grid_end)
        tail_rows.append(
            f"Phase 7 winner on macro days ({tail['macro_days']} sessions): "
            f"net ${tail['macro_net']:,.0f} (avg ${tail['macro_avg']:,.0f}) vs "
            f"non-macro net ${tail['non_macro_net']:,.0f} "
            f"(avg ${tail['non_macro_avg']:,.0f})"
        )

    stress_targets: list[tuple[str, str, dict]] = []

    for fam, fcfg in cfg["families"].items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        space = fcfg["param_grid"]
        log.info("=== Phase 9 family %s ===", fam)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(cls.timeframe_minutes), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase9_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        final_params[fam] = chosen
        (processed / f"phase9_params_{fam}.yaml").write_text(yaml.dump(chosen))

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

        name = fam
        ledger = oos
        if cfg.get("post_overlays", {}).get("skip_monday") and not chosen.get(
            "skip_weekdays"
        ):
            name = f"{fam} +skipMon"
            ledger = skip_monday(oos)

        r = evaluate_ledger(name, ledger, rules, mc_cfg, lucid_costs)
        r["journey"] = _pass_and_payout_mc(ledger, rules)
        r["params"] = chosen
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
        "# Phase 9 Leaderboard — long-only, macro skip, portfolio research",
        "",
        "Sorted by Lucid 25K pass rate @1 micro, then UPI. "
        f"MC: {mc_cfg['n_attempts']} block-bootstrap attempts. "
        "`Pass+Payout` = pass eval AND reach first $500-eligible payout (same attempt).",
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

    if tail_rows:
        lb += ["", "## Macro-day P&L (Phase 7 winner, skipMon)", ""] + [
            f"- {t}" for t in tail_rows
        ]

    st_cfg = cfg["stress"]
    stress_lines = ["", "## Slippage stress (2025, final params)", ""]
    for fam, strategy_name, params in stress_targets[:3]:
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
        stress_lines += render_stress_section(fam, rows)
    lb += stress_lines

    (reports / "phase9_leaderboard.md").write_text("\n".join(lb) + "\n")
    (reports / "phase9_walk_forward.md").write_text("\n".join(wf_report) + "\n")
    (reports / "phase9_metrics.json").write_text(
        json.dumps(_sanitize({"candidates": results, "final_params": final_params}), indent=1)
    )

    _write_report(results, tail_rows, reports)
    log.info("Phase 9 complete → %s", reports)


def _write_report(results: list[dict], tail_rows: list[str], reports: Path) -> None:
    winner = results[0] if results else {}
    p7 = next((r for r in results if "PHASE7 orb_width" in r["name"]), {})
    best_new = next((r for r in results if r["name"].startswith("orb_")), {})

    lines = [
        "# Phase 9 Report — Profitable Future Strategy Research",
        "",
        f"Date: 2026-07-08. Builds on Phase 7 winner (ORB-W + Skip Monday, ~61.8% pass).",
        "",
        "## TL;DR",
        "",
    ]
    if best_new and p7 and best_new["mc"][1]["pass_rate"] > p7["mc"][1]["pass_rate"]:
        lines += [
            f"**New candidate `{best_new['name']}` beats Phase 7 baseline on pass rate "
            f"({100*best_new['mc'][1]['pass_rate']:.1f}% vs "
            f"{100*p7['mc'][1]['pass_rate']:.1f}%).** See leaderboard for full metrics.",
        ]
    else:
        lines += [
            "**Phase 7 ORB-W + Skip Monday remains the recommendation.** "
            "Phase 9 filters (long-only, macro skip, combined) did not beat the "
            "validated baseline on walk-forward pass rate.",
        ]
    lines += [
        "",
        "## What we tested",
        "",
        "1. **Long-only ORB-W** — disable short breakouts (equity drift hypothesis).",
        "2. **Macro-day skip** — stand aside on NFP / CPI / FOMC release days.",
        "3. **Long-only + macro + skipMon** — combined filter stack.",
        "4. **Portfolio baselines** — NR7 ORB as second-account diversifier.",
        "5. **End-to-end journey MC** — pass eval AND first payout-eligible state.",
        "",
        "## Top candidates (pass rate @1 micro)",
        "",
        "| Candidate | Pass % | Pass+Payout % | Net $ | UPI |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results[:8]:
        mc = r["mc"][1]
        j = r.get("journey", {})
        c = r["consistency"]["full"]
        lines.append(
            f"| {r['name']} | {100*mc['pass_rate']:.1f}% "
            f"| {100*j.get('pass_and_payout', 0):.1f}% "
            f"| ${c.get('net_pnl', 0):,.0f} | {c.get('upi', 0):.1f} |"
        )

    if tail_rows:
        lines += ["", "## Macro-day analysis (Phase 7 winner)", ""] + [
            f"- {t}" for t in tail_rows
        ]

    lines += [
        "",
        "## Automation (live execution)",
        "",
        "Lucid allows TradingView → TradersPost → Tradovate automation (no HFT). "
        "Each account must run a **unique** strategy — identical copy-trading "
        "across many Lucid accounts violates their automation policy.",
        "",
        "Checklist:",
        "1. Re-add fixed `lucid_orb_width_25k.pine` (Phase 8 flat-at-15:55 fix).",
        "2. Chart: MNQ1!, 5m, America/New_York, 1 micro.",
        "3. Connect TradersPost webhook alerts (entry, flat 15:55, skip badges).",
        "4. Log every live fill vs Python ledger (slippage monitor).",
        "5. Do NOT copy identical signals to multiple Lucid accounts.",
        "",
        "## Multi-instrument expansion (MES / ES)",
        "",
        "The pipeline is instrument-agnostic. To add MES:",
        "1. Purchase Databento GLBX.MDP3 batch for `MES.FUT` (same schema as MNQ).",
        "2. Add `config/data_mes.yaml` with `point_value: 5.0`, `tick_size: 0.25`.",
        "3. Re-run Phases 3–7 grid on MES — **do not port MNQ params blindly**.",
        "4. MES has smaller $/point → better fit for $1,000 MLL in high-vol regimes.",
        "5. Run on a **different prop firm or Lucid account** as a genuinely unique bot.",
        "",
        "## Scaling path (compliant)",
        "",
        "| Account | Strategy | Role |",
        "| --- | --- | --- |",
        "| 1 | ORB-W + Skip Mon (MNQ) | Primary — ~62% pass |",
        "| 2 | NR7 ORB (MNQ) | Slow diversifier — ~60% pass, ~40 trades/yr |",
        "| 3+ | MES ORB-W (after validation) | Different instrument = unique bot |",
        "",
        "## Recommendation",
        "",
        "See `data/reports/phase9_leaderboard.md` for full ranking. "
        "Re-run walk-forward ~2026-12 when new data is available.",
        "",
        "## Artifacts",
        "",
        "| File | Content |",
        "| --- | --- |",
        "| `data/reports/phase9_leaderboard.md` | Full ranking + journey MC |",
        "| `data/reports/phase9_walk_forward.md` | Fold tables |",
        "| `data/calendar/macro_events.csv` | NFP/CPI/FOMC skip dates |",
        "| `src/data/macro_calendar.py` | Calendar generator |",
        "| `config/phase9.yaml`, `scripts/run_phase9.py` | Reproducible pipeline |",
    ]
    (Path("docs") / "PHASE_9_REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

"""Phase 11: GC (full-size gold) Lucid Flex 50K strategy research.

Usage:
  .venv/bin/python scripts/build_bars.py --config config/data_gc.yaml
  .venv/bin/python scripts/run_phase11.py
  .venv/bin/python scripts/run_phase11.py --holdout comex_orb ny_orb

Prerequisites: GC processed bars with fixed roll calendar (liquid months G,J,M,Q,V,Z).

Writes:
  data/reports/gc/phase11_leaderboard.md
  data/reports/gc/phase11_walk_forward.md
  data/reports/gc/phase11_sizing.md
  data/reports/gc/phase11_metrics.json
  data/reports/gc/phase11_holdout.md          (--holdout only)
  docs/PHASE_11_REPORT.md
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

from scripts.run_phase7 import (
    STRATEGY_CLASSES as BASE_CLASSES,
    _as_date,
    _filter,
    _sanitize,
    evaluate_ledger,
)
from src.backtest.engine import EngineConfig
from src.backtest.fees import CostModel
from src.data.macro_calendar import macro_event_dates
from src.evaluation.lucid_rules import LucidRules
from src.logging_setup import setup_logging
from src.strategies.gc_macro_breakout import GcMacroBreakout
from src.strategies.gc_nr_orb import GcNrOrb
from src.strategies.gc_session_orb import GcSessionOrb
from src.strategies.gc_vwap import GcVwapReversion, GcVwapTrend
from src.strategies.indicators import ADJ, atr
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase11")

STRATEGY_CLASSES = {
    **BASE_CLASSES,
    "gc_session_orb": GcSessionOrb,
    "gc_nr_orb": GcNrOrb,
    "gc_macro_breakout": GcMacroBreakout,
    "gc_vwap_trend": GcVwapTrend,
    "gc_vwap_reversion": GcVwapReversion,
}


def run_sizing_check(
    processed: Path,
    data_cfg: dict,
    sizing_cfg: dict,
    out_path: Path,
) -> dict[str, Any]:
    """ATR-based $ risk per 1 GC contract at several timeframes."""
    pv = float(data_cfg["point_value"])
    mll = float(sizing_cfg["mll"])
    lo, hi = sizing_cfg["risk_pct_low"], sizing_cfg["risk_pct_high"]
    budget_lo, budget_hi = mll * lo, mll * hi

    lines = [
        "# GC Sizing Check — 1 full-size contract vs Lucid 50K MLL",
        "",
        f"- MLL: ${mll:,.0f}; target risk band: {100*lo:.0f}–{100*hi:.0f}% "
        f"= **${budget_lo:,.0f}–${budget_hi:,.0f}** per trade",
        f"- Point value: **${pv}/pt** (${pv/10:.0f}/tick @ 0.10 tick)",
        "",
        "| Timeframe | Med ATR(14) pts | Med ATR $ | 1.5×ATR $ | 2×ATR $ | Fits budget? |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    stats: dict[str, Any] = {}
    for tf in (5, 15, 30):
        path = processed / f"continuous_{tf}m.parquet"
        if not path.exists():
            continue
        df = pl.read_parquet(path).sort("ts_utc")
        df = df.with_columns(atr(14).alias("_atr"))
        daily = (
            df.group_by("trading_date")
            .agg(pl.col("_atr").median().alias("atr_pts"))
            .filter(pl.col("atr_pts").is_not_null())
        )
        med_pts = float(daily["atr_pts"].median())
        med_usd = med_pts * pv
        s15 = med_usd * 1.5
        s20 = med_usd * 2.0
        fits = budget_lo <= s15 <= budget_hi
        lines.append(
            f"| {tf}m | {med_pts:.2f} | ${med_usd:,.0f} | ${s15:,.0f} | ${s20:,.0f} "
            f"| {'yes (1.5×)' if fits else 'marginal/tight'} |"
        )
        stats[f"{tf}m"] = {
            "median_atr_pts": med_pts,
            "median_atr_usd": med_usd,
            "atr_1p5_usd": s15,
            "atr_2x_usd": s20,
        }

    # Daily RTH range in dollars (typical full-day move)
    bars_1m = pl.read_parquet(processed / "continuous_1m.parquet")
    rth = bars_1m.filter(pl.col("session") == "rth")
    daily_rng = (
        rth.group_by("trading_date")
        .agg(
            (pl.col(ADJ["high"]).max() - pl.col(ADJ["low"]).min()).alias("rng_pts")
        )
    )
    p50 = float(daily_rng["rng_pts"].median())
    p95 = float(daily_rng["rng_pts"].quantile(0.95))
    worst = float(daily_rng["rng_pts"].max())
    lines += [
        "",
        "## Daily RTH range (1 contract, $/day)",
        "",
        f"- Median: **${p50 * pv:,.0f}** ({p50:.1f} pts)",
        f"- P95: **${p95 * pv:,.0f}** ({p95:.1f} pts)",
        f"- Max: **${worst * pv:,.0f}** ({worst:.1f} pts)",
        "",
        "## Verdict",
        "",
    ]
    med5 = stats.get("5m", {}).get("median_atr_usd", 0)
    if med5 * 1.5 > budget_hi:
        verdict = (
            "Typical ATR-based stops (1.5×) exceed the $300–500 comfort band on 5m bars. "
            "Use explicit `max_risk_points` caps (3–5 pts = $300–500). "
            f"However, median **daily RTH range is ${p50 * pv:,.0f}** and P95 is "
            f"**${p95 * pv:,.0f}** — a single adverse day can exceed the entire "
            f"**${mll:,.0f} MLL** even with per-trade caps. Full-size GC at 1 contract "
            "is structurally high-variance for 50K; **MGC micro ($10/pt)** is the safer "
            "sizing fallback if pursuing gold."
        )
    elif p95 * pv > mll:
        verdict = (
            "Per-trade caps (3–5 pts) can fit the $300–500 band, but **P95 daily RTH "
            f"range (${p95 * pv:,.0f}) exceeds the $2,000 MLL**. Strategies need "
            "1 trade/day discipline and capped stops; blow risk remains elevated vs MNQ."
        )
    else:
        verdict = "Structural stops appear compatible with 50K MLL at 1 GC contract."
    lines.append(verdict)
    out_path.write_text("\n".join(lines) + "\n")
    stats["daily_rth_median_usd"] = p50 * pv
    stats["daily_rth_p95_usd"] = p95 * pv
    stats["verdict"] = verdict
    return stats


def macro_day_baseline(exec_bars: pl.DataFrame, cost: CostModel, eng: dict) -> dict:
    """Simple COMEX ORB on macro vs non-macro days (no WF)."""
    from src.backtest.engine import run_backtest

    sig = pl.read_parquet(Path("data/processed/gc/continuous_5m.parquet"))
    strat = GcSessionOrb({"anchor_minute": 500, "max_risk_points": 4.0})
    prepared = strat.prepare(sig)
    ecfg = EngineConfig(
        qty=eng["qty"],
        flat_time=eng["flat_time"],
        no_entry_after=eng["no_entry_after"],
        max_trades_per_day=1,
    )
    res = run_backtest(exec_bars, prepared, 5, cost, ecfg, strat.name)
    trades = res.trades
    if trades.height == 0:
        return {"macro_trades": 0, "macro_net": 0, "non_macro_net": 0}
    d0, d1 = trades["trading_date"].min(), trades["trading_date"].max()
    macro = macro_event_dates(d0, d1, "all")
    on = trades.filter(pl.col("trading_date").is_in(sorted(macro)))
    off = trades.filter(~pl.col("trading_date").is_in(sorted(macro)))
    return {
        "macro_days": on.height,
        "macro_net": float(on["net_pnl"].sum()) if on.height else 0.0,
        "macro_avg": float(on["net_pnl"].mean()) if on.height else 0.0,
        "non_macro_trades": off.height,
        "non_macro_net": float(off["net_pnl"].sum()) if off.height else 0.0,
        "non_macro_avg": float(off["net_pnl"].mean()) if off.height else 0.0,
    }


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--holdout",
        nargs="*",
        metavar="FAMILY",
        help="Run 2026 holdout ONCE for named families (uses saved params).",
    )
    args = ap.parse_args()

    cfg = yaml.safe_load(Path("config/gc_phase11.yaml").read_text())
    data_cfg = yaml.safe_load(Path("config/data_gc.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies_gc.yaml").read_text())
    eng = strat_cfg["engine"]

    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    # Roll calendar sanity
    rc = pl.read_parquet(processed / "roll_calendar.parquet")
    rc = rc.with_columns(pl.col("symbol").str.slice(-2, 1).alias("month_code"))
    bad = rc.filter(~pl.col("month_code").is_in(["G", "J", "M", "Q", "V", "Z"]))
    if bad.height:
        raise SystemExit(
            f"GC roll calendar still has non-liquid months ({bad.height} days). "
            "Re-run: .venv/bin/python scripts/build_bars.py --config config/data_gc.yaml"
        )

    sizing_stats = run_sizing_check(
        processed, data_cfg, cfg["sizing"], reports / "phase11_sizing.md"
    )
    log.info("Sizing check written; verdict: %s", sizing_stats.get("verdict", "")[:80])

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
    log.info("Walk-forward folds: %d (18m train / 6m test)", len(folds))
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

    if args.holdout is not None:
        _run_holdout(args.holdout, cfg, processed, exec_full, cost, eng, rules, splits)
        return

    macro_bl = {}
    if cfg.get("macro_baseline", {}).get("enabled"):
        macro_bl = macro_day_baseline(exec_grid, cost, eng)

    results: list[dict[str, Any]] = []
    wf_report: list[str] = [
        "# Phase 11 GC Walk-Forward",
        "",
        f"- Folds: {len(folds)} × (18m train / 6m test)",
        f"- Grid: {grid_start} → {grid_end}",
        "",
    ]
    final_params: dict[str, dict] = {}
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
        log.info("=== Phase 11 GC family %s ===", fam)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(cls.timeframe_minutes), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase11_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        final_params[fam] = chosen
        (processed / f"phase11_params_{fam}.yaml").write_text(yaml.dump(chosen))

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

        r = evaluate_ledger(f"GC {fam}", oos, rules, mc_cfg, lucid_costs)
        r["params"] = chosen
        r["family"] = fam
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
        "# Phase 11 GC Leaderboard — Lucid Flex 50K @ 1 full-size contract",
        "",
        "Sorted by 50K pass rate @1 GC, then UPI. MC: 10k block-bootstrap.",
        f"Sizing verdict: see `phase11_sizing.md`.",
        "",
        "| Candidate | Trades | Pass@1 | Fail % | Med d | Net $ | Sharpe | UPI | MaxDD | Last252 $ |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        mc = r["mc"][1]
        c = r["consistency"]["full"]
        med = mc.get("median_days")
        med_s = f"{med:.0f}" if med else "—"
        lb.append(
            f"| {r['name']} | {r['trade_metrics'].get('n_trades', 0)} "
            f"| {100 * mc['pass_rate']:.1f}% "
            f"| {100 * mc['fail_rate']:.1f}% "
            f"| {med_s} "
            f"| ${c.get('net_pnl', 0):,.0f} "
            f"| {c.get('sharpe_daily', 0):.2f} "
            f"| {c.get('upi', 0):.1f} "
            f"| ${c.get('max_drawdown', 0):,.0f} "
            f"| ${r['consistency']['last_252d'].get('net_pnl', 0):,.0f} |"
        )

    st_cfg = cfg["stress"]
    stress_lines = ["", "## Slippage stress (2025, top 2 by pass rate)", ""]
    top_for_stress = sorted(results, key=sort_key, reverse=True)[:2]
    for r in top_for_stress:
        fam = r["family"]
        strategy_name = cfg["families"][fam]["strategy"]
        params = r.get("params") or final_params.get(fam, {})
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
        stress_lines += render_stress_section(f"GC {fam}", rows)
    lb += stress_lines

    (reports / "phase11_leaderboard.md").write_text("\n".join(lb) + "\n")
    (reports / "phase11_walk_forward.md").write_text("\n".join(wf_report) + "\n")
    (reports / "phase11_metrics.json").write_text(
        json.dumps(
            _sanitize({
                "candidates": results,
                "final_params": final_params,
                "sizing": sizing_stats,
                "macro_baseline": macro_bl,
                "folds": len(folds),
            }),
            indent=1,
        )
    )
    _write_report(results, final_params, sizing_stats, macro_bl, len(folds), reports)
    log.info("Phase 11 GC complete → %s", reports)


def _run_holdout(
    families: list[str],
    cfg: dict,
    processed: Path,
    exec_full: pl.DataFrame,
    cost: CostModel,
    eng: dict,
    rules: LucidRules,
    splits: dict,
) -> None:
    from src.backtest.engine import run_backtest

    hs, he = _as_date(splits["holdout_start"]), _as_date(splits["holdout_end"])
    exec_h = _filter(exec_full, hs, he)
    lines = [
        "# Phase 11 GC Holdout (2026)",
        "",
        f"Single run {hs} → {he}. Frozen params from walk-forward.",
        "",
        "| Family | Trades | Net $ | Pass MC % |",
        "| --- | --- | --- | --- |",
    ]
    for fam in families:
        ppath = processed / f"phase11_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | params missing | — |")
            continue
        params = yaml.safe_load(ppath.read_text()) or {}
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        sig = _filter(
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            hs,
            he,
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
        trades.write_parquet(processed / f"trades_phase11_{fam}_holdout.parquet")
        mc = evaluate_ledger(
            fam, trades, rules, cfg["monte_carlo"],
            yaml.safe_load(Path("config/lucid_50k.yaml").read_text())["costs"],
        )
        net = float(trades["net_pnl"].sum()) if trades.height else 0.0
        lines.append(
            f"| {fam} | {trades.height} | ${net:,.0f} "
            f"| {100 * mc['mc'][1]['pass_rate']:.1f}% |"
        )
    Path("data/reports/gc/phase11_holdout.md").write_text("\n".join(lines) + "\n")
    log.info("Holdout report → data/reports/gc/phase11_holdout.md")


def _write_report(
    results: list[dict],
    final_params: dict[str, dict],
    sizing: dict,
    macro_bl: dict,
    n_folds: int,
    reports: Path,
) -> None:
    winner = results[0] if results else {}
    w_pass = 100 * winner["mc"][1]["pass_rate"] if winner else 0
    bar = 30  # Phase 10 MES floor

    holdout_path = reports / "phase11_holdout.md"
    holdout_note = ""
    if holdout_path.exists():
        holdout_note = holdout_path.read_text()

    lines = [
        "# Phase 11 Report — Gold (GC) Lucid Flex 50K Research",
        "",
        "Date: 2026-07-10. Full-size COMEX GC, gold-native strategy families.",
        "",
        "## TL;DR",
        "",
    ]
    holdout_failed = "macro_nfp_cpi" in holdout_note and "$-1" in holdout_note
    if holdout_failed or (winner and w_pass < bar):
        lines.append(
            "**No GC strategy clears all success criteria for Lucid 50K eval.** "
            "Best walk-forward OOS was `GC macro_nfp_cpi` (53.9% pass) but **2026 holdout "
            "collapsed** (17 trades, −$1,366, 11.3% MC pass). **Stay on validated MNQ "
            "ORB-W (~64% pass on 25K).** Optional next step: **MGC micro** sizing study."
        )
    elif winner and w_pass >= bar:
        lines.append(
            f"**Candidate `{winner['name']}` clears the research bar "
            f"({w_pass:.1f}% 50K pass @1 GC).** Validate holdout before live use."
        )
    else:
        lines.append("**No GC candidates produced OOS trades.**")

    lines += [
        "",
        "## Task 0 — Roll calendar",
        "",
        "Restricted to liquid months {G,J,M,Q,V,Z} with `confirm_sessions=2`. "
        "Rebuilt via `build_bars.py --config config/data_gc.yaml`.",
        "",
        "## Sizing check (1 full-size GC vs $2,000 MLL)",
        "",
        sizing.get("verdict", "See phase11_sizing.md"),
        "",
        f"- Median daily RTH range: ~${sizing.get('daily_rth_median_usd', 0):,.0f}",
        f"- P95 daily RTH range: ~${sizing.get('daily_rth_p95_usd', 0):,.0f}",
        "",
        "## Walk-forward",
        "",
        f"- {n_folds} folds, 18m train / 6m test, grid through 2025-12-31",
        "- Holdout 2026: run once via `--holdout` on finalists",
        "",
    ]
    if macro_bl:
        lines += [
            "## Macro-day baseline (COMEX ORB, capped 4pt stop)",
            "",
            f"- Macro release days: {macro_bl.get('macro_days', 0)} trades, "
            f"net ${macro_bl.get('macro_net', 0):,.0f} "
            f"(avg ${macro_bl.get('macro_avg', 0):,.0f})",
            f"- Non-macro: {macro_bl.get('non_macro_trades', 0)} trades, "
            f"net ${macro_bl.get('non_macro_net', 0):,.0f} "
            f"(avg ${macro_bl.get('non_macro_avg', 0):,.0f})",
            "",
        ]

    lines += [
        "## Top candidates (50K pass @1 GC)",
        "",
        "| Candidate | Pass % | Net $ | UPI | MaxDD |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results[:8]:
        mc = r["mc"][1]
        c = r["consistency"]["full"]
        lines.append(
            f"| {r['name']} | {100 * mc['pass_rate']:.1f}% "
            f"| ${c.get('net_pnl', 0):,.0f} | {c.get('upi', 0):.1f} "
            f"| ${c.get('max_drawdown', 0):,.0f} |"
        )

    lines += ["", "## Rejected / failed families", ""]
    tried = {r["family"] for r in results}
    for fam in final_params:
        if fam not in tried:
            lines.append(f"- **{fam}**: no OOS trades after walk-forward")
    for r in results:
        if r["mc"][1]["pass_rate"] < 0.30:
            lines.append(
                f"- **{r['name']}**: {100*r['mc'][1]['pass_rate']:.1f}% pass — below 30% bar"
            )

    if final_params:
        lines += ["", "## Selected params (last WF fold)", ""]
        for fam, p in final_params.items():
            lines.append(f"- **{fam}**: `{p}`")

    lines += [
        "",
        "## 2026 holdout (single run, frozen params)",
        "",
    ]
    if holdout_path.exists():
        lines.append(holdout_note.strip())
    else:
        lines.append(
            "Not run yet. Execute: "
            "`.venv/bin/python scripts/run_phase11.py --holdout macro_nfp_cpi`"
        )

    lines += [
        "",
        "## Recommendation",
        "",
    ]
    if holdout_failed:
        lines.append(
            "1. **Do not deploy full-size GC on Lucid 50K** — holdout failed. "
            "2. **Primary eval:** MNQ ORB-W long-only + skipMon @ 1 micro (~64% pass). "
            "3. **If pursuing gold:** ingest MGC micro data and re-run with $10/pt sizing."
        )
    elif winner and w_pass >= bar:
        lines.append(
            f"1. Paper-trade `{winner['name']}` 10 sessions. "
            "2. Build TradingView GC Pine (bar-close flat logic). "
            "3. Confirm holdout before 50K eval."
        )
    else:
        lines.append(
            "1. **Do not run full-size GC on Lucid 50K** with these results. "
            "2. Stay on MNQ ORB-W long-only (~64% pass on 25K). "
            "3. Optional: MGC micro gold sizing study."
        )

    lines += [
        "",
        "## Artifacts",
        "",
        "| File | Content |",
        "| --- | --- |",
        "| `data/reports/gc/phase11_leaderboard.md` | Full ranking |",
        "| `data/reports/gc/phase11_sizing.md` | ATR / MLL sizing check |",
        "| `data/reports/gc/phase11_walk_forward.md` | Fold tables |",
        "| `config/gc_phase11.yaml`, `config/strategies_gc.yaml` | Reproducible config |",
    ]
    Path("docs/PHASE_11_REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

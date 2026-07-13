"""Phase 16: Structure / Levels / Profile / MES Divergence on MNQ Lucid 25K.

Usage:
  .venv/bin/python scripts/run_phase16.py
  .venv/bin/python scripts/run_phase16.py --families structure_gated_orb poc_reversion
  .venv/bin/python scripts/run_phase16.py --holdout structure_gated_orb mes_agree_orb
  .venv/bin/python scripts/run_phase16.py --report

Discipline: WF on pre-2026 only; 2026 holdout once; no re-tune.
Incumbent ORB-W long-only + skipMon included on every leaderboard.
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

from scripts.run_phase7 import _as_date, _filter, _sanitize, evaluate_ledger, skip_monday
from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.evaluation.lucid_rules import LucidRules
from src.logging_setup import setup_logging
from src.strategies.base import Strategy
from src.strategies.mes_divergence_orb import MesDivergenceOrb
from src.strategies.overnight_levels import OvernightLevels
from src.strategies.poc_value_area import PocValueArea
from src.strategies.prior_day_levels import PriorDayLevels
from src.strategies.round_number_magnet import RoundNumberMagnet
from src.strategies.structure_gated_orb import StructureGatedOrb
from src.strategies.structure_gated_vwap import StructureGatedVwap
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    param_grid,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase16")

CONFIG = Path("config/phase16_structure.yaml")
DATA_CONFIG = Path("config/data.yaml")
STRAT_CONFIG = Path("config/strategies.yaml")

STRATEGY_CLASSES: dict[str, type[Strategy]] = {
    "structure_gated_orb": StructureGatedOrb,
    "structure_gated_vwap": StructureGatedVwap,
    "overnight_levels": OvernightLevels,
    "prior_day_levels": PriorDayLevels,
    "poc_value_area": PocValueArea,
    "mes_divergence_orb": MesDivergenceOrb,
    "round_number_magnet": RoundNumberMagnet,
}


def _mc1(mc_by_contracts: dict) -> dict:
    if 1 in mc_by_contracts:
        return mc_by_contracts[1]
    return mc_by_contracts["1"]


def _accounts(mc_cfg: dict) -> dict[str, tuple[LucidRules, dict]]:
    out = {}
    for acct in mc_cfg["accounts"]:
        path = Path("config") / f"{acct}.yaml"
        out[acct] = (LucidRules.from_yaml(path), yaml.safe_load(path.read_text())["costs"])
    return out


def sparsity_stats(trades: pl.DataFrame) -> dict[str, float]:
    if trades.height == 0:
        return {"trades_per_month": 0.0, "active_days": 0, "days_span": 0}
    days = trades["trading_date"].unique().sort()
    n_days = days.len()
    span = (days[-1] - days[0]).days + 1 if n_days else 0
    months = max(span / 30.44, 1e-9)
    return {
        "trades_per_month": trades.height / months,
        "active_days": float(n_days),
        "days_span": float(span),
    }


def engine_cfg(eng: dict, fcfg: dict) -> EngineConfig:
    return EngineConfig(
        qty=eng["qty"],
        flat_time=eng["flat_time"],
        no_entry_after=eng["no_entry_after"],
        max_trades_per_day=fcfg.get("max_trades_per_day"),
    )


def evaluate_baseline(cfg: dict, accounts: dict, mc_cfg: dict) -> dict[str, Any] | None:
    b = cfg.get("baseline") or {}
    path = Path(b.get("trades_parquet", ""))
    if not path.exists():
        log.warning("Baseline ledger missing: %s", path)
        return None
    trades = pl.read_parquet(path)
    if b.get("skip_monday"):
        trades = skip_monday(trades)
    primary = mc_cfg["primary_account"]
    rules, costs = accounts[primary]
    r = evaluate_ledger(b.get("name", "incumbent"), trades, rules, mc_cfg, costs)
    r["family"] = "_baseline"
    r["grid_size"] = 0
    r["pos_fold_share"] = None
    r["params"] = {"note": "frozen Phase 9 ORB-W long-only + skipMon"}
    r["primary_pass"] = _mc1(r["mc"])["pass_rate"]
    r["sparsity"] = sparsity_stats(trades)
    yp = (
        trades.group_by(pl.col("trading_date").dt.year().alias("y"))
        .agg(pl.col("net_pnl").sum().alias("net"))
        .sort("y")
    )
    r["year_pnls_oos"] = {str(row["y"]): float(row["net"]) for row in yp.to_dicts()}
    r["oos_trades"] = trades.height
    r["oos_net"] = float(trades["net_pnl"].sum())
    return r


def run_families(fam_names: list[str] | None) -> None:
    cfg = yaml.safe_load(CONFIG.read_text())
    data_cfg = yaml.safe_load(DATA_CONFIG.read_text())
    strat_cfg = yaml.safe_load(STRAT_CONFIG.read_text())
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
    accounts = _accounts(mc_cfg)
    primary = mc_cfg["primary_account"]

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
    log.info("Phase 16: %d WF folds", len(folds))

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
    if fam_names:
        families = {k: families[k] for k in fam_names if k in families}

    for fam, fcfg in families.items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", cls.timeframe_minutes))
        space = fcfg["param_grid"]
        n_combo = len(param_grid(space))
        min_tr = int(fcfg.get("min_trades_train", wf_cfg["min_trades_train"]))
        scorer = lambda t, mt=min_tr: score_sharpe(t, min_trades=mt)
        ecfg = engine_cfg(eng, fcfg)
        log.info("=== Phase 16 %s (%d combos, %dm) ===", fam, n_combo, tf)

        # Dynamic TF if needed
        if cls.timeframe_minutes != tf:
            cls = type(f"{cls.__name__}_{tf}m", (cls,), {"timeframe_minutes": tf})

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(tf), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase16_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        (processed / f"phase16_params_{fam}.yaml").write_text(yaml.dump(chosen))

        nets = [float(fr.test_net) for fr in wf.folds]
        pos_share = (sum(1 for n in nets if n > 0) / len(nets)) if nets else 0.0
        med_test = float(sorted(nets)[len(nets) // 2]) if nets else 0.0
        sparse = sparsity_stats(oos)

        partial: dict[str, Any] = {
            "family": fam,
            "grid_size": n_combo,
            "timeframe_minutes": tf,
            "params": chosen,
            "pos_fold_share": pos_share,
            "median_test_pnl": med_test,
            "fold_table_md": render_fold_table(wf.folds),
            "oos_trades": oos.height,
            "oos_net": float(oos["net_pnl"].sum()) if oos.height else 0.0,
            "sparsity": sparse,
        }
        if oos.height:
            yp = (
                oos.group_by(pl.col("trading_date").dt.year().alias("y"))
                .agg(pl.len().alias("n"), pl.col("net_pnl").sum().alias("net"))
                .sort("y")
            )
            partial["year_pnls_oos"] = {
                str(r["y"]): float(r["net"]) for r in yp.to_dicts()
            }
            rules, costs = accounts[primary]
            r = evaluate_ledger(f"P16 {fam}", oos, rules, mc_cfg, costs)
            partial["result"] = r
            partial["primary_pass"] = _mc1(r["mc"])["pass_rate"]
        else:
            partial["primary_pass"] = 0.0

        (processed / f"phase16_partial_{fam}.json").write_text(
            json.dumps(_sanitize(partial), indent=1)
        )
        log.info(
            "%s done: OOS %d net $%.0f fold+=%.0f%% pass=%.1f%%",
            fam,
            oos.height,
            partial["oos_net"],
            100 * pos_share,
            100 * partial["primary_pass"],
        )


def write_report() -> None:
    cfg = yaml.safe_load(CONFIG.read_text())
    data_cfg = yaml.safe_load(DATA_CONFIG.read_text())
    strat_cfg = yaml.safe_load(STRAT_CONFIG.read_text())
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)
    mc_cfg = cfg["monte_carlo"]
    accounts = _accounts(mc_cfg)
    primary = mc_cfg["primary_account"]

    partials = []
    for fam in cfg["families"]:
        p = processed / f"phase16_partial_{fam}.json"
        if p.exists():
            partials.append(json.loads(p.read_text()))
    if not partials:
        raise SystemExit("No phase16_partial_*.json — run families first.")

    baseline = evaluate_baseline(cfg, accounts, mc_cfg)

    def sort_key(pt: dict) -> tuple:
        r = pt.get("result") or {}
        upi = (r.get("consistency", {}).get("full", {}) or {}).get("upi")
        return (
            pt.get("primary_pass", 0),
            pt.get("pos_fold_share") or 0,
            -1e9 if upi is None else upi,
        )

    partials.sort(key=sort_key, reverse=True)

    lb = [
        "# Phase 16 Leaderboard — Structure / Levels / Profile / MES (MNQ 25K)",
        "",
        "Sorted by 25K pass → fold stability → UPI. "
        "Incumbent ORB-W long-only + skipMon shown first for comparison.",
        "",
        "| Candidate | Combos | Trades | Pass 25K | Fold+ % | Net $ | UPI | MaxDD | 2025 $ | t/mo |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def row_from_eval(name: str, r: dict, pt: dict | None = None) -> str:
        c = r["consistency"]["full"]
        mc = _mc1(r["mc"])
        upi = c.get("upi")
        upi_s = f"{upi:.1f}" if upi is not None else "—"
        fold = pt.get("pos_fold_share") if pt else None
        fold_s = f"{100 * fold:.0f}%" if fold is not None else "—"
        y2025 = (pt or {}).get("year_pnls_oos", r.get("year_pnls_oos", {})).get("2025", 0)
        tpm = (pt or {}).get("sparsity", r.get("sparsity", {})).get("trades_per_month", 0)
        grid = (pt or {}).get("grid_size", 0)
        ntr = r["trade_metrics"].get("n_trades", (pt or {}).get("oos_trades", 0))
        return (
            f"| {name} | {grid} | {ntr} "
            f"| {100 * mc['pass_rate']:.1f}% "
            f"| {fold_s} "
            f"| ${c.get('net_pnl', 0):,.0f} "
            f"| {upi_s} "
            f"| ${c.get('max_drawdown', 0):,.0f} "
            f"| ${y2025:,.0f} "
            f"| {tpm:.1f} |"
        )

    if baseline:
        lb.append(row_from_eval(f"**{baseline['name']}**", baseline, baseline))

    for pt in partials:
        r = pt.get("result")
        name = f"P16 {pt['family']}"
        if not r:
            lb.append(
                f"| {name} | {pt['grid_size']} | 0 | 0.0% "
                f"| {100 * (pt.get('pos_fold_share') or 0):.0f}% | $0 | — | — | — | 0 |"
            )
            continue
        lb.append(row_from_eval(name, r, pt))

    # Stress top 3 non-baseline
    st_cfg = cfg["stress"]
    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    stress_lines = ["", "## Slippage stress (2025, top 3 by pass rate)", ""]
    for pt in partials[:3]:
        if not pt.get("result"):
            continue
        fam = pt["family"]
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", cls.timeframe_minutes))
        if cls.timeframe_minutes != tf:
            cls = type(f"{cls.__name__}_{tf}m", (cls,), {"timeframe_minutes": tf})
        params = pt.get("params") or {}
        rows = slippage_sweep(
            cls,
            params,
            exec_full,
            pl.read_parquet(processed / f"continuous_{tf}m.parquet"),
            cost,
            st_cfg["slippage_ticks"],
            engine_cfg(eng, fcfg),
            _as_date(st_cfg["period_start"]),
            _as_date(st_cfg["period_end"]),
        )
        stress_lines += render_stress_section(f"P16 {fam}", rows)

    sparse_lines = [
        "",
        "## Sparsity / wall-clock",
        "",
        "| Family | Active days | Span days | Trades/mo |",
        "| --- | --- | --- | --- |",
    ]
    if baseline:
        s = baseline.get("sparsity") or {}
        sparse_lines.append(
            f"| incumbent | {s.get('active_days', 0):.0f} "
            f"| {s.get('days_span', 0):.0f} | {s.get('trades_per_month', 0):.1f} |"
        )
    for pt in partials:
        s = pt.get("sparsity") or {}
        sparse_lines.append(
            f"| {pt['family']} | {s.get('active_days', 0):.0f} "
            f"| {s.get('days_span', 0):.0f} | {s.get('trades_per_month', 0):.1f} |"
        )

    wf_lines = ["# Phase 16 Walk-Forward", ""]
    for pt in partials:
        wf_lines += [
            f"## {pt['family']}",
            "",
            f"- Params: `{pt.get('params')}`",
            f"- Fold+: {100 * (pt.get('pos_fold_share') or 0):.0f}%",
            "",
            pt.get("fold_table_md") or "",
            "",
        ]

    out = reports / "phase16_leaderboard.md"
    out.write_text("\n".join(lb + stress_lines + sparse_lines) + "\n")
    (reports / "phase16_walk_forward.md").write_text("\n".join(wf_lines) + "\n")
    (reports / "phase16_metrics.json").write_text(
        json.dumps(
            _sanitize({"partials": partials, "baseline": baseline}),
            indent=1,
        )
    )
    log.info("Report → %s", out)


def run_holdout(fam_names: list[str]) -> None:
    cfg = yaml.safe_load(CONFIG.read_text())
    data_cfg = yaml.safe_load(DATA_CONFIG.read_text())
    strat_cfg = yaml.safe_load(STRAT_CONFIG.read_text())
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
    accounts = _accounts(mc_cfg)
    primary = mc_cfg["primary_account"]
    splits = cfg["splits"]
    hs, he = _as_date(splits["holdout_start"]), _as_date(splits["holdout_end"])
    exec_h = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), hs, he)

    lines = [
        "# Phase 16 Holdout (2026)",
        "",
        f"Single run {hs} → {he}. Frozen Phase 16 WF params — **no re-tune**.",
        "",
        "| Family | Trades | Net $ | Pass 25K |",
        "| --- | --- | --- | --- |",
    ]
    rows = []
    for fam in fam_names:
        ppath = processed / f"phase16_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | params missing | — |")
            continue
        params = yaml.safe_load(ppath.read_text()) or {}
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", cls.timeframe_minutes))
        if cls.timeframe_minutes != tf:
            cls = type(f"{cls.__name__}_{tf}m", (cls,), {"timeframe_minutes": tf})
        sig = _filter(pl.read_parquet(processed / f"continuous_{tf}m.parquet"), hs, he)
        res = run_backtest(
            exec_h,
            cls(params).prepare(sig),
            tf,
            cost,
            engine_cfg(eng, fcfg),
            cls.name,
        )
        trades = res.trades
        trades.write_parquet(processed / f"trades_phase16_{fam}_holdout.parquet")
        if trades.height == 0:
            lines.append(f"| {fam} | 0 | $0 | — |")
            continue
        rules, costs = accounts[primary]
        mc = evaluate_ledger(f"P16 {fam} holdout", trades, rules, mc_cfg, costs)
        net = float(trades["net_pnl"].sum())
        lines.append(
            f"| {fam} | {trades.height} | ${net:,.0f} "
            f"| {100 * _mc1(mc['mc'])['pass_rate']:.1f}% |"
        )
        rows.append(
            {
                "family": fam,
                "net": net,
                "trades": trades.height,
                "pass": _mc1(mc["mc"])["pass_rate"],
                "params": params,
            }
        )
    out = reports / "phase16_holdout.md"
    out.write_text("\n".join(lines) + "\n")
    (reports / "phase16_holdout.json").write_text(
        json.dumps(_sanitize({"holdout": rows}), indent=1)
    )
    log.info("Holdout → %s", out)


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="*", help="Subset of family keys")
    ap.add_argument("--holdout", nargs="*", metavar="FAMILY")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    if args.holdout is not None:
        run_holdout(args.holdout)
        return
    if args.report:
        write_report()
        return
    run_families(args.families)
    write_report()


if __name__ == "__main__":
    main()

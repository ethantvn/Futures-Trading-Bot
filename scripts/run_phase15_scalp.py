"""Phase 15: Scalping research (FVG / VWAP / Volume) on MNQ + GC.

Usage:
  .venv/bin/python scripts/run_phase15_scalp.py --instrument mnq
  .venv/bin/python scripts/run_phase15_scalp.py --instrument gc
  .venv/bin/python scripts/run_phase15_scalp.py --instrument mnq --families mnq_fvg_1m
  .venv/bin/python scripts/run_phase15_scalp.py --instrument mnq --holdout mnq_fvg_1m mnq_vol_spike
  .venv/bin/python scripts/run_phase15_scalp.py --report

Discipline: WF params on pre-2026 only; 2026 holdout once; no re-tune.
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
from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.evaluation.lucid_rules import LucidRules
from src.logging_setup import setup_logging
from src.strategies.base import Strategy
from src.strategies.fvg_scalp import FvgScalp
from src.strategies.fvg_volume_scalp import FvgVolumeScalp
from src.strategies.volume_spike_scalp import VolumeSpikeScalp
from src.strategies.vwap_band_scalp import VwapBandScalp
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    param_grid,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase15")

CONFIG = Path("config/phase15_scalp.yaml")

STRATEGY_CLASSES: dict[str, type[Strategy]] = {
    "fvg_scalp": FvgScalp,
    "vwap_band_scalp": VwapBandScalp,
    "volume_spike_scalp": VolumeSpikeScalp,
    "fvg_volume_scalp": FvgVolumeScalp,
}


def _tf_cls(base: type[Strategy], tf: int) -> type[Strategy]:
    """Dynamic subclass with overridden timeframe_minutes."""
    if base.timeframe_minutes == tf:
        return base
    return type(f"{base.__name__}_{tf}m", (base,), {"timeframe_minutes": tf})


def _accounts(mc_cfg: dict) -> dict[str, tuple[LucidRules, dict]]:
    out = {}
    for acct in mc_cfg["accounts"]:
        path = Path("config") / f"{acct}.yaml"
        out[acct] = (LucidRules.from_yaml(path), yaml.safe_load(path.read_text())["costs"])
    return out


def evaluate_multi(
    name: str,
    trades: pl.DataFrame,
    accounts: dict[str, tuple[LucidRules, dict]],
    mc_cfg: dict,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    mc_by_acct: dict[str, Any] = {}
    for acct, (rules, costs) in accounts.items():
        r = evaluate_ledger(name, trades, rules, mc_cfg, costs)
        mc_by_acct[acct] = r["mc"]
        out = out or r
    out["mc_accounts"] = mc_by_acct
    return out


def _mc1(mc_by_contracts: dict) -> dict:
    """MC results keyed by contracts=1 (int from live eval, str after JSON)."""
    if 1 in mc_by_contracts:
        return mc_by_contracts[1]
    return mc_by_contracts["1"]


def ambiguity_pct(trades: pl.DataFrame) -> float:
    if trades.height == 0 or "ambiguous" not in trades.columns:
        return 0.0
    return float(trades["ambiguous"].sum()) / trades.height


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


def engine_cfg(eng: dict, overrides: dict, fcfg: dict) -> EngineConfig:
    return EngineConfig(
        qty=eng["qty"],
        flat_time=overrides.get("flat_time", eng["flat_time"]),
        no_entry_after=overrides.get("no_entry_after", eng["no_entry_after"]),
        max_trades_per_day=fcfg.get("max_trades_per_day"),
        daily_loss_stop=overrides.get("daily_loss_stop"),
    )


def run_instrument(inst: str, fam_names: list[str] | None) -> None:
    root = yaml.safe_load(CONFIG.read_text())
    icfg = root["instruments"][inst]
    data_cfg = yaml.safe_load(Path(icfg["data_config"]).read_text())
    strat_cfg = yaml.safe_load(Path(icfg["strat_config"]).read_text())
    eng = strat_cfg["engine"]
    overrides = icfg.get("engine_overrides", {})
    processed = Path(icfg["processed_dir"])
    reports = Path(icfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    mc_cfg = icfg["monte_carlo"]
    accounts = _accounts(mc_cfg)
    primary = mc_cfg["primary_account"]
    max_amb = float(root.get("max_ambiguity_pct", 0.10))

    splits = icfg["splits"]
    grid_start, grid_end = _as_date(splits["grid_start"]), _as_date(splits["grid_end"])
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    exec_grid = _filter(exec_full, grid_start, grid_end)
    wf_cfg = icfg["walk_forward"]
    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]),
        _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"],
        wf_cfg["test_months"],
    )
    log.info("%s: %d WF folds", inst.upper(), len(folds))

    sig_cache: dict[int, pl.DataFrame] = {}

    def sig_bars(tf: int) -> pl.DataFrame:
        if tf not in sig_cache:
            path = processed / f"continuous_{tf}m.parquet"
            sig_cache[tf] = _filter(pl.read_parquet(path), grid_start, grid_end)
        return sig_cache[tf]

    families = icfg["families"]
    if fam_names:
        families = {k: families[k] for k in fam_names if k in families}

    for fam, fcfg in families.items():
        base = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", base.timeframe_minutes))
        cls = _tf_cls(base, tf)
        space = fcfg["param_grid"]
        n_combo = len(param_grid(space))
        min_tr = int(fcfg.get("min_trades_train", wf_cfg["min_trades_train"]))
        scorer = lambda t, mt=min_tr: score_sharpe(t, min_trades=mt)
        ecfg = engine_cfg(eng, overrides, fcfg)
        log.info("=== Phase 15 %s/%s (%d combos, %dm) ===", inst, fam, n_combo, tf)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(tf), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase15_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        (processed / f"phase15_params_{fam}.yaml").write_text(yaml.dump(chosen))

        nets = [float(fr.test_net) for fr in wf.folds]
        pos_share = (sum(1 for n in nets if n > 0) / len(nets)) if nets else 0.0
        med_test = float(sorted(nets)[len(nets) // 2]) if nets else 0.0
        amb = ambiguity_pct(oos)
        sparse = sparsity_stats(oos)

        partial: dict[str, Any] = {
            "instrument": inst,
            "family": fam,
            "grid_size": n_combo,
            "timeframe_minutes": tf,
            "params": chosen,
            "pos_fold_share": pos_share,
            "median_test_pnl": med_test,
            "fold_table_md": render_fold_table(wf.folds),
            "oos_trades": oos.height,
            "oos_net": float(oos["net_pnl"].sum()) if oos.height else 0.0,
            "ambiguity_pct": amb,
            "ambiguity_reject": amb > max_amb,
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
            r = evaluate_multi(f"P15 {inst} {fam}", oos, accounts, mc_cfg)
            partial["result"] = r
            # primary pass for convenience
            partial["primary_pass"] = _mc1(r["mc_accounts"][primary])["pass_rate"]
        else:
            partial["primary_pass"] = 0.0

        (processed / f"phase15_partial_{fam}.json").write_text(
            json.dumps(_sanitize(partial), indent=1)
        )
        log.info(
            "%s/%s done: OOS %d trades net $%.0f amb=%.1f%% fold+=%.0f%% pass=%.1f%%",
            inst,
            fam,
            oos.height,
            partial["oos_net"],
            100 * amb,
            100 * pos_share,
            100 * partial["primary_pass"],
        )


def write_instrument_report(inst: str) -> None:
    root = yaml.safe_load(CONFIG.read_text())
    icfg = root["instruments"][inst]
    data_cfg = yaml.safe_load(Path(icfg["data_config"]).read_text())
    strat_cfg = yaml.safe_load(Path(icfg["strat_config"]).read_text())
    eng = strat_cfg["engine"]
    overrides = icfg.get("engine_overrides", {})
    processed = Path(icfg["processed_dir"])
    reports = Path(icfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)
    mc_cfg = icfg["monte_carlo"]
    primary = mc_cfg["primary_account"]
    accounts_list = mc_cfg["accounts"]

    partials = []
    for fam in icfg["families"]:
        p = processed / f"phase15_partial_{fam}.json"
        if p.exists():
            partials.append(json.loads(p.read_text()))
    if not partials:
        raise SystemExit(f"No phase15_partial_*.json for {inst}")

    def sort_key(pt: dict) -> tuple:
        # Ambiguity rejects sort last
        rej = 1 if pt.get("ambiguity_reject") else 0
        r = pt.get("result") or {}
        upi = (r.get("consistency", {}).get("full", {}) or {}).get("upi")
        return (
            -rej,
            pt.get("primary_pass", 0),
            pt.get("pos_fold_share", 0),
            -1e9 if upi is None else upi,
        )

    partials.sort(key=sort_key, reverse=True)

    acct_hdr = " | ".join(f"Pass {a.replace('lucid_', '').upper()}" for a in accounts_list)
    lb = [
        f"# Phase 15 Scalp Leaderboard — {inst.upper()}",
        "",
        f"Primary ranking: {primary} pass → fold stability → UPI. "
        "Ambiguity >10% flagged REJECT. Grids through 2025-12-31; 2026 holdout separate.",
        "",
        f"| Candidate | Combos | Trades | {acct_hdr} | Amb % | Fold+ % | Net $ | "
        f"UPI | MaxDD | 2025 $ | t/mo |",
        "| --- | --- | --- | " + " | ".join(["---"] * len(accounts_list))
        + " | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for pt in partials:
        r = pt.get("result")
        name = f"{inst} {pt['family']}"
        if pt.get("ambiguity_reject"):
            name += " ❌AMB"
        if not r:
            lb.append(
                f"| {name} | {pt['grid_size']} | 0 | "
                + " | ".join(["—"] * len(accounts_list))
                + f" | {100 * pt.get('ambiguity_pct', 0):.1f}% "
                f"| {100 * pt.get('pos_fold_share', 0):.0f}% | $0 | — | — | — | 0 |"
            )
            continue
        c = r["consistency"]["full"]
        passes = []
        for a in accounts_list:
            pr = _mc1(r["mc_accounts"][a])["pass_rate"]
            passes.append(f"{100 * pr:.1f}%")
        y2025 = pt.get("year_pnls_oos", {}).get("2025", 0)
        upi = c.get("upi")
        upi_s = f"{upi:.1f}" if upi is not None else "—"
        tpm = pt.get("sparsity", {}).get("trades_per_month", 0)
        lb.append(
            f"| {name} | {pt['grid_size']} "
            f"| {r['trade_metrics'].get('n_trades', 0)} "
            f"| {' | '.join(passes)} "
            f"| {100 * pt.get('ambiguity_pct', 0):.1f}% "
            f"| {100 * pt.get('pos_fold_share', 0):.0f}% "
            f"| ${c.get('net_pnl', 0):,.0f} "
            f"| {upi_s} "
            f"| ${c.get('max_drawdown', 0):,.0f} "
            f"| ${y2025:,.0f} "
            f"| {tpm:.1f} |"
        )

    # Slippage stress top 3 non-rejected
    st_cfg = root["stress"]
    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    stress_lines = ["", "## Slippage stress (2025, top eligible)", ""]
    eligible = [p for p in partials if not p.get("ambiguity_reject") and p.get("result")]
    for pt in eligible[:3]:
        fam = pt["family"]
        fcfg = icfg["families"][fam]
        base = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", base.timeframe_minutes))
        cls = _tf_cls(base, tf)
        params = pt.get("params") or {}
        ecfg = engine_cfg(eng, overrides, fcfg)
        rows = slippage_sweep(
            cls,
            params,
            exec_full,
            pl.read_parquet(processed / f"continuous_{tf}m.parquet"),
            cost,
            st_cfg["slippage_ticks"],
            ecfg,
            _as_date(st_cfg["period_start"]),
            _as_date(st_cfg["period_end"]),
        )
        stress_lines += render_stress_section(f"P15 {inst} {fam}", rows)

    # Wall-clock sparsity note
    sparse_lines = [
        "",
        "## Sparsity / wall-clock",
        "",
        "| Family | Active days | Span days | Trades/mo | Ambiguity |",
        "| --- | --- | --- | --- | --- |",
    ]
    for pt in partials:
        s = pt.get("sparsity") or {}
        sparse_lines.append(
            f"| {pt['family']} | {s.get('active_days', 0):.0f} "
            f"| {s.get('days_span', 0):.0f} "
            f"| {s.get('trades_per_month', 0):.1f} "
            f"| {100 * pt.get('ambiguity_pct', 0):.1f}% |"
        )

    wf_lines = [f"# Phase 15 {inst.upper()} Walk-Forward", ""]
    for pt in partials:
        wf_lines += [
            f"## {pt['family']}",
            "",
            f"- Params: `{pt.get('params')}`",
            f"- Fold+: {100 * pt.get('pos_fold_share', 0):.0f}%",
            f"- Ambiguity: {100 * pt.get('ambiguity_pct', 0):.1f}%",
            "",
            pt.get("fold_table_md") or "",
            "",
        ]

    out_lb = reports / f"phase15_{inst}_leaderboard.md"
    out_lb.write_text("\n".join(lb + stress_lines + sparse_lines) + "\n")
    (reports / f"phase15_{inst}_walk_forward.md").write_text("\n".join(wf_lines) + "\n")
    (reports / f"phase15_{inst}_metrics.json").write_text(
        json.dumps(_sanitize({"partials": partials}), indent=1)
    )
    log.info("Report → %s", out_lb)


def run_holdout(inst: str, fam_names: list[str]) -> None:
    root = yaml.safe_load(CONFIG.read_text())
    icfg = root["instruments"][inst]
    data_cfg = yaml.safe_load(Path(icfg["data_config"]).read_text())
    strat_cfg = yaml.safe_load(Path(icfg["strat_config"]).read_text())
    eng = strat_cfg["engine"]
    overrides = icfg.get("engine_overrides", {})
    processed = Path(icfg["processed_dir"])
    reports = Path(icfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    mc_cfg = icfg["monte_carlo"]
    accounts = _accounts(mc_cfg)
    splits = icfg["splits"]
    hs, he = _as_date(splits["holdout_start"]), _as_date(splits["holdout_end"])
    exec_h = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), hs, he)

    acct_hdr = " | ".join(
        f"Pass {a.replace('lucid_', '').upper()}" for a in mc_cfg["accounts"]
    )
    lines = [
        f"# Phase 15 {inst.upper()} Holdout (2026)",
        "",
        f"Single run {hs} → {he}. Frozen Phase 15 WF params — **no re-tune**.",
        "",
        f"| Family | Trades | Net $ | Amb % | {acct_hdr} |",
        "| --- | --- | --- | --- | "
        + " | ".join(["---"] * len(mc_cfg["accounts"]))
        + " |",
    ]
    rows = []
    for fam in fam_names:
        ppath = processed / f"phase15_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | params missing | — | — |")
            continue
        params = yaml.safe_load(ppath.read_text()) or {}
        fcfg = icfg["families"][fam]
        base = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", base.timeframe_minutes))
        cls = _tf_cls(base, tf)
        sig = _filter(pl.read_parquet(processed / f"continuous_{tf}m.parquet"), hs, he)
        ecfg = engine_cfg(eng, overrides, fcfg)
        prepared = cls(params).prepare(sig)
        res = run_backtest(exec_h, prepared, tf, cost, ecfg, cls.name)
        trades = res.trades
        trades.write_parquet(processed / f"trades_phase15_{fam}_holdout.parquet")
        amb = ambiguity_pct(trades)
        if trades.height == 0:
            lines.append(f"| {fam} | 0 | $0 | — | " + " | ".join(["—"] * len(accounts)) + " |")
            continue
        mc = evaluate_multi(f"P15 {inst} {fam} holdout", trades, accounts, mc_cfg)
        net = float(trades["net_pnl"].sum())
        passes = [
            f"{100 * _mc1(mc['mc_accounts'][a])['pass_rate']:.1f}%"
            for a in mc_cfg["accounts"]
        ]
        lines.append(
            f"| {fam} | {trades.height} | ${net:,.0f} | {100 * amb:.1f}% | "
            + " | ".join(passes)
            + " |"
        )
        rows.append(
            {
                "family": fam,
                "net": net,
                "trades": trades.height,
                "ambiguity_pct": amb,
                "mc": mc["mc_accounts"],
                "params": params,
            }
        )
    out = reports / f"phase15_{inst}_holdout.md"
    out.write_text("\n".join(lines) + "\n")
    (reports / f"phase15_{inst}_holdout.json").write_text(
        json.dumps(_sanitize({"holdout": rows}), indent=1)
    )
    log.info("Holdout → %s", out)


def merge_leaderboard() -> None:
    """Combine MNQ + GC into one phase15_scalp_leaderboard.md."""
    root = yaml.safe_load(CONFIG.read_text())
    parts = [
        "# Phase 15 Scalping Leaderboard (MNQ + GC)",
        "",
        "See Task 0 sizing: `data/reports/phase15_scalp_sizing.md`.",
        "Incumbent benchmark: MNQ ORB-W long-only + skipMon @ 25K ≈ **64%** pass.",
        "",
    ]
    for inst in root["instruments"]:
        path = Path(root["instruments"][inst]["reports_dir"]) / f"phase15_{inst}_leaderboard.md"
        if path.exists():
            parts.append(path.read_text())
            parts.append("")
        else:
            parts.append(f"_(no {inst} leaderboard yet)_")
            parts.append("")
    Path("data/reports/phase15_scalp_leaderboard.md").write_text("\n".join(parts))
    log.info("Merged → data/reports/phase15_scalp_leaderboard.md")


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--instrument", choices=["mnq", "gc"], help="Run WF for one instrument")
    ap.add_argument("--families", nargs="*", help="Subset of family keys")
    ap.add_argument("--holdout", nargs="*", metavar="FAMILY")
    ap.add_argument("--report", action="store_true", help="Write leaderboards from partials")
    ap.add_argument("--merge", action="store_true", help="Merge MNQ+GC leaderboards")
    args = ap.parse_args()

    if args.holdout is not None:
        if not args.instrument:
            raise SystemExit("--holdout requires --instrument")
        run_holdout(args.instrument, args.holdout)
        return
    if args.report:
        if args.instrument:
            write_instrument_report(args.instrument)
        else:
            for inst in yaml.safe_load(CONFIG.read_text())["instruments"]:
                try:
                    write_instrument_report(inst)
                except SystemExit as e:
                    log.warning("%s", e)
            merge_leaderboard()
        return
    if args.merge:
        merge_leaderboard()
        return
    if not args.instrument:
        raise SystemExit("Specify --instrument mnq|gc, or --report / --holdout")
    run_instrument(args.instrument, args.families)
    write_instrument_report(args.instrument)


if __name__ == "__main__":
    main()

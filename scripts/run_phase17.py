"""Phase 17: ORB-W causal enhancers (VIX / overnight / regime) + portfolio MC.

Usage:
  .venv/bin/python scripts/run_phase17.py
  .venv/bin/python scripts/run_phase17.py --families orb_vix_band orb_on_context
  .venv/bin/python scripts/run_phase17.py --holdout orb_vix_band orb_vix_on_stack
  .venv/bin/python scripts/run_phase17.py --report
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl
import yaml

from scripts.run_phase7 import _as_date, _filter, _sanitize, evaluate_ledger, skip_monday
from scripts.run_phase14_100k import journey_mc
from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import run_monte_carlo
from src.logging_setup import setup_logging
from src.strategies.orb_enhanced import OrbEnhanced
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    param_grid,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase17")
CONFIG = Path("config/phase17_orb_enhance.yaml")
DATA_CONFIG = Path("config/data.yaml")
STRAT_CONFIG = Path("config/strategies.yaml")

STRATEGY_CLASSES = {"orb_enhanced": OrbEnhanced}


def _mc1(d: dict) -> dict:
    return d[1] if 1 in d else d["1"]


def sparsity_stats(trades: pl.DataFrame) -> dict[str, float]:
    if trades.height == 0:
        return {"trades_per_month": 0.0, "active_days": 0, "days_span": 0}
    days = trades["trading_date"].unique().sort()
    span = (days[-1] - days[0]).days + 1
    return {
        "trades_per_month": trades.height / max(span / 30.44, 1e-9),
        "active_days": float(days.len()),
        "days_span": float(span),
    }


def engine_cfg(eng: dict, fcfg: dict) -> EngineConfig:
    return EngineConfig(
        qty=eng["qty"],
        flat_time=eng["flat_time"],
        no_entry_after=eng["no_entry_after"],
        max_trades_per_day=fcfg.get("max_trades_per_day", 1),
    )


def daily_from_trades(trades: pl.DataFrame) -> pl.DataFrame:
    return (
        trades.group_by("trading_date")
        .agg(pl.col("net_pnl").sum().alias("net_pnl"))
        .sort("trading_date")
    )


def portfolio_mc(
    ledgers: list[tuple[str, pl.DataFrame]],
    rules: LucidRules,
    costs: dict,
    mc_cfg: dict,
) -> dict[str, Any]:
    """Sum daily PnL across ledgers; MC on combined path (1 'trade' per day)."""
    daily = None
    for name, t in ledgers:
        d = daily_from_trades(t).rename({"net_pnl": name})
        if daily is None:
            daily = d
        else:
            daily = daily.join(d, on="trading_date", how="full", coalesce=True).sort("trading_date")
    assert daily is not None
    cols = [c for c in daily.columns if c != "trading_date"]
    daily = daily.with_columns(
        [pl.col(c).cast(pl.Float64).fill_null(0.0) for c in cols]
    ).with_columns(pl.sum_horizontal([pl.col(c) for c in cols]).alias("net_pnl"))
    # Synthetic trade ledger for MC helpers (one row per day)
    syn = daily.select(
        pl.col("trading_date"),
        pl.col("net_pnl"),
        pl.col("net_pnl").alias("gross_pnl"),
        pl.lit(0.0).alias("costs"),
        pl.lit(1).alias("side"),
        pl.lit(False).alias("ambiguous"),
        pl.lit("portfolio_day").alias("exit_reason"),
        pl.col("trading_date").cast(pl.Datetime("us")).alias("entry_ts"),
        pl.col("trading_date").cast(pl.Datetime("us")).alias("exit_ts"),
    )
    r = evaluate_ledger("portfolio", syn, rules, mc_cfg, costs)
    j = journey_mc(syn, "lucid_25k", 1)
    r["journey"] = j
    r["daily_rows"] = daily.height
    r["component_days"] = {c: int((daily[c] != 0).sum()) for c in cols}
    return r


def evaluate_baseline(cfg: dict, rules: LucidRules, costs: dict, mc_cfg: dict) -> dict | None:
    b = cfg.get("baseline") or {}
    path = Path(b.get("trades_parquet", ""))
    if not path.exists():
        return None
    trades = pl.read_parquet(path)
    if b.get("skip_monday"):
        trades = skip_monday(trades)
    r = evaluate_ledger(b.get("name", "incumbent"), trades, rules, mc_cfg, costs)
    r["journey"] = journey_mc(trades, "lucid_25k", 1)
    r["family"] = "_baseline"
    r["primary_pass"] = _mc1(r["mc"])["pass_rate"]
    r["sparsity"] = sparsity_stats(trades)
    r["params"] = {"note": "Phase 9 ORB-W + skipMon"}
    r["oos_trades"] = trades.height
    r["oos_net"] = float(trades["net_pnl"].sum())
    yp = (
        trades.group_by(pl.col("trading_date").dt.year().alias("y"))
        .agg(pl.col("net_pnl").sum().alias("net"))
        .sort("y")
    )
    r["year_pnls_oos"] = {str(row["y"]): float(row["net"]) for row in yp.to_dicts()}
    return r


def run_families(fam_names: list[str] | None) -> None:
    cfg = yaml.safe_load(CONFIG.read_text())
    data_cfg = yaml.safe_load(DATA_CONFIG.read_text())
    strat_cfg = yaml.safe_load(STRAT_CONFIG.read_text())
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)

    if not Path("data/processed/vix_daily.parquet").exists():
        raise SystemExit("Missing data/processed/vix_daily.parquet — ingest VIX first")

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    mc_cfg = cfg["monte_carlo"]
    primary = mc_cfg["primary_account"]
    rules = LucidRules.from_yaml(Path("config") / f"{primary}.yaml")
    costs = yaml.safe_load((Path("config") / f"{primary}.yaml").read_text())["costs"]

    splits = cfg["splits"]
    grid_start, grid_end = _as_date(splits["grid_start"]), _as_date(splits["grid_end"])
    exec_grid = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), grid_start, grid_end)
    wf_cfg = cfg["walk_forward"]
    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]),
        _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"],
        wf_cfg["test_months"],
    )
    sig = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), grid_start, grid_end)

    families = cfg["families"]
    if fam_names:
        families = {k: families[k] for k in fam_names if k in families}

    for fam, fcfg in families.items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        n_combo = len(param_grid(fcfg["param_grid"]))
        min_tr = int(fcfg.get("min_trades_train", wf_cfg["min_trades_train"]))
        scorer = lambda t, mt=min_tr: score_sharpe(t, min_trades=mt)
        ecfg = engine_cfg(eng, fcfg)
        log.info("=== Phase 17 %s (%d combos) ===", fam, n_combo)

        grid_runs = run_full_period_grid(
            cls, fcfg["param_grid"], exec_grid, sig, cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        # Post-hoc skip Monday only if not already in params
        chosen = wf.final_params or {}
        ledger = oos
        if chosen.get("skip_weekdays") in (None, (), [], ""):
            ledger = skip_monday(oos)
            name_suffix = " +skipMon"
        else:
            name_suffix = ""

        oos.write_parquet(processed / f"trades_phase17_{fam}_wf_oos.parquet")
        (processed / f"phase17_params_{fam}.yaml").write_text(yaml.dump(chosen))

        nets = [float(fr.test_net) for fr in wf.folds]
        pos_share = (sum(1 for n in nets if n > 0) / len(nets)) if nets else 0.0
        partial: dict[str, Any] = {
            "family": fam,
            "grid_size": n_combo,
            "params": chosen,
            "pos_fold_share": pos_share,
            "fold_table_md": render_fold_table(wf.folds),
            "oos_trades": ledger.height,
            "oos_net": float(ledger["net_pnl"].sum()) if ledger.height else 0.0,
            "sparsity": sparsity_stats(ledger),
        }
        if ledger.height:
            yp = (
                ledger.group_by(pl.col("trading_date").dt.year().alias("y"))
                .agg(pl.len().alias("n"), pl.col("net_pnl").sum().alias("net"))
                .sort("y")
            )
            partial["year_pnls_oos"] = {str(r["y"]): float(r["net"]) for r in yp.to_dicts()}
            r = evaluate_ledger(f"P17 {fam}{name_suffix}", ledger, rules, mc_cfg, costs)
            r["journey"] = journey_mc(ledger, "lucid_25k", 1)
            partial["result"] = r
            partial["primary_pass"] = _mc1(r["mc"])["pass_rate"]
            partial["pass_and_payout"] = r["journey"]["pass_and_payout"]
        else:
            partial["primary_pass"] = 0.0
            partial["pass_and_payout"] = 0.0

        (processed / f"phase17_partial_{fam}.json").write_text(
            json.dumps(_sanitize(partial), indent=1)
        )
        log.info(
            "%s done: n=%d net=$%.0f fold+=%.0f%% pass=%.1f%% payout=%.1f%%",
            fam, ledger.height, partial["oos_net"], 100 * pos_share,
            100 * partial["primary_pass"], 100 * partial["pass_and_payout"],
        )


def write_report() -> None:
    cfg = yaml.safe_load(CONFIG.read_text())
    data_cfg = yaml.safe_load(DATA_CONFIG.read_text())
    strat_cfg = yaml.safe_load(STRAT_CONFIG.read_text())
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    mc_cfg = cfg["monte_carlo"]
    primary = mc_cfg["primary_account"]
    rules = LucidRules.from_yaml(Path("config") / f"{primary}.yaml")
    costs = yaml.safe_load((Path("config") / f"{primary}.yaml").read_text())["costs"]

    partials = []
    for fam in cfg["families"]:
        p = processed / f"phase17_partial_{fam}.json"
        if p.exists():
            partials.append(json.loads(p.read_text()))
    if not partials:
        raise SystemExit("No phase17_partial_*.json")

    baseline = evaluate_baseline(cfg, rules, costs, mc_cfg)
    partials.sort(
        key=lambda pt: (pt.get("primary_pass", 0), pt.get("pos_fold_share") or 0),
        reverse=True,
    )

    lb = [
        "# Phase 17 Leaderboard — ORB-W Causal Enhancers (MNQ 25K)",
        "",
        "Gates use prior VIX close, causal overnight (18:00–09:30), prior-day regime. "
        "Incumbent ORB-W shown for comparison.",
        "",
        "| Candidate | Combos | Trades | Pass % | Pass+payout % | Fold+ % | Net $ | 2025 $ | t/mo |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def row(name: str, r: dict, pt: dict | None = None) -> str:
        mc = _mc1(r["mc"])
        j = r.get("journey") or {}
        pap = j.get("pass_and_payout", 0)
        fold = pt.get("pos_fold_share") if pt else None
        fold_s = f"{100 * fold:.0f}%" if fold is not None else "—"
        y2025 = (pt or {}).get("year_pnls_oos", r.get("year_pnls_oos", {})).get("2025", 0)
        tpm = (pt or {}).get("sparsity", r.get("sparsity", {})).get("trades_per_month", 0)
        grid = (pt or {}).get("grid_size", 0)
        ntr = r["trade_metrics"].get("n_trades", (pt or {}).get("oos_trades", 0))
        net = r["consistency"]["full"].get("net_pnl", 0)
        return (
            f"| {name} | {grid} | {ntr} | {100 * mc['pass_rate']:.1f}% "
            f"| {100 * pap:.1f}% | {fold_s} | ${net:,.0f} | ${y2025:,.0f} | {tpm:.1f} |"
        )

    if baseline:
        lb.append(row(f"**{baseline['name']}**", baseline, baseline))
    for pt in partials:
        r = pt.get("result")
        if not r:
            continue
        lb.append(row(f"P17 {pt['family']}", r, pt))

    # Portfolio: incumbent + best dense enhancer (skip sparsity traps)
    port_lines = ["", "## Portfolio MC (daily sum)", ""]

    def _dense_enhancer(pt: dict) -> bool:
        if not pt.get("result") or pt["family"] == "orb_w_control":
            return False
        if pt.get("primary_pass", 0) < 0.50:
            return False
        if (pt.get("pos_fold_share") or 0) < 0.50:
            return False
        s = pt.get("sparsity") or {}
        return (
            pt.get("oos_trades", 0) >= 100
            and s.get("trades_per_month", 0) >= 4.0
        )

    enhancers = [pt for pt in partials if _dense_enhancer(pt)]
    if baseline and enhancers:
        best = enhancers[0]
        base_t = pl.read_parquet(cfg["baseline"]["trades_parquet"])
        if cfg["baseline"].get("skip_monday"):
            base_t = skip_monday(base_t)
        enh_t = pl.read_parquet(processed / f"trades_phase17_{best['family']}_wf_oos.parquet")
        # If enhancer already skips Mon in params, don't double-filter
        port = portfolio_mc(
            [("orb_w", base_t), (best["family"], enh_t)],
            rules, costs, mc_cfg,
        )
        port_lines += [
            f"Components: incumbent ORB-W + **{best['family']}** (daily PnL sum).",
            f"- Pass: **{100 * _mc1(port['mc'])['pass_rate']:.1f}%**",
            f"- Pass+payout: **{100 * port['journey']['pass_and_payout']:.1f}%**",
            f"- Active days: {port['component_days']}",
            "",
        ]
        (reports / "phase17_portfolio.json").write_text(json.dumps(_sanitize(port), indent=1))
    else:
        port_lines.append("_No enhancer ≥50% pass for portfolio stack._")

    # Stress top 2
    st = cfg["stress"]
    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    stress = ["", "## Slippage stress (2025, top 2)", ""]
    for pt in partials[:2]:
        if not pt.get("result"):
            continue
        fam = pt["family"]
        fcfg = cfg["families"][fam]
        rows = slippage_sweep(
            OrbEnhanced, pt.get("params") or {}, exec_full,
            pl.read_parquet(processed / "continuous_5m.parquet"),
            cost, st["slippage_ticks"], engine_cfg(eng, fcfg),
            _as_date(st["period_start"]), _as_date(st["period_end"]),
        )
        stress += render_stress_section(f"P17 {fam}", rows)

    wf_lines = ["# Phase 17 Walk-Forward", ""]
    for pt in partials:
        wf_lines += [
            f"## {pt['family']}", "", f"- Params: `{pt.get('params')}`",
            f"- Fold+: {100 * (pt.get('pos_fold_share') or 0):.0f}%", "",
            pt.get("fold_table_md") or "", "",
        ]

    (reports / "phase17_leaderboard.md").write_text("\n".join(lb + port_lines + stress) + "\n")
    (reports / "phase17_walk_forward.md").write_text("\n".join(wf_lines) + "\n")
    (reports / "phase17_metrics.json").write_text(
        json.dumps(_sanitize({"partials": partials, "baseline": baseline}), indent=1)
    )
    log.info("Report → data/reports/phase17_leaderboard.md")


def run_holdout(fam_names: list[str]) -> None:
    cfg = yaml.safe_load(CONFIG.read_text())
    data_cfg = yaml.safe_load(DATA_CONFIG.read_text())
    strat_cfg = yaml.safe_load(STRAT_CONFIG.read_text())
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
    rules = LucidRules.from_yaml(Path("config/lucid_25k.yaml"))
    costs = yaml.safe_load(Path("config/lucid_25k.yaml").read_text())["costs"]
    hs, he = _as_date(cfg["splits"]["holdout_start"]), _as_date(cfg["splits"]["holdout_end"])
    exec_h = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), hs, he)
    sig_h = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), hs, he)

    lines = [
        "# Phase 17 Holdout (2026)", "",
        f"Single run {hs} → {he}. Frozen WF params — no re-tune.", "",
        "| Family | Trades | Net $ | Pass % | Pass+payout % |",
        "| --- | --- | --- | --- | --- |",
    ]
    rows = []
    for fam in fam_names:
        ppath = processed / f"phase17_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | missing | — | — |")
            continue
        params = yaml.safe_load(ppath.read_text()) or {}
        fcfg = cfg["families"][fam]
        res = run_backtest(
            exec_h, OrbEnhanced(params).prepare(sig_h), 5, cost,
            engine_cfg(eng, fcfg), "orb_enhanced",
        )
        trades = res.trades
        trades.write_parquet(processed / f"trades_phase17_{fam}_holdout.parquet")
        if trades.height == 0:
            lines.append(f"| {fam} | 0 | $0 | — | — |")
            continue
        r = evaluate_ledger(fam, trades, rules, mc_cfg, costs)
        j = journey_mc(trades, "lucid_25k", 1)
        net = float(trades["net_pnl"].sum())
        lines.append(
            f"| {fam} | {trades.height} | ${net:,.0f} "
            f"| {100 * _mc1(r['mc'])['pass_rate']:.1f}% "
            f"| {100 * j['pass_and_payout']:.1f}% |"
        )
        rows.append({"family": fam, "net": net, "pass": _mc1(r["mc"])["pass_rate"],
                     "pass_and_payout": j["pass_and_payout"], "params": params})
    (reports / "phase17_holdout.md").write_text("\n".join(lines) + "\n")
    (reports / "phase17_holdout.json").write_text(json.dumps(_sanitize({"holdout": rows}), indent=1))
    log.info("Holdout → data/reports/phase17_holdout.md")


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="*")
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

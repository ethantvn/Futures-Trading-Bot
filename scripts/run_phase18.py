"""Phase 18: deep multi-family Lucid pass search (UPI train scorer).

Usage:
  .venv/bin/python scripts/run_phase18.py
  .venv/bin/python scripts/run_phase18.py --families orb_fade vwap_reversion
  .venv/bin/python scripts/run_phase18.py --holdout orb_fade donchian
  .venv/bin/python scripts/run_phase18.py --report
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
from src.logging_setup import setup_logging
from src.strategies.atr_breakout import AtrBreakout
from src.strategies.donchian_breakout import DonchianBreakout
from src.strategies.trend import EmaTrend
from src.strategies.macd_momentum import MacdMomentum
from src.strategies.mean_reversion import BollingerMeanReversion
from src.strategies.mes_divergence_orb import MesDivergenceOrb
from src.strategies.orb_fade import OpeningRangeFade
from src.strategies.orb_filtered import FilteredOrb
from src.strategies.overnight_levels import OvernightLevels
from src.strategies.prior_day_levels import PriorDayLevels
from src.strategies.roc_momentum import RocMomentum
from src.strategies.rsi_fade import RsiFade
from src.strategies.session_tod import SessionTodOrb
from src.strategies.vwap_reversion import VwapReversion
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    param_grid,
    run_full_period_grid,
    score_sharpe,
    score_upi,
    walk_forward,
)

log = logging.getLogger("run_phase18")
CONFIG = Path("config/phase18_deep.yaml")
DATA_CONFIG = Path("config/data.yaml")
STRAT_CONFIG = Path("config/strategies.yaml")

STRATEGY_CLASSES = {
    "filtered_orb": FilteredOrb,
    "orb_fade": OpeningRangeFade,
    "vwap_reversion": VwapReversion,
    "bollinger_mr": BollingerMeanReversion,
    "rsi_fade": RsiFade,
    "prior_day_levels": PriorDayLevels,
    "overnight_levels": OvernightLevels,
    "donchian_breakout": DonchianBreakout,
    "ema_trend": EmaTrend,
    "atr_breakout": AtrBreakout,
    "macd_momentum": MacdMomentum,
    "roc_momentum": RocMomentum,
    "session_tod_orb": SessionTodOrb,
    "mes_divergence_orb": MesDivergenceOrb,
}


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
        max_hold_minutes=fcfg.get("max_hold_minutes"),
    )


def pick_scorer(name: str, min_tr: int):
    if name == "upi":
        return lambda t, mt=min_tr: score_upi(t, min_trades=mt)
    return lambda t, mt=min_tr: score_sharpe(t, min_trades=mt)


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
    scorer_name = wf_cfg.get("scorer", "upi")

    families = cfg["families"]
    if fam_names:
        families = {k: families[k] for k in fam_names if k in families}

    # Cache signal frames by timeframe
    sig_cache: dict[int, pl.DataFrame] = {}

    for fam, fcfg in families.items():
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        n_combo = len(param_grid(fcfg["param_grid"]))
        min_tr = int(fcfg.get("min_trades_train", wf_cfg["min_trades_train"]))
        scorer = pick_scorer(scorer_name, min_tr)
        ecfg = engine_cfg(eng, fcfg)
        tf = int(fcfg.get("timeframe_minutes", 5))
        if tf not in sig_cache:
            sig_cache[tf] = _filter(
                pl.read_parquet(processed / f"continuous_{tf}m.parquet"),
                grid_start, grid_end,
            )
        sig = sig_cache[tf]
        log.info("=== Phase 18 %s (%d combos, scorer=%s) ===", fam, n_combo, scorer_name)

        grid_runs = run_full_period_grid(cls, fcfg["param_grid"], exec_grid, sig, cost, ecfg)
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        chosen = wf.final_params or {}
        ledger = oos
        if chosen.get("skip_weekdays") in (None, (), [], ""):
            # post-hoc Monday skip only when strategy didn't encode it
            if fam.startswith("orb") or fam in ("prior_day_fade", "prior_day_break"):
                pass  # many non-ORB families benefit from skip Mon — apply lightly
            ledger = oos

        oos.write_parquet(processed / f"trades_phase18_{fam}_wf_oos.parquet")
        (processed / f"phase18_params_{fam}.yaml").write_text(yaml.dump(chosen))

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
            "scorer": scorer_name,
        }
        if ledger.height:
            yp = (
                ledger.group_by(pl.col("trading_date").dt.year().alias("y"))
                .agg(pl.len().alias("n"), pl.col("net_pnl").sum().alias("net"))
                .sort("y")
            )
            partial["year_pnls_oos"] = {str(r["y"]): float(r["net"]) for r in yp.to_dicts()}
            r = evaluate_ledger(f"P18 {fam}", ledger, rules, mc_cfg, costs)
            r["journey"] = journey_mc(ledger, "lucid_25k", 1)
            partial["result"] = r
            partial["primary_pass"] = _mc1(r["mc"])["pass_rate"]
            partial["pass_and_payout"] = r["journey"]["pass_and_payout"]
        else:
            partial["primary_pass"] = 0.0
            partial["pass_and_payout"] = 0.0

        (processed / f"phase18_partial_{fam}.json").write_text(
            json.dumps(_sanitize(partial), indent=1)
        )
        log.info(
            "%s done: n=%d net=$%.0f fold+=%.0f%% pass=%.1f%% payout=%.1f%%",
            fam, ledger.height, partial["oos_net"], 100 * pos_share,
            100 * partial["primary_pass"], 100 * partial["pass_and_payout"],
        )


def _dense(pt: dict, gates: dict) -> bool:
    s = pt.get("sparsity") or {}
    return (
        pt.get("oos_trades", 0) >= gates.get("min_oos_trades", 100)
        and s.get("trades_per_month", 0) >= gates.get("min_trades_per_month", 4.0)
        and (pt.get("pos_fold_share") or 0) >= gates.get("min_fold_pos_share", 0.5)
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
    gates = cfg.get("gates") or {}

    partials = []
    for fam in cfg["families"]:
        p = processed / f"phase18_partial_{fam}.json"
        if p.exists():
            partials.append(json.loads(p.read_text()))
    if not partials:
        raise SystemExit("No phase18_partial_*.json — run families first")

    baseline = evaluate_baseline(cfg, rules, costs, mc_cfg)
    partials.sort(
        key=lambda pt: (pt.get("primary_pass", 0), pt.get("pass_and_payout") or 0),
        reverse=True,
    )

    lb = [
        "# Phase 18 Leaderboard — Deep Multi-Family (MNQ 25K)",
        "",
        "Train scorer = **UPI** (Lucid-survival proxy). Ranked by MC pass, then pass+payout.",
        "Dense = ≥100 OOS trades, ≥4 t/mo, ≥50% positive folds.",
        "",
        "| Candidate | Combos | Dense? | Trades | Pass % | Pass+payout % | Fold+ % | Net $ | t/mo |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def row(name: str, r: dict, pt: dict | None = None) -> str:
        mc = _mc1(r["mc"])
        j = r.get("journey") or {}
        pap = j.get("pass_and_payout", 0)
        fold = pt.get("pos_fold_share") if pt else None
        fold_s = f"{100 * fold:.0f}%" if fold is not None else "—"
        tpm = (pt or {}).get("sparsity", r.get("sparsity", {})).get("trades_per_month", 0)
        grid = (pt or {}).get("grid_size", 0)
        ntr = r["trade_metrics"].get("n_trades", (pt or {}).get("oos_trades", 0))
        net = r["consistency"]["full"].get("net_pnl", 0)
        dense = "Y" if pt and _dense(pt, gates) else ("—" if not pt else "n")
        return (
            f"| {name} | {grid} | {dense} | {ntr} | {100 * mc['pass_rate']:.1f}% "
            f"| {100 * pap:.1f}% | {fold_s} | ${net:,.0f} | {tpm:.1f} |"
        )

    if baseline:
        lb.append(row(f"**{baseline['name']}**", baseline, baseline))
    for pt in partials:
        r = pt.get("result")
        if not r:
            continue
        mark = " ★" if _dense(pt, gates) and pt.get("primary_pass", 0) >= gates.get(
            "min_pass_to_challenge", 0.55
        ) else ""
        lb.append(row(f"P18 {pt['family']}{mark}", r, pt))

    # Challengers vs incumbent
    inc_pass = baseline["primary_pass"] if baseline else 0.64
    challengers = [
        pt for pt in partials
        if pt.get("result") and _dense(pt, gates)
        and pt.get("primary_pass", 0) >= inc_pass - 0.02
        and pt["family"] != "orb_w_control"
    ]
    chal = ["", "## Challengers (≥ incumbent−2pts, dense)", ""]
    if challengers:
        for pt in challengers:
            chal.append(
                f"- **{pt['family']}**: pass={100*pt['primary_pass']:.1f}% "
                f"payout={100*pt.get('pass_and_payout',0):.1f}% params=`{pt.get('params')}`"
            )
    else:
        chal.append("_No dense challenger within 2pts of incumbent._")

    st = cfg["stress"]
    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    stress = ["", "## Slippage stress (2025, top dense)", ""]
    dense_sorted = [pt for pt in partials if pt.get("result") and _dense(pt, gates)]
    for pt in dense_sorted[:3]:
        fam = pt["family"]
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        rows = slippage_sweep(
            cls, pt.get("params") or {}, exec_full,
            pl.read_parquet(processed / f"continuous_{fcfg.get('timeframe_minutes', 5)}m.parquet"),
            cost, st["slippage_ticks"], engine_cfg(eng, fcfg),
            _as_date(st["period_start"]), _as_date(st["period_end"]),
        )
        stress += render_stress_section(f"P18 {fam}", rows)

    wf_lines = ["# Phase 18 Walk-Forward", ""]
    for pt in partials:
        wf_lines += [
            f"## {pt['family']}", "", f"- Params: `{pt.get('params')}`",
            f"- Fold+: {100 * (pt.get('pos_fold_share') or 0):.0f}%",
            f"- Pass: {100 * pt.get('primary_pass', 0):.1f}%", "",
            pt.get("fold_table_md") or "", "",
        ]

    (reports / "phase18_leaderboard.md").write_text("\n".join(lb + chal + stress) + "\n")
    (reports / "phase18_walk_forward.md").write_text("\n".join(wf_lines) + "\n")
    (reports / "phase18_metrics.json").write_text(
        json.dumps(_sanitize({"partials": partials, "baseline": baseline}), indent=1)
    )
    log.info("Report → data/reports/phase18_leaderboard.md")


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

    lines = [
        "# Phase 18 Holdout (2026)", "",
        f"Single run {hs} → {he}. Frozen WF params — no re-tune.", "",
        "| Family | Trades | Net $ | Pass % | Pass+payout % |",
        "| --- | --- | --- | --- | --- |",
    ]
    rows = []
    for fam in fam_names:
        ppath = processed / f"phase18_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | missing | — | — |")
            continue
        params = yaml.safe_load(ppath.read_text()) or {}
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        tf = int(fcfg.get("timeframe_minutes", 5))
        sig_h = _filter(pl.read_parquet(processed / f"continuous_{tf}m.parquet"), hs, he)
        res = run_backtest(
            exec_h, cls(params).prepare(sig_h), tf, cost,
            engine_cfg(eng, fcfg), fcfg["strategy"],
        )
        trades = res.trades
        trades.write_parquet(processed / f"trades_phase18_{fam}_holdout.parquet")
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
        rows.append({
            "family": fam, "net": net,
            "pass": _mc1(r["mc"])["pass_rate"],
            "pass_and_payout": j["pass_and_payout"],
            "params": params,
        })
    (reports / "phase18_holdout.md").write_text("\n".join(lines) + "\n")
    (reports / "phase18_holdout.json").write_text(json.dumps(_sanitize({"holdout": rows}), indent=1))
    log.info("Holdout → data/reports/phase18_holdout.md")


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

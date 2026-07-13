"""Phase 13: MGC (micro gold) eval-strategy research for Lucid Flex 25K/50K.

Usage:
  .venv/bin/python scripts/build_bars.py --config config/data_mgc.yaml
  .venv/bin/python scripts/run_phase13_mgc.py --sizing
  .venv/bin/python scripts/run_phase13_mgc.py --families comex_orb ny_orb
  .venv/bin/python scripts/run_phase13_mgc.py --report
  .venv/bin/python scripts/run_phase13_mgc.py --holdout comex_orb macro_nfp
  .venv/bin/python scripts/run_phase13_mgc.py --contracts comex_orb

Selection discipline (mirrors Phase 11/12):
  - Params chosen on pre-2026 walk-forward only (18m train / 6m test)
  - MC on BOTH tiers (25K + 50K); primary ranking = 25K pass rate,
    then fold stability (% positive OOS folds), then UPI
  - Holdout 2026 run ONCE for finalists — no re-tune after looking
  - Families can be sharded across processes via --families; --report merges
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
from src.evaluation.monte_carlo import run_monte_carlo
from src.logging_setup import setup_logging
from src.strategies.indicators import ADJ, atr
from src.validation.reporting import render_fold_table, render_stress_section
from src.validation.stress import slippage_sweep
from src.validation.walk_forward import (
    make_folds,
    param_grid,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("run_phase13")

CONFIG = Path("config/mgc_phase13.yaml")
DATA_CONFIG = Path("config/data_mgc.yaml")
STRAT_CONFIG = Path("config/strategies_mgc.yaml")


def _load() -> tuple[dict, dict, dict]:
    return (
        yaml.safe_load(CONFIG.read_text()),
        yaml.safe_load(DATA_CONFIG.read_text()),
        yaml.safe_load(STRAT_CONFIG.read_text()),
    )


def _accounts(cfg: dict) -> dict[str, tuple[LucidRules, dict]]:
    out = {}
    for acct in cfg["monte_carlo"]["accounts"]:
        acct_yaml = yaml.safe_load((Path("config") / f"{acct}.yaml").read_text())
        out[acct] = (LucidRules.from_yaml(Path("config") / f"{acct}.yaml"), acct_yaml["costs"])
    return out


def evaluate_dual(
    name: str,
    trades: pl.DataFrame,
    accounts: dict[str, tuple[LucidRules, dict]],
    mc_cfg: dict,
) -> dict[str, Any]:
    """evaluate_ledger for each Lucid tier; shared trade/consistency metrics."""
    out: dict[str, Any] = {}
    mc_by_acct: dict[str, Any] = {}
    for acct, (rules, costs) in accounts.items():
        r = evaluate_ledger(name, trades, rules, mc_cfg, costs)
        mc_by_acct[acct] = r["mc"]
        out = out or r
    out["mc_accounts"] = mc_by_acct
    return out


def run_sizing_check(processed: Path, data_cfg: dict, cfg: dict, out_path: Path) -> dict:
    """ATR/daily-range $ risk at 1 MGC vs both Lucid MLL tiers."""
    pv = float(data_cfg["point_value"])
    sz = cfg["sizing"]
    lo, hi = sz["risk_pct_low"], sz["risk_pct_high"]

    lines = [
        "# MGC Sizing Check — 1 micro contract vs Lucid MLL (25K & 50K)",
        "",
        f"- Point value: **${pv:.0f}/pt** (${pv / 10:.2f}/tick @ 0.10 tick)",
        "",
        "| Tier | MLL | Risk band ({}–{}%) | Stop pts @ $10/pt |".format(
            int(100 * lo), int(100 * hi)
        ),
        "| --- | --- | --- | --- |",
    ]
    tier_budgets = {}
    for acct, t in sz["tiers"].items():
        mll = float(t["mll"])
        blo, bhi = mll * lo, mll * hi
        tier_budgets[acct] = (blo, bhi)
        lines.append(
            f"| {acct} | ${mll:,.0f} | ${blo:,.0f}–${bhi:,.0f} "
            f"| {blo / pv:.0f}–{bhi / pv:.0f} pts |"
        )

    lines += [
        "",
        "## ATR(14) $ risk at 1 MGC",
        "",
        "| Timeframe | Med ATR pts | Med ATR $ | 1.5×ATR $ | 2×ATR $ |",
        "| --- | --- | --- | --- | --- |",
    ]
    stats: dict[str, Any] = {}
    for tf in (5, 15, 30):
        path = processed / f"continuous_{tf}m.parquet"
        if not path.exists():
            continue
        df = pl.read_parquet(path).sort("ts_utc").with_columns(atr(14).alias("_atr"))
        daily = (
            df.group_by("trading_date")
            .agg(pl.col("_atr").median().alias("atr_pts"))
            .filter(pl.col("atr_pts").is_not_null())
        )
        med_pts = float(daily["atr_pts"].median())
        lines.append(
            f"| {tf}m | {med_pts:.2f} | ${med_pts * pv:,.0f} "
            f"| ${med_pts * pv * 1.5:,.0f} | ${med_pts * pv * 2:,.0f} |"
        )
        stats[f"{tf}m_median_atr_pts"] = med_pts

    bars_1m = pl.read_parquet(processed / "continuous_1m.parquet")
    rth = bars_1m.filter(pl.col("session") == "rth")
    daily_rng = rth.group_by("trading_date").agg(
        (pl.col(ADJ["high"]).max() - pl.col(ADJ["low"]).min()).alias("rng_pts")
    )
    p50 = float(daily_rng["rng_pts"].median())
    p95 = float(daily_rng["rng_pts"].quantile(0.95))
    worst = float(daily_rng["rng_pts"].max())
    lines += [
        "",
        "## Daily RTH range at 1 MGC ($/day)",
        "",
        f"- Median: **${p50 * pv:,.0f}** ({p50:.1f} pts) — GC full-size was ~$1,930",
        f"- P95: **${p95 * pv:,.0f}** ({p95:.1f} pts) — GC full-size was ~$7,810",
        f"- Max: **${worst * pv:,.0f}** ({worst:.1f} pts)",
        "",
        "### By year (regime shift matters)",
        "",
        "| Year | Median $ | P95 $ |",
        "| --- | --- | --- |",
    ]
    yr = (
        daily_rng.group_by(pl.col("trading_date").dt.year().alias("y"))
        .agg(
            pl.col("rng_pts").median().alias("med"),
            pl.col("rng_pts").quantile(0.95).alias("p95"),
        )
        .sort("y")
    )
    for r in yr.to_dicts():
        lines.append(f"| {r['y']} | ${r['med'] * pv:,.0f} | ${r['p95'] * pv:,.0f} |")

    b25 = tier_budgets.get("lucid_25k", (150, 250))
    b50 = tier_budgets.get("lucid_50k", (300, 500))
    verdict = (
        f"1 MGC fits both tiers: median daily RTH range ${p50 * pv:,.0f} is well "
        f"inside both MLLs (vs GC full-size where P95 ${p95 * pv * 10:,.0f} broke the "
        f"$2,000 MLL). Per-trade caps: use ~{b25[0] / pv:.0f}–{b25[1] / pv:.0f} pts on "
        f"25K, ~{b50[0] / pv:.0f}–{b50[1] / pv:.0f} pts on 50K. Caveat: 2025–2026 "
        "volatility is 3–4× the 2021–2023 regime (2026 median daily range "
        f"${float(yr.filter(pl.col('y') == 2026)['med'][0]) * pv:,.0f}); "
        "vol-normalized filters are preferred over absolute point thresholds, and "
        "P95 2026 days approach the 25K MLL — capped stops + 1 trade/day discipline required."
    )
    lines += ["", "## Verdict", "", verdict]
    out_path.write_text("\n".join(lines) + "\n")
    stats.update(
        daily_rth_median_usd=p50 * pv,
        daily_rth_p95_usd=p95 * pv,
        daily_rth_max_usd=worst * pv,
        verdict=verdict,
    )
    return stats


def _roll_sanity(processed: Path) -> None:
    rc = pl.read_parquet(processed / "roll_calendar.parquet")
    rc = rc.with_columns(pl.col("symbol").str.slice(-2, 1).alias("month_code"))
    bad = rc.filter(~pl.col("month_code").is_in(["G", "J", "M", "Q", "V", "Z"]))
    if bad.height:
        raise SystemExit(
            f"MGC roll calendar has non-liquid months ({bad.height} days). "
            "Re-run: .venv/bin/python scripts/build_bars.py --config config/data_mgc.yaml"
        )


def run_families(fam_names: list[str] | None) -> None:
    cfg, data_cfg, strat_cfg = _load()
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    _roll_sanity(processed)

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    accounts = _accounts(cfg)
    mc_cfg = cfg["monte_carlo"]

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
        space = fcfg["param_grid"]
        n_combo = len(param_grid(space))
        min_tr = int(fcfg.get("min_trades_train", wf_cfg["min_trades_train"]))
        scorer = lambda t, mt=min_tr: score_sharpe(t, min_trades=mt)
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        log.info("=== Phase 13 %s (%d combos) ===", fam, n_combo)

        grid_runs = run_full_period_grid(
            cls, space, exec_grid, sig_bars(cls.timeframe_minutes), cost, ecfg
        )
        wf = walk_forward(grid_runs, folds, scorer=scorer)
        oos = wf.oos_trades
        oos.write_parquet(processed / f"trades_phase13_{fam}_wf_oos.parquet")
        chosen = wf.final_params or {}
        (processed / f"phase13_params_{fam}.yaml").write_text(yaml.dump(chosen))

        nets = [float(fr.test_net) for fr in wf.folds]
        pos_share = (sum(1 for n in nets if n > 0) / len(nets)) if nets else 0.0
        med_test = float(sorted(nets)[len(nets) // 2]) if nets else 0.0

        partial: dict[str, Any] = {
            "family": fam,
            "grid_size": n_combo,
            "params": chosen,
            "pos_fold_share": pos_share,
            "median_test_pnl": med_test,
            "fold_table_md": render_fold_table(wf.folds),
            "oos_trades": oos.height,
            "oos_net": float(oos["net_pnl"].sum()) if oos.height else 0.0,
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
            r = evaluate_dual(f"MGC {fam}", oos, accounts, mc_cfg)
            partial["result"] = r
        (processed / f"phase13_partial_{fam}.json").write_text(
            json.dumps(_sanitize(partial), indent=1)
        )
        log.info("Phase 13 %s done -> phase13_partial_%s.json", fam, fam)


def write_report() -> None:
    cfg, data_cfg, strat_cfg = _load()
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)
    mc_cfg = cfg["monte_carlo"]
    primary = mc_cfg["primary_account"]
    secondary = [a for a in mc_cfg["accounts"] if a != primary]

    partials = []
    for fam in cfg["families"]:
        p = processed / f"phase13_partial_{fam}.json"
        if p.exists():
            partials.append(json.loads(p.read_text()))
    if not partials:
        raise SystemExit("No phase13_partial_*.json found — run families first.")

    def pass_rate(pt: dict, acct: str) -> float:
        r = pt.get("result")
        if not r:
            return -1.0
        return r["mc_accounts"][acct]["1"]["pass_rate"]

    def sort_key(pt: dict) -> tuple:
        r = pt.get("result") or {}
        upi = (r.get("consistency", {}).get("full", {}) or {}).get("upi")
        return (
            pass_rate(pt, primary),
            pt.get("pos_fold_share", 0),
            -1e9 if upi is None else upi,
        )

    partials.sort(key=sort_key, reverse=True)

    wf_cfg = cfg["walk_forward"]
    folds = make_folds(
        _as_date(wf_cfg["first_train_start"]),
        _as_date(wf_cfg["last_test_end"]),
        wf_cfg["train_months"],
        wf_cfg["test_months"],
    )

    lb = [
        "# Phase 13 MGC Leaderboard — Lucid Flex 25K (primary) & 50K @ 1 micro",
        "",
        f"Sorted by {primary} pass rate -> fold stability -> UPI. "
        "MC: 10k block-bootstrap on stitched WF OOS ledger (grids through 2025-12-31).",
        "",
        "| Candidate | Combos | Trades | Pass 25K | Pass 50K | Med d (25K) | Fold+ % "
        "| Net $ | UPI | MaxDD | 2025 $ |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for pt in partials:
        r = pt.get("result")
        if not r:
            lb.append(
                f"| MGC {pt['family']} | {pt['grid_size']} | 0 | — | — | — "
                f"| {100 * pt.get('pos_fold_share', 0):.0f}% | $0 | — | — | — |"
            )
            continue
        c = r["consistency"]["full"]
        mc25 = r["mc_accounts"][primary]["1"]
        mc50 = r["mc_accounts"][secondary[0]]["1"] if secondary else {}
        med = mc25.get("median_days")
        med_s = f"{med:.0f}" if med else "—"
        y2025 = pt.get("year_pnls_oos", {}).get("2025", 0)
        upi = c.get("upi")
        upi_s = f"{upi:.1f}" if upi is not None else "—"
        lb.append(
            f"| MGC {pt['family']} | {pt['grid_size']} "
            f"| {r['trade_metrics'].get('n_trades', 0)} "
            f"| {100 * mc25['pass_rate']:.1f}% "
            f"| {100 * mc50.get('pass_rate', 0):.1f}% "
            f"| {med_s} "
            f"| {100 * pt.get('pos_fold_share', 0):.0f}% "
            f"| ${c.get('net_pnl', 0):,.0f} "
            f"| {upi_s} "
            f"| ${c.get('max_drawdown', 0):,.0f} "
            f"| ${y2025:,.0f} |"
        )

    # Slippage stress: top 3 with OOS trades
    st_cfg = cfg["stress"]
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    stress_lines = ["", "## Slippage stress (2025, top 3 by primary pass rate)", ""]
    stressed = 0
    for pt in partials:
        if stressed >= 3 or not pt.get("result"):
            continue
        fam = pt["family"]
        fcfg = cfg["families"][fam]
        cls = STRATEGY_CLASSES[fcfg["strategy"]]
        ecfg = EngineConfig(
            qty=eng["qty"],
            flat_time=eng["flat_time"],
            no_entry_after=eng["no_entry_after"],
            max_trades_per_day=fcfg.get("max_trades_per_day"),
        )
        rows = slippage_sweep(
            cls,
            pt.get("params") or {},
            exec_full,
            pl.read_parquet(processed / f"continuous_{cls.timeframe_minutes}m.parquet"),
            cost,
            st_cfg["slippage_ticks"],
            ecfg,
            _as_date(st_cfg["period_start"]),
            _as_date(st_cfg["period_end"]),
        )
        stress_lines += render_stress_section(f"MGC {fam}", rows)
        stressed += 1
    lb += stress_lines
    (reports / "phase13_leaderboard.md").write_text("\n".join(lb) + "\n")

    wf_report = [
        "# Phase 13 MGC Walk-Forward",
        "",
        f"- Folds: {len(folds)} × ({wf_cfg['train_months']}m train / "
        f"{wf_cfg['test_months']}m test)",
        f"- Grid: {cfg['splits']['grid_start']} → {cfg['splits']['grid_end']}",
        "",
    ]
    for pt in partials:
        wf_report += [
            f"## {pt['family']}",
            "",
            f"- Grid size: **{pt['grid_size']}** combos",
            f"- Final params: `{pt.get('params', {})}`",
            f"- OOS trades: {pt.get('oos_trades', 0)}, net ${pt.get('oos_net', 0):,.0f}",
            f"- Fold stability: {100 * pt.get('pos_fold_share', 0):.0f}% positive "
            f"test folds (median test ${pt.get('median_test_pnl', 0):,.0f})",
            f"- OOS by year: {pt.get('year_pnls_oos', {})}",
            "",
            pt.get("fold_table_md", ""),
            "",
        ]
    (reports / "phase13_walk_forward.md").write_text("\n".join(wf_report) + "\n")

    (reports / "phase13_metrics.json").write_text(
        json.dumps(_sanitize({"candidates": partials, "folds": len(folds)}), indent=1)
    )
    log.info("Phase 13 report -> %s", reports)


def run_holdout(fam_names: list[str]) -> None:
    cfg, data_cfg, strat_cfg = _load()
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    accounts = _accounts(cfg)
    mc_cfg = cfg["monte_carlo"]
    primary = mc_cfg["primary_account"]
    secondary = [a for a in mc_cfg["accounts"] if a != primary]

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    splits = cfg["splits"]
    hs, he = _as_date(splits["holdout_start"]), _as_date(splits["holdout_end"])
    exec_full = pl.read_parquet(processed / "continuous_1m.parquet")
    exec_h = _filter(exec_full, hs, he)
    lines = [
        "# Phase 13 MGC Holdout (2026)",
        "",
        f"Single run {hs} → {he}. Frozen Phase 13 params — no re-tune.",
        "",
        "| Family | Trades | Net $ | Pass 25K % | Pass 50K % |",
        "| --- | --- | --- | --- | --- |",
    ]
    for fam in fam_names:
        ppath = processed / f"phase13_params_{fam}.yaml"
        if not ppath.exists():
            lines.append(f"| {fam} | — | params missing | — | — |")
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
        trades.write_parquet(processed / f"trades_phase13_{fam}_holdout.parquet")
        if trades.height == 0:
            lines.append(f"| {fam} | 0 | $0 | — | — |")
            continue
        r = evaluate_dual(fam, trades, accounts, mc_cfg)
        net = float(trades["net_pnl"].sum())
        p25 = r["mc_accounts"][primary][1]["pass_rate"]
        p50 = r["mc_accounts"][secondary[0]][1]["pass_rate"] if secondary else 0.0
        lines.append(
            f"| {fam} | {trades.height} | ${net:,.0f} "
            f"| {100 * p25:.1f}% | {100 * p50:.1f}% |"
        )
    (reports / "phase13_holdout.md").write_text("\n".join(lines) + "\n")
    log.info("Holdout -> %s", reports / "phase13_holdout.md")


def run_contract_sweep(fam_names: list[str], contracts: list[int]) -> None:
    cfg, data_cfg, _ = _load()
    processed = Path(data_cfg["processed_dir"])
    accounts = _accounts(cfg)
    mc_cfg = cfg["monte_carlo"]
    for fam in fam_names:
        tpath = processed / f"trades_phase13_{fam}_wf_oos.parquet"
        if not tpath.exists():
            log.warning("%s: no OOS ledger", fam)
            continue
        trades = pl.read_parquet(tpath)
        print(f"\n== {fam} contract sweep (WF OOS ledger, {trades.height} trades) ==")
        for acct, (rules, costs) in accounts.items():
            for k in contracts:
                mc = run_monte_carlo(
                    trades,
                    rules,
                    contracts=k,
                    n_attempts=mc_cfg["n_attempts"],
                    max_days=mc_cfg["max_days"],
                    seed=mc_cfg["seed"],
                    evaluation_cost=costs["evaluation_cost"],
                    reset_cost=costs["reset_cost"],
                    strategy=fam,
                )
                med = mc.median_days_to_pass
                med_s = f"{med:.0f}" if med else "—"
                print(
                    f"  {acct} @ {k} MGC: pass {100 * mc.pass_rate:.1f}% "
                    f"fail {100 * mc.fail_rate:.1f}% median-days {med_s}"
                )


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizing", action="store_true", help="Sizing report only")
    ap.add_argument("--families", nargs="*", metavar="FAMILY")
    ap.add_argument("--report", action="store_true", help="Merge partials + stress")
    ap.add_argument("--holdout", nargs="*", metavar="FAMILY")
    ap.add_argument("--contracts", nargs="*", metavar="FAMILY")
    ap.add_argument("--ns", nargs="*", type=int, default=[1, 2, 3])
    args = ap.parse_args()

    cfg, data_cfg, _ = _load()
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])
    reports.mkdir(parents=True, exist_ok=True)

    if args.sizing:
        stats = run_sizing_check(
            processed, data_cfg, cfg, reports / "phase13_sizing.md"
        )
        log.info("Sizing verdict: %s", stats["verdict"][:100])
        return
    if args.holdout is not None:
        run_holdout(args.holdout)
        return
    if args.contracts is not None:
        run_contract_sweep(args.contracts, args.ns)
        return
    if args.report:
        write_report()
        return
    if args.families is not None:
        run_families(args.families)  # shard: no sizing/report
        return
    # default: everything serially
    run_sizing_check(processed, data_cfg, cfg, reports / "phase13_sizing.md")
    run_families(None)
    write_report()


if __name__ == "__main__":
    main()

"""Re-backtest ORB-W at Lucid-verified $0.50/side commission + updated MC rules.

Usage:
  .venv/bin/python scripts/run_rebacktest_orb_w.py
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl
import yaml

from scripts.run_phase7 import (
    _as_date,
    _filter,
    _sanitize,
    evaluate_ledger,
    skip_monday,
)
from src.backtest.engine import EngineConfig
from src.backtest.fees import CostModel
from src.backtest.metrics import compute_metrics
from src.evaluation.journey import journey_mc
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.recommendation import run_policy_monte_carlo
from src.evaluation.sizing import FixedSizing
from src.logging_setup import setup_logging
from src.strategies.orb_filtered import FilteredOrb
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("rebacktest")
OLD_LEDGER = Path("data/processed/trades_phase9_orb_longonly_wf_oos.parquet")
NEW_LEDGER = Path("data/processed/trades_rebacktest_orb_w_wf_oos.parquet")
HOLDOUT_OUT = Path("data/processed/trades_rebacktest_orb_w_holdout.parquet")
REPORT = Path("data/reports/rebacktest_commission050.md")

# Frozen Phase 9 winner (width + long-only; skip Mon applied post-hoc)
FROZEN_PARAMS = {
    "range_minutes": 30,
    "target_r": 1.0,
    "expire_minutes": 120,
    "min_width_ratio": 0.25,
    "max_width_ratio": 0.7,
    "long_only": True,
}


def main() -> None:
    setup_logging()
    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    reports = Path("data/reports")
    reports.mkdir(parents=True, exist_ok=True)

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    log.info(
        "Cost model: $%.2f/side comm + $%.2f/side exch + %d tick slip",
        eng["commission_per_side"],
        eng["exchange_fees_per_side"],
        eng["slippage_ticks"],
    )

    grid_start = _as_date("2019-06-01")
    grid_end = _as_date("2025-12-31")
    exec_grid = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), grid_start, grid_end)
    sig = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), grid_start, grid_end)
    ecfg = EngineConfig(
        qty=eng["qty"],
        flat_time=eng["flat_time"],
        no_entry_after=eng["no_entry_after"],
        max_trades_per_day=1,
    )

    folds = make_folds(grid_start, grid_end, train_months=24, test_months=6)
    space = {k: [v] for k, v in FROZEN_PARAMS.items()}
    grid_runs = run_full_period_grid(
        FilteredOrb, space, exec_grid, sig, cost, ecfg
    )
    wf = walk_forward(
        grid_runs, folds, scorer=lambda t: score_sharpe(t, min_trades=30)
    )
    oos = skip_monday(wf.oos_trades)
    oos.write_parquet(NEW_LEDGER)
    log.info("WF OOS: %d trades net=$%.0f", oos.height, float(oos["net_pnl"].sum()))

    # 2026 holdout
    hs, he = _as_date("2026-01-01"), _as_date("2026-06-28")
    from src.backtest.engine import run_backtest

    exec_h = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), hs, he)
    sig_h = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), hs, he)
    hold = run_backtest(
        exec_h, FilteredOrb(FROZEN_PARAMS).prepare(sig_h), 5, cost, ecfg, "orb_filtered"
    ).trades
    hold = skip_monday(hold)
    hold.write_parquet(HOLDOUT_OUT)

    rules = LucidRules.from_yaml("config/lucid_25k.yaml")
    lucid_costs = yaml.safe_load(Path("config/lucid_25k.yaml").read_text())["costs"]
    mc_cfg = {
        "n_attempts": 10_000,
        "seed": 42,
        "sample_mode": "block",
        "block_size": 5,
    }
    policy = FixedSizing("fixed_1", 1)

    def run_mc(ledger: pl.DataFrame, max_days: int | None) -> dict:
        mc = run_policy_monte_carlo(
            ledger, rules, policy,
            n_attempts=mc_cfg["n_attempts"],
            max_days=max_days if max_days is not None else 9999,
            seed=mc_cfg["seed"],
            sample_mode=mc_cfg["sample_mode"],
            block_size=mc_cfg["block_size"],
            evaluation_cost=lucid_costs["evaluation_cost_discounted"],
            reset_cost=lucid_costs["reset_cost"],
        )
        j = journey_mc(
            ledger, rules, policy,
            n=mc_cfg["n_attempts"],
            max_days=max_days,
            seed=mc_cfg["seed"],
            sample_mode=mc_cfg["sample_mode"],
            block_size=mc_cfg["block_size"],
        )
        return {
            "pass": mc.pass_rate,
            "fail": mc.fail_rate,
            "timeout": mc.timeout_rate,
            "pap": j["pass_and_payout"],
            "med_days": mc.median_days_to_pass,
        }

    new_60 = run_mc(oos, 60)
    new_free = run_mc(oos, None)
    ho = run_mc(hold, None)

    old_stats = {}
    if OLD_LEDGER.exists():
        old = skip_monday(pl.read_parquet(OLD_LEDGER))
        old_stats = {
            "trades": old.height,
            "net": float(old["net_pnl"].sum()),
            "costs": float(old["costs"].sum()) if "costs" in old.columns else None,
            **{f"mc_{k}": v for k, v in run_mc(old, 60).items()},
            **{f"free_{k}": v for k, v in run_mc(old, None).items()},
        }

    m = compute_metrics(oos)
    hm = compute_metrics(hold)

    lines = [
        "# Re-backtest — ORB-W @ Lucid $0.50/side + verified rules",
        "",
        f"Commission: **${eng['commission_per_side']:.2f}/side** "
        f"(was $0.62 + $0.37 exchange). Slippage: {eng['slippage_ticks']} tick.",
        "",
        f"Frozen params: `{FROZEN_PARAMS}` + skip Monday.",
        "",
        "## Ledger",
        "",
        "| | Trades | Net $ | Costs $ | Sharpe |",
        "| --- | --- | --- | --- | --- |",
    ]
    if old_stats:
        om = compute_metrics(skip_monday(pl.read_parquet(OLD_LEDGER)))
        lines.append(
            f"| Old ($0.99/side) | {old_stats['trades']} | ${old_stats['net']:,.0f} "
            f"| ${old_stats.get('costs') or 0:,.0f} | {om.get('sharpe_daily', 0):.2f} |"
        )
    lines.append(
        f"| **New ($0.50/side)** | {oos.height} | ${m.get('net_pnl', 0):,.0f} "
        f"| ${float(oos['costs'].sum()) if oos.height else 0:,.0f} "
        f"| {m.get('sharpe_daily', 0):.2f} |"
    )
    lines += [
        "",
        "## Lucid 25K Monte Carlo (1 micro, block bootstrap)",
        "",
        "| Ledger | max_days | Pass % | Fail % | Timeout % | Pass+payout % | Med days |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if old_stats:
        lines.append(
            f"| Old WF OOS | 60 | {100*old_stats['mc_pass']:.1f}% | {100*old_stats['mc_fail']:.1f}% "
            f"| {100*old_stats['mc_timeout']:.1f}% | {100*old_stats['mc_pap']:.1f}% "
            f"| {old_stats['mc_med_days']:.0f} |"
        )
        lines.append(
            f"| Old WF OOS | none | {100*old_stats['free_pass']:.1f}% | {100*old_stats['free_fail']:.1f}% "
            f"| {100*old_stats['free_timeout']:.1f}% | {100*old_stats['free_pap']:.1f}% "
            f"| {old_stats['free_med_days']:.0f} |"
        )
    lines.append(
        f"| **New WF OOS** | 60 | {100*new_60['pass']:.1f}% | {100*new_60['fail']:.1f}% "
        f"| {100*new_60['timeout']:.1f}% | {100*new_60['pap']:.1f}% "
        f"| {new_60['med_days']:.0f} |"
    )
    lines.append(
        f"| **New WF OOS** | **none** | **{100*new_free['pass']:.1f}%** | {100*new_free['fail']:.1f}% "
        f"| {100*new_free['timeout']:.1f}% | **{100*new_free['pap']:.1f}%** "
        f"| {new_free['med_days']:.0f} |"
    )
    lines.append(
        f"| New 2026 holdout | none | {100*ho['pass']:.1f}% | {100*ho['fail']:.1f}% "
        f"| {100*ho['timeout']:.1f}% | {100*ho['pap']:.1f}% | {ho['med_days']:.0f} |"
    )
    lines += [
        "",
        "## Holdout 2026",
        "",
        f"- Trades: {hold.height}, net ${hm.get('net_pnl', 0):,.0f}",
        "",
        "## Recommendation (updated)",
        "",
        "**ORB-W long-only + skip Monday @ 1 micro** — unchanged.",
        f"Use **{100*new_free['pass']:.1f}%** pass / **{100*new_free['pap']:.1f}%** pass+payout "
        "(no eval time limit, verified Lucid rules).",
        "",
    ]

    REPORT.write_text("\n".join(lines))
    out_json = {
        "params": FROZEN_PARAMS,
        "new_ledger": str(NEW_LEDGER),
        "metrics": m,
        "mc_60d": new_60,
        "mc_free": new_free,
        "holdout": {"trades": hold.height, "metrics": hm, "mc": ho},
        "old": old_stats,
    }
    (reports / "rebacktest_commission050.json").write_text(
        json.dumps(_sanitize(out_json), indent=1)
    )
    log.info("Report → %s", REPORT)
    print("\n".join(lines[-12:]))


if __name__ == "__main__":
    main()

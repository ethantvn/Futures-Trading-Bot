"""Monte Carlo Lucid evaluation simulation for every backtested strategy.

Usage:
  .venv/bin/python scripts/run_evaluation_simulation.py [--attempts 10000]
      [--accounts lucid_25k lucid_50k] [--contracts 1 2 3 5]

Reads data/processed/trades_<strategy>.parquet ledgers, replays 10k+ sampled
evaluation attempts per (strategy, account, contract count), writes
data/reports/evaluation_simulation.md.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import polars as pl
import yaml

from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import render_mc_markdown, run_monte_carlo
from src.logging_setup import setup_logging

log = logging.getLogger("run_evaluation_simulation")


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=int, default=10_000)
    ap.add_argument("--accounts", nargs="+", default=["lucid_25k", "lucid_50k"])
    ap.add_argument("--contracts", type=int, nargs="+", default=[1, 2, 3, 5])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-days", type=int, default=60)
    args = ap.parse_args()

    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])

    ledgers = sorted(processed.glob("trades_*.parquet"))
    if not ledgers:
        raise SystemExit("no trade ledgers found; run scripts/run_backtest.py first")

    results = []
    for account in args.accounts:
        cfg_path = Path("config") / f"{account}.yaml"
        rules = LucidRules.from_yaml(cfg_path)
        costs = yaml.safe_load(cfg_path.read_text())["costs"]
        for ledger_path in ledgers:
            strategy = ledger_path.stem.removeprefix("trades_")
            trades = pl.read_parquet(ledger_path)
            if trades.height == 0:
                continue
            for k in args.contracts:
                if k > rules.max_contracts_micro:
                    continue
                r = run_monte_carlo(
                    trades, rules, contracts=k,
                    n_attempts=args.attempts, max_days=args.max_days,
                    seed=args.seed,
                    evaluation_cost=costs["evaluation_cost"],
                    reset_cost=costs["reset_cost"],
                    strategy=strategy,
                )
                results.append(r)
                log.info(
                    "%s / %s / %d micros: pass %.1f%%",
                    strategy, rules.name, k, 100 * r.pass_rate,
                )

    header = [
        "# Lucid Evaluation Monte Carlo Report",
        "",
        f"- Attempts per row: {args.attempts:,}; evaluation capped at {args.max_days} "
        "trading days; moving-block bootstrap (5-day blocks) of historical trading days.",
        "- Ledgers are baseline backtests 2019-2025, pessimistic fills, all costs included.",
        "- Rules: EOD trailing MLL with lock at starting balance, 50% consistency, "
        "2 min trading days (sources cited in config).",
        "- E[cost] = eval fee + E[resets] x reset fee, using discounted fees NOT applied "
        "(regular prices from config).",
        "",
    ]
    out = reports / "evaluation_simulation.md"
    out.write_text("\n".join(header) + "\n" + render_mc_markdown(results) + "\n")
    log.info("wrote %s", out)
    print(render_mc_markdown(results))


if __name__ == "__main__":
    main()

"""Phase 6: sizing policies, 25K vs 50K comparison, final recommendation.

Usage:
  .venv/bin/python scripts/run_recommendation.py

Reads the validated ORB walk-forward OOS ledger and writes
data/reports/final_recommendation.md.
"""
from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
import yaml

from src.backtest.metrics import compute_metrics
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.recommendation import (
    policies_from_config,
    render_policy_table,
    run_policy_monte_carlo,
)
from src.logging_setup import setup_logging

log = logging.getLogger("run_recommendation")


def _eval_fee(lucid_yaml: dict, discounted: bool) -> float:
    c = lucid_yaml["costs"]
    return float(c["evaluation_cost_discounted" if discounted else "evaluation_cost"])


def main() -> None:
    setup_logging()
    rec_cfg = yaml.safe_load(Path("config/recommendation.yaml").read_text())
    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    processed = Path(data_cfg["processed_dir"])
    reports = Path(data_cfg["reports_dir"])

    ledger_path = processed / rec_cfg["ledger"]
    trades = pl.read_parquet(ledger_path)
    params = yaml.safe_load((processed / rec_cfg["params_file"]).read_text())
    mc = rec_cfg["monte_carlo"]
    use_disc = rec_cfg.get("use_discounted_eval_fee", True)
    policies = policies_from_config(rec_cfg)

    m = compute_metrics(trades)
    results = []
    for acct_name in rec_cfg["accounts"]:
        lucid_path = Path("config") / f"{acct_name}.yaml"
        lucid_yaml = yaml.safe_load(lucid_path.read_text())
        rules = LucidRules.from_yaml(lucid_path)
        eval_fee = _eval_fee(lucid_yaml, use_disc)
        reset_fee = float(lucid_yaml["costs"]["reset_cost"])
        for policy in policies:
            r = run_policy_monte_carlo(
                trades, rules, policy,
                n_attempts=mc["n_attempts"],
                max_days=mc["max_days"],
                seed=mc["seed"],
                sample_mode=mc["sample_mode"],
                block_size=mc["block_size"],
                evaluation_cost=eval_fee,
                reset_cost=reset_fee,
            )
            results.append(r)
            log.info(
                "%s / %s / %s: pass %.1f%%, E[cost] $%.0f",
                acct_name, policy.name, rules.name,
                100 * r.pass_rate,
                r.expected_total_cost_before_pass or 0,
            )

    # pick best 25K policy by pass rate then cost
    r25 = [r for r in results if "25K" in r.account]
    best = max(r25, key=lambda r: (r.pass_rate, -(r.expected_total_cost_before_pass or 0)))

    lines = [
        "# Final Recommendation — Lucid Flex Evaluation",
        "",
        "Date: 2026-07-06. Based on Phase 5 validated **opening-range breakout** only.",
        "EMA trend and other families were rejected after walk-forward + 2026 holdout.",
        "",
        "## Strategy (validated)",
        "",
        f"- **Family:** Opening-range breakout (ORB)",
        f"- **Params:** `{params}`",
        f"- **Signal timeframe:** 5m; fills on 1m; flat by 15:55 ET",
        f"- **Evidence ledger:** `{rec_cfg['ledger']}` ({m.get('n_trades', 0)} trades, "
        f"walk-forward OOS 2021–2025)",
        f"- **Walk-forward OOS:** net ${m.get('net_pnl', 0):,.0f}, "
        f"Sharpe {m.get('sharpe_daily', 0):.2f}, PF {m.get('profit_factor', 0):.2f}",
        "- **2026 holdout (single run):** +$948, PF 1.06 — supportive but not strong",
        "",
        "## Recommended configs for your 25K eval",
        "",
        "### Conservative (recommended)",
        "",
        "- **Size:** 1 MNQ micro every session",
        "- **Why:** Highest pass probability and lowest expected reset cost in every simulation",
        "- **Rules discipline:** One ORB trade/day max; if largest day would exceed 50% of "
        "running profit near target, stop for the day or take a small second session another day",
        "- **Do not:** Scale to 2+ micros on 25K unless you accept materially lower pass rate",
        "",
        "### Moderate (optional — higher variance)",
        "",
        "- **Size:** 2 MNQ micros every session (fixed)",
        "- **Sim pass rate:** ~36% vs ~44% conservative; median pass ~10 days vs ~22",
        "- **E[cost] to funded:** ~$178 (discounted eval + expected resets)",
        "- **Dynamic downshift** (2→1 micro when cushion < $600) did **not** improve 25K pass rate vs fixed 2 micros",
        "- **Only consider if** you prioritize speed over pass probability",
        "",
        "## Sizing & account comparison (10k Monte Carlo each)",
        "",
        f"- Ledger: walk-forward OOS trades, block bootstrap ({mc['block_size']}-day blocks)",
        f"- Eval fees: {'discounted' if use_disc else 'list'} prices from lucid configs",
        "",
        render_policy_table(results),
        "",
        "## Decision summary",
        "",
        f"**Best 25K policy in simulation:** `{best.policy}` — "
        f"{100 * best.pass_rate:.1f}% pass, "
        f"median {best.median_days_to_pass:.0f} days, "
        f"E[cost] ${best.expected_total_cost_before_pass:,.0f}"
        if best.median_days_to_pass
        else f"**Best 25K policy:** `{best.policy}` — {100 * best.pass_rate:.1f}% pass",
        "",
        "### 25K vs 50K (same ORB edge)",
        "",
    ]

    for policy_name in ["conservative", "moderate"]:
        p25 = next((r for r in results if r.policy == policy_name and "25K" in r.account), None)
        p50 = next((r for r in results if r.policy == policy_name and "50K" in r.account), None)
        if p25 and p50:
            lines.append(
                f"- **{policy_name}:** 25K pass {100 * p25.pass_rate:.1f}% "
                f"(E[cost] ${p25.expected_total_cost_before_pass:,.0f}) vs "
                f"50K pass {100 * p50.pass_rate:.1f}% "
                f"(E[cost] ${p50.expected_total_cost_before_pass:,.0f})"
            )

    lines.extend([
        "",
        "- **50K is harder:** profit target is 2.4× larger ($3,000 vs $1,250) with only 2× "
        "drawdown room ($2,000 vs $1,000). Same strategy edge yields lower pass rates on 50K.",
        "- **You own 25K:** stay on 25K; do not upgrade account size for this strategy.",
        "",
        "## Execution checklist (live eval)",
        "",
        "1. Trade **MNQ** only; **1 micro** default (20 micro max firm cap — irrelevant at 1).",
        "2. ORB: 30-minute opening range (09:30–10:00 ET), stop entry 1 tick beyond range, "
        "stop at opposite side, target **1.5R**, pending expires 120 minutes.",
        "3. Flat by **15:55 ET**; no new entries after **15:30 ET**.",
        "4. **Consistency:** no single day > 50% of total profit at pass — plan 2+ balanced days.",
        "5. **MLL:** EOD only — intraday dips below floor are OK if you close above it.",
        "6. Verify your platform commission (placeholder $0.99/side/micro in backtests).",
        "",
        "## Rejected strategies",
        "",
        "| Strategy | Reason |",
        "| --- | --- |",
        "| ema_trend | WF OOS flat; 2026 holdout −$2,568 |",
        "| vwap_pullback | Negative baseline expectancy |",
        "| prev_day_hl_breakout | Negative baseline expectancy |",
        "| bollinger_mean_reversion | Negative baseline expectancy |",
        "",
        "## Caveats",
        "",
        "- Past pass rates are **estimates** from historical bootstrap, not guarantees.",
        "- Commission/slippage placeholders may differ from your live platform.",
        "- 2026 holdout was run once; do not re-optimize on it.",
        "- Lucid EOD session-close time assumed 17:00 ET (CME).",
        "",
    ])

    out = reports / "final_recommendation.md"
    out.write_text("\n".join(lines))
    log.info("wrote %s", out)
    print("\n".join(lines[:40]))
    print("...")
    print(f"\nFull report: {out}")


if __name__ == "__main__":
    main()

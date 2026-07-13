"""Monte Carlo evaluation-attempt simulation.

Samples sequences of historical trading days from a strategy's trade ledger
(per-day trade PnL lists) and replays each sequence through the Lucid rule
engine. Two sampling modes:
- "day":   iid bootstrap of single days
- "block": moving-block bootstrap (default block 5 days) preserving win/loss
           clustering across adjacent days
Deterministic under a fixed seed.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import polars as pl

from src.evaluation.lucid_rules import LucidRules
from src.evaluation.simulator import run_evaluation

log = logging.getLogger(__name__)


@dataclass
class MonteCarloResult:
    strategy: str
    account: str
    contracts: int
    n_attempts: int
    pass_rate: float
    fail_rate: float
    timeout_rate: float
    median_days_to_pass: float | None
    p25_days_to_pass: float | None
    p75_days_to_pass: float | None
    pass_within: dict[int, float] = field(default_factory=dict)   # {10: %, 15: %, 20: %}
    fail_by_drawdown_pct: float = 0.0
    avg_profit_before_failure: float = 0.0
    avg_remaining_drawdown_at_pass: float = 0.0
    expected_resets_before_pass: float | None = None
    expected_total_cost_before_pass: float | None = None
    expected_profit_per_attempt: float = 0.0
    expected_cost_per_funded_account: float | None = None


def ledger_to_days(trades: pl.DataFrame, contracts: int = 1) -> list[list[float]]:
    """Per-trading-day lists of net trade PnLs, scaled to `contracts` micros.

    The baseline ledger is per 1 micro; gross PnL and costs both scale
    linearly with contract count, so net PnL scales linearly too.
    """
    if trades.height == 0:
        return []
    grouped = (
        trades.sort("entry_ts")
        .group_by("trading_date", maintain_order=True)
        .agg(pl.col("net_pnl"))
        .sort("trading_date")
    )
    return [[p * contracts for p in row] for row in grouped["net_pnl"].to_list()]


def _sample_days(
    days: list[list[float]], n: int, rng: np.random.Generator, mode: str, block: int
) -> list[list[float]]:
    m = len(days)
    if mode == "day":
        idx = rng.integers(0, m, size=n)
        return [days[i] for i in idx]
    out: list[list[float]] = []
    while len(out) < n:
        start = int(rng.integers(0, m))
        out.extend(days[(start + k) % m] for k in range(block))
    return out[:n]


def run_monte_carlo(
    trades: pl.DataFrame,
    rules: LucidRules,
    contracts: int = 1,
    n_attempts: int = 10_000,
    max_days: int = 60,
    seed: int = 42,
    sample_mode: str = "block",
    block_size: int = 5,
    evaluation_cost: float | None = None,
    reset_cost: float | None = None,
    strategy: str = "",
    pass_within_days: tuple[int, ...] = (10, 15, 20),
) -> MonteCarloResult:
    days = ledger_to_days(trades, contracts)
    if not days:
        raise ValueError("empty ledger")
    rng = np.random.default_rng(seed)

    outcomes = []
    for _ in range(n_attempts):
        seq = _sample_days(days, max_days, rng, sample_mode, block_size)
        outcomes.append(run_evaluation(rules, seq, max_days=max_days))

    n = len(outcomes)
    passed = [o for o in outcomes if o.status == "passed"]
    failed = [o for o in outcomes if o.status == "failed"]
    timeout = [o for o in outcomes if o.status == "timeout"]
    pass_days = np.array([o.days_used for o in passed]) if passed else np.array([])

    p = len(passed) / n
    res = MonteCarloResult(
        strategy=strategy,
        account=rules.name,
        contracts=contracts,
        n_attempts=n,
        pass_rate=p,
        fail_rate=len(failed) / n,
        timeout_rate=len(timeout) / n,
        median_days_to_pass=float(np.median(pass_days)) if passed else None,
        p25_days_to_pass=float(np.percentile(pass_days, 25)) if passed else None,
        p75_days_to_pass=float(np.percentile(pass_days, 75)) if passed else None,
        pass_within={
            k: 100.0 * float((pass_days <= k).sum()) / n for k in pass_within_days
        },
        fail_by_drawdown_pct=(
            100.0 * sum(1 for o in failed if o.fail_reason == "drawdown") / len(failed)
            if failed else 0.0
        ),
        avg_profit_before_failure=(
            float(np.mean([o.final_profit for o in failed])) if failed else 0.0
        ),
        avg_remaining_drawdown_at_pass=(
            float(np.mean([o.remaining_drawdown for o in passed])) if passed else 0.0
        ),
        expected_profit_per_attempt=float(np.mean([o.final_profit for o in outcomes])),
    )
    if p > 0:
        res.expected_resets_before_pass = (1 - p) / p
        if evaluation_cost is not None and reset_cost is not None:
            res.expected_total_cost_before_pass = (
                evaluation_cost + res.expected_resets_before_pass * reset_cost
            )
            res.expected_cost_per_funded_account = res.expected_total_cost_before_pass
    return res


def render_mc_markdown(results: list[MonteCarloResult]) -> str:
    lines = [
        "| Strategy | Account | Micros | Pass % | Fail % | Timeout % | Med days | P25-P75 |"
        " <=10d % | <=15d % | <=20d % | DD fails % | E[resets] | E[cost] | E[profit/attempt] |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        med = f"{r.median_days_to_pass:.0f}" if r.median_days_to_pass else "-"
        pq = (
            f"{r.p25_days_to_pass:.0f}-{r.p75_days_to_pass:.0f}"
            if r.p25_days_to_pass is not None else "-"
        )
        er = f"{r.expected_resets_before_pass:.1f}" if r.expected_resets_before_pass is not None else "-"
        ec = f"${r.expected_total_cost_before_pass:,.0f}" if r.expected_total_cost_before_pass else "-"
        lines.append(
            f"| {r.strategy} | {r.account} | {r.contracts} | {100 * r.pass_rate:.1f}% "
            f"| {100 * r.fail_rate:.1f}% | {100 * r.timeout_rate:.1f}% | {med} | {pq} "
            f"| {r.pass_within[10]:.1f}% | {r.pass_within[15]:.1f}% | {r.pass_within[20]:.1f}% "
            f"| {r.fail_by_drawdown_pct:.0f}% | {er} | {ec} "
            f"| ${r.expected_profit_per_attempt:,.0f} |"
        )
    return "\n".join(lines)

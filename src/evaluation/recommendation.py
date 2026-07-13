"""Phase 6 Monte Carlo with sizing policies and account comparison."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import polars as pl

from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import ledger_to_days
from src.evaluation.sizing import (
    ConsistencyCapSizing,
    CushionSkipSizing,
    DownshiftSizing,
    FixedSizing,
    PostLockSizing,
    SizingPolicy,
    UpshiftSizing,
    run_evaluation_sized,
)

log = logging.getLogger(__name__)


@dataclass
class PolicyMonteCarloResult:
    policy: str
    account: str
    n_attempts: int
    pass_rate: float
    fail_rate: float
    timeout_rate: float
    median_days_to_pass: float | None
    pass_within: dict[int, float] = field(default_factory=dict)
    expected_resets_before_pass: float | None = None
    expected_total_cost_before_pass: float | None = None
    expected_profit_per_attempt: float = 0.0
    avg_remaining_drawdown_at_pass: float = 0.0


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


def run_policy_monte_carlo(
    trades: pl.DataFrame,
    rules: LucidRules,
    policy: SizingPolicy,
    n_attempts: int = 10_000,
    max_days: int = 60,
    seed: int = 42,
    sample_mode: str = "block",
    block_size: int = 5,
    evaluation_cost: float | None = None,
    reset_cost: float | None = None,
) -> PolicyMonteCarloResult:
    days = ledger_to_days(trades, contracts=1)
    if not days:
        raise ValueError("empty ledger")
    rng = np.random.default_rng(seed)
    outcomes = []
    for _ in range(n_attempts):
        seq = _sample_days(days, max_days, rng, sample_mode, block_size)
        outcomes.append(run_evaluation_sized(rules, seq, policy, max_days=max_days))

    n = len(outcomes)
    passed = [o for o in outcomes if o.status == "passed"]
    failed = [o for o in outcomes if o.status == "failed"]
    timeout = [o for o in outcomes if o.status == "timeout"]
    pass_days = np.array([o.days_used for o in passed]) if passed else np.array([])
    p = len(passed) / n

    res = PolicyMonteCarloResult(
        policy=policy.name,
        account=rules.name,
        n_attempts=n,
        pass_rate=p,
        fail_rate=len(failed) / n,
        timeout_rate=len(timeout) / n,
        median_days_to_pass=float(np.median(pass_days)) if passed else None,
        pass_within={
            k: 100.0 * float((pass_days <= k).sum()) / n for k in (10, 15, 20, 30)
        },
        expected_profit_per_attempt=float(np.mean([o.final_profit for o in outcomes])),
        avg_remaining_drawdown_at_pass=(
            float(np.mean([o.remaining_drawdown for o in passed])) if passed else 0.0
        ),
    )
    if p > 0:
        res.expected_resets_before_pass = (1 - p) / p
        if evaluation_cost is not None and reset_cost is not None:
            res.expected_total_cost_before_pass = (
                evaluation_cost + res.expected_resets_before_pass * reset_cost
            )
    return res


def policies_from_config(cfg: dict[str, Any]) -> list[SizingPolicy]:
    out: list[SizingPolicy] = []
    for name, p in cfg.get("fixed_policies", {}).items():
        out.append(FixedSizing(name=name, contracts=int(p["contracts"])))
    for name, p in cfg.get("dynamic_policies", {}).items():
        out.append(
            DownshiftSizing(
                name=name,
                max_contracts=int(p["max_contracts"]),
                min_contracts=int(p["min_contracts"]),
                cushion_threshold=float(p["cushion_threshold"]),
            )
        )
    return out


def build_policy_grid(cfg: dict[str, Any]) -> list[SizingPolicy]:
    """Expand Phase 19 policy grid from YAML."""
    policies: list[SizingPolicy] = []
    grid = cfg.get("policy_grid") or {}

    if grid.get("include_baseline", True):
        policies.append(FixedSizing("fixed_1", 1))
        policies.append(FixedSizing("fixed_2", 2))

    for thresh in grid.get("upshift_threshold", []):
        policies.append(
            UpshiftSizing(
                name=f"upshift_{int(thresh)}",
                min_contracts=1,
                max_contracts=2,
                cushion_threshold=float(thresh),
            )
        )

    for thresh in grid.get("downshift_threshold", []):
        policies.append(
            DownshiftSizing(
                name=f"downshift_{int(thresh)}",
                min_contracts=1,
                max_contracts=2,
                cushion_threshold=float(thresh),
            )
        )

    for mx in grid.get("post_lock_max", []):
        policies.append(
            PostLockSizing(
                name=f"post_lock_{int(mx)}",
                min_contracts=1,
                max_contracts=int(mx),
            )
        )

    for floor in grid.get("cushion_skip_floor", []):
        policies.append(
            CushionSkipSizing(
                name=f"skip_cushion_{int(floor)}",
                base_contracts=1,
                min_cushion=float(floor),
            )
        )

    for floor in grid.get("cushion_skip_upshift_floor", []):
        policies.append(
            CushionSkipSizing(
                name=f"skip_then_1_{int(floor)}",
                base_contracts=1,
                min_cushion=float(floor),
            )
        )

    # Upshift + consistency cap combos (small set)
    for up in grid.get("upshift_with_consistency_cap", []):
        base = UpshiftSizing(
            name=f"upshift_{int(up['threshold'])}",
            min_contracts=1,
            max_contracts=2,
            cushion_threshold=float(up["threshold"]),
        )
        policies.append(
            ConsistencyCapSizing(
                name=f"upshift_{int(up['threshold'])}_cap",
                base=base,
                profit_threshold=float(up.get("profit_threshold", 800)),
                consistency_pct=float(up.get("consistency_pct", 50)),
            )
        )

    # Dedupe by name
    seen: set[str] = set()
    uniq: list[SizingPolicy] = []
    for p in policies:
        if p.name not in seen:
            seen.add(p.name)
            uniq.append(p)
    return uniq


def render_policy_table(results: list[PolicyMonteCarloResult]) -> str:
    lines = [
        "| Policy | Account | Pass % | Fail % | Med days | <=15d % | <=20d % | E[resets] | E[cost] | E[profit/attempt] | Cushion@pass |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        med = f"{r.median_days_to_pass:.0f}" if r.median_days_to_pass else "—"
        er = f"{r.expected_resets_before_pass:.1f}" if r.expected_resets_before_pass else "—"
        ec = f"${r.expected_total_cost_before_pass:,.0f}" if r.expected_total_cost_before_pass else "—"
        lines.append(
            f"| {r.policy} | {r.account} | {100 * r.pass_rate:.1f}% | {100 * r.fail_rate:.1f}% "
            f"| {med} | {r.pass_within.get(15, 0):.1f}% | {r.pass_within.get(20, 0):.1f}% "
            f"| {er} | {ec} | ${r.expected_profit_per_attempt:,.0f} "
            f"| ${r.avg_remaining_drawdown_at_pass:,.0f} |"
        )
    return "\n".join(lines)

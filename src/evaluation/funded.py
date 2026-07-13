"""Lucid Flex funded-phase simulation (post-eval)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.evaluation.lucid_rules import EvalAccount, LucidRules


@dataclass
class FundedRules:
    qualifying_day_min: float
    qualifying_days_required: int
    min_payout_request: float
    max_payout_pct: float
    max_payout_cap: float
    scaling_tiers: list[tuple[float | None, int]]  # (profit_upto, max_micros)

    @classmethod
    def from_lucid_yaml(cls, data: dict[str, Any]) -> "FundedRules":
        f = data["funded"]
        tiers = []
        for t in f["scaling_tiers"]:
            tiers.append((t.get("profit_upto"), int(t["max_micros"])))
        return cls(
            qualifying_day_min=float(f["qualifying_day_min_profit"]),
            qualifying_days_required=int(f["qualifying_days_required"]),
            min_payout_request=float(f["min_payout_request"]),
            max_payout_pct=float(f["max_payout_pct"]),
            max_payout_cap=float(f["max_payout_cap"]),
            scaling_tiers=tiers,
        )

    def max_micros_for_profit(self, profit: float) -> int:
        for upto, mx in self.scaling_tiers:
            if upto is None or profit <= upto:
                return mx
        return self.scaling_tiers[-1][1]


def replay_funded_to_payout(
    rules: LucidRules,
    funded: FundedRules,
    day_pnls_per_micro: list[list[float]],
    contracts: int = 1,
    max_sessions: int = 120,
) -> bool:
    """Return True if first payout-eligible state reached without breach."""
    acct = EvalAccount(rules)
    qual = 0
    cycle_start = acct.balance

    for day in day_pnls_per_micro[:max_sessions]:
        k = min(contracts, rules.max_contracts_micro)
        dp = sum(p * k for p in day)
        if dp == 0:
            continue
        for pnl in day:
            if acct.status != "active":
                return False
            acct.on_trade(pnl * k)
            if acct.status == "failed":
                return False
        acct.on_session_close()
        if acct.status == "passed":
            # Eval pass check fires again once profit >= target; funded continues.
            acct.status = "active"
        if acct.status == "failed":
            return False
        if dp >= funded.qualifying_day_min:
            qual += 1
        profit = acct.balance - rules.starting_balance
        cycle_net = acct.balance - cycle_start
        if qual >= funded.qualifying_days_required and cycle_net > 0:
            requestable = min(
                funded.max_payout_cap,
                profit * funded.max_payout_pct,
            )
            if requestable >= funded.min_payout_request:
                return True
    return False

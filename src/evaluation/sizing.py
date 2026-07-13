"""Position-sizing policies for Lucid evaluation Monte Carlo.

Policies operate on a per-1-micro trade ledger. Each trading day may use a
different contract count based on prior end-of-day account state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.evaluation.lucid_rules import EvalAccount, LucidRules
from src.evaluation.simulator import EvalOutcome


class SizingPolicy(Protocol):
    name: str

    def contracts_for_day(self, acct: EvalAccount) -> int:
        """Contracts to use for the upcoming session (based on prior EOD state)."""


@dataclass(frozen=True)
class FixedSizing:
    name: str
    contracts: int

    def contracts_for_day(self, acct: EvalAccount) -> int:
        return self.contracts


@dataclass(frozen=True)
class DownshiftSizing:
    """Trade larger when cushion is comfortable; shrink near the MLL floor."""

    name: str
    max_contracts: int
    min_contracts: int
    cushion_threshold: float

    def contracts_for_day(self, acct: EvalAccount) -> int:
        cushion = acct.balance - acct.mll
        if cushion >= self.cushion_threshold:
            return self.max_contracts
        return self.min_contracts


@dataclass(frozen=True)
class UpshiftSizing:
    """1 micro base; upshift when EOD cushion is comfortable."""

    name: str
    max_contracts: int
    min_contracts: int
    cushion_threshold: float

    def contracts_for_day(self, acct: EvalAccount) -> int:
        cushion = acct.balance - acct.mll
        if cushion >= self.cushion_threshold:
            return self.max_contracts
        return self.min_contracts


@dataclass(frozen=True)
class PostLockSizing:
    """Aggressive size only after the MLL has locked at starting balance."""

    name: str
    max_contracts: int
    min_contracts: int

    def contracts_for_day(self, acct: EvalAccount) -> int:
        if acct.mll_locked:
            return self.max_contracts
        return self.min_contracts


@dataclass(frozen=True)
class CushionSkipSizing:
    """Skip the session (0 contracts) when cushion is below a floor."""

    name: str
    base_contracts: int
    min_cushion: float

    def contracts_for_day(self, acct: EvalAccount) -> int:
        if acct.balance - acct.mll < self.min_cushion:
            return 0
        return self.base_contracts


@dataclass(frozen=True)
class ConsistencyCapSizing:
    """Cap size at 1 micro when a large day would threaten the 50% rule near target."""

    name: str
    base: SizingPolicy
    profit_threshold: float
    consistency_pct: float

    def contracts_for_day(self, acct: EvalAccount) -> int:
        k = self.base.contracts_for_day(acct)
        if k <= 1:
            return k
        profit = acct.profit
        if profit < self.profit_threshold or not acct.day_pnls:
            return k
        largest = max(acct.day_pnls)
        cap = (self.consistency_pct / 100.0) * profit
        if largest >= cap * 0.85:
            return 1
        return k


def run_evaluation_sized(
    rules: LucidRules,
    day_pnls_per_micro: list[list[float]],
    policy: SizingPolicy,
    max_days: int | None = None,
) -> EvalOutcome:
    """Replay daily trade lists with a sizing policy."""
    acct = EvalAccount(rules)
    used = 0
    for day in day_pnls_per_micro:
        if max_days is not None and used >= max_days:
            break
        if acct.status != "active":
            break
        k = min(policy.contracts_for_day(acct), rules.max_contracts_micro)
        used += 1
        if k <= 0:
            continue
        for pnl in day:
            acct.on_trade(pnl * k)
            if acct.status == "failed":
                break
        acct.on_session_close()
        if acct.status == "passed":
            return EvalOutcome(
                status="passed",
                days_used=used,
                fail_reason=None,
                final_profit=acct.profit,
                remaining_drawdown=acct.balance - acct.mll,
            )
    status = acct.status if acct.status in ("passed", "failed") else "timeout"
    return EvalOutcome(
        status=status,
        days_used=used,
        fail_reason=acct.fail_reason,
        final_profit=acct.profit,
        remaining_drawdown=acct.balance - acct.mll,
    )

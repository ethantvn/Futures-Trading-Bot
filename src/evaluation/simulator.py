"""Replay trading days through the Lucid rule engine.

A "day" is an ordered list of per-trade net PnLs (dollars, already scaled to
the contract count under test). Because Flex checks drawdown only at EOD,
daily granularity is exact for eod_trailing; trade granularity matters only
for the intraday_trailing stress mode.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.lucid_rules import EvalAccount, LucidRules


@dataclass
class EvalOutcome:
    status: str                 # passed | failed | timeout
    days_used: int
    fail_reason: str | None
    final_profit: float
    remaining_drawdown: float   # balance - MLL at the end


def run_evaluation(
    rules: LucidRules,
    days: list[list[float]],
    max_days: int | None = None,
) -> EvalOutcome:
    acct = EvalAccount(rules)
    used = 0
    for day in days:
        if max_days is not None and used >= max_days:
            break
        used += 1
        for pnl in day:
            acct.on_trade(pnl)
            if acct.status == "failed":
                break
        acct.on_session_close()
        if acct.status in ("passed", "failed"):
            return EvalOutcome(
                status=acct.status,
                days_used=used,
                fail_reason=acct.fail_reason,
                final_profit=acct.profit,
                remaining_drawdown=acct.balance - acct.mll,
            )
    return EvalOutcome(
        status="timeout",
        days_used=used,
        fail_reason=None,
        final_profit=acct.profit,
        remaining_drawdown=acct.balance - acct.mll,
    )

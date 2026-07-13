"""Lucid Flex evaluation account state machine. Entirely config-driven.

Rule sources (checked 2026-07-06; official help center unreachable, values
cross-confirmed by the user's dashboard screenshot and 4 independent sources):
- Max Loss Limit (MLL) starts at starting_balance - max_drawdown, trails the
  highest END-OF-DAY closing balance, and locks permanently once it reaches
  starting_balance (+ optional lock_buffer).
- Breach is checked at session close only for eod_trailing; the optional
  intraday_trailing mode (checked after every trade) is included for
  stress-testing the assumption.
- No daily loss limit on Flex (config supports one for other products).
- Pass requires: total profit >= profit_target AND largest single-day profit
  <= consistency_rule_pct% of total profit AND >= min_trading_days traded.
  Checked at end of day.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class LucidRules:
    name: str
    starting_balance: float
    profit_target: float
    max_drawdown: float
    drawdown_method: str            # "eod_trailing" | "intraday_trailing"
    drawdown_locks_at_start_balance: bool
    lock_buffer: float
    daily_loss_limit: float | None
    consistency_rule_pct: float
    min_trading_days: int
    max_contracts_micro: int

    @classmethod
    def from_yaml(cls, path: str | Path) -> "LucidRules":
        a = yaml.safe_load(Path(path).read_text())["account"]
        return cls(
            name=a["name"],
            starting_balance=float(a["starting_balance"]),
            profit_target=float(a["profit_target"]),
            max_drawdown=float(a["max_drawdown"]),
            drawdown_method=a["drawdown_method"],
            drawdown_locks_at_start_balance=bool(a["drawdown_locks_at_start_balance"]),
            lock_buffer=float(a.get("lock_buffer", 0.0)),
            daily_loss_limit=a.get("daily_loss_limit"),
            consistency_rule_pct=float(a["consistency_rule_pct"]),
            min_trading_days=int(a["min_trading_days"]),
            max_contracts_micro=int(a["max_contracts_micro"]),
        )


@dataclass
class EvalAccount:
    """Evaluation account replayed one trade / one session at a time."""

    rules: LucidRules
    balance: float = field(init=False)
    mll: float = field(init=False)
    mll_locked: bool = field(init=False, default=False)
    trading_days: int = field(init=False, default=0)
    day_pnls: list[float] = field(init=False, default_factory=list)
    status: str = field(init=False, default="active")  # active|passed|failed
    fail_reason: str | None = field(init=False, default=None)
    _day_pnl: float = field(init=False, default=0.0)
    _day_open: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self.balance = self.rules.starting_balance
        self.mll = self.rules.starting_balance - self.rules.max_drawdown

    # -- intra-day events -------------------------------------------------
    def on_trade(self, net_pnl: float) -> None:
        assert self.status == "active"
        self.balance += net_pnl
        self._day_pnl += net_pnl
        self._day_open = True
        if self.rules.drawdown_method == "intraday_trailing" and self.balance <= self.mll:
            self._fail("drawdown")
            return
        dll = self.rules.daily_loss_limit
        if dll is not None and self._day_pnl <= -dll:
            self._fail("daily_loss_limit")

    # -- session close -----------------------------------------------------
    def on_session_close(self) -> None:
        """Apply EOD checks and trail the MLL. Call once per traded day."""
        if self.status != "active" or not self._day_open:
            return
        self.trading_days += 1
        self.day_pnls.append(self._day_pnl)
        self._day_pnl = 0.0
        self._day_open = False

        # 1) EOD breach check (balance AT close vs current floor)
        if self.balance <= self.mll:
            self._fail("drawdown")
            return

        # 2) trail the MLL on new EOD highs, with permanent lock
        if not self.mll_locked:
            candidate = self.balance - self.rules.max_drawdown
            lock_level = self.rules.starting_balance + self.rules.lock_buffer
            if self.rules.drawdown_locks_at_start_balance and candidate >= lock_level:
                self.mll = lock_level
                self.mll_locked = True
            elif candidate > self.mll:
                self.mll = candidate

        # 3) pass check
        profit = self.balance - self.rules.starting_balance
        if profit >= self.rules.profit_target and self.trading_days >= self.rules.min_trading_days:
            largest = max(self.day_pnls)
            if largest <= (self.rules.consistency_rule_pct / 100.0) * profit:
                self.status = "passed"

    def _fail(self, reason: str) -> None:
        self.status = "failed"
        self.fail_reason = reason

    @property
    def profit(self) -> float:
        return self.balance - self.rules.starting_balance

    def consistency_ratio(self) -> float | None:
        """largest day / total profit, None when profit <= 0."""
        if not self.day_pnls or self.profit <= 0:
            return None
        return max(self.day_pnls) / self.profit

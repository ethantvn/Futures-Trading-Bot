"""Phase 19 sizing policy tests."""
from __future__ import annotations

from datetime import date, datetime, timezone

import polars as pl

from src.evaluation.journey import journey_mc
from src.evaluation.lucid_rules import EvalAccount
from src.evaluation.recommendation import run_policy_monte_carlo
from src.evaluation.sizing import (
    CushionSkipSizing,
    FixedSizing,
    PostLockSizing,
    UpshiftSizing,
    run_evaluation_sized,
)
from tests.test_lucid_rules import RULES_25K

SCHEMA = {
    "trading_date": pl.Date,
    "entry_ts": pl.Datetime("ns", "UTC"),
    "exit_ts": pl.Datetime("ns", "UTC"),
    "net_pnl": pl.Float64,
    "gross_pnl": pl.Float64,
    "costs": pl.Float64,
}


def _ledger(daily: float, n: int = 80) -> pl.DataFrame:
    rows = []
    d0 = date(2024, 1, 2)
    for i in range(n):
        d = d0.replace(day=min(2 + (i % 25), 28))
        ts = datetime(d.year, d.month, d.day, 15, tzinfo=timezone.utc)
        rows.append({
            "trading_date": d, "entry_ts": ts, "exit_ts": ts,
            "net_pnl": daily, "gross_pnl": daily, "costs": 0.0,
        })
    return pl.DataFrame(rows, schema=SCHEMA)


def test_cushion_skip_returns_zero():
    p = CushionSkipSizing("skip", base_contracts=1, min_cushion=600)
    acct = EvalAccount(RULES_25K)
    acct.on_trade(-450.0)
    acct.on_session_close()
    # balance 24550, mll 24000, cushion 550 < 600
    assert p.contracts_for_day(acct) == 0


def test_upshift_uses_max_when_cushion_high():
    p = UpshiftSizing("up", min_contracts=1, max_contracts=2, cushion_threshold=500)
    acct = EvalAccount(RULES_25K)
    assert p.contracts_for_day(acct) == 2


def test_post_lock_upsizes_when_locked():
    p = PostLockSizing("pl", min_contracts=1, max_contracts=3)
    acct = EvalAccount(RULES_25K)
    acct.mll_locked = True
    assert p.contracts_for_day(acct) == 3


def test_skip_day_does_not_trade():
    days = [[100.0], [100.0]]
    policy = CushionSkipSizing("skip", base_contracts=1, min_cushion=10_000)
    out = run_evaluation_sized(RULES_25K, days, policy)
    assert out.status == "timeout"


def test_policy_mc_and_journey_run():
    ledger = _ledger(75, 100)
    p = FixedSizing("fixed_1", 1)
    mc = run_policy_monte_carlo(ledger, RULES_25K, p, n_attempts=100, seed=1)
    j = journey_mc(ledger, RULES_25K, p, n=100, seed=1)
    assert 0 <= mc.pass_rate <= 1
    assert 0 <= j["pass_and_payout"] <= j["pass_rate"]

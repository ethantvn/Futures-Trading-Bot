from __future__ import annotations

from datetime import date, datetime, timezone

import numpy as np
import polars as pl
import pytest

from src.evaluation.lucid_rules import LucidRules
from src.evaluation.recommendation import run_policy_monte_carlo
from src.evaluation.sizing import DownshiftSizing, FixedSizing, run_evaluation_sized
from tests.test_lucid_rules import RULES_25K

SCHEMA = {
    "trading_date": pl.Date,
    "entry_ts": pl.Datetime("ns", "UTC"),
    "exit_ts": pl.Datetime("ns", "UTC"),
    "net_pnl": pl.Float64,
    "gross_pnl": pl.Float64,
    "costs": pl.Float64,
}


def _ledger(daily_pnl: float, n: int = 80) -> pl.DataFrame:
    rows = []
    d0 = date(2024, 1, 2)
    for i in range(n):
        d = d0.replace(day=min(2 + i, 28))
        ts = datetime(d.year, d.month, d.day, 15, tzinfo=timezone.utc)
        rows.append(
            {
                "trading_date": d, "entry_ts": ts, "exit_ts": ts,
                "net_pnl": daily_pnl, "gross_pnl": daily_pnl, "costs": 0.0,
            }
        )
    return pl.DataFrame(rows, schema=SCHEMA)


def test_fixed_2x_scales_pnl():
    days = [[100.0], [100.0], [100.0]]
    out1 = run_evaluation_sized(RULES_25K, days, FixedSizing("c1", 1))
    out2 = run_evaluation_sized(RULES_25K, days, FixedSizing("c2", 2))
    assert out2.final_profit == pytest.approx(2 * out1.final_profit)


def test_downshift_picks_contracts_from_cushion():
    policy = DownshiftSizing("ds", max_contracts=2, min_contracts=1, cushion_threshold=400)
    from src.evaluation.lucid_rules import EvalAccount

    acct = EvalAccount(RULES_25K)
    assert policy.contracts_for_day(acct) == 2  # cushion 1000 >= 400

    acct.on_trade(-300.0)
    acct.on_session_close()
    # balance 24700, mll still 24000, cushion 700
    assert policy.contracts_for_day(acct) == 2

    acct.on_trade(-350.0)
    acct.on_session_close()
    # balance 24350, mll trails to 24000? candidate 24350-1000=23350 < 24000, mll stays 24000
    # cushion 350 < 400 -> 1 micro
    assert policy.contracts_for_day(acct) == 1


def test_policy_mc_deterministic():
    ledger = _ledger(80, 100)
    p = FixedSizing("conservative", 1)
    a = run_policy_monte_carlo(ledger, RULES_25K, p, n_attempts=200, seed=9)
    b = run_policy_monte_carlo(ledger, RULES_25K, p, n_attempts=200, seed=9)
    assert a.pass_rate == b.pass_rate


def test_conservative_beats_moderate_on_high_variance():
    rng = np.random.default_rng(1)
    rows = []
    d0 = date(2023, 1, 3)
    for i in range(120):
        d = d0.replace(day=3 + (i % 25))
        ts = datetime(d.year, d.month, d.day, 15, tzinfo=timezone.utc)
        pnl = float(rng.normal(60, 200))
        rows.append(
            {
                "trading_date": d, "entry_ts": ts, "exit_ts": ts,
                "net_pnl": pnl, "gross_pnl": pnl, "costs": 0.0,
            }
        )
    ledger = pl.DataFrame(rows, schema=SCHEMA)
    c1 = run_policy_monte_carlo(ledger, RULES_25K, FixedSizing("c1", 1), n_attempts=400, seed=3)
    c2 = run_policy_monte_carlo(ledger, RULES_25K, FixedSizing("c2", 2), n_attempts=400, seed=3)
    assert c1.pass_rate >= c2.pass_rate

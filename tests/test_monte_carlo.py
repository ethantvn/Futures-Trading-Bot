from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import numpy as np
import polars as pl

from src.evaluation.monte_carlo import ledger_to_days, run_monte_carlo
from tests.test_lucid_rules import RULES_25K


def synthetic_ledger(daily_mean: float, daily_sd: float, n_days: int = 200, seed: int = 1) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    d0 = date(2024, 1, 1)
    for i in range(n_days):
        d = d0 + timedelta(days=i)
        for k in range(2):  # two trades per day
            pnl = rng.normal(daily_mean / 2, daily_sd / 2)
            ts = datetime(d.year, d.month, d.day, 15, k, tzinfo=timezone.utc)
            rows.append(
                {
                    "trading_date": d, "entry_ts": ts, "exit_ts": ts,
                    "net_pnl": pnl, "gross_pnl": pnl, "costs": 0.0,
                }
            )
    return pl.DataFrame(rows)


def test_ledger_to_days_scales_with_contracts():
    ledger = synthetic_ledger(100, 50, n_days=3)
    d1 = ledger_to_days(ledger, contracts=1)
    d3 = ledger_to_days(ledger, contracts=3)
    assert len(d1) == 3
    assert all(abs(a * 3 - b) < 1e-9 for day1, day3 in zip(d1, d3) for a, b in zip(day1, day3))


def test_deterministic_under_seed():
    ledger = synthetic_ledger(80, 150)
    a = run_monte_carlo(ledger, RULES_25K, n_attempts=300, seed=7)
    b = run_monte_carlo(ledger, RULES_25K, n_attempts=300, seed=7)
    assert a.pass_rate == b.pass_rate
    assert a.median_days_to_pass == b.median_days_to_pass


def test_profitable_strategy_mostly_passes():
    # +$150/day mean, low variance: should pass nearly always, rarely by drawdown
    ledger = synthetic_ledger(150, 60, seed=3)
    r = run_monte_carlo(ledger, RULES_25K, n_attempts=500, seed=11)
    assert r.pass_rate > 0.95
    assert r.median_days_to_pass is not None and r.median_days_to_pass <= 15


def test_losing_strategy_mostly_fails_by_drawdown():
    ledger = synthetic_ledger(-120, 100, seed=5)
    r = run_monte_carlo(ledger, RULES_25K, n_attempts=300, seed=13)
    assert r.fail_rate > 0.9
    assert r.fail_by_drawdown_pct > 95.0


def test_expected_costs():
    ledger = synthetic_ledger(150, 60, seed=3)
    r = run_monte_carlo(
        ledger, RULES_25K, n_attempts=400, seed=17,
        evaluation_cost=100.0, reset_cost=60.0,
    )
    assert r.expected_resets_before_pass is not None
    assert r.expected_total_cost_before_pass >= 100.0

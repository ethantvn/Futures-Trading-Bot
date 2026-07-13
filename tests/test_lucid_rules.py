from __future__ import annotations

import pytest

from src.evaluation.lucid_rules import EvalAccount, LucidRules
from src.evaluation.simulator import run_evaluation

RULES_25K = LucidRules(
    name="LucidFlex 25K",
    starting_balance=25_000.0,
    profit_target=1_250.0,
    max_drawdown=1_000.0,
    drawdown_method="eod_trailing",
    drawdown_locks_at_start_balance=True,
    lock_buffer=0.0,
    daily_loss_limit=None,
    consistency_rule_pct=50.0,
    min_trading_days=2,
    max_contracts_micro=20,
)


def replay(days: list[list[float]], rules: LucidRules = RULES_25K) -> EvalAccount:
    acct = EvalAccount(rules)
    for day in days:
        for pnl in day:
            if acct.status != "active":
                return acct
            acct.on_trade(pnl)
        acct.on_session_close()
        if acct.status != "active":
            return acct
    return acct


class TestTrailingDrawdown:
    def test_mll_starts_one_thousand_below(self):
        acct = EvalAccount(RULES_25K)
        assert acct.mll == 24_000.0

    def test_mll_trails_highest_eod_close(self):
        acct = replay([[300.0], [-100.0]])
        # day1 close 25300 -> MLL 24300; day2 close 25200 (no new high) -> MLL stays
        assert acct.mll == 24_300.0
        assert acct.status == "active"

    def test_intraday_dip_below_mll_survives_in_eod_mode(self):
        # dip to 23900 intraday, recover to close at 24100 > MLL 24000
        acct = replay([[-1_100.0, +1_200.0, -900.0, +900.0]])
        assert acct.status == "active"

    def test_eod_close_at_or_below_mll_fails(self):
        acct = replay([[-1_000.0]])   # close 24000 == MLL
        assert acct.status == "failed" and acct.fail_reason == "drawdown"

    def test_intraday_mode_fails_on_the_dip(self):
        rules = LucidRules(**{**RULES_25K.__dict__, "drawdown_method": "intraday_trailing"})
        acct = replay([[-1_100.0, +1_200.0]], rules)
        assert acct.status == "failed" and acct.fail_reason == "drawdown"

    def test_mll_locks_at_starting_balance(self):
        # +600/day: closes 25600, 26200 -> candidate MLL 25200 > 25000 -> locks at 25000
        acct = replay([[600.0], [600.0], [-100.0]])
        assert acct.mll == 25_000.0 and acct.mll_locked
        # after lock, further highs never move it
        acct.on_trade(2_000.0)
        acct.on_session_close()
        assert acct.mll == 25_000.0


class TestPassRules:
    def test_pass_requires_min_trading_days(self):
        # $1,300 on day one satisfies target but not 2-day minimum
        acct = replay([[1_300.0]])
        assert acct.status == "active"

    def test_consistency_blocks_single_day_pass(self):
        # day1 +$1,200, day2 +$100: total 1300 >= 1250 but largest day 1200
        # is 92% of profit -> keep trading
        acct = replay([[1_200.0], [100.0]])
        assert acct.status == "active"
        assert acct.consistency_ratio() == pytest.approx(1_200 / 1_300)

    def test_pass_with_two_balanced_days(self):
        acct = replay([[650.0], [650.0]])  # 1300 total, largest 650 = 50% exactly
        assert acct.status == "passed"

    def test_pass_after_grinding_consistency_down(self):
        # big day then small days until ratio <= 50%
        acct = replay([[1_200.0], [400.0], [400.0], [500.0]])
        # total 2500, largest 1200 = 48% -> passes on day 4
        assert acct.status == "passed"
        assert acct.trading_days == 4


class TestSimulator:
    def test_outcome_fields(self):
        out = run_evaluation(RULES_25K, [[650.0], [650.0]])
        assert out.status == "passed"
        assert out.days_used == 2
        assert out.final_profit == 1_300.0

    def test_timeout(self):
        out = run_evaluation(RULES_25K, [[0.01]] * 5, max_days=5)
        assert out.status == "timeout"
        assert out.days_used == 5

    def test_drawdown_failure_day_index(self):
        out = run_evaluation(RULES_25K, [[100.0], [-1_200.0]])
        assert out.status == "failed"
        assert out.fail_reason == "drawdown"
        assert out.days_used == 2

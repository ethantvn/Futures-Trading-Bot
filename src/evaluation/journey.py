"""Eval pass → first funded payout Monte Carlo (with optional sizing policy)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import yaml

from src.evaluation.funded import FundedRules, replay_funded_to_payout
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.monte_carlo import _sample_days, ledger_to_days
from src.evaluation.sizing import FixedSizing, SizingPolicy, run_evaluation_sized


def _load_funded_rules(_rules: LucidRules) -> FundedRules:
    data = yaml.safe_load(Path("config/lucid_25k.yaml").read_text())
    return FundedRules.from_lucid_yaml(data)


def journey_mc(
    trades: pl.DataFrame,
    rules: LucidRules,
    policy: SizingPolicy | None = None,
    n: int = 10_000,
    max_days: int | None = 60,
    seed: int = 42,
    sample_mode: str = "block",
    block_size: int = 5,
    funded_contracts: int = 1,
    eval_seq_len: int = 365,
    funded_rules: FundedRules | None = None,
) -> dict[str, float]:
    """End-to-end: pass eval then reach first payout-eligible funded state.

    Eval: Lucid Flex has no time limit — set max_days=None to run until
    pass/fail within eval_seq_len sampled days.
    Funded: Flex has no consistency rule; payout needs 5× $100+ days and
    net-positive cycle with requestable amount >= $500 (25K tier).
    """
    if policy is None:
        policy = FixedSizing("fixed_1", 1)
    if funded_rules is None:
        funded_rules = _load_funded_rules(rules)
    days = ledger_to_days(trades, contracts=1)
    if not days:
        return {"pass_rate": 0.0, "pass_and_payout": 0.0}

    rng = np.random.default_rng(seed)
    pass_n = payout_n = 0
    seq_len = eval_seq_len if max_days is None else max(eval_seq_len, max_days + 120)

    for _ in range(n):
        seq = _sample_days(days, seq_len, rng, sample_mode, block_size)
        outcome = run_evaluation_sized(rules, seq, policy, max_days=max_days)
        if outcome.status == "passed":
            pass_n += 1
            rest = seq[outcome.days_used :]
            if replay_funded_to_payout(
                rules, funded_rules, rest, contracts=funded_contracts
            ):
                payout_n += 1

    return {"pass_rate": pass_n / n, "pass_and_payout": payout_n / n}

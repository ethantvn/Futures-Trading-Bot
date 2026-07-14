"""Phase 20 — Joint multi-account Monte Carlo: ORB-W (acct 1) + NR7 ORB (acct 2).

Both accounts are replayed on the SAME sampled calendar-day sequence so the
natural co-movement of two long-only equity-index breakout systems is
preserved (unlike a naive independent-Bernoulli P(>=1 pass) estimate).

Also runs a sequential single-account (ORB-W only, with resets on failure)
baseline over the same cumulative day budget, for a fair economics comparison.

Outputs: data/reports/phase20_joint_mc.md
"""
from __future__ import annotations

import numpy as np
import polars as pl

from src.evaluation.lucid_rules import EvalAccount, LucidRules
from src.evaluation.monte_carlo import run_monte_carlo

RULES_PATH = "config/lucid_25k.yaml"
DAY_BUDGET = 250
N_ATTEMPTS = 10_000
BLOCK = 5
SEED = 42
EVAL_COST = 70.0
RESET_COST = 60.0


def load_ledger(path: str) -> pl.DataFrame:
    return pl.read_parquet(path).filter(pl.col("trading_date").dt.weekday() != 1)


def daily_pnl_series(trades: pl.DataFrame, calendar: pl.DataFrame) -> pl.DataFrame:
    per_day = (
        trades.group_by("trading_date")
        .agg(pl.col("net_pnl").sum().alias("day_pnl"), pl.col("net_pnl").alias("trade_pnls"))
    )
    return (
        calendar.join(per_day, on="trading_date", how="left")
        .with_columns(
            pl.col("day_pnl").fill_null(0.0),
            pl.col("trade_pnls").fill_null([]),
        )
        .sort("trading_date")
    )


def build_calendar(a: pl.DataFrame, b: pl.DataFrame) -> pl.DataFrame:
    bars = pl.read_parquet("data/processed/continuous_5m.parquet")
    start = min(a["trading_date"].min(), b["trading_date"].min())
    end = max(a["trading_date"].max(), b["trading_date"].max())
    cal = (
        bars.filter(
            (pl.col("trading_date") >= start)
            & (pl.col("trading_date") <= end)
            & (pl.col("trading_date").dt.weekday() != 1)
        )
        .select("trading_date")
        .unique()
        .sort("trading_date")
    )
    return cal


def block_bootstrap_indices(m: int, n_days: int, rng: np.random.Generator, block: int) -> list[int]:
    out: list[int] = []
    while len(out) < n_days:
        start = int(rng.integers(0, m))
        out.extend((start + k) % m for k in range(block))
    return out[:n_days]


def run_paired_account(rules: LucidRules, pnl_lists: list[list[float]]) -> tuple[str, int, float]:
    """Replay one account's per-day trade PnL list. Returns (status, days_used, final_profit)."""
    acct = EvalAccount(rules)
    used = 0
    for day in pnl_lists:
        used += 1
        for pnl in day:
            acct.on_trade(pnl)
            if acct.status == "failed":
                break
        acct.on_session_close()
        if acct.status in ("passed", "failed"):
            return acct.status, used, acct.profit
    return "timeout", used, acct.profit


def main() -> None:
    rules = LucidRules.from_yaml(RULES_PATH)
    a = load_ledger("data/processed/trades_phase9_orb_longonly_wf_oos.parquet")
    b = load_ledger("data/processed/trades_phase7_nr7_orb_wf_oos.parquet")
    cal = build_calendar(a, b)

    da = daily_pnl_series(a, cal)
    db = daily_pnl_series(b, cal)
    assert da.height == db.height == cal.height

    corr_all = float(np.corrcoef(da["day_pnl"].to_numpy(), db["day_pnl"].to_numpy())[0, 1])
    both_active = (da["day_pnl"].to_numpy() != 0) & (db["day_pnl"].to_numpy() != 0)
    corr_active = float(
        np.corrcoef(da["day_pnl"].to_numpy()[both_active], db["day_pnl"].to_numpy()[both_active])[0, 1]
    ) if both_active.sum() > 5 else float("nan")

    pnl_a = da["trade_pnls"].to_list()
    pnl_b = db["trade_pnls"].to_list()
    m = len(pnl_a)

    rng = np.random.default_rng(SEED)
    outcomes = []
    for _ in range(N_ATTEMPTS):
        idx = block_bootstrap_indices(m, DAY_BUDGET, rng, BLOCK)
        seq_a = [pnl_a[i] for i in idx]
        seq_b = [pnl_b[i] for i in idx]
        sa, da_days, pa = run_paired_account(rules, seq_a)
        sb, db_days, pb = run_paired_account(rules, seq_b)
        outcomes.append((sa, da_days, pa, sb, db_days, pb))

    n = len(outcomes)
    a_pass = sum(1 for o in outcomes if o[0] == "passed")
    b_pass = sum(1 for o in outcomes if o[3] == "passed")
    both_pass = sum(1 for o in outcomes if o[0] == "passed" and o[3] == "passed")
    at_least_one = sum(1 for o in outcomes if o[0] == "passed" or o[3] == "passed")
    naive_both = (a_pass / n) * (b_pass / n)
    naive_at_least_one = 1 - (1 - a_pass / n) * (1 - b_pass / n)

    time_to_first = []
    for sa, dda, pa, sb, ddb, pb in outcomes:
        cands = []
        if sa == "passed":
            cands.append(dda)
        if sb == "passed":
            cands.append(ddb)
        if cands:
            time_to_first.append(min(cands))

    # Sequential single-account (ORB-W only) baseline over the SAME cumulative day budget,
    # restarting (paying reset cost) on failure, using independently-sampled continuations.
    rng2 = np.random.default_rng(SEED + 1)
    seq_outcomes = []
    for _ in range(N_ATTEMPTS):
        days_left = DAY_BUDGET
        passed = False
        resets = 0
        while days_left > 0:
            take = min(days_left, DAY_BUDGET)  # each restart gets a fresh full block-bootstrap draw
            idx = block_bootstrap_indices(m, take, rng2, BLOCK)
            seq = [pnl_a[i] for i in idx]
            status, used, profit = run_paired_account(rules, seq)
            days_left -= used
            if status == "passed":
                passed = True
                break
            if status == "failed":
                resets += 1
                continue
            break  # timeout: budget exhausted without a decision
        seq_outcomes.append((passed, resets))
    seq_pass_rate = sum(1 for p, _ in seq_outcomes if p) / len(seq_outcomes)
    seq_avg_resets = float(np.mean([r for _, r in seq_outcomes]))
    seq_cost = EVAL_COST + seq_avg_resets * RESET_COST

    joint_cost_at_least_one = 2 * EVAL_COST  # both fees paid upfront, no restarts modeled in joint scenario

    lines = [
        "# Phase 20 — Joint Multi-Account Monte Carlo (ORB-W + NR7 ORB)",
        "",
        f"Day budget: {DAY_BUDGET} calendar trading days/attempt · {N_ATTEMPTS:,} MC attempts, "
        f"block bootstrap (block={BLOCK}), seed={SEED}. Both accounts skip-Monday.",
        "",
        "## Correlation",
        "",
        f"- Day-level net-PnL correlation (full calendar, {cal.height} trading days, "
        f"0-fill on no-trade days): **{corr_all:.3f}**",
        f"- Correlation on days BOTH strategies traded ({int(both_active.sum())} days): **{corr_active:.3f}**",
        "",
        "## Marginal pass rates (within joint MC's paired draws)",
        "",
        f"| Account | Pass % |",
        f"| --- | --- |",
        f"| ORB-W (acct 1) | {100*a_pass/n:.1f}% |",
        f"| NR7 ORB (acct 2) | {100*b_pass/n:.1f}% |",
        "",
        "## Joint outcome (correlated draws) vs naive independent assumption",
        "",
        "| Metric | Correlated (actual) | Naive independent |",
        "| --- | --- | --- |",
        f"| P(both pass) | {100*both_pass/n:.1f}% | {100*naive_both:.1f}% |",
        f"| P(at least one pass) | {100*at_least_one/n:.1f}% | {100*naive_at_least_one:.1f}% |",
        "",
        f"Median days to FIRST funded account (either): "
        f"{np.median(time_to_first):.0f}" if time_to_first else "n/a",
        "",
        "## Sequential single-account baseline (ORB-W only, restarts on failure)",
        "",
        f"Same {DAY_BUDGET}-day cumulative budget, restart with fresh reset-cost attempt on failure:",
        "",
        f"- P(at least one pass within budget): **{100*seq_pass_rate:.1f}%**",
        f"- E[resets] before pass/budget exhaustion: {seq_avg_resets:.2f}",
        f"- E[cost] (eval + resets): ${seq_cost:,.0f}",
        "",
        "## Parallel two-account cost (single attempt each, no restarts modeled)",
        "",
        f"- Upfront cost: ${joint_cost_at_least_one:,.0f} (2 × ${EVAL_COST:.0f} eval fee)",
        f"- P(at least one funded): {100*at_least_one/n:.1f}%",
        "",
        "## Verdict",
        "",
    ]

    gap = at_least_one / n - seq_pass_rate
    if corr_active > 0.5 and gap < 0.02:
        verdict = (
            "Correlation is high enough and the parallel P(>=1 funded) is within ~2pts of the "
            "sequential-restart baseline -> parallel accounts mostly pay extra eval fees for "
            "correlated risk. **Prefer sequential restarts** unless a genuinely decorrelated "
            "second bot exists."
        )
    else:
        verdict = (
            "Parallel two-account P(>=1 funded) clears the sequential-restart baseline by "
            f"{100*gap:.1f}pts at {'low' if corr_active < 0.5 else 'moderate'} correlation "
            f"({corr_active:.2f} on shared trading days) -> **parallel accounts are worth the "
            "extra eval fee** for faster time-to-first-funded, income diversification."
        )
    lines.append(verdict)

    out = "\n".join(lines)
    with open("data/reports/phase20_joint_mc.md", "w") as f:
        f.write(out + "\n")
    print(out)


if __name__ == "__main__":
    main()

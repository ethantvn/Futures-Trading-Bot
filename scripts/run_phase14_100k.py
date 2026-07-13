"""Phase 14: Lucid Flex 100K tier study — MNQ ORB-W sizing + gold re-check.

Usage:
  .venv/bin/python scripts/run_phase14_100k.py

No strategy re-optimization: replays FROZEN ledgers through tier MC.
  Part A: MNQ Phase 9 orb_longonly (+skipMon) — 25K/50K/100K contract sweeps,
          pass-within-N-days, E[resets/cost] (discounted fees), journey MC
          (funded-phase structure mirrored from 25K — VERIFY), 2026 holdout
          at the recommended 100K size.
  Part B: GC sizing vs $3,000 MLL + best frozen GC ledgers @ 1 contract;
          MGC comex_orb_deep contract sweep with wall-clock + holdout guards.

Writes data/reports/phase14_100k_leaderboard.md.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import polars as pl
import yaml

from scripts.run_phase7 import skip_monday
from src.evaluation.lucid_rules import EvalAccount, LucidRules
from src.evaluation.monte_carlo import _sample_days, ledger_to_days, run_monte_carlo
from src.logging_setup import setup_logging
from src.strategies.indicators import ADJ

log = logging.getLogger("run_phase14")

N_ATTEMPTS = 10_000
MAX_DAYS = 60
SEED = 42
PASS_WITHIN = (10, 15, 20, 40)

TIERS = ("lucid_25k", "lucid_50k", "lucid_100k")


def _tier(acct: str) -> tuple[LucidRules, dict]:
    y = yaml.safe_load((Path("config") / f"{acct}.yaml").read_text())
    return LucidRules.from_yaml(Path("config") / f"{acct}.yaml"), y["costs"]


def _eval_fee(costs: dict) -> float:
    return float(costs.get("evaluation_cost_discounted") or costs["evaluation_cost"])


def mc_row(name: str, trades: pl.DataFrame, acct: str, k: int) -> dict:
    rules, costs = _tier(acct)
    mc = run_monte_carlo(
        trades,
        rules,
        contracts=k,
        n_attempts=N_ATTEMPTS,
        max_days=MAX_DAYS,
        seed=SEED,
        evaluation_cost=_eval_fee(costs),
        reset_cost=costs["reset_cost"],
        strategy=name,
        pass_within_days=PASS_WITHIN,
    )
    return {
        "name": name,
        "acct": acct,
        "k": k,
        "pass": 100 * mc.pass_rate,
        "fail": 100 * mc.fail_rate,
        "timeout": 100 * mc.timeout_rate,
        "med_days": mc.median_days_to_pass,
        "within": mc.pass_within,
        "e_resets": mc.expected_resets_before_pass,
        "e_cost": mc.expected_total_cost_before_pass,
    }


def journey_mc(
    trades: pl.DataFrame,
    acct: str,
    contracts: int,
    n: int = N_ATTEMPTS,
    seed: int = SEED,
) -> dict[str, float]:
    """Eval pass -> first payout-eligible state in the funded account.

    Funded-phase structure is MIRRORED from the Phase 9 25K implementation
    (trailing floor = eval MLL distance, no lock; qualifying day >= $100;
    5 qualifying days; payout = min(MLL, 50% of profit) with $500 minimum).
    Dollar thresholds beyond the MLL distance are NOT verified for 50K/100K —
    treat cross-tier journey numbers as ESTIMATES (VERIFY).
    """
    rules, _ = _tier(acct)
    days = ledger_to_days(trades, contracts)
    if not days:
        return {"pass_rate": 0.0, "pass_and_payout": 0.0}
    start = rules.starting_balance
    dist = rules.max_drawdown
    rng = np.random.default_rng(seed)
    pass_n = payout_n = 0

    def funded_phase(seq, start_idx) -> bool:
        balance, floor, qual, n_pay = start, start - dist, 0, 0
        for day in seq[start_idx : start_idx + 120]:
            dp = sum(day)
            balance += dp
            if balance <= floor:
                return False
            if balance - dist > floor:
                floor = balance - dist
            if dp >= 100:
                qual += 1
            if qual >= 5 and balance - start >= dist and n_pay < 6:
                if min(dist, (balance - start) * 0.5) >= 500:
                    return True
        return False

    for _ in range(n):
        seq = _sample_days(days, 180, rng, "block", 5)
        acct_state = EvalAccount(rules)
        idx = 0
        passed = False
        for day in seq[:MAX_DAYS]:
            idx += 1
            for pnl in day:
                acct_state.on_trade(pnl)
                if acct_state.status == "failed":
                    break
            acct_state.on_session_close()
            if acct_state.status == "passed":
                passed = True
                break
            if acct_state.status == "failed":
                break
        if passed:
            pass_n += 1
            if funded_phase(seq, idx):
                payout_n += 1
    return {"pass_rate": pass_n / n, "pass_and_payout": payout_n / n}


def render_rows(rows: list[dict]) -> list[str]:
    out = [
        "| Ledger | Account | Micros | Pass % | Fail % | Timeout % | Med d "
        "| ≤10d | ≤15d | ≤20d | ≤40d | E[resets] | E[cost] |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        med = f"{r['med_days']:.0f}" if r["med_days"] else "—"
        er = f"{r['e_resets']:.1f}" if r["e_resets"] is not None else "—"
        ec = f"${r['e_cost']:,.0f}" if r["e_cost"] is not None else "—"
        w = r["within"]
        out.append(
            f"| {r['name']} | {r['acct']} | {r['k']} "
            f"| **{r['pass']:.1f}%** | {r['fail']:.1f}% | {r['timeout']:.1f}% | {med} "
            f"| {w[10]:.0f}% | {w[15]:.0f}% | {w[20]:.0f}% | {w[40]:.0f}% "
            f"| {er} | {ec} |"
        )
    return out


def gc_sizing_vs_100k() -> list[str]:
    """Daily RTH dollar range for full-size GC vs the $3,000 100K MLL."""
    path = Path("data/processed/gc/continuous_1m.parquet")
    if not path.exists():
        return ["- GC processed data not found; using Phase 11 figures "
                "(median ~$1,930, P95 ~$7,810/day at $100/pt)."]
    pv = 100.0
    bars = pl.read_parquet(path)
    rng = (
        bars.filter(pl.col("session") == "rth")
        .group_by("trading_date")
        .agg((pl.col(ADJ["high"]).max() - pl.col(ADJ["low"]).min()).alias("r"))
    )
    p50, p95 = float(rng["r"].median()) * pv, float(rng["r"].quantile(0.95)) * pv
    mx = float(rng["r"].max()) * pv
    share = float((rng["r"] * pv > 3000).mean()) * 100
    return [
        f"- Median daily RTH range: **${p50:,.0f}**; P95: **${p95:,.0f}**; "
        f"max: ${mx:,.0f} (at $100/pt, 1 GC)",
        f"- **{share:.0f}% of all days** have a full range above the $3,000 100K MLL "
        "— one adverse open-to-close move can still end the eval",
        "- Verdict: structurally unsound at 1 GC even on 100K; deep grids not reopened",
    ]


def main() -> None:
    setup_logging()
    reports = Path("data/reports")
    reports.mkdir(parents=True, exist_ok=True)

    # ---------------- Part A: MNQ ORB-W (frozen Phase 9 ledger) -------------
    mnq = skip_monday(
        pl.read_parquet("data/processed/trades_phase9_orb_longonly_wf_oos.parquet")
    )
    log.info("MNQ WF OOS ledger (skipMon): %d trades", mnq.height)

    rows_a: list[dict] = []
    rows_a.append(mc_row("MNQ ORB-W", mnq, "lucid_25k", 1))
    for k in (1, 2, 3, 4):
        rows_a.append(mc_row("MNQ ORB-W", mnq, "lucid_50k", k))
    for k in (1, 2, 3, 4, 5, 6, 8, 10):
        rows_a.append(mc_row("MNQ ORB-W", mnq, "lucid_100k", k))

    # Journey MC (structure mirrored from 25K — see docstring)
    journeys = {
        ("lucid_25k", 1): journey_mc(mnq, "lucid_25k", 1),
    }
    best_100k = max(
        (r for r in rows_a if r["acct"] == "lucid_100k"), key=lambda r: r["pass"]
    )
    k_star = best_100k["k"]
    journeys[("lucid_100k", k_star)] = journey_mc(mnq, "lucid_100k", k_star)
    best_50k = max(
        (r for r in rows_a if r["acct"] == "lucid_50k"), key=lambda r: r["pass"]
    )
    journeys[("lucid_50k", best_50k["k"])] = journey_mc(mnq, "lucid_50k", best_50k["k"])

    # 2026 holdout at recommended 100K size (frozen params, no re-tune)
    hold = skip_monday(
        pl.read_parquet("data/processed/trades_phase9_orb_longonly_holdout.parquet")
    )
    hold_rows = [
        mc_row("MNQ ORB-W holdout26", hold, "lucid_25k", 1),
        mc_row("MNQ ORB-W holdout26", hold, "lucid_50k", best_50k["k"]),
        mc_row("MNQ ORB-W holdout26", hold, "lucid_100k", k_star),
    ]

    # ---------------- Part B: gold under $3,000 MLL --------------------------
    gc_lines = gc_sizing_vs_100k()
    rows_b: list[dict] = []
    gc_ledgers = {
        "GC11 macro_nfp_cpi": "data/processed/gc/trades_phase11_macro_nfp_cpi_wf_oos.parquet",
        "GC12 macro_nfp": "data/processed/gc/trades_phase12_macro_nfp_wf_oos.parquet",
        "GC12 comex_orb_deep": "data/processed/gc/trades_phase12_comex_orb_deep_wf_oos.parquet",
    }
    gc_wall: list[str] = []
    for name, p in gc_ledgers.items():
        if Path(p).exists():
            t = pl.read_parquet(p)
            rows_b.append(mc_row(name, t, "lucid_100k", 1))
            months = (t["trading_date"].max() - t["trading_date"].min()).days / 30.4
            freq = t.height / months
            rules100, costs100 = _tier("lucid_100k")
            md6 = max(1, round(freq * 6))
            m6 = run_monte_carlo(
                t, rules100, contracts=1, n_attempts=N_ATTEMPTS, max_days=md6,
                seed=SEED, evaluation_cost=_eval_fee(costs100),
                reset_cost=costs100["reset_cost"], strategy=name,
            )
            gc_wall.append(
                f"- {name}: {freq:.1f} trades/mo — 6-month wall-clock "
                f"(~{md6} active days): pass {100 * m6.pass_rate:.1f}%, "
                f"timeout {100 * m6.timeout_rate:.1f}%"
            )

    # GC 2026 holdout ledgers replayed through 100K MC (frozen; single replay)
    gc_hold_rows: list[dict] = []
    for name, p in {
        "GC11 macro_nfp_cpi holdout26": "data/processed/gc/trades_phase11_macro_nfp_cpi_holdout.parquet",
        "GC12 macro_nfp holdout26": "data/processed/gc/trades_phase12_macro_nfp_holdout.parquet",
    }.items():
        if Path(p).exists():
            gc_hold_rows.append(mc_row(name, pl.read_parquet(p), "lucid_100k", 1))

    mgc_path = "data/processed/mgc/trades_phase13_comex_orb_deep_wf_oos.parquet"
    mgc = pl.read_parquet(mgc_path)
    months = (mgc["trading_date"].max() - mgc["trading_date"].min()).days / 30.4
    mgc_freq = mgc.height / months
    for k in (2, 3, 5, 8, 10):
        rows_b.append(mc_row("MGC13 comex_orb_deep", mgc, "lucid_100k", k))
    # Wall-clock guard: pass within ~2 and ~6 months of active days
    mgc_wall: list[str] = []
    best_mgc = max(
        (r for r in rows_b if r["name"].startswith("MGC13")), key=lambda r: r["pass"]
    )
    rules100, costs100 = _tier("lucid_100k")
    for label, wall_months in (("2-month", 2), ("6-month", 6)):
        md = max(1, round(mgc_freq * wall_months))
        m = run_monte_carlo(
            mgc, rules100, contracts=best_mgc["k"], n_attempts=N_ATTEMPTS,
            max_days=md, seed=SEED, evaluation_cost=_eval_fee(costs100),
            reset_cost=costs100["reset_cost"], strategy="mgc_wallclock",
        )
        mgc_wall.append(
            f"- {label} wall-clock (~{md} active days) @ {best_mgc['k']} MGC: "
            f"pass {100 * m.pass_rate:.1f}%, fail {100 * m.fail_rate:.1f}%, "
            f"timeout {100 * m.timeout_rate:.1f}%"
        )
    # MGC 2026 holdout at best k (frozen)
    mgc_hold = pl.read_parquet(
        "data/processed/mgc/trades_phase13_comex_orb_deep_holdout.parquet"
    )
    mgc_hold_row = mc_row("MGC13 c_o_d holdout26", mgc_hold, "lucid_100k", best_mgc["k"])

    # ---------------- Render -------------------------------------------------
    j_lines = [
        "",
        "## Journey MC — pass + first payout (funded rules mirrored from 25K; VERIFY)",
        "",
        "| Account | Micros | Pass % | Pass+Payout % |",
        "| --- | --- | --- | --- |",
    ]
    for (acct, k), j in journeys.items():
        j_lines.append(
            f"| {acct} | {k} | {100 * j['pass_rate']:.1f}% "
            f"| {100 * j['pass_and_payout']:.1f}% |"
        )

    lines = [
        "# Phase 14 — Lucid Flex 100K Leaderboard (frozen ledgers, 10k MC)",
        "",
        "Target/MLL ratio: 25K = 1.25x, 50K = 1.50x, **100K = 2.00x** — the 100K "
        "tier needs twice the edge-per-drawdown-dollar of the 25K.",
        "",
        "Fees: discounted eval fee + reset fee per tier "
        "(25K $70/$60, 50K $98/$95, 100K $157.50/$140 — VERIFY).",
        "",
        "## Part A — MNQ ORB-W long-only + skipMon (Phase 9 frozen WF OOS ledger)",
        "",
        *render_rows(rows_a),
        *j_lines,
        "",
        "### 2026 holdout (frozen params, single replay through tier MC)",
        "",
        *render_rows(hold_rows),
        "",
        "## Part B — Gold under the $3,000 100K MLL",
        "",
        "### B1: full-size GC sizing check",
        "",
        *gc_lines,
        "",
        "### B2: frozen gold ledgers on 100K",
        "",
        *render_rows(rows_b),
        "",
        "GC macro wall-clock reality (sparse-event families):",
        "",
        *gc_wall,
        "",
        "### GC 2026 holdout ledgers on 100K (frozen, single replay)",
        "",
        *render_rows(gc_hold_rows),
        "",
        f"MGC comex_orb_deep OOS frequency: {mgc_freq:.1f} trades/month — "
        "wall-clock reality at best contract count:",
        "",
        *mgc_wall,
        "",
        "### MGC 2026 holdout @ best k (frozen)",
        "",
        *render_rows([mgc_hold_row]),
        "",
    ]
    (reports / "phase14_100k_leaderboard.md").write_text("\n".join(lines) + "\n")
    log.info("Phase 14 leaderboard -> data/reports/phase14_100k_leaderboard.md")


if __name__ == "__main__":
    main()

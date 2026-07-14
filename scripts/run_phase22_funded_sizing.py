"""Phase 22 — Funded-phase sizing sweep (pass + FIRST payout).

Eval phase is locked at fixed 1 micro (Phase 19). This sweeps the FUNDED
phase only, where the game differs: no consistency rule, $100 qualifying-day
threshold (18% of 1-micro win days miss it), scaling allows 10-20 micros.

Key scoping fact: the open payout-vs-MLL rule question only affects payout
cycles AFTER the first request — pass+FIRST-payout (the goal metric) is
independent of it, so this sweep is not blocked.

Stage 1: screen all policies on WF-OOS ledger (block, seed 42, 10k).
Stage 2: any policy beating fixed_1 by >= +1pt goes to the full battery:
         3 seeds x {block, day} x {WF OOS, 2026 holdout}.
Pre-registered accept bar (brain/Experiments/funded-phase-sizing.md):
         >= +2pts pass+payout over fixed_1 across ALL battery cells.

Output: data/reports/phase22_funded_sizing.md (+ .json)
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl

from src.evaluation.journey import journey_mc
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.sizing import FixedSizing
from src.logging_setup import setup_logging

log = logging.getLogger("phase22")

PROC = Path("data/processed")
REPORT = Path("data/reports/phase22_funded_sizing.md")
REPORT_JSON = Path("data/reports/phase22_funded_sizing.json")

WF = PROC / "trades_rebacktest_orb_w_wf_oos.parquet"
HOLDOUT = PROC / "trades_rebacktest_orb_w_holdout.parquet"

N = 10_000
SCREEN_SEED = 42
BATTERY_SEEDS = (42, 43, 44)
ACCEPT_MARGIN = 0.02   # +2pts pap over fixed_1, every battery cell
STAGE2_MARGIN = 0.01   # screen survivors need +1pt to advance


# --- funded sizing policies: (qual_days, profit, cushion) -> micros ---------
def fixed(k: int):
    f = lambda q, p, c: k
    f.__name__ = f"fixed_{k}"
    return f


def qual_rush(k: int, need: int = 5):
    """k micros until `need` qualifying days banked, then 1."""
    f = lambda q, p, c: k if q < need else 1
    f.__name__ = f"qual_rush_{k}"
    return f


def cushion_up(k: int, thr: float):
    """k micros while cushion >= thr, else 1."""
    f = lambda q, p, c: k if c >= thr else 1
    f.__name__ = f"cushion{int(thr)}_{k}"
    return f


def qual_cushion(k: int, thr: float, need: int = 5):
    """k micros only while unqualified AND cushion comfortable."""
    f = lambda q, p, c: k if (q < need and c >= thr) else 1
    f.__name__ = f"qualcush{int(thr)}_{k}"
    return f


POLICIES = [
    fixed(1),            # control — current recommendation
    fixed(2),
    fixed(3),
    qual_rush(2),
    qual_rush(3),
    cushion_up(2, 600.0),
    qual_cushion(2, 600.0),
    qual_cushion(3, 800.0),
]


def run_cell(trades: pl.DataFrame, rules: LucidRules, policy, seed: int,
             mode: str) -> dict[str, float]:
    return journey_mc(
        trades, rules, FixedSizing("fixed_1", 1),   # eval phase: locked 1 micro
        n=N, max_days=None, seed=seed, sample_mode=mode, block_size=5,
        funded_policy=policy,
    )


def main() -> None:
    setup_logging()
    rules = LucidRules.from_yaml("config/lucid_25k.yaml")
    wf = pl.read_parquet(WF)
    ho = pl.read_parquet(HOLDOUT)

    # ---- Stage 1: screen ----
    screen = {}
    for pol in POLICIES:
        r = run_cell(wf, rules, pol, SCREEN_SEED, "block")
        screen[pol.__name__] = r
        log.info("screen %-14s pass=%.1f%% pap=%.1f%%",
                 pol.__name__, 100 * r["pass_rate"], 100 * r["pass_and_payout"])
    base_pap = screen["fixed_1"]["pass_and_payout"]
    survivors = [p for p in POLICIES
                 if p.__name__ != "fixed_1"
                 and screen[p.__name__]["pass_and_payout"] >= base_pap + STAGE2_MARGIN]
    log.info("stage-2 survivors: %s", [p.__name__ for p in survivors])

    # ---- Stage 2: full battery for survivors (+ fixed_1 control) ----
    battery: dict[str, dict[str, dict]] = {}
    battery_pols = [POLICIES[0]] + survivors
    for pol in battery_pols:
        cells = {}
        for ledger_name, ledger in (("wf", wf), ("holdout", ho)):
            for mode in ("block", "day"):
                for seed in BATTERY_SEEDS:
                    key = f"{ledger_name}/{mode}/s{seed}"
                    cells[key] = run_cell(ledger, rules, pol, seed, mode)
        battery[pol.__name__] = cells
        paps = [c["pass_and_payout"] for c in cells.values()]
        log.info("battery %-14s pap min=%.1f%% max=%.1f%%",
                 pol.__name__, 100 * min(paps), 100 * max(paps))

    # ---- accept check: beat fixed_1 by >= ACCEPT_MARGIN in EVERY cell ----
    verdicts = {}
    if survivors:
        ctrl = battery["fixed_1"]
        for pol in survivors:
            name = pol.__name__
            diffs = [battery[name][k]["pass_and_payout"] - ctrl[k]["pass_and_payout"]
                     for k in ctrl]
            verdicts[name] = {
                "min_diff": min(diffs), "max_diff": max(diffs),
                "accepted": min(diffs) >= ACCEPT_MARGIN,
            }

    # ---- report ----
    lines = [
        "# Phase 22 — Funded-phase sizing sweep (pass + first payout)",
        "",
        "Eval phase locked at 1 micro (Phase 19). Funded phase swept — it differs:",
        "no consistency rule, $100 qualifying day (18% of 1-micro win days miss it),",
        "scaling tiers allow 10-20 micros. First-payout metric is independent of the",
        "open payout-vs-MLL rule question (that affects later cycles only).",
        "",
        f"Ledgers: incumbent re-backtest WF-OOS ({wf.height} trades) + 2026 holdout "
        f"({ho.height} trades). 10k MC per cell, no eval time limit.",
        "",
        "## Stage 1 — screen (WF-OOS, block, seed 42)",
        "",
        "| Funded policy | Pass % | Pass+payout % | vs fixed_1 |",
        "| --- | --- | --- | --- |",
    ]
    for pol in POLICIES:
        r = screen[pol.__name__]
        d = r["pass_and_payout"] - base_pap
        lines.append(
            f"| {pol.__name__} | {100*r['pass_rate']:.1f}% "
            f"| {100*r['pass_and_payout']:.1f}% | {100*d:+.1f}pt |"
        )
    lines += ["", "## Stage 2 — full battery (3 seeds x block/day x WF+holdout)", ""]
    if survivors:
        lines += [
            "| Policy | pap min | pap max | min diff vs fixed_1 | Accepted (>= +2pt everywhere)? |",
            "| --- | --- | --- | --- | --- |",
        ]
        for pol in survivors:
            name = pol.__name__
            paps = [c["pass_and_payout"] for c in battery[name].values()]
            v = verdicts[name]
            lines.append(
                f"| {name} | {100*min(paps):.1f}% | {100*max(paps):.1f}% "
                f"| {100*v['min_diff']:+.1f}pt | {'**YES**' if v['accepted'] else 'no'} |"
            )
        ctrl_paps = [c["pass_and_payout"] for c in battery["fixed_1"].values()]
        lines.append(
            f"| fixed_1 (control) | {100*min(ctrl_paps):.1f}% | {100*max(ctrl_paps):.1f}% | — | — |"
        )
    else:
        lines.append("_No policy beat fixed_1 by +1pt on the screen — battery skipped._")
    accepted = [n for n, v in verdicts.items() if v["accepted"]]
    lines += [
        "",
        "## Verdict",
        "",
        (f"**ACCEPT: {', '.join(accepted)}** — clears +2pts over fixed_1 in every cell."
         if accepted else
         "**Keep 1 micro in the funded phase.** No policy clears the pre-registered "
         "bar (+2pts pass+payout over fixed_1 across all seeds, sample modes, and "
         "both ledgers)."),
        "",
        "Pre-registered in `brain/Experiments/funded-phase-sizing.md` before running.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    REPORT_JSON.write_text(json.dumps(
        {"screen": screen, "battery": battery, "verdicts": verdicts}, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()

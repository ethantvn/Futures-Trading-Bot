"""Phase 19: eval-policy optimization on frozen ORB-W ledger.

Usage:
  .venv/bin/python scripts/run_phase19.py
  .venv/bin/python scripts/run_phase19.py --quick   # fewer seeds/modes for dev
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl
import yaml

from scripts.run_phase7 import skip_monday
from src.evaluation.journey import journey_mc
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.recommendation import build_policy_grid, run_policy_monte_carlo
from src.logging_setup import setup_logging

log = logging.getLogger("run_phase19")
CONFIG = Path("config/phase19_eval_policy.yaml")


def _eval_fee(lucid_yaml: dict, discounted: bool) -> float:
    c = lucid_yaml["costs"]
    return float(c["evaluation_cost_discounted" if discounted else "evaluation_cost"])


def load_ledger(spec: dict) -> pl.DataFrame:
    t = pl.read_parquet(spec["path"])
    if spec.get("skip_monday"):
        t = skip_monday(t)
    return t


def run_sweep(quick: bool = False) -> dict[str, Any]:
    cfg = yaml.safe_load(CONFIG.read_text())
    lucid_path = Path("config") / f"{cfg['account']}.yaml"
    lucid_yaml = yaml.safe_load(lucid_path.read_text())
    rules = LucidRules.from_yaml(lucid_path)
    eval_fee = _eval_fee(lucid_yaml, cfg.get("use_discounted_eval_fee", True))
    reset_fee = float(lucid_yaml["costs"]["reset_cost"])

    mc = cfg["monte_carlo"]
    n = 2000 if quick else int(mc["n_attempts"])
    seeds = [42] if quick else list(mc["seeds"])
    modes = ["block"] if quick else list(mc["sample_modes"])
    max_days_list = [60] if quick else list(mc["max_days"])

    policies = build_policy_grid(cfg)
    ledgers = {k: load_ledger(v) for k, v in cfg["ledgers"].items()}

    rows: list[dict[str, Any]] = []
    for ledger_key, trades in ledgers.items():
        label = cfg["ledgers"][ledger_key]["label"]
        for policy in policies:
            for max_days in max_days_list:
                for mode in modes:
                    for seed in seeds:
                        mc_r = run_policy_monte_carlo(
                            trades, rules, policy,
                            n_attempts=n,
                            max_days=max_days,
                            seed=seed,
                            sample_mode=mode,
                            block_size=mc["block_size"],
                            evaluation_cost=eval_fee,
                            reset_cost=reset_fee,
                        )
                        j = journey_mc(
                            trades, rules, policy,
                            n=n, max_days=max_days, seed=seed,
                            sample_mode=mode, block_size=mc["block_size"],
                        )
                        rows.append({
                            "ledger": ledger_key,
                            "ledger_label": label,
                            "policy": policy.name,
                            "max_days": max_days,
                            "sample_mode": mode,
                            "seed": seed,
                            "pass_rate": mc_r.pass_rate,
                            "fail_rate": mc_r.fail_rate,
                            "timeout_rate": mc_r.timeout_rate,
                            "pass_and_payout": j["pass_and_payout"],
                            "median_days": mc_r.median_days_to_pass,
                            "e_cost": mc_r.expected_total_cost_before_pass,
                        })
                        log.info(
                            "%s %s d=%d %s s=%d pass=%.1f%% pap=%.1f%%",
                            label, policy.name, max_days, mode, seed,
                            100 * mc_r.pass_rate, 100 * j["pass_and_payout"],
                        )

    return {"rows": rows, "cfg": cfg, "n_attempts": n}


def summarize(results: dict[str, Any]) -> tuple[list[dict], str]:
    rows = results["rows"]
    cfg = results["cfg"]
    baseline = cfg["baseline"]
    b_pass = float(baseline["pass_target"])
    b_pap = float(baseline["pass_payout_target"])
    lift = cfg["acceptance"]["min_pass_lift"]

    # Aggregate primary view: max_days=60, all seeds/modes mean
    primary = [r for r in rows if r["max_days"] == 60]
    by_policy: dict[str, list[dict]] = {}
    for r in primary:
        by_policy.setdefault(r["policy"], []).append(r)

    summary = []
    for policy, prs in sorted(by_policy.items()):
        wf = [r for r in prs if r["ledger"] == "wf_oos"]
        ho = [r for r in prs if r["ledger"] == "holdout"]
        if not wf:
            continue
        summary.append({
            "policy": policy,
            "wf_pass": sum(r["pass_rate"] for r in wf) / len(wf),
            "wf_pap": sum(r["pass_and_payout"] for r in wf) / len(wf),
            "ho_pass": sum(r["pass_rate"] for r in ho) / len(ho) if ho else 0,
            "ho_pap": sum(r["pass_and_payout"] for r in ho) / len(ho) if ho else 0,
            "n_runs": len(wf),
        })

    summary.sort(key=lambda s: (s["wf_pass"], s["wf_pap"]), reverse=True)

    lines = [
        "# Phase 19 Leaderboard — Eval Policy on Frozen ORB-W",
        "",
        f"Baseline incumbent: **{100*b_pass:.1f}%** pass / **{100*b_pap:.1f}%** pass+payout @ 1 micro.",
        "Same trade ledger; only contract policy changes.",
        "",
        "| Policy | WF Pass % | WF Pass+payout % | Holdout Pass % | Holdout P+p % |",
        "| --- | --- | --- | --- | --- |",
    ]
    for s in summary:
        mark = ""
        if (
            s["wf_pass"] >= b_pass + lift
            and s["wf_pap"] >= b_pap + lift
            and s["ho_pass"] >= b_pass - 0.02
        ):
            mark = " ★"
        lines.append(
            f"| {s['policy']}{mark} | {100*s['wf_pass']:.1f}% | {100*s['wf_pap']:.1f}% "
            f"| {100*s['ho_pass']:.1f}% | {100*s['ho_pap']:.1f}% |"
        )

    challengers = [
        s for s in summary
        if s["policy"] != "fixed_1"
        and s["wf_pass"] >= b_pass + lift
        and s["wf_pap"] >= b_pap
    ]
    lines += ["", "## Challengers", ""]
    if challengers:
        for s in challengers[:5]:
            lines.append(
                f"- **{s['policy']}**: WF {100*s['wf_pass']:.1f}% / {100*s['wf_pap']:.1f}% "
                f"(holdout {100*s['ho_pass']:.1f}%)"
            )
    else:
        lines.append("_No policy clears +3pt pass lift with pass+payout ≥ baseline on WF._")

    # max_days sensitivity for fixed_1 and top 3
    lines += ["", "## max_days sensitivity (fixed_1 + top policies)", ""]
    lines.append("| Policy | max_days | WF pass % | WF pap % |")
    lines.append("| --- | --- | --- | --- |")
    top_names = {s["policy"] for s in summary[:4]} | {"fixed_1"}
    for r in sorted(rows, key=lambda x: (-x["pass_rate"], x["policy"])):
        if r["policy"] not in top_names or r["ledger"] != "wf_oos":
            continue
        if r["sample_mode"] != "block" or r["seed"] != 42:
            continue
        lines.append(
            f"| {r['policy']} | {r['max_days']} | {100*r['pass_rate']:.1f}% "
            f"| {100*r['pass_and_payout']:.1f}% |"
        )

    return summary, "\n".join(lines) + "\n"


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="Fast dev run (1 seed, block only)")
    args = ap.parse_args()

    results = run_sweep(quick=args.quick)
    summary, md = summarize(results)

    reports = Path("data/reports")
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "phase19_leaderboard.md").write_text(md)
    (reports / "phase19_metrics.json").write_text(
        json.dumps({"summary": summary, "rows": results["rows"]}, indent=1)
    )

    best = summary[0] if summary else None
    if best:
        log.info(
            "Best: %s WF pass=%.1f%% pap=%.1f%%",
            best["policy"], 100 * best["wf_pass"], 100 * best["wf_pap"],
        )
    log.info("Report → data/reports/phase19_leaderboard.md")


if __name__ == "__main__":
    main()

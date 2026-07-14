"""Phase 21 — Re-score frozen challenger ledgers under VERIFIED Lucid rules.

Audit only: no new fitting, no param changes. Frozen WF-OOS (and holdout)
ledgers from Phases 7/16/17/18 are cost-corrected from the old $0.99/side
model to the verified $0.50/side ($1.00/RT; slippage is embedded in fill
prices and unchanged), then re-scored with:
  - 10k MC, block bootstrap (5), seed 42, NO eval time limit
  - verified funded journey (no consistency rule, $100 qualifying day,
    $500 min / $1,000 cap payout) via src/evaluation/journey.py

Bar: incumbent re-backtest = 69.8% pass / 51.6% pass+payout.
Flag rule (pre-registered): within 2pts of incumbent on BOTH metrics AND
picky-bar density (>=100 OOS trades, >=4 t/mo, fold+ >=50%).

Output: data/reports/phase21_rescore_audit.md (+ .json)
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
from src.evaluation.recommendation import run_policy_monte_carlo
from src.evaluation.sizing import FixedSizing
from src.logging_setup import setup_logging

log = logging.getLogger("phase21")

PROC = Path("data/processed")
REPORT = Path("data/reports/phase21_rescore_audit.md")
REPORT_JSON = Path("data/reports/phase21_rescore_audit.json")

NEW_RT_COST = 1.00           # $/round trip per contract (2 x $0.50/side)
INCUMBENT_PASS = 0.698
INCUMBENT_PAP = 0.516
FLAG_MARGIN = 0.02
MIN_TRADES = 100
MIN_T_PER_MO = 4.0
MIN_FOLD_POS = 0.50

# (name, wf_oos_path, holdout_path|None, old_wf_pass%, fold_pos_share|None,
#  apply_skip_monday_posthoc, note)
CANDIDATES = [
    ("incumbent_rebacktest", "trades_rebacktest_orb_w_wf_oos.parquet",
     "trades_rebacktest_orb_w_holdout.parquet", 69.8, 0.89, False,
     "Bar. Already at $0.50/side - no correction."),
    ("p9_orb_longonly (xcheck)", "trades_phase9_orb_longonly_wf_oos.parquet",
     "trades_phase9_orb_longonly_holdout.parquet", 64.3, 0.89, True,
     "Old incumbent ledger, arithmetic correction cross-check."),
    # Phase 18
    ("p18_orb_w_control", "trades_phase18_orb_w_control_wf_oos.parquet",
     "trades_phase18_orb_w_control_holdout.parquet", 63.8, 0.78, False, ""),
    ("p18_orb_tod", "trades_phase18_orb_tod_wf_oos.parquet",
     "trades_phase18_orb_tod_holdout.parquet", 59.2, 0.78, False, ""),
    ("p18_mes_diverge_orb", "trades_phase18_mes_diverge_orb_wf_oos.parquet",
     "trades_phase18_mes_diverge_orb_holdout.parquet", 58.4, 0.78, False, ""),
    ("p18_orb_risk_cap", "trades_phase18_orb_risk_cap_wf_oos.parquet",
     "trades_phase18_orb_risk_cap_holdout.parquet", 58.3, 0.78, False, ""),
    ("p18_orb_macro_skip", "trades_phase18_orb_macro_skip_wf_oos.parquet",
     None, 56.9, 0.78, False, ""),
    # Phase 17
    ("p17_orb_w_control", "trades_phase17_orb_w_control_wf_oos.parquet",
     "trades_phase17_orb_w_control_holdout.parquet", 64.5, 0.89, False, ""),
    ("p17_orb_inside_day", "trades_phase17_orb_inside_day_wf_oos.parquet",
     "trades_phase17_orb_inside_day_holdout.parquet", 64.2, 0.89, False, ""),
    ("p17_orb_prior_regime", "trades_phase17_orb_prior_regime_wf_oos.parquet",
     "trades_phase17_orb_prior_regime_holdout.parquet", 61.6, 0.78, False, ""),
    ("p17_orb_vix_on_stack", "trades_phase17_orb_vix_on_stack_wf_oos.parquet",
     "trades_phase17_orb_vix_on_stack_holdout.parquet", 58.3, 0.89, False, ""),
    ("p17_orb_on_context", "trades_phase17_orb_on_context_wf_oos.parquet",
     None, 57.4, 0.78, False, ""),
    ("p17_orb_vix_band", "trades_phase17_orb_vix_band_wf_oos.parquet",
     None, 52.2, 0.89, False, ""),
    ("p17_orb_only_inside", "trades_phase17_orb_only_inside_wf_oos.parquet",
     None, 98.1, 0.11, False, "Known sparsity trap - density gate applies."),
    # Phase 16
    ("p16_structure_gated_orb", "trades_phase16_structure_gated_orb_wf_oos.parquet",
     "trades_phase16_structure_gated_orb_holdout.parquet", None, None, False,
     "P16 verdict: modest, too sparse. Ledger as-run (no post-hoc skipMon)."),
    # Phase 7 (skip Monday applied post-hoc, matching reported numbers)
    ("p7_nr7_orb", "trades_phase7_nr7_orb_wf_oos.parquet",
     "trades_phase7_nr7_orb_holdout.parquet", 63.5, None, True,
     "Account-2 diversifier; known slow (~40 t/yr)."),
    ("p7_orb_width", "trades_phase7_orb_width_wf_oos.parquet",
     "trades_phase7_orb_width_holdout.parquet", 61.8, None, True,
     "Pre-long-only Phase 7 winner (takes shorts)."),
]


def skip_monday(trades: pl.DataFrame) -> pl.DataFrame:
    return trades.filter(pl.col("trading_date").dt.weekday() != 1)


def correct_costs(trades: pl.DataFrame) -> tuple[pl.DataFrame, float, float]:
    """Rebuild net_pnl from gross_pnl at verified $1.00/RT. Returns
    (corrected_df, old_per_trade_cost, new_per_trade_cost)."""
    if trades.height == 0:
        return trades, 0.0, 0.0
    old_pt = float((trades["costs"] / trades["qty"]).mean())
    out = trades.with_columns(
        (pl.col("qty") * NEW_RT_COST).alias("costs"),
    ).with_columns(
        (pl.col("gross_pnl") - pl.col("costs")).alias("net_pnl"),
    )
    return out, old_pt, NEW_RT_COST


def trades_per_month(trades: pl.DataFrame) -> float:
    if trades.height == 0:
        return 0.0
    d0, d1 = trades["trading_date"].min(), trades["trading_date"].max()
    months = max((d1 - d0).days / 30.44, 1.0)
    return trades.height / months


def score(trades: pl.DataFrame, rules: LucidRules) -> dict:
    policy = FixedSizing("fixed_1", 1)
    mc = run_policy_monte_carlo(
        trades, rules, policy, n_attempts=10_000, max_days=9999, seed=42,
        sample_mode="block", block_size=5,
        evaluation_cost=70.0, reset_cost=60.0,
    )
    j = journey_mc(
        trades, rules, policy, n=10_000, max_days=None, seed=42,
        sample_mode="block", block_size=5,
    )
    return {
        "pass": mc.pass_rate,
        "pap": j["pass_and_payout"],
        "med_days": mc.median_days_to_pass,
        "fail": mc.fail_rate,
    }


def main() -> None:
    setup_logging()
    rules = LucidRules.from_yaml("config/lucid_25k.yaml")
    rows = []
    for name, wf_path, ho_path, old_pass, fold_pos, posthoc_mon, note in CANDIDATES:
        p = PROC / wf_path
        if not p.exists():
            log.warning("%s: missing %s — skipped", name, wf_path)
            continue
        t = pl.read_parquet(p)
        if posthoc_mon:
            t = skip_monday(t)
        t, old_pt, new_pt = correct_costs(t)
        already_new = abs(old_pt - NEW_RT_COST) < 0.05
        s = score(t, rules)
        tpm = trades_per_month(t)
        dense = (
            t.height >= MIN_TRADES
            and tpm >= MIN_T_PER_MO
            and (fold_pos is None or fold_pos >= MIN_FOLD_POS)
        )
        ho = None
        if ho_path and (PROC / ho_path).exists():
            th = pl.read_parquet(PROC / ho_path)
            if posthoc_mon:
                th = skip_monday(th)
            th, _, _ = correct_costs(th)
            if th.height > 0:
                ho = score(th, rules)
                ho["trades"] = th.height
                ho["net"] = float(th["net_pnl"].sum())
        flagged = (
            dense
            and s["pass"] >= INCUMBENT_PASS - FLAG_MARGIN
            and s["pap"] >= INCUMBENT_PAP - FLAG_MARGIN
            and name != "incumbent_rebacktest"
        )
        rows.append({
            "name": name, "trades": t.height, "net": float(t["net_pnl"].sum()),
            "t_per_mo": tpm, "fold_pos": fold_pos, "old_wf_pass": old_pass,
            "old_per_trade_cost": old_pt, "cost_corrected": not already_new,
            "dense": dense, "flagged": flagged, "note": note,
            **{f"new_{k}": v for k, v in s.items()},
            "holdout": ho,
        })
        log.info(
            "%s: pass %.1f%% (old %s) pap %.1f%% dense=%s flag=%s",
            name, 100 * s["pass"],
            f"{old_pass:.1f}%" if old_pass else "n/a",
            100 * s["pap"], dense, flagged,
        )

    rows.sort(key=lambda r: (r["new_pass"], r["new_pap"]), reverse=True)
    flagged_rows = [r for r in rows if r["flagged"]]

    lines = [
        "# Phase 21 — Re-scoring audit: frozen ledgers under verified Lucid rules",
        "",
        "Frozen WF-OOS ledgers (Phases 7/16/17/18), cost-corrected to the verified",
        "$0.50/side ($1.00/RT; slippage unchanged in fill prices), re-scored with",
        "10k MC block bootstrap seed 42, **no eval time limit**, and the verified",
        "funded journey (no consistency rule, $100 qualifying day, $500/$1,000 payout).",
        "**No new fitting. No param changes.** Audit of old conclusions only.",
        "",
        f"Bar (incumbent re-backtest): **{100*INCUMBENT_PASS:.1f}% pass / "
        f"{100*INCUMBENT_PAP:.1f}% pass+payout**. Flag rule: within 2pts on BOTH + "
        f"density (>= {MIN_TRADES} trades, >= {MIN_T_PER_MO:.0f} t/mo, fold+ >= 50%).",
        "",
        "## WF-OOS re-scores (ranked by corrected pass rate)",
        "",
        "| Candidate | Trades | t/mo | Fold+ | Old pass | **New pass** | **New pass+payout** | Med d | Net $ | Dense? | FLAG |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        fp = f"{100*r['fold_pos']:.0f}%" if r["fold_pos"] is not None else "n/a"
        op = f"{r['old_wf_pass']:.1f}%" if r["old_wf_pass"] else "n/a"
        md = f"{r['new_med_days']:.0f}" if r["new_med_days"] else "-"
        lines.append(
            f"| {r['name']} | {r['trades']} | {r['t_per_mo']:.1f} | {fp} | {op} "
            f"| **{100*r['new_pass']:.1f}%** | **{100*r['new_pap']:.1f}%** | {md} "
            f"| ${r['net']:,.0f} | {'Y' if r['dense'] else 'n'} "
            f"| {'**FLAG**' if r['flagged'] else '—'} |"
        )
    lines += [
        "",
        "## 2026 holdout re-scores (frozen, cost-corrected, no time limit)",
        "",
        "| Candidate | Trades | Net $ | Pass % | Pass+payout % |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        if r["holdout"]:
            h = r["holdout"]
            lines.append(
                f"| {r['name']} | {h['trades']} | ${h['net']:,.0f} "
                f"| {100*h['pass']:.1f}% | {100*h['pap']:.1f}% |"
            )
    lines += ["", "## Flagged candidates", ""]
    if flagged_rows:
        for r in flagged_rows:
            lines.append(f"- **{r['name']}** — see table. {r['note']}")
    else:
        lines.append("_None. No dense challenger comes within 2pts of the incumbent "
                     "on both pass and pass+payout under verified rules._")
    lines += [
        "",
        "## Notes",
        "",
        "- Cost correction is exact for commission (a per-trade constant); fills and",
        "  slippage are unchanged from the original engine runs.",
        "- Fold+ shares carried from the original phase leaderboards (a property of",
        "  the frozen WF runs, unaffected by re-scoring).",
        "- p7 ledgers get skip-Monday post-hoc (matching their reported numbers);",
        "  P17/P18 families already skip Monday in-grid.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    REPORT_JSON.write_text(json.dumps(rows, indent=1, default=str))
    print("\n".join(lines))


if __name__ == "__main__":
    main()

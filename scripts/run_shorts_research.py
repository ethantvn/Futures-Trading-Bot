"""Research: can filtered ORB shorts help under verified Lucid 25K rules?

Compares long-only (incumbent) vs long+short / short-only / asymmetric short
gates on the same frozen ORB-W core + $0.50/side commission.

Usage:
  .venv/bin/python scripts/run_shorts_research.py
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl
import yaml

from scripts.run_phase7 import _as_date, _filter, _sanitize, skip_monday
from src.backtest.engine import EngineConfig, run_backtest
from src.backtest.fees import CostModel
from src.backtest.metrics import compute_metrics
from src.backtest.execution import LONG, SHORT
from src.data.macro_calendar import macro_event_dates
from src.evaluation.journey import journey_mc
from src.evaluation.lucid_rules import LucidRules
from src.evaluation.recommendation import run_policy_monte_carlo
from src.evaluation.sizing import FixedSizing
from src.logging_setup import setup_logging
from src.strategies.base import with_signal_defaults
from src.strategies.indicators import prev_day_context
from src.strategies.opening_range import OpeningRangeBreakout
from src.strategies.orb_filtered import FilteredOrb
from src.validation.walk_forward import (
    make_folds,
    run_full_period_grid,
    score_sharpe,
    walk_forward,
)

log = logging.getLogger("shorts_research")
REPORT = Path("data/reports/shorts_research.md")
JSON_OUT = Path("data/reports/shorts_research.json")

CORE = {
    "range_minutes": 30,
    "target_r": 1.0,
    "expire_minutes": 120,
    "min_width_ratio": 0.25,
    "max_width_ratio": 0.7,
}


class AsymmetricOrb(FilteredOrb):
    """ORB-W with independent long/short enable + short-specific width/weekday gates."""

    name = "asymmetric_orb"
    default_params = {
        **FilteredOrb.default_params,
        "long_only": False,
        "short_only": False,
        "enable_long": True,
        "enable_short": True,
        # None => reuse long width band
        "short_min_width_ratio": None,
        "short_max_width_ratio": None,
        "short_skip_weekdays": (),
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        # Base ORB OCO emits (ignore FilteredOrb long_only until end)
        out = OpeningRangeBreakout.prepare(self, df)

        ctx = prev_day_context(df, vol_ref_days=p["vol_ref_days"])
        out = out.join(
            ctx.select("trading_date", "vol_ref"), on="trading_date", how="left"
        ).sort("ts_utc")

        ratio = (pl.col("or_high") - pl.col("or_low")) / pl.col("vol_ref")
        long_gate = (
            (ratio > p["min_width_ratio"]) & (ratio <= p["max_width_ratio"])
        ).fill_null(False)
        if p["skip_weekdays"]:
            long_gate = long_gate & ~pl.col("trading_date").dt.weekday().is_in(
                list(p["skip_weekdays"])
            )
        if p["skip_macro_days"]:
            dates = out["trading_date"]
            d0, d1 = dates.min(), dates.max()
            if d0 is not None and d1 is not None:
                skip = macro_event_dates(
                    d0 if isinstance(d0, date) else d0,
                    d1 if isinstance(d1, date) else d1,
                    p["macro_events"],
                )
                if skip:
                    long_gate = long_gate & ~pl.col("trading_date").is_in(sorted(skip))

        s_min = p["min_width_ratio"] if p["short_min_width_ratio"] is None else p["short_min_width_ratio"]
        s_max = p["max_width_ratio"] if p["short_max_width_ratio"] is None else p["short_max_width_ratio"]
        short_gate = ((ratio > s_min) & (ratio <= s_max)).fill_null(False)
        if p["skip_weekdays"]:
            short_gate = short_gate & ~pl.col("trading_date").dt.weekday().is_in(
                list(p["skip_weekdays"])
            )
        if p["short_skip_weekdays"]:
            short_gate = short_gate & ~pl.col("trading_date").dt.weekday().is_in(
                list(p["short_skip_weekdays"])
            )
        if p["skip_macro_days"]:
            dates = out["trading_date"]
            d0, d1 = dates.min(), dates.max()
            if d0 is not None and d1 is not None:
                skip = macro_event_dates(
                    d0 if isinstance(d0, date) else d0,
                    d1 if isinstance(d1, date) else d1,
                    p["macro_events"],
                )
                if skip:
                    short_gate = short_gate & ~pl.col("trading_date").is_in(sorted(skip))

        enable_long = bool(p.get("enable_long", True)) and not bool(p.get("short_only", False))
        enable_short = bool(p.get("enable_short", True)) and not bool(p.get("long_only", False))
        if p.get("short_only"):
            enable_long, enable_short = False, True
        if p.get("long_only"):
            enable_long, enable_short = True, False

        out = out.with_columns(
            (pl.col("enter_long") & long_gate & enable_long).alias("enter_long"),
            (pl.col("enter_short") & short_gate & enable_short).alias("enter_short"),
        )
        if p["exit_minute"] is not None:
            from src.strategies.indicators import minute_of_day

            past_exit = minute_of_day() >= (p["exit_minute"] - self.timeframe_minutes)
            out = out.with_columns(
                (pl.col("exit_long") | past_exit).alias("exit_long"),
                (pl.col("exit_short") | past_exit).alias("exit_short"),
            )
        if p["max_risk_points"] is not None:
            cap = float(p["max_risk_points"])
            out = out.with_columns(
                pl.max_horizontal(
                    pl.col("stop_long_adj"),
                    pl.col("entry_price_long_adj") - cap,
                ).alias("stop_long_adj"),
                pl.min_horizontal(
                    pl.col("stop_short_adj"),
                    pl.col("entry_price_short_adj") + cap,
                ).alias("stop_short_adj"),
            )
        return with_signal_defaults(out)


def side_breakdown(trades: pl.DataFrame) -> dict:
    if trades.is_empty():
        return {"n_long": 0, "n_short": 0, "net_long": 0.0, "net_short": 0.0,
                "wr_long": None, "wr_short": None, "exp_long": None, "exp_short": None}
    long = trades.filter(pl.col("side") == LONG)
    short = trades.filter(pl.col("side") == SHORT)

    def _side(t: pl.DataFrame) -> dict:
        if t.is_empty():
            return {"n": 0, "net": 0.0, "wr": None, "exp": None}
        n = t.height
        net = float(t["net_pnl"].sum())
        wr = float((t["net_pnl"] > 0).mean())
        return {"n": n, "net": net, "wr": wr, "exp": net / n}

    L, S = _side(long), _side(short)
    return {
        "n_long": L["n"], "n_short": S["n"],
        "net_long": L["net"], "net_short": S["net"],
        "wr_long": L["wr"], "wr_short": S["wr"],
        "exp_long": L["exp"], "exp_short": S["exp"],
    }


def run_mc(ledger: pl.DataFrame, rules: LucidRules, lucid_costs: dict, n: int = 8_000) -> dict:
    policy = FixedSizing("fixed_1", 1)
    mc = run_policy_monte_carlo(
        ledger, rules, policy,
        n_attempts=n, max_days=9999, seed=42,
        sample_mode="block", block_size=5,
        evaluation_cost=lucid_costs["evaluation_cost_discounted"],
        reset_cost=lucid_costs["reset_cost"],
    )
    j = journey_mc(
        ledger, rules, policy,
        n=n, max_days=None, seed=42,
        sample_mode="block", block_size=5,
    )
    return {
        "pass": mc.pass_rate,
        "fail": mc.fail_rate,
        "pap": j["pass_and_payout"],
        "med_days": mc.median_days_to_pass,
    }


def build_variants() -> list[tuple[str, dict]]:
    """Frozen ORB-W core; skip Monday applied post-hoc like Phase 9 / rebacktest."""
    return [
        ("long_only", {**CORE, "long_only": True, "enable_long": True, "enable_short": False}),
        ("long_short_same", {**CORE, "long_only": False, "enable_long": True, "enable_short": True}),
        ("short_only", {**CORE, "short_only": True, "long_only": False}),
        # Shorts only in mid width band (avoid noise + wild ranges)
        ("long_+_short_midwidth", {
            **CORE, "long_only": False,
            "short_min_width_ratio": 0.35, "short_max_width_ratio": 0.55,
        }),
        # Shorts only on tighter band (closer to compression breakouts)
        ("long_+_short_tight", {
            **CORE, "long_only": False,
            "short_min_width_ratio": 0.25, "short_max_width_ratio": 0.40,
        }),
        # Shorts only Tue–Thu (skip Fri in addition to Mon post-filter)
        ("long_+_short_tue_thu", {
            **CORE, "long_only": False,
            "short_skip_weekdays": (5,),  # Fri; Mon still skipped post-hoc for both
        }),
        # Shorts only wider ranges (momentum days)
        ("long_+_short_wide", {
            **CORE, "long_only": False,
            "short_min_width_ratio": 0.45, "short_max_width_ratio": 0.70,
        }),
        # Short-only midwidth diagnostic
        ("short_only_midwidth", {
            **CORE, "short_only": True, "long_only": False,
            "short_min_width_ratio": 0.35, "short_max_width_ratio": 0.55,
            "min_width_ratio": 0.35, "max_width_ratio": 0.55,
        }),
    ]


def main() -> None:
    setup_logging()
    data_cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    strat_cfg = yaml.safe_load(Path("config/strategies.yaml").read_text())
    eng = strat_cfg["engine"]
    processed = Path(data_cfg["processed_dir"])
    Path("data/reports").mkdir(parents=True, exist_ok=True)

    cost = CostModel(
        commission_per_side=eng["commission_per_side"],
        exchange_fees_per_side=eng["exchange_fees_per_side"],
        slippage_ticks=eng["slippage_ticks"],
        tick_size=data_cfg["tick_size"],
        point_value=data_cfg["point_value"],
    )
    ecfg = EngineConfig(
        qty=eng["qty"],
        flat_time=eng["flat_time"],
        no_entry_after=eng["no_entry_after"],
        max_trades_per_day=1,
    )

    grid_start, grid_end = _as_date("2019-06-01"), _as_date("2025-12-31")
    exec_grid = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), grid_start, grid_end)
    sig = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), grid_start, grid_end)
    folds = make_folds(grid_start, grid_end, train_months=24, test_months=6)

    hs, he = _as_date("2026-01-01"), _as_date("2026-06-28")
    exec_h = _filter(pl.read_parquet(processed / "continuous_1m.parquet"), hs, he)
    sig_h = _filter(pl.read_parquet(processed / "continuous_5m.parquet"), hs, he)

    rules = LucidRules.from_yaml("config/lucid_25k.yaml")
    lucid_costs = yaml.safe_load(Path("config/lucid_25k.yaml").read_text())["costs"]

    rows = []
    for name, params in build_variants():
        log.info("=== %s ===", name)
        space = {k: [v] for k, v in params.items()}
        grid_runs = run_full_period_grid(AsymmetricOrb, space, exec_grid, sig, cost, ecfg)
        wf = walk_forward(grid_runs, folds, scorer=lambda t: score_sharpe(t, min_trades=20))
        oos = skip_monday(wf.oos_trades)
        hold = run_backtest(
            exec_h, AsymmetricOrb(params).prepare(sig_h), 5, cost, ecfg, name
        ).trades
        hold = skip_monday(hold)

        m = compute_metrics(oos)
        sb = side_breakdown(oos)
        mc = run_mc(oos, rules, lucid_costs) if oos.height >= 40 else {
            "pass": float("nan"), "fail": float("nan"), "pap": float("nan"), "med_days": float("nan"),
        }
        hm = compute_metrics(hold) if hold.height else {}
        hsb = side_breakdown(hold)

        row = {
            "name": name,
            "params": params,
            "trades": oos.height,
            "net": float(m.get("net_pnl", 0) or 0),
            "sharpe": float(m.get("sharpe_daily", 0) or 0),
            "maxdd": float(m.get("max_drawdown", 0) or 0),
            **sb,
            **{f"mc_{k}": v for k, v in mc.items()},
            "hold_trades": hold.height,
            "hold_net": float(hm.get("net_pnl", 0) or 0),
            "hold_n_short": hsb["n_short"],
            "hold_net_short": hsb["net_short"],
        }
        rows.append(row)
        log.info(
            "%s: n=%d net=$%.0f sharpe=%.2f pass=%.1f%% pap=%.1f%% | L %d/$%.0f S %d/$%.0f",
            name, row["trades"], row["net"], row["sharpe"],
            100 * (row["mc_pass"] or 0), 100 * (row["mc_pap"] or 0),
            row["n_long"], row["net_long"], row["n_short"], row["net_short"],
        )

    # Rank by pass, then pass+payout, then net
    ranked = sorted(
        rows,
        key=lambda r: (
            -(r["mc_pass"] if r["mc_pass"] == r["mc_pass"] else -1),
            -(r["mc_pap"] if r["mc_pap"] == r["mc_pap"] else -1),
            -r["net"],
        ),
    )
    control = next(r for r in rows if r["name"] == "long_only")

    lines = [
        "# Shorts research — ORB-W under verified Lucid 25K ($0.50/side)",
        "",
        "Question: can we add shorts (raw or filtered) to raise trade density "
        "and speed pass/payout without hurting Lucid survival?",
        "",
        f"Core params: `{CORE}` + skip Monday (post-hoc). Commission ${eng['commission_per_side']:.2f}/side.",
        "",
        "## Leaderboard (WF OOS, no eval time limit)",
        "",
        "| Candidate | Trades | Pass% | Pass+payout% | Med d | Net $ | Sharpe | MaxDD | "
        "Long n/net | Short n/net | Short exp |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in ranked:
        se = r["exp_short"]
        se_s = f"${se:.1f}" if se is not None else "—"
        lines.append(
            f"| {r['name']} | {r['trades']} | {100*r['mc_pass']:.1f}% | {100*r['mc_pap']:.1f}% | "
            f"{r['mc_med_days']:.0f} | ${r['net']:,.0f} | {r['sharpe']:.2f} | ${r['maxdd']:,.0f} | "
            f"{r['n_long']}/${r['net_long']:,.0f} | {r['n_short']}/${r['net_short']:,.0f} | {se_s} |"
        )

    best = ranked[0]
    delta_pass = best["mc_pass"] - control["mc_pass"]
    delta_pap = best["mc_pap"] - control["mc_pap"]

    lines += [
        "",
        "## Side diagnosis (any short trades in WF OOS)",
        "",
    ]
    short_rows = [r for r in rows if r["n_short"] > 0]
    if short_rows:
        avg_exp = sum(r["exp_short"] for r in short_rows if r["exp_short"] is not None) / len(short_rows)
        lines.append(
            f"- Short expectancy across short-enabled variants: **${avg_exp:.2f}/trade** "
            f"(control long expectancy ${control['exp_long']:.2f}/trade)."
        )
        for r in short_rows:
            lines.append(
                f"- `{r['name']}`: {r['n_short']} shorts, net ${r['net_short']:,.0f}, "
                f"WR {100*(r['wr_short'] or 0):.1f}%, exp ${r['exp_short']:.2f}"
            )
    else:
        lines.append("- No short fills in any variant (unexpected).")

    lines += [
        "",
        "## 2026 holdout (spot check)",
        "",
        "| Candidate | Trades | Net $ | Shorts n/net |",
        "| --- | --- | --- | --- |",
    ]
    for r in ranked:
        lines.append(
            f"| {r['name']} | {r['hold_trades']} | ${r['hold_net']:,.0f} | "
            f"{r['hold_n_short']}/${r['hold_net_short']:,.0f} |"
        )

    add_shorts = (
        best["name"] != "long_only"
        and best["mc_pass"] >= control["mc_pass"] - 0.005
        and best["mc_pap"] >= control["mc_pap"]
        and best["n_short"] > 0
        and (best["exp_short"] or 0) > 0
    )
    lines += [
        "",
        "## Verdict",
        "",
    ]
    if add_shorts:
        lines.append(
            f"**Candidate `{best['name']}` beats / matches long-only** "
            f"(Δpass {100*delta_pass:+.1f} pts, Δpass+payout {100*delta_pap:+.1f} pts). "
            "Worth promoting to Pine / live stack."
        )
    else:
        lines.append(
            f"**Keep long-only.** Best overall is `{best['name']}` "
            f"(pass {100*best['mc_pass']:.1f}% vs control {100*control['mc_pass']:.1f}%). "
            "Shorts add density but do not improve Lucid pass / pass+payout under verified rules. "
            "Do **not** flip `longOnly` in Pine."
        )
        if control["exp_short"] is None and short_rows:
            worst = min(short_rows, key=lambda r: r["exp_short"] or 0)
            lines.append(
                f"Short edge remains weak (example `{worst['name']}` exp "
                f"${worst['exp_short']:.2f}/trade vs long ${control['exp_long']:.2f})."
            )

    lines += ["", f"Control: `{control['name']}` pass={100*control['mc_pass']:.1f}% "
              f"pap={100*control['mc_pap']:.1f}% med_days={control['mc_med_days']:.0f}.", ""]

    REPORT.write_text("\n".join(lines))
    JSON_OUT.write_text(json.dumps(_sanitize({"rows": rows, "verdict_add_shorts": add_shorts}), indent=1))
    log.info("Report → %s", REPORT)
    print("\n".join(lines))


if __name__ == "__main__":
    main()

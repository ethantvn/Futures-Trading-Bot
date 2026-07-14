"""Phase 23 — Stage A screen: TradingSim article gold setups on GC + MGC.

User-override test (brain/Experiments/article-gold-setups.md). Full-period
grids 2021-06-11 -> 2025-12-31 (2026 stays a frozen holdout, untouched here).
Families: ema_stoch_pullback (article #4, daily_gate=True adds #2),
momentum_reversal_50 (#5), gold_round_magnet (#3, raw-anchored levels).
Article #1 (yen correlation) untestable — no 6J data.

Kill criteria (pre-registered): family dies if best combo's after-cost
expectancy <= $0 (GC) or < $2 (MGC), or < 1.5 trades/mo. Survivors only
would advance to WF + MC + holdout (Stage B).

Output: data/reports/gc/phase23_article_screen.md (+ .json)
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

from src.backtest.engine import EngineConfig
from src.backtest.fees import CostModel
from src.strategies.gold_article import (
    EmaStochPullback,
    GoldRoundMagnet,
    MomentumReversal50,
)
from src.logging_setup import setup_logging
from src.validation.walk_forward import run_full_period_grid

log = logging.getLogger("phase23")

START, END = date(2021, 6, 11), date(2025, 12, 31)
REPORT = Path("data/reports/gc/phase23_article_screen.md")
REPORT_JSON = Path("data/reports/gc/phase23_article_screen.json")

WIN_AM = (8 * 60, 12 * 60)        # article's 8:00-12:00 ET liquidity window
WIN_FULL = (3 * 60, 17 * 60)      # full liquid day, clear of maintenance

FAMILIES = [
    ("ema_stoch", EmaStochPullback, 2, {
        "touch_bars": [3, 6],
        "stop_atr": [1.0, 1.5],
        "target_r": [1.0, 1.5, 2.0],
        "entry_start_minute": [WIN_AM[0], WIN_FULL[0]],
        "entry_end_minute": [None],   # paired below
        "daily_gate": [False, True],
    }),
    ("mom_rev_50", MomentumReversal50, 2, {
        "body_atr_frac": [0.5, 0.8],
        "entry_start_minute": [WIN_AM[0], WIN_FULL[0]],
        "entry_end_minute": [None],
    }),
    ("round_magnet", GoldRoundMagnet, 2, {
        "mode": ["fade", "break"],
        "round_step": [10.0, 25.0],
        "stop_atr": [1.0, 1.5],
        "target_r": [1.0, 1.5],
        "entry_start_minute": [WIN_AM[0]],
        "entry_end_minute": [None],
    }),
]

WINDOW_END = {WIN_AM[0]: WIN_AM[1], WIN_FULL[0]: WIN_FULL[1]}


def expand_windows(space: dict) -> list[dict]:
    """Pair entry_end with entry_start (windows aren't a free cross-product)."""
    from itertools import product
    keys = [k for k in space if k != "entry_end_minute"]
    combos = []
    for vals in product(*[space[k] for k in keys]):
        d = dict(zip(keys, vals))
        d["entry_end_minute"] = WINDOW_END[d["entry_start_minute"]]
        combos.append(d)
    return combos


def load_instrument(sym: str) -> tuple[dict, dict, pl.DataFrame, dict[int, pl.DataFrame]]:
    data_cfg = yaml.safe_load(Path(f"config/data_{sym}.yaml").read_text())
    strat_cfg = yaml.safe_load(Path(f"config/strategies_{sym}.yaml").read_text())
    proc = Path(data_cfg["processed_dir"])
    def _f(df):
        return df.filter(
            (pl.col("trading_date") >= START) & (pl.col("trading_date") <= END)
        )
    exec_bars = _f(pl.read_parquet(proc / "continuous_1m.parquet"))
    sig = {
        5: _f(pl.read_parquet(proc / "continuous_5m.parquet")),
        30: _f(pl.read_parquet(proc / "continuous_30m.parquet")),
    }
    return data_cfg, strat_cfg, exec_bars, sig


def score(trades: pl.DataFrame) -> dict:
    if trades.height == 0:
        return {"trades": 0, "net": 0.0, "exp": 0.0, "wr": 0.0, "pf": 0.0, "tpm": 0.0}
    months = max((trades["trading_date"].max() - trades["trading_date"].min()).days / 30.44, 1)
    wins = trades.filter(pl.col("net_pnl") > 0)["net_pnl"].sum()
    losses = -trades.filter(pl.col("net_pnl") < 0)["net_pnl"].sum()
    return {
        "trades": trades.height,
        "net": float(trades["net_pnl"].sum()),
        "exp": float(trades["net_pnl"].mean()),
        "wr": float((trades["net_pnl"] > 0).mean()),
        "pf": float(wins / losses) if losses > 0 else float("inf"),
        "tpm": trades.height / months,
    }


def main() -> None:
    setup_logging()
    results = {}
    for sym in ("gc", "mgc"):
        data_cfg, strat_cfg, exec_bars, sig = load_instrument(sym)
        eng = strat_cfg["engine"]
        cost = CostModel(
            commission_per_side=eng["commission_per_side"],
            exchange_fees_per_side=eng["exchange_fees_per_side"],
            slippage_ticks=eng["slippage_ticks"],
            tick_size=data_cfg["tick_size"],
            point_value=data_cfg["point_value"],
        )
        rt = 2 * (eng["commission_per_side"] + eng["exchange_fees_per_side"])
        log.info("%s: point=$%.0f fees=$%.2f/RT + %d tick slip",
                 sym.upper(), data_cfg["point_value"], rt, eng["slippage_ticks"])
        for fam, cls, mtpd, space in FAMILIES:
            ecfg = EngineConfig(
                qty=1, flat_time=eng["flat_time"],
                no_entry_after=eng["no_entry_after"], max_trades_per_day=mtpd,
            )
            combos = expand_windows(space)
            grid_space = {"__combo__": combos}  # run one-by-one for pairing
            runs = []
            for i, params in enumerate(combos, 1):
                r = run_full_period_grid(
                    cls, {k: [v] for k, v in params.items()},
                    exec_bars, sig[cls.timeframe_minutes], cost, ecfg,
                )
                runs.extend(r)
            scored = [(g.params, score(g.trades)) for g in runs]
            scored.sort(key=lambda x: x[1]["net"], reverse=True)
            best_p, best_s = scored[0]
            results[f"{sym}/{fam}"] = {
                "best_params": best_p, "best": best_s,
                "all": [{"params": p, **s} for p, s in scored],
            }
            log.info("%s/%s BEST: exp=$%.2f net=$%.0f wr=%.0f%% pf=%.2f t/mo=%.1f (%d combos)",
                     sym, fam, best_s["exp"], best_s["net"], 100 * best_s["wr"],
                     best_s["pf"], best_s["tpm"], len(scored))

    # ---- report ----
    lines = [
        "# Phase 23 Stage A — TradingSim article gold setups screen",
        "",
        f"Full period {START} -> {END} (2026 = frozen holdout, untouched).",
        "Costs: GC $2.50+$1.50/side + 1 tick ($10) slip; MGC $0.75+$0.75/side + 1 tick ($1) slip.",
        "Kill bar: best-combo expectancy <= $0 (GC) / < $2 (MGC), or < 1.5 t/mo.",
        "",
        "| Family | Instrument | Best combo | Trades | t/mo | WR | PF | Exp $/trade | Net $ | Verdict |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    verdicts = {}
    for key, r in results.items():
        sym, fam = key.split("/")
        s = r["best"]
        floor = 0.0 if sym == "gc" else 2.0
        alive = s["exp"] > floor and s["tpm"] >= 1.5
        verdicts[key] = alive
        pshort = {k: v for k, v in r["best_params"].items()
                  if k in ("mode", "round_step", "target_r", "stop_atr", "daily_gate",
                            "body_atr_frac", "touch_bars", "entry_start_minute")}
        lines.append(
            f"| {fam} | {sym.upper()} | `{pshort}` | {s['trades']} | {s['tpm']:.1f} "
            f"| {100*s['wr']:.0f}% | {s['pf']:.2f} | ${s['exp']:.2f} | ${s['net']:,.0f} "
            f"| {'**SURVIVES -> Stage B**' if alive else 'KILL'} |"
        )
    lines += [
        "",
        "## Notes",
        "- Article #1 (yen 6J correlation) untestable: no yen futures data in repo.",
        "- Best-combo selection is in-sample by construction (screen only); any",
        "  survivor must clear WF 18m/6m + MC + frozen 2026 holdout in Stage B",
        "  before being called anything.",
        "- 'Highest odds of winning' is judged by expectancy, not win rate.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")
    REPORT_JSON.write_text(json.dumps(results, indent=1, default=str))
    print("\n".join(lines))


if __name__ == "__main__":
    main()

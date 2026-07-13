"""Fair Value Gap (FVG) scalp — Phase 15.

Bullish FVG: bar[i-2].high < bar[i].low (displacement gap up).
Bearish FVG: bar[i-2].low > bar[i].high (displacement gap down).

On the bar that *forms* the gap (bar i), place a LIMIT at the gap midpoint
(or near-side edge). Protective stop beyond the far gap edge (+ buffer ticks).
Target = entry ± target_r × risk. Optional VWAP-side filter and session window.
Gaps smaller than min_gap_points are ignored (cost/ambiguity floor).
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, minute_of_day, session_vwap


class FvgScalp(Strategy):
    name = "fvg_scalp"
    timeframe_minutes = 1
    default_params = {
        "min_gap_points": 30.0,       # MNQ: gap/2 risk ≥ cost+ambiguity floor
        "entry_mode": "mid",          # mid | near
        "target_r": 1.0,
        "expire_minutes": 30,
        "tick": 0.25,
        "buffer_ticks": 1,
        "entry_start_minute": 9 * 60 + 35,
        "entry_end_minute": 15 * 60,
        "vwap_filter": False,         # only long above VWAP / short below
        "min_stop_points": 15.0,      # widen stop if gap risk too tight
        "max_risk_points": None,      # optional stop-distance cap
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        tick = float(p["tick"])
        buf = float(p["buffer_ticks"]) * tick
        min_gap = float(p["min_gap_points"])
        mod = minute_of_day()

        df = df.sort("ts_utc").with_columns(
            pl.col(ADJ["high"]).shift(2).alias("_h2"),
            pl.col(ADJ["low"]).shift(2).alias("_l2"),
            pl.col(ADJ["high"]).alias("_h0"),
            pl.col(ADJ["low"]).alias("_l0"),
            session_vwap().alias("_vwap"),
            mod.alias("_mod"),
        )
        # Gap formed on current bar using completed prior bars (causal).
        bull_gap = (pl.col("_h2") < pl.col("_l0")) & pl.col("_h2").is_not_null()
        bear_gap = (pl.col("_l2") > pl.col("_h0")) & pl.col("_l2").is_not_null()
        bull_size = pl.col("_l0") - pl.col("_h2")
        bear_size = pl.col("_l2") - pl.col("_h0")

        window = (
            (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
        )
        bull_ok = bull_gap & (bull_size >= min_gap) & window
        bear_ok = bear_gap & (bear_size >= min_gap) & window

        if p["vwap_filter"]:
            bull_ok = bull_ok & (pl.col(ADJ["close"]) > pl.col("_vwap"))
            bear_ok = bear_ok & (pl.col(ADJ["close"]) < pl.col("_vwap"))

        if p["entry_mode"] == "near":
            long_entry = pl.col("_l0") - tick          # near top of bullish gap
            short_entry = pl.col("_h0") + tick
        else:
            long_entry = (pl.col("_h2") + pl.col("_l0")) / 2.0
            short_entry = (pl.col("_l2") + pl.col("_h0")) / 2.0

        long_stop = pl.col("_h2") - buf
        short_stop = pl.col("_l2") + buf
        min_stop = float(p.get("min_stop_points") or 0.0)
        # Enforce cost/ambiguity floor: stop at least min_stop away from entry
        long_stop = pl.min_horizontal(long_stop, long_entry - min_stop)
        short_stop = pl.max_horizontal(short_stop, short_entry + min_stop)

        cap = p.get("max_risk_points")
        if cap is not None:
            cap = float(cap)
            long_stop = pl.max_horizontal(long_stop, long_entry - cap)
            short_stop = pl.min_horizontal(short_stop, short_entry + cap)

        long_risk = long_entry - long_stop
        short_risk = short_stop - short_entry
        long_tgt = long_entry + float(p["target_r"]) * long_risk
        short_tgt = short_entry - float(p["target_r"]) * short_risk

        df = df.with_columns(
            bull_ok.alias("enter_long"),
            bear_ok.alias("enter_short"),
            pl.lit("limit").alias("entry_kind"),
            long_entry.alias("entry_price_long_adj"),
            short_entry.alias("entry_price_short_adj"),
            long_stop.alias("stop_long_adj"),
            short_stop.alias("stop_short_adj"),
            long_tgt.alias("target_long_adj"),
            short_tgt.alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_h2", "_l2", "_h0", "_l0", "_vwap", "_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["min_gap_points", "target_r", "expire_minutes", "entry_mode"]

"""Afternoon range breakout ("power hour", Phase 7).

Hypothesis: the 13:00-14:00 ET lunch consolidation sets a range; the breakout
into the 14:00-15:30 window rides institutional repositioning into the close.
Different time window than ORB — diversifies the daily P&L source.

Rules (signal timeframe 5m):
- Range = high/low of [range_start_minute, range_start_minute+range_minutes).
- OCO stop entries 1 tick beyond the range once it completes; protective stop
  at the opposite side; target = target_r x range risk; pendings expire after
  expire_minutes (engine also blocks entries after 15:30 and flattens 15:55).
- Optional trend filter: long only if the range-completion close is above the
  session VWAP, short only if below.
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, minute_of_day, session_vwap


class AfternoonRangeBreakout(Strategy):
    name = "afternoon_breakout"
    timeframe_minutes = 5
    default_params = {
        "range_start_minute": 13 * 60,   # 13:00 ET
        "range_minutes": 60,
        "target_r": 1.5,
        "expire_minutes": 60,
        "with_trend_filter": True,
        "tick": 0.25,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        start = p["range_start_minute"]
        end = start + p["range_minutes"]

        in_window = (mod >= start) & (mod < end)
        df = df.sort("ts_utc").with_columns(
            pl.when(in_window).then(pl.col(ADJ["high"])).otherwise(None)
            .max().over("trading_date").alias("pm_high"),
            pl.when(in_window).then(pl.col(ADJ["low"])).otherwise(None)
            .min().over("trading_date").alias("pm_low"),
            session_vwap().alias("_vwap"),
            mod.alias("_mod"),
        )
        emit = (
            (pl.col("_mod") == (end - self.timeframe_minutes))
            & pl.col("pm_high").is_not_null()
            & pl.col("pm_low").is_not_null()
        )
        long_ok = emit
        short_ok = emit
        if p["with_trend_filter"]:
            long_ok = emit & (pl.col(ADJ["close"]) > pl.col("_vwap"))
            short_ok = emit & (pl.col(ADJ["close"]) < pl.col("_vwap"))

        risk = pl.col("pm_high") - pl.col("pm_low")
        tick = p["tick"]
        df = df.with_columns(
            long_ok.fill_null(False).alias("enter_long"),
            short_ok.fill_null(False).alias("enter_short"),
            pl.lit("stop").alias("entry_kind"),
            (pl.col("pm_high") + tick).alias("entry_price_long_adj"),
            (pl.col("pm_low") - tick).alias("entry_price_short_adj"),
            (pl.col("pm_low") - tick).alias("stop_long_adj"),
            (pl.col("pm_high") + tick).alias("stop_short_adj"),
            (pl.col("pm_high") + tick + p["target_r"] * risk).alias("target_long_adj"),
            (pl.col("pm_low") - tick - p["target_r"] * risk).alias("target_short_adj"),
            pl.lit(p["expire_minutes"], dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["range_start_minute", "range_minutes", "target_r", "expire_minutes"]

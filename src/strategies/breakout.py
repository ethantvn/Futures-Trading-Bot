"""Previous-day high/low breakout.

Hypothesis: the prior RTH session's extremes are widely watched liquidity
levels; a decisive break tends to attract momentum in the break direction.

Rules (signal timeframe 15m):
- Levels: previous trading date's RTH high and low (back-adjusted, so levels
  survive contract rolls).
- At the first RTH signal bar of the day, place an OCO stop-entry pair:
  long at PDH + 1 tick, short at PDL - 1 tick, active until `expire_minutes`.
- Protective stop: `stop_atr` x ATR(atr_n) from entry.
- Target: `target_r` x the stop distance.
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day, rth_day_high_low


class PrevDayLevelBreakout(Strategy):
    name = "prev_day_hl_breakout"
    timeframe_minutes = 15
    default_params = {
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 2.0,
        "expire_minutes": 300,
        "tick": 0.25,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        df = df.sort("ts_utc")

        levels = rth_day_high_low(df).with_columns(
            pl.col("rth_high").shift(1).alias("pdh"),
            pl.col("rth_low").shift(1).alias("pdl"),
        ).select("trading_date", "pdh", "pdl")
        df = df.join(levels, on="trading_date", how="left")

        df = df.with_columns(
            atr(p["atr_n"]).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        # First RTH bar of the day whose levels exist; it completes 15 minutes
        # after 09:30, so orders go live at 09:45.
        emit = rising_edge(
            (pl.col("session") == "rth")
            & pl.col("pdh").is_not_null()
            & pl.col("pdl").is_not_null()
            & pl.col("_atr").is_not_null()
        )
        tick = p["tick"]
        stop_dist = p["stop_atr"] * pl.col("_atr")
        long_entry = pl.col("pdh") + tick
        short_entry = pl.col("pdl") - tick

        df = df.with_columns(
            emit.alias("enter_long"),
            emit.alias("enter_short"),
            pl.lit("stop").alias("entry_kind"),
            long_entry.alias("entry_price_long_adj"),
            short_entry.alias("entry_price_short_adj"),
            (long_entry - stop_dist).alias("stop_long_adj"),
            (short_entry + stop_dist).alias("stop_short_adj"),
            (long_entry + p["target_r"] * stop_dist).alias("target_long_adj"),
            (short_entry - p["target_r"] * stop_dist).alias("target_short_adj"),
            pl.lit(p["expire_minutes"], dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["stop_atr", "target_r", "expire_minutes"]

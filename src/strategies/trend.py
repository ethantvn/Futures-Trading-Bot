"""EMA-alignment trend following.

Hypothesis: persistent intraday trends exist on momentum days; a fast/slow
EMA cross filtered by a higher/longer EMA rides them while cutting chop.

Rules (signal timeframe 5m, RTH window):
- Long when EMA(fast) crosses above EMA(slow) while close > EMA(filter);
  short symmetric. Market entry on the next bar.
- Protective stop: `stop_atr` x ATR(atr_n). Target: `target_r` x stop
  distance (set target_r null/large for pure trend exit).
- Exit also on the opposite cross (signal exit).
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, atr, ema, minute_of_day


class EmaTrend(Strategy):
    name = "ema_trend"
    timeframe_minutes = 5
    default_params = {
        "ema_fast": 9,
        "ema_slow": 21,
        "ema_filter": 50,
        "atr_n": 14,
        "stop_atr": 2.0,
        "target_r": 3.0,
        "entry_start_minute": 10 * 60,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        df = df.sort("ts_utc").with_columns(
            ema(ADJ["close"], p["ema_fast"]).alias("_ef"),
            ema(ADJ["close"], p["ema_slow"]).alias("_es"),
            ema(ADJ["close"], p["ema_filter"]).alias("_efil"),
            atr(p["atr_n"]).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        above = pl.col("_ef") > pl.col("_es")
        cross_up = above & ~above.shift(1, fill_value=False)
        cross_dn = ~above & above.shift(1, fill_value=True)
        window = (pl.col("session") == "rth") & (pl.col("_mod") >= p["entry_start_minute"])

        stop_dist = p["stop_atr"] * pl.col("_atr")
        px = pl.col(ADJ["close"])  # reference for stop/target around next-bar market fill
        df = df.with_columns(
            (window & cross_up & (px > pl.col("_efil"))).alias("enter_long"),
            (window & cross_dn & (px < pl.col("_efil"))).alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (px - stop_dist).alias("stop_long_adj"),
            (px + stop_dist).alias("stop_short_adj"),
            (px + p["target_r"] * stop_dist).alias("target_long_adj"),
            (px - p["target_r"] * stop_dist).alias("target_short_adj"),
            cross_dn.alias("exit_long"),
            cross_up.alias("exit_short"),
            pl.lit(10, dtype=pl.Int64).alias("expire_minutes"),  # market orders fill immediately
        ).drop("_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["ema_fast", "ema_slow", "ema_filter", "stop_atr", "target_r"]

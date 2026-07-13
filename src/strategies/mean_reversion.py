"""Bollinger Band mean reversion, range-regime filtered.

Hypothesis: when the market is NOT trending (low ADX), closes stretched
outside the Bollinger bands revert toward the mean. This is the deliberate
counter-hypothesis to the four momentum strategies.

Rules (signal timeframe 5m, RTH window):
- Regime: ADX(adx_n) < adx_max.
- Short when the bar CLOSES above the upper band; long when it closes below
  the lower band (market entry next bar).
- Protective stop: `stop_atr` x ATR beyond the close.
- Target: the middle band (frozen at signal time — interpretable, causal).
- Engine max_hold closes stale trades (configured per strategy).
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, adx, atr, bollinger, minute_of_day


class BollingerMeanReversion(Strategy):
    name = "bollinger_mean_reversion"
    timeframe_minutes = 5
    default_params = {
        "bb_n": 20,
        "bb_k": 2.0,
        "adx_n": 14,
        "adx_max": 20.0,
        "atr_n": 14,
        "stop_atr": 1.5,
        "entry_start_minute": 10 * 60,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mid, upper, lower = bollinger(p["bb_n"], p["bb_k"])
        df = df.sort("ts_utc").with_columns(
            mid.alias("_mid"), upper.alias("_up"), lower.alias("_lo"),
            adx(p["adx_n"]).alias("_adx"),
            atr(p["atr_n"]).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= p["entry_start_minute"])
            & (pl.col("_adx") < p["adx_max"])
            & pl.col("_up").is_not_null()
        )
        c = pl.col(ADJ["close"])
        stretch_short = window & (c > pl.col("_up"))
        stretch_long = window & (c < pl.col("_lo"))

        stop_dist = p["stop_atr"] * pl.col("_atr")
        df = df.with_columns(
            rising_edge(stretch_long).alias("enter_long"),
            rising_edge(stretch_short).alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (c - stop_dist).alias("stop_long_adj"),
            (c + stop_dist).alias("stop_short_adj"),
            pl.col("_mid").alias("target_long_adj"),
            pl.col("_mid").alias("target_short_adj"),
            pl.lit(10, dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["bb_n", "bb_k", "adx_max", "stop_atr"]

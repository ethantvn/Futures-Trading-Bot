"""VWAP pullback in trend.

Hypothesis: on trending days, intraday retracements to the session VWAP find
passive buyers/sellers defending the average price, resuming the trend.

Rules (signal timeframe 5m, RTH only between entry_start and no-entry time):
- Trend up: close > VWAP and EMA(fast) > EMA(slow).
- Setup (long): while trend up, the bar's low touches/crosses VWAP.
  On the setup's rising edge, place a LIMIT buy at the current VWAP.
- Protective stop: `stop_atr` x ATR below the limit; target `target_r` x stop
  distance above. Shorts symmetric. Pending expires after `expire_minutes`.
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, ema, minute_of_day, session_vwap


class VwapPullback(Strategy):
    name = "vwap_pullback"
    timeframe_minutes = 5
    default_params = {
        "ema_fast": 20,
        "ema_slow": 50,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 2.0,
        "expire_minutes": 45,
        "entry_start_minute": 10 * 60,  # no setups before 10:00 ET
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        df = df.sort("ts_utc").with_columns(
            session_vwap().alias("_vwap"),
            ema(ADJ["close"], p["ema_fast"]).alias("_ef"),
            ema(ADJ["close"], p["ema_slow"]).alias("_es"),
            atr(p["atr_n"]).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        window = (pl.col("session") == "rth") & (pl.col("_mod") >= p["entry_start_minute"])
        trend_up = (pl.col(ADJ["close"]) > pl.col("_vwap")) & (pl.col("_ef") > pl.col("_es"))
        trend_dn = (pl.col(ADJ["close"]) < pl.col("_vwap")) & (pl.col("_ef") < pl.col("_es"))
        pull_long = window & trend_up & (pl.col(ADJ["low"]) <= pl.col("_vwap"))
        pull_short = window & trend_dn & (pl.col(ADJ["high"]) >= pl.col("_vwap"))

        stop_dist = p["stop_atr"] * pl.col("_atr")
        df = df.with_columns(
            rising_edge(pull_long).alias("enter_long"),
            rising_edge(pull_short).alias("enter_short"),
            pl.lit("limit").alias("entry_kind"),
            pl.col("_vwap").alias("entry_price_long_adj"),
            pl.col("_vwap").alias("entry_price_short_adj"),
            (pl.col("_vwap") - stop_dist).alias("stop_long_adj"),
            (pl.col("_vwap") + stop_dist).alias("stop_short_adj"),
            (pl.col("_vwap") + p["target_r"] * stop_dist).alias("target_long_adj"),
            (pl.col("_vwap") - p["target_r"] * stop_dist).alias("target_short_adj"),
            pl.lit(p["expire_minutes"], dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["ema_fast", "ema_slow", "stop_atr", "target_r", "expire_minutes"]

"""Gold session VWAP strategies (Phase 11).

Trend continuation and mean reversion using cumulative session VWAP on
Globex/RTH bars. Stops sized in ATR multiples; optional max_risk_points
cap for Lucid 50K.
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, ema, minute_of_day, session_vwap


class GcVwapTrend(Strategy):
    name = "gc_vwap_trend"
    timeframe_minutes = 5
    default_params = {
        "ema_fast": 20,
        "ema_slow": 50,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 60,
        "entry_start_minute": 9 * 60,   # after London/NY overlap begins
        "max_risk_points": 4.0,
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
        window = pl.col("_mod") >= p["entry_start_minute"]
        trend_up = (pl.col(ADJ["close"]) > pl.col("_vwap")) & (pl.col("_ef") > pl.col("_es"))
        trend_dn = (pl.col(ADJ["close"]) < pl.col("_vwap")) & (pl.col("_ef") < pl.col("_es"))
        brk_long = window & trend_up & rising_edge(pl.col(ADJ["close"]) > pl.col("_vwap"))
        brk_short = window & trend_dn & rising_edge(pl.col(ADJ["close"]) < pl.col("_vwap"))
        stop_dist = pl.min_horizontal(
            p["stop_atr"] * pl.col("_atr"),
            pl.lit(float(p["max_risk_points"])) if p.get("max_risk_points") else p["stop_atr"] * pl.col("_atr"),
        )
        df = df.with_columns(
            brk_long.alias("enter_long"),
            brk_short.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (pl.col(ADJ["close"]) - stop_dist).alias("stop_long_adj"),
            (pl.col(ADJ["close"]) + stop_dist).alias("stop_short_adj"),
            (pl.col(ADJ["close"]) + p["target_r"] * stop_dist).alias("target_long_adj"),
            (pl.col(ADJ["close"]) - p["target_r"] * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)


class GcVwapReversion(Strategy):
    name = "gc_vwap_reversion"
    timeframe_minutes = 5
    default_params = {
        "atr_n": 14,
        "extension_atr": 2.0,         # fade when price extends this far from VWAP
        "stop_atr": 1.0,
        "target_r": 1.0,
        "expire_minutes": 45,
        "entry_start_minute": 9 * 60,
        "max_risk_points": 4.0,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        df = df.sort("ts_utc").with_columns(
            session_vwap().alias("_vwap"),
            atr(p["atr_n"]).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        window = pl.col("_mod") >= p["entry_start_minute"]
        ext = p["extension_atr"] * pl.col("_atr")
        fade_long = window & (pl.col(ADJ["close"]) < pl.col("_vwap") - ext)
        fade_short = window & (pl.col(ADJ["close"]) > pl.col("_vwap") + ext)
        stop_dist = pl.min_horizontal(
            p["stop_atr"] * pl.col("_atr"),
            pl.lit(float(p["max_risk_points"])) if p.get("max_risk_points") else p["stop_atr"] * pl.col("_atr"),
        )
        df = df.with_columns(
            rising_edge(fade_long).alias("enter_long"),
            rising_edge(fade_short).alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (pl.col(ADJ["close"]) - stop_dist).alias("stop_long_adj"),
            (pl.col(ADJ["close"]) + stop_dist).alias("stop_short_adj"),
            (pl.col(ADJ["close"]) + p["target_r"] * stop_dist).alias("target_long_adj"),
            (pl.col(ADJ["close"]) - p["target_r"] * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)

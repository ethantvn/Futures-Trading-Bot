"""VWAP band scalping — Phase 15.

Two modes:
  reversion — fade touches of VWAP ± k·ATR back toward VWAP
  pullback  — enter at VWAP in the direction of session trend (close vs VWAP
              open bias after warmup)

Stops sized in ATR multiples with optional max_risk_points cap.
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day, session_vwap


class VwapBandScalp(Strategy):
    name = "vwap_band_scalp"
    timeframe_minutes = 1
    default_params = {
        "mode": "reversion",          # reversion | pullback
        "band_k": 1.5,
        "atr_n": 14,
        "stop_atr": 1.0,
        "target_r": 1.0,
        "expire_minutes": 20,
        "entry_start_minute": 9 * 60 + 45,
        "entry_end_minute": 15 * 60,
        "max_risk_points": None,
        "min_stop_points": 10.0,      # MNQ ambiguity/cost floor
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        df = df.sort("ts_utc").with_columns(
            session_vwap().alias("_vwap"),
            atr(int(p["atr_n"])).alias("_atr"),
            mod.alias("_mod"),
        )
        band = float(p["band_k"]) * pl.col("_atr")
        upper = pl.col("_vwap") + band
        lower = pl.col("_vwap") - band
        window = (
            (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
        )

        stop_dist = pl.max_horizontal(
            float(p["stop_atr"]) * pl.col("_atr"),
            pl.lit(float(p["min_stop_points"])),
        )
        if p.get("max_risk_points") is not None:
            stop_dist = pl.min_horizontal(stop_dist, pl.lit(float(p["max_risk_points"])))

        if p["mode"] == "pullback":
            # Trend: price above VWAP → long pullbacks to VWAP; below → short
            trend_up = pl.col(ADJ["close"]) > pl.col("_vwap")
            trend_dn = pl.col(ADJ["close"]) < pl.col("_vwap")
            touch_vwap = (
                (pl.col(ADJ["low"]) <= pl.col("_vwap"))
                & (pl.col(ADJ["high"]) >= pl.col("_vwap"))
            )
            long_sig = window & trend_up & rising_edge(touch_vwap)
            short_sig = window & trend_dn & rising_edge(touch_vwap)
            entry_l = pl.col("_vwap")
            entry_s = pl.col("_vwap")
        else:
            # Reversion: fade outer band
            hit_upper = pl.col(ADJ["high"]) >= upper
            hit_lower = pl.col(ADJ["low"]) <= lower
            long_sig = window & rising_edge(hit_lower)
            short_sig = window & rising_edge(hit_upper)
            entry_l = lower
            entry_s = upper

        df = df.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("limit").alias("entry_kind"),
            entry_l.alias("entry_price_long_adj"),
            entry_s.alias("entry_price_short_adj"),
            (entry_l - stop_dist).alias("stop_long_adj"),
            (entry_s + stop_dist).alias("stop_short_adj"),
            (entry_l + float(p["target_r"]) * stop_dist).alias("target_long_adj"),
            (entry_s - float(p["target_r"]) * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_vwap", "_atr", "_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["band_k", "stop_atr", "target_r", "mode", "expire_minutes"]

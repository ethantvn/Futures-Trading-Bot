"""VWAP strategies gated by market structure — Phase 16.

mode=reversion: fade VWAP ± band only in range regime
mode=pullback: enter at VWAP with trend only in up/down regime
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import (
    ADJ,
    atr,
    ema,
    minute_of_day,
    session_vwap,
    structure_regime,
)


class StructureGatedVwap(Strategy):
    name = "structure_gated_vwap"
    timeframe_minutes = 5
    default_params = {
        "mode": "reversion",  # reversion | pullback
        "pivot_n": 3,
        "band_atr": 1.0,
        "ema_fast": 20,
        "ema_slow": 50,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 60,
        "entry_start_minute": 10 * 60,
        "entry_end_minute": 15 * 60,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        struct = structure_regime(df, pivot_n=int(p["pivot_n"]))
        df = (
            df.sort("ts_utc")
            .join(struct.select("ts_utc", "structure_regime"), on="ts_utc", how="left")
            .with_columns(
                session_vwap().alias("_vwap"),
                atr(int(p["atr_n"])).alias("_atr"),
                ema(ADJ["close"], int(p["ema_fast"])).alias("_ef"),
                ema(ADJ["close"], int(p["ema_slow"])).alias("_es"),
                minute_of_day().alias("_mod"),
            )
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
        )
        stop_dist = float(p["stop_atr"]) * pl.col("_atr")
        band = float(p["band_atr"]) * pl.col("_atr")

        if p["mode"] == "pullback":
            # Trend pullback only in directional regimes
            regime_ok_long = pl.col("structure_regime") == "up"
            regime_ok_short = pl.col("structure_regime") == "down"
            trend_up = (pl.col(ADJ["close"]) > pl.col("_vwap")) & (
                pl.col("_ef") > pl.col("_es")
            )
            trend_dn = (pl.col(ADJ["close"]) < pl.col("_vwap")) & (
                pl.col("_ef") < pl.col("_es")
            )
            long_sig = (
                window
                & regime_ok_long
                & trend_up
                & rising_edge(pl.col(ADJ["low"]) <= pl.col("_vwap"))
            )
            short_sig = (
                window
                & regime_ok_short
                & trend_dn
                & rising_edge(pl.col(ADJ["high"]) >= pl.col("_vwap"))
            )
            entry_l = pl.col("_vwap")
            entry_s = pl.col("_vwap")
        else:
            # Reversion fades only in range
            regime_ok = pl.col("structure_regime") == "range"
            upper = pl.col("_vwap") + band
            lower = pl.col("_vwap") - band
            long_sig = window & regime_ok & rising_edge(pl.col(ADJ["low"]) <= lower)
            short_sig = window & regime_ok & rising_edge(pl.col(ADJ["high"]) >= upper)
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
        ).drop("_vwap", "_atr", "_ef", "_es", "_mod", "structure_regime")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["mode", "band_atr", "stop_atr", "target_r", "pivot_n"]

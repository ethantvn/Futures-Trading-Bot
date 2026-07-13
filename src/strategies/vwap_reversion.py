"""VWAP stretch reversion using ATR-relative bands."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, adx, atr, minute_of_day, session_vwap


class VwapReversion(Strategy):
    name = "vwap_reversion"
    timeframe_minutes = 5
    default_params = {
        "band_k": 2.0,
        "atr_n": 14,
        "stop_atr": 1.25,
        "target_r": 1.0,
        "expire_minutes": 60,
        "adx_n": 14,
        "adx_max": 25.0,
        "entry_start_minute": 10 * 60,
        "entry_end_minute": 14 * 60,
        "skip_weekdays": [],
        "long_only": False,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = df.sort("ts_utc").with_columns(
            session_vwap().alias("_vwap"),
            atr(int(p["atr_n"])).alias("_atr"),
            adx(int(p["adx_n"])).alias("_adx"),
            minute_of_day().alias("_mod"),
        )
        band = float(p["band_k"]) * pl.col("_atr")
        adx_gate = (
            pl.lit(True)
            if float(p["adx_max"]) <= 0
            else (pl.col("_adx") < float(p["adx_max"]))
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & adx_gate
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        c = pl.col(ADJ["close"])
        long_sig = rising_edge(window & (c < pl.col("_vwap") - band)).fill_null(False)
        short_sig = rising_edge(window & (c > pl.col("_vwap") + band)).fill_null(False)
        if p["long_only"]:
            short_sig = pl.lit(False)

        stop_dist = float(p["stop_atr"]) * pl.col("_atr")
        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (c - stop_dist).alias("stop_long_adj"),
            (c + stop_dist).alias("stop_short_adj"),
            pl.col("_vwap").alias("target_long_adj"),
            pl.col("_vwap").alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_vwap", "_atr", "_adx", "_mod")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["band_k", "stop_atr", "adx_max", "entry_start_minute", "entry_end_minute"]

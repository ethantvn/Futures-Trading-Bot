"""Donchian channel breakout with ATR risk sizing."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, adx, atr, donchian, minute_of_day


class DonchianBreakout(Strategy):
    name = "donchian_breakout"
    timeframe_minutes = 5
    default_params = {
        "channel_n": 20,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 120,
        "entry_start_minute": 10 * 60,
        "entry_end_minute": 15 * 60,
        "adx_n": 14,
        "adx_min": 0.0,
        "skip_weekdays": [],
        "long_only": False,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        d_hi, d_lo = donchian(int(p["channel_n"]))
        out = df.sort("ts_utc").with_columns(
            d_hi.shift(1).alias("_dhi_prev"),
            d_lo.shift(1).alias("_dlo_prev"),
            atr(int(p["atr_n"])).alias("_atr"),
            adx(int(p["adx_n"])).alias("_adx"),
            minute_of_day().alias("_mod"),
        )
        adx_gate = (
            pl.lit(True)
            if float(p["adx_min"]) <= 0
            else (pl.col("_adx") >= float(p["adx_min"]))
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & adx_gate
            & pl.col("_dhi_prev").is_not_null()
            & pl.col("_dlo_prev").is_not_null()
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        c = pl.col(ADJ["close"])
        long_sig = rising_edge(window & (c > pl.col("_dhi_prev"))).fill_null(False)
        short_sig = rising_edge(window & (c < pl.col("_dlo_prev"))).fill_null(False)
        if p["long_only"]:
            short_sig = pl.lit(False)

        stop_dist = float(p["stop_atr"]) * pl.col("_atr")
        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (c - stop_dist).alias("stop_long_adj"),
            (c + stop_dist).alias("stop_short_adj"),
            (c + float(p["target_r"]) * stop_dist).alias("target_long_adj"),
            (c - float(p["target_r"]) * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_dhi_prev", "_dlo_prev", "_atr", "_adx", "_mod")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["channel_n", "stop_atr", "target_r", "adx_min"]

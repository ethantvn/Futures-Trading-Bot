"""MACD histogram momentum entries."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, atr, macd, minute_of_day


class MacdMomentum(Strategy):
    name = "macd_momentum"
    timeframe_minutes = 5
    default_params = {
        "fast": 12,
        "slow": 26,
        "signal": 9,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 90,
        "entry_start_minute": 10 * 60,
        "entry_end_minute": 14 * 60,
        "skip_weekdays": [],
        "hist_cross": True,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        m_line, m_sig, m_hist = macd(int(p["fast"]), int(p["slow"]), int(p["signal"]))
        out = df.sort("ts_utc").with_columns(
            m_line.alias("_macd"),
            m_sig.alias("_sig"),
            m_hist.alias("_hist"),
            atr(int(p["atr_n"])).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        if p["hist_cross"]:
            prev = pl.col("_hist").shift(1)
            long_sig = (window & (pl.col("_hist") > 0) & (prev <= 0)).fill_null(False)
            short_sig = (window & (pl.col("_hist") < 0) & (prev >= 0)).fill_null(False)
        else:
            above = pl.col("_macd") > pl.col("_sig")
            long_sig = (window & above & ~above.shift(1, fill_value=False)).fill_null(False)
            short_sig = (window & ~above & above.shift(1, fill_value=True)).fill_null(False)

        c = pl.col(ADJ["close"])
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
        ).drop("_macd", "_sig", "_hist", "_atr", "_mod")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["fast", "slow", "signal", "stop_atr", "target_r", "hist_cross"]

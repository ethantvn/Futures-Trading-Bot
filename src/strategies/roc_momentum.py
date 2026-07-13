"""Rate-of-change momentum with volume confirmation."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day, roc


class RocMomentum(Strategy):
    name = "roc_momentum"
    timeframe_minutes = 5
    default_params = {
        "roc_n": 10,
        "roc_thresh": 0.15,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 90,
        "entry_start_minute": 10 * 60,
        "entry_end_minute": 14 * 60,
        "vol_mult": 1.5,
        "vol_lookback": 20,
        "skip_weekdays": [],
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = df.sort("ts_utc").with_columns(
            roc(int(p["roc_n"])).alias("_roc"),
            atr(int(p["atr_n"])).alias("_atr"),
            pl.col("volume").rolling_mean(int(p["vol_lookback"])).alias("_vol_ma"),
            minute_of_day().alias("_mod"),
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & pl.col("_vol_ma").is_not_null()
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        vol_ok = pl.col("volume") > float(p["vol_mult"]) * pl.col("_vol_ma")
        long_sig = rising_edge(window & vol_ok & (pl.col("_roc") > float(p["roc_thresh"]))).fill_null(False)
        short_sig = rising_edge(window & vol_ok & (pl.col("_roc") < -float(p["roc_thresh"]))).fill_null(False)

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
        ).drop("_roc", "_atr", "_vol_ma", "_mod")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["roc_n", "roc_thresh", "vol_mult", "stop_atr", "target_r"]

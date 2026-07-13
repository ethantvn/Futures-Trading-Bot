"""Opening-range failed-breakout fade."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, minute_of_day

RTH_OPEN_MIN = 9 * 60 + 30


class OpeningRangeFade(Strategy):
    name = "opening_range_fade"
    timeframe_minutes = 5
    default_params = {
        "range_minutes": 30,
        "target_r": 1.0,
        "stop_buffer_ticks": 2,
        "expire_minutes": 90,
        "tick": 0.25,
        "long_only": False,
        "skip_weekdays": [],
        "entry_end_minute": 14 * 60,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        range_end = RTH_OPEN_MIN + int(p["range_minutes"])
        in_range_window = (mod >= RTH_OPEN_MIN) & (mod < range_end)
        stop_buf = float(p["stop_buffer_ticks"]) * float(p["tick"])

        out = df.sort("ts_utc").with_columns(
            pl.when(in_range_window).then(pl.col(ADJ["high"])).otherwise(None)
            .max().over("trading_date").alias("or_high"),
            pl.when(in_range_window).then(pl.col(ADJ["low"])).otherwise(None)
            .min().over("trading_date").alias("or_low"),
            mod.alias("_mod"),
        )

        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= range_end)
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & pl.col("or_high").is_not_null()
            & pl.col("or_low").is_not_null()
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        reclaim_short = (
            (pl.col(ADJ["high"]) >= pl.col("or_high"))
            & (pl.col(ADJ["close"]) < pl.col("or_high"))
        )
        reclaim_long = (
            (pl.col(ADJ["low"]) <= pl.col("or_low"))
            & (pl.col(ADJ["close"]) > pl.col("or_low"))
        )
        short_sig = (window & rising_edge(reclaim_short)).fill_null(False)
        long_sig = (window & rising_edge(reclaim_long)).fill_null(False)
        if p["long_only"]:
            short_sig = pl.lit(False)

        stop_long = pl.col("or_low") - stop_buf
        stop_short = pl.col("or_high") + stop_buf
        risk_long = pl.col("or_low") - stop_long
        risk_short = stop_short - pl.col("or_high")
        t_r = float(p["target_r"])

        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            stop_long.alias("stop_long_adj"),
            stop_short.alias("stop_short_adj"),
            (pl.col("or_low") + t_r * risk_long).alias("target_long_adj"),
            (pl.col("or_high") - t_r * risk_short).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["range_minutes", "target_r", "stop_buffer_ticks", "entry_end_minute"]

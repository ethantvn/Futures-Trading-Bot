"""ATR breakout from RTH open anchor."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day


class AtrBreakout(Strategy):
    name = "atr_breakout"
    timeframe_minutes = 5
    default_params = {
        "atr_n": 14,
        "break_atr": 1.0,
        "stop_atr": 1.0,
        "target_r": 1.5,
        "expire_minutes": 120,
        "entry_start_minute": 9 * 60 + 35,
        "entry_end_minute": 12 * 60,
        "skip_weekdays": [],
        "long_only": False,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = df.sort("ts_utc").with_columns(
            minute_of_day().alias("_mod"),
            atr(int(p["atr_n"])).alias("_atr"),
        )
        out = out.with_columns(
            pl.when(pl.col("session") == "rth").then(pl.col(ADJ["open"])).otherwise(None)
            .first().over("trading_date").alias("_rth_open")
        )
        up = pl.col("_rth_open") + float(p["break_atr"]) * pl.col("_atr")
        dn = pl.col("_rth_open") - float(p["break_atr"]) * pl.col("_atr")
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & pl.col("_rth_open").is_not_null()
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        brk_long = (pl.col(ADJ["high"]) >= up) & (pl.col(ADJ["close"]) > up)
        brk_short = (pl.col(ADJ["low"]) <= dn) & (pl.col(ADJ["close"]) < dn)
        long_sig = rising_edge(window & brk_long).fill_null(False)
        short_sig = rising_edge(window & brk_short).fill_null(False)
        if p["long_only"]:
            short_sig = pl.lit(False)

        c = pl.col(ADJ["close"])
        atr_stop = float(p["stop_atr"]) * pl.col("_atr")
        stop_long = pl.max_horizontal(pl.col("_rth_open"), c - atr_stop)
        stop_short = pl.min_horizontal(pl.col("_rth_open"), c + atr_stop)
        risk_long = c - stop_long
        risk_short = stop_short - c

        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            stop_long.alias("stop_long_adj"),
            stop_short.alias("stop_short_adj"),
            (c + float(p["target_r"]) * risk_long).alias("target_long_adj"),
            (c - float(p["target_r"]) * risk_short).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod", "_atr", "_rth_open")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["break_atr", "stop_atr", "target_r", "entry_start_minute", "entry_end_minute"]

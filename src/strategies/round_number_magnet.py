"""Round-number magnet fade/break — Phase 16."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day, nearest_round


class RoundNumberMagnet(Strategy):
    name = "round_number_magnet"
    timeframe_minutes = 5
    default_params = {
        "mode": "fade",  # fade | break
        "round_step": 100.0,
        "atr_n": 14,
        "stop_atr": 1.25,
        "target_r": 1.0,
        "expire_minutes": 60,
        "entry_start_minute": 9 * 60 + 35,
        "entry_end_minute": 11 * 60,  # first 90m RTH focus
        "tick": 0.25,
        "touch_ticks": 4,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        tick = float(p["tick"])
        step = float(p["round_step"])
        touch = int(p["touch_ticks"]) * tick
        df = df.sort("ts_utc").with_columns(
            nearest_round(pl.col(ADJ["close"]), step).alias("_rnd"),
            atr(int(p["atr_n"])).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
        )
        near = (pl.col(ADJ["close"]) - pl.col("_rnd")).abs() <= touch
        stop_dist = float(p["stop_atr"]) * pl.col("_atr")

        if p["mode"] == "break":
            long_sig = window & rising_edge(
                (pl.col(ADJ["close"]) > pl.col("_rnd") + touch)
                & (pl.col(ADJ["low"]) <= pl.col("_rnd") + touch)
            )
            short_sig = window & rising_edge(
                (pl.col(ADJ["close"]) < pl.col("_rnd") - touch)
                & (pl.col(ADJ["high"]) >= pl.col("_rnd") - touch)
            )
            entry_l = pl.col("_rnd") + touch
            entry_s = pl.col("_rnd") - touch
            kind = "stop"
        else:
            long_sig = window & near & rising_edge(
                (pl.col(ADJ["low"]) <= pl.col("_rnd"))
                & (pl.col(ADJ["close"]) > pl.col("_rnd"))
            )
            short_sig = window & near & rising_edge(
                (pl.col(ADJ["high"]) >= pl.col("_rnd"))
                & (pl.col(ADJ["close"]) < pl.col("_rnd"))
            )
            entry_l = pl.col("_rnd")
            entry_s = pl.col("_rnd")
            kind = "limit"

        df = df.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit(kind).alias("entry_kind"),
            entry_l.alias("entry_price_long_adj"),
            entry_s.alias("entry_price_short_adj"),
            (entry_l - stop_dist).alias("stop_long_adj"),
            (entry_s + stop_dist).alias("stop_short_adj"),
            (entry_l + float(p["target_r"]) * stop_dist).alias("target_long_adj"),
            (entry_s - float(p["target_r"]) * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_rnd", "_atr", "_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["mode", "round_step", "stop_atr", "target_r"]

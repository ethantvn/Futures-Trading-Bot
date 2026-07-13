"""Session POC / value-area mean-reversion and breakout — Phase 16."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day, session_volume_profile


class PocValueArea(Strategy):
    name = "poc_value_area"
    timeframe_minutes = 5
    default_params = {
        "mode": "reversion",  # reversion | breakout
        "bin_size": 10.0,  # MNQ points per profile bin
        "va_pct": 0.70,
        "atr_n": 14,
        "stop_atr": 1.25,
        "target_r": 1.5,
        "expire_minutes": 90,
        "entry_start_minute": 10 * 60,  # let profile mature
        "entry_end_minute": 15 * 60,
        "tick": 0.25,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        tick = float(p["tick"])
        prof = session_volume_profile(
            df, bin_size=float(p["bin_size"]), va_pct=float(p["va_pct"])
        )
        df = prof.with_columns(
            atr(int(p["atr_n"])).alias("_atr"),
            minute_of_day().alias("_mod"),
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & pl.col("poc").is_not_null()
            & pl.col("vah").is_not_null()
        )
        stop_dist = float(p["stop_atr"]) * pl.col("_atr")

        if p["mode"] == "breakout":
            long_sig = window & rising_edge(pl.col(ADJ["close"]) > pl.col("vah") + tick)
            short_sig = window & rising_edge(pl.col(ADJ["close"]) < pl.col("val") - tick)
            entry_l = pl.col("vah") + tick
            entry_s = pl.col("val") - tick
            # stop back toward POC
            stop_l = pl.col("poc")
            stop_s = pl.col("poc")
            tgt_l = entry_l + float(p["target_r"]) * (entry_l - stop_l)
            tgt_s = entry_s - float(p["target_r"]) * (stop_s - entry_s)
            kind = "stop"
        else:
            # Fade VAH/VAL back to POC
            long_sig = window & rising_edge(
                (pl.col(ADJ["low"]) <= pl.col("val"))
                & (pl.col(ADJ["close"]) >= pl.col("val"))
            )
            short_sig = window & rising_edge(
                (pl.col(ADJ["high"]) >= pl.col("vah"))
                & (pl.col(ADJ["close"]) <= pl.col("vah"))
            )
            entry_l = pl.col("val")
            entry_s = pl.col("vah")
            stop_l = entry_l - stop_dist
            stop_s = entry_s + stop_dist
            tgt_l = pl.col("poc")
            tgt_s = pl.col("poc")
            kind = "limit"

        df = df.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit(kind).alias("entry_kind"),
            entry_l.alias("entry_price_long_adj"),
            entry_s.alias("entry_price_short_adj"),
            stop_l.alias("stop_long_adj"),
            stop_s.alias("stop_short_adj"),
            tgt_l.alias("target_long_adj"),
            tgt_s.alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_atr", "_mod", "poc", "vah", "val")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["mode", "bin_size", "stop_atr", "target_r"]

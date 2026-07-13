"""Overnight high/low break or fade at RTH — Phase 16."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, minute_of_day, overnight_levels, prior_day_hl


class OvernightLevels(Strategy):
    name = "overnight_levels"
    timeframe_minutes = 5
    default_params = {
        "mode": "break",  # break | fade
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 120,
        "tick": 0.25,
        "entry_start_minute": 9 * 60 + 35,
        "entry_end_minute": 12 * 60,
        "require_pdh_confluence": False,
        "confluence_ticks": 8,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        tick = float(p["tick"])
        on = overnight_levels(df)
        pdhl = prior_day_hl(df)
        df = (
            df.sort("ts_utc")
            .join(on, on="trading_date", how="left")
            .join(pdhl, on="trading_date", how="left")
            .with_columns(
                atr(int(p["atr_n"])).alias("_atr"),
                minute_of_day().alias("_mod"),
            )
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & pl.col("on_high").is_not_null()
        )
        stop_dist = float(p["stop_atr"]) * pl.col("_atr")
        conf = int(p["confluence_ticks"]) * tick

        if p["require_pdh_confluence"]:
            near_pdh = (pl.col("on_high") - pl.col("pdh")).abs() <= conf
            near_pdl = (pl.col("on_low") - pl.col("pdl")).abs() <= conf
        else:
            near_pdh = pl.lit(True)
            near_pdl = pl.lit(True)

        if p["mode"] == "fade":
            # Fade rejection of overnight extremes
            long_sig = (
                window
                & near_pdl
                & rising_edge(
                    (pl.col(ADJ["low"]) <= pl.col("on_low"))
                    & (pl.col(ADJ["close"]) > pl.col("on_low"))
                )
            )
            short_sig = (
                window
                & near_pdh
                & rising_edge(
                    (pl.col(ADJ["high"]) >= pl.col("on_high"))
                    & (pl.col(ADJ["close"]) < pl.col("on_high"))
                )
            )
            entry_l = pl.col("on_low")
            entry_s = pl.col("on_high")
            kind = "limit"
        else:
            long_sig = (
                window
                & near_pdh
                & rising_edge(pl.col(ADJ["high"]) >= pl.col("on_high") + tick)
            )
            short_sig = (
                window
                & near_pdl
                & rising_edge(pl.col(ADJ["low"]) <= pl.col("on_low") - tick)
            )
            # Stop entries at overnight break levels
            entry_l = pl.col("on_high") + tick
            entry_s = pl.col("on_low") - tick
            kind = "stop"
            # Emit OCO once per day at first window bar with levels (like PDH)
            # rising_edge of break is fine for momentum continuation

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
        ).drop("_atr", "_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["mode", "stop_atr", "target_r", "expire_minutes"]

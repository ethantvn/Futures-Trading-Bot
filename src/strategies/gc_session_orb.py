"""Gold-native session range breakout (Phase 11).

Parameterized opening-range anchor (COMEX ~8:20, London ~5:30, NY 9:30,
Globex ~18:00 ET). Same OCO stop-entry structure as equity ORB but the
window start is configurable. Optional width band and stop-distance cap
for Lucid 50K sizing discipline ($100/pt full-size GC).
"""
from __future__ import annotations

from datetime import date

import polars as pl

from src.data.macro_calendar import macro_event_dates
from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import minute_of_day, prev_day_context


class GcSessionOrb(Strategy):
    name = "gc_session_orb"
    timeframe_minutes = 5
    default_params = {
        "anchor_minute": 8 * 60 + 20,   # COMEX pit-legacy open ~8:20 ET
        "range_minutes": 30,
        "target_r": 1.0,
        "expire_minutes": 120,
        "tick": 0.10,
        "min_width_ratio": 0.0,
        "max_width_ratio": 1e9,
        "vol_ref_days": 14,
        "skip_weekdays": (),
        "max_risk_points": None,        # cap stop distance in price points
        "long_only": False,
        "skip_macro_days": False,
        "macro_events": "all",
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        anchor = int(p["anchor_minute"])
        range_end = anchor + int(p["range_minutes"])

        in_range = (mod >= anchor) & (mod < range_end)
        df = df.sort("ts_utc").with_columns(
            pl.when(in_range).then(pl.col("open_adj")).alias("_or_o"),
            pl.when(in_range).then(pl.col("high_adj")).alias("_or_h"),
            pl.when(in_range).then(pl.col("low_adj")).alias("_or_l"),
            mod.alias("_mod"),
        )
        df = df.with_columns(
            pl.col("_or_h").max().over("trading_date").alias("or_high"),
            pl.col("_or_l").min().over("trading_date").alias("or_low"),
        )
        emit_bar = (
            (pl.col("_mod") == (range_end - self.timeframe_minutes))
            & pl.col("or_high").is_not_null()
            & pl.col("or_low").is_not_null()
        )
        risk = pl.col("or_high") - pl.col("or_low")
        tick = float(p["tick"])

        df = df.with_columns(
            emit_bar.alias("enter_long"),
            emit_bar.alias("enter_short"),
            pl.lit("stop").alias("entry_kind"),
            (pl.col("or_high") + tick).alias("entry_price_long_adj"),
            (pl.col("or_low") - tick).alias("entry_price_short_adj"),
            (pl.col("or_low") - tick).alias("stop_long_adj"),
            (pl.col("or_high") + tick).alias("stop_short_adj"),
            (pl.col("or_high") + tick + p["target_r"] * risk).alias("target_long_adj"),
            (pl.col("or_low") - tick - p["target_r"] * risk).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod", "_or_o", "_or_h", "_or_l")

        ctx = prev_day_context(df, vol_ref_days=p["vol_ref_days"])
        df = df.join(
            ctx.select("trading_date", "vol_ref"), on="trading_date", how="left"
        ).sort("ts_utc")

        ratio = (pl.col("or_high") - pl.col("or_low")) / pl.col("vol_ref")
        gate = (
            (ratio > p["min_width_ratio"]) & (ratio <= p["max_width_ratio"])
        ).fill_null(False)
        if p["skip_weekdays"]:
            gate = gate & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))
        if p["skip_macro_days"]:
            dates = df["trading_date"]
            d0, d1 = dates.min(), dates.max()
            if d0 is not None and d1 is not None:
                skip = macro_event_dates(
                    d0 if isinstance(d0, date) else d0,
                    d1 if isinstance(d1, date) else d1,
                    p["macro_events"],
                )
                if skip:
                    gate = gate & ~pl.col("trading_date").is_in(sorted(skip))

        df = df.with_columns(
            (pl.col("enter_long") & gate).alias("enter_long"),
            (pl.col("enter_short") & gate).alias("enter_short"),
        )
        if p["long_only"]:
            df = df.with_columns(pl.lit(False).alias("enter_short"))
        if p["max_risk_points"] is not None:
            cap = float(p["max_risk_points"])
            df = df.with_columns(
                pl.max_horizontal(
                    pl.col("or_low") - tick,
                    pl.col("entry_price_long_adj") - cap,
                ).alias("stop_long_adj"),
                pl.min_horizontal(
                    pl.col("or_high") + tick,
                    pl.col("entry_price_short_adj") + cap,
                ).alias("stop_short_adj"),
            )
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return [
            "anchor_minute", "range_minutes", "target_r", "expire_minutes",
            "min_width_ratio", "max_width_ratio", "max_risk_points",
        ]

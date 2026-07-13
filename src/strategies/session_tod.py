"""ORB variant with time-of-day emission windows."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, minute_of_day, prev_day_context

RTH_OPEN_MIN = 9 * 60 + 30


class SessionTodOrb(Strategy):
    name = "session_tod_orb"
    timeframe_minutes = 5
    default_params = {
        "range_minutes": 30,
        "target_r": 1.0,
        "expire_minutes": 120,
        "tick": 0.25,
        "min_width_ratio": 0.25,
        "max_width_ratio": 0.7,
        "long_only": True,
        "skip_weekdays": [1],
        "trade_window": "full",  # full | first60 | midday | last90
        "vol_ref_days": 14,
    }

    def _emit_minute(self) -> int:
        base_emit = RTH_OPEN_MIN + int(self.params["range_minutes"]) - self.timeframe_minutes
        tw = str(self.params["trade_window"])
        if tw == "first60":
            return max(base_emit, 10 * 60 - self.timeframe_minutes)
        if tw == "midday":
            return max(base_emit, 11 * 60 - self.timeframe_minutes)
        if tw == "last90":
            return max(base_emit, 14 * 60 - self.timeframe_minutes)
        return base_emit

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        range_end = RTH_OPEN_MIN + int(p["range_minutes"])
        in_range_window = (mod >= RTH_OPEN_MIN) & (mod < range_end)
        emit_mod = self._emit_minute()
        tick = float(p["tick"])

        out = df.sort("ts_utc").with_columns(
            pl.when(in_range_window).then(pl.col(ADJ["high"])).otherwise(None)
            .max().over("trading_date").alias("or_high"),
            pl.when(in_range_window).then(pl.col(ADJ["low"])).otherwise(None)
            .min().over("trading_date").alias("or_low"),
            mod.alias("_mod"),
        )
        ctx = prev_day_context(out, vol_ref_days=int(p["vol_ref_days"]))
        out = out.join(ctx.select("trading_date", "vol_ref"), on="trading_date", how="left").sort("ts_utc")

        ratio = (pl.col("or_high") - pl.col("or_low")) / pl.col("vol_ref")
        width_gate = (
            pl.col("vol_ref").is_not_null()
            & (ratio > float(p["min_width_ratio"]))
            & (ratio <= float(p["max_width_ratio"]))
        )
        emit = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") == emit_mod)
            & (pl.col("_mod") >= (range_end - self.timeframe_minutes))
            & pl.col("or_high").is_not_null()
            & pl.col("or_low").is_not_null()
            & width_gate
        )
        if p["skip_weekdays"]:
            emit = emit & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        risk = pl.col("or_high") - pl.col("or_low")
        out = out.with_columns(
            emit.fill_null(False).alias("enter_long"),
            pl.when(p["long_only"]).then(False).otherwise(emit.fill_null(False)).alias("enter_short"),
            pl.lit("stop").alias("entry_kind"),
            (pl.col("or_high") + tick).alias("entry_price_long_adj"),
            (pl.col("or_low") - tick).alias("entry_price_short_adj"),
            (pl.col("or_low") - tick).alias("stop_long_adj"),
            (pl.col("or_high") + tick).alias("stop_short_adj"),
            (pl.col("or_high") + tick + float(p["target_r"]) * risk).alias("target_long_adj"),
            (pl.col("or_low") - tick - float(p["target_r"]) * risk).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod", "vol_ref")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["range_minutes", "target_r", "min_width_ratio", "max_width_ratio", "trade_window"]

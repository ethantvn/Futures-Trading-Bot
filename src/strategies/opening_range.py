"""Opening-range breakout (ORB).

Hypothesis: order flow concentrates around the 09:30 ET open; once the
initial range breaks, the move tends to continue in that direction.

Rules (all times ET, signal timeframe 5m):
- Range = high/low of the first `range_minutes` of RTH (default 09:30-10:00).
- After the range completes, place an OCO pair of stop entries: long at range
  high + 1 tick, short at range low - 1 tick.
- Protective stop: the opposite side of the range.
- Target: entry +/- `target_r` times the range risk. Time exit via engine
  flat_time; pending entries expire after `expire_minutes`.
- One trade per day (engine max_trades_per_day=1 in config).
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, minute_of_day

RTH_OPEN_MIN = 9 * 60 + 30


class OpeningRangeBreakout(Strategy):
    name = "opening_range_breakout"
    timeframe_minutes = 5
    default_params = {
        "range_minutes": 30,
        "target_r": 2.0,
        "expire_minutes": 90,
        "tick": 0.25,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        range_end = RTH_OPEN_MIN + p["range_minutes"]

        in_range_window = (mod >= RTH_OPEN_MIN) & (mod < range_end)
        df = df.sort("ts_utc").with_columns(
            pl.when(in_range_window).then(pl.col(ADJ["high"])).otherwise(None)
            .max().over("trading_date").alias("or_high"),
            pl.when(in_range_window).then(pl.col(ADJ["low"])).otherwise(None)
            .min().over("trading_date").alias("or_low"),
            mod.alias("_mod"),
        )
        # The range is only KNOWN once the window has fully elapsed; the last
        # in-window bar (open at range_end - tf) completes exactly at
        # range_end, so bars with open >= range_end - tf may emit (their
        # signals act after completion, i.e. at/after range_end).
        emit_bar = (
            (pl.col("_mod") == (range_end - self.timeframe_minutes))
            & pl.col("or_high").is_not_null()
            & pl.col("or_low").is_not_null()
        )
        risk = pl.col("or_high") - pl.col("or_low")
        tick = p["tick"]

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
            pl.lit(p["expire_minutes"], dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["range_minutes", "target_r", "expire_minutes"]

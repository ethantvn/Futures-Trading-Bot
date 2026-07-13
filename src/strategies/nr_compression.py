"""NR-n / inside-day compression gate on ORB (Phase 7).

Hypothesis: after an unusually narrow or inside prior day (volatility
compression), the opening-range breakout resolves the compression and follows
through more reliably. Far fewer signals than plain ORB — the eval takes more
calendar days, which the user accepts in exchange for steadier equity.

Gate modes:
  "nr"      prior day was the narrowest RTH range of the last nr_n days
  "inside"  prior day was an inside day
  "either"  nr OR inside
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import with_signal_defaults
from src.strategies.indicators import prev_day_context
from src.strategies.opening_range import OpeningRangeBreakout


class NrCompressionOrb(OpeningRangeBreakout):
    name = "nr7_orb"
    timeframe_minutes = 5
    default_params = {
        **OpeningRangeBreakout.default_params,
        "nr_n": 7,
        "mode": "either",   # "nr" | "inside" | "either"
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = super().prepare(df)
        ctx = prev_day_context(df, nr_n=p["nr_n"])
        out = out.join(
            ctx.select("trading_date", "nr_flag", "inside_flag"),
            on="trading_date",
            how="left",
        ).sort("ts_utc")

        if p["mode"] == "nr":
            gate = pl.col("nr_flag")
        elif p["mode"] == "inside":
            gate = pl.col("inside_flag")
        elif p["mode"] == "either":
            gate = pl.col("nr_flag") | pl.col("inside_flag")
        else:
            raise ValueError(f"unknown mode {p['mode']!r}")
        gate = gate.fill_null(False)

        out = out.with_columns(
            (pl.col("enter_long") & gate).alias("enter_long"),
            (pl.col("enter_short") & gate).alias("enter_short"),
        )
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["range_minutes", "target_r", "expire_minutes", "nr_n", "mode"]

"""NR-n / inside-day compression gate on gold session ORB (Phase 11)."""
from __future__ import annotations

import polars as pl

from src.strategies.base import with_signal_defaults
from src.strategies.gc_session_orb import GcSessionOrb
from src.strategies.indicators import prev_day_context


class GcNrOrb(GcSessionOrb):
    name = "gc_nr_orb"
    default_params = {
        **GcSessionOrb.default_params,
        "nr_n": 7,
        "mode": "either",
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
        return super().overfit_prone_params() + ["nr_n", "mode"]

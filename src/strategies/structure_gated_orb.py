"""ORB-W with market-structure regime gate — Phase 16."""
from __future__ import annotations

import polars as pl

from src.strategies.base import with_signal_defaults
from src.strategies.indicators import structure_regime
from src.strategies.orb_filtered import FilteredOrb


class StructureGatedOrb(FilteredOrb):
    name = "structure_gated_orb"
    timeframe_minutes = 5
    default_params = {
        **FilteredOrb.default_params,
        "pivot_n": 3,
        # allow_regimes: comma-joined or list — e.g. "up,range"
        "allow_regimes": "up,range",
        "long_only": True,
        "min_width_ratio": 0.25,
        "max_width_ratio": 0.7,
        "skip_weekdays": (1,),
        "target_r": 1.0,
        "range_minutes": 30,
        "expire_minutes": 120,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = super().prepare(df)
        struct = structure_regime(df, pivot_n=int(p["pivot_n"]))
        out = out.join(
            struct.select("ts_utc", "structure_regime"), on="ts_utc", how="left"
        ).sort("ts_utc")
        allow = p["allow_regimes"]
        if isinstance(allow, str):
            allow_set = {x.strip() for x in allow.split(",") if x.strip()}
        else:
            allow_set = set(allow)
        gate = pl.col("structure_regime").is_in(sorted(allow_set)).fill_null(False)
        out = out.with_columns(
            (pl.col("enter_long") & gate).alias("enter_long"),
            (pl.col("enter_short") & gate).alias("enter_short"),
        )
        return with_signal_defaults(out.drop("structure_regime"))

    def overfit_prone_params(self) -> list[str]:
        return super().overfit_prone_params() + ["pivot_n", "allow_regimes"]

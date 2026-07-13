"""FVG + volume spike + VWAP-side stacked scalp — Phase 15."""
from __future__ import annotations

import polars as pl

from src.strategies.base import with_signal_defaults
from src.strategies.fvg_scalp import FvgScalp


class FvgVolumeScalp(FvgScalp):
    name = "fvg_volume_scalp"
    default_params = {
        **FvgScalp.default_params,
        "vol_lookback": 20,
        "z_threshold": 1.5,
        "vwap_filter": True,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = super().prepare(df)
        n = int(p["vol_lookback"])
        # Recompute volume z on original frame and join by row order
        vol = df.sort("ts_utc").with_columns(
            pl.col("volume").rolling_mean(n).alias("_vmean"),
            pl.col("volume").rolling_std(n).alias("_vstd"),
        )
        z = (pl.col("volume") - pl.col("_vmean")) / pl.col("_vstd")
        spike = (z >= float(p["z_threshold"])).fill_null(False)
        vol = vol.with_columns(spike.alias("_spike")).select("ts_utc", "_spike")
        out = out.join(vol, on="ts_utc", how="left").sort("ts_utc")
        out = out.with_columns(
            (pl.col("enter_long") & pl.col("_spike").fill_null(False)).alias("enter_long"),
            (pl.col("enter_short") & pl.col("_spike").fill_null(False)).alias("enter_short"),
        ).drop("_spike")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return super().overfit_prone_params() + ["z_threshold", "vol_lookback"]

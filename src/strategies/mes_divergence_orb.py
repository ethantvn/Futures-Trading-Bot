"""MNQ ORB gated by MES agreement / divergence — Phase 16."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import polars as pl

from src.strategies.base import with_signal_defaults
from src.strategies.indicators import ADJ, align_mes_bars, minute_of_day
from src.strategies.orb_filtered import FilteredOrb


@lru_cache(maxsize=4)
def _load_mes(path: str) -> pl.DataFrame:
    return pl.read_parquet(path)


class MesDivergenceOrb(FilteredOrb):
    name = "mes_divergence_orb"
    timeframe_minutes = 5
    default_params = {
        **FilteredOrb.default_params,
        "mes_mode": "agree",  # agree | diverge
        "mes_path": "data/processed/mes/continuous_5m.parquet",
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
        if "mes_high_adj" not in df.columns:
            path = Path(p["mes_path"])
            if path.exists():
                mes = _load_mes(str(path.resolve()))
                d0, d1 = df["trading_date"].min(), df["trading_date"].max()
                mes = mes.filter(
                    (pl.col("trading_date") >= d0) & (pl.col("trading_date") <= d1)
                )
                df = align_mes_bars(df, mes)
            else:
                df = df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias("mes_high_adj"),
                    pl.lit(None, dtype=pl.Float64).alias("mes_low_adj"),
                    pl.lit(None, dtype=pl.Float64).alias("mes_close_adj"),
                    pl.lit(None, dtype=pl.Float64).alias("mes_open_adj"),
                )

        out = super().prepare(df)
        mod = minute_of_day()
        range_end = 9 * 60 + 30 + int(p["range_minutes"])
        in_range = (mod >= 9 * 60 + 30) & (mod < range_end)
        mes_df = df.sort("ts_utc").with_columns(
            pl.when(in_range)
            .then(pl.col("mes_high_adj"))
            .otherwise(None)
            .max()
            .over("trading_date")
            .alias("mes_or_high"),
            pl.when(in_range)
            .then(pl.col("mes_low_adj"))
            .otherwise(None)
            .min()
            .over("trading_date")
            .alias("mes_or_low"),
            pl.col(ADJ["close"]).alias("_mnq_c"),
            pl.col("mes_close_adj").alias("_mes_c"),
        )
        out = out.join(
            mes_df.select("ts_utc", "mes_or_high", "mes_or_low", "_mnq_c", "_mes_c"),
            on="ts_utc",
            how="left",
        ).sort("ts_utc")

        # At OR completion price is still inside the range (stop entries pending).
        # Gate on MES directional bias vs MES OR midpoint, not a completed break.
        mes_mid = (pl.col("mes_or_high") + pl.col("mes_or_low")) / 2.0
        mes_bull = pl.col("_mes_c") > mes_mid
        mes_bear = pl.col("_mes_c") < mes_mid
        mes_ok = pl.col("mes_or_high").is_not_null() & pl.col("_mes_c").is_not_null()

        if p["mes_mode"] == "diverge":
            # MNQ long setup only when MES is bearishly biased (and vice versa)
            gate_l = mes_ok & mes_bear
            gate_s = mes_ok & mes_bull
        else:
            gate_l = mes_ok & mes_bull
            gate_s = mes_ok & mes_bear

        out = out.with_columns(
            (pl.col("enter_long") & gate_l).alias("enter_long"),
            (pl.col("enter_short") & gate_s).alias("enter_short"),
        ).drop("mes_or_high", "mes_or_low", "_mnq_c", "_mes_c")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return super().overfit_prone_params() + ["mes_mode"]

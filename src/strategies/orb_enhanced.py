"""ORB-W with Phase 17 causal enhancers (VIX / overnight context / regime).

All gates use only information known before or at OR completion — no
same-day afternoon leakage. VIX uses PRIOR session close (shifted).
Overnight range uses 18:00–09:30 ET only (see overnight_levels).
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

from src.strategies.base import with_signal_defaults
from src.strategies.indicators import overnight_levels, prev_day_context, structure_regime
from src.strategies.orb_filtered import FilteredOrb


def load_vix_prior_close(path: str | Path = "data/processed/vix_daily.parquet") -> pl.DataFrame:
    """Map trading_date → prior VIX close (known before RTH open)."""
    v = pl.read_parquet(path).sort("date")
    return v.select(
        pl.col("date").alias("trading_date"),
        pl.col("vix_close").shift(1).alias("vix_prior"),
    )


class OrbEnhanced(FilteredOrb):
    name = "orb_enhanced"
    timeframe_minutes = 5
    default_params = {
        **FilteredOrb.default_params,
        "long_only": True,
        "min_width_ratio": 0.25,
        "max_width_ratio": 0.7,
        "skip_weekdays": (1,),
        "target_r": 1.0,
        "range_minutes": 30,
        "expire_minutes": 120,
        # VIX prior-close band (None / 0 / huge = off)
        "vix_path": "data/processed/vix_daily.parquet",
        "vix_min": 0.0,
        "vix_max": 1e9,
        # Overnight range / vol_ref band (causal ON)
        "on_range_min_ratio": 0.0,
        "on_range_max_ratio": 1e9,
        # Prior-day structure regime at last bar of prior session
        "pivot_n": 3,
        "allow_regimes": "",  # empty = off; e.g. "up,range"
        # Prev-day inside-day flag
        "skip_inside_day": False,
        "only_inside_day": False,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = super().prepare(df)

        # --- VIX prior close ---
        vix_min, vix_max = float(p["vix_min"]), float(p["vix_max"])
        if vix_min > 0.0 or vix_max < 1e8:
            path = Path(p["vix_path"])
            if path.exists():
                vix = load_vix_prior_close(path)
                out = out.join(vix, on="trading_date", how="left").sort("ts_utc")
                vgate = (
                    pl.col("vix_prior").is_not_null()
                    & (pl.col("vix_prior") >= vix_min)
                    & (pl.col("vix_prior") <= vix_max)
                )
                out = out.with_columns(
                    (pl.col("enter_long") & vgate).alias("enter_long"),
                    (pl.col("enter_short") & vgate).alias("enter_short"),
                ).drop("vix_prior")

        # --- Causal overnight range vs vol_ref ---
        on_lo, on_hi = float(p["on_range_min_ratio"]), float(p["on_range_max_ratio"])
        if on_lo > 0.0 or on_hi < 1e8:
            on = overnight_levels(df)
            ctx = prev_day_context(df, vol_ref_days=int(p["vol_ref_days"]))
            on = on.join(ctx.select("trading_date", "vol_ref"), on="trading_date", how="left")
            on = on.with_columns(
                ((pl.col("on_high") - pl.col("on_low")) / pl.col("vol_ref")).alias("_on_ratio")
            )
            out = out.join(
                on.select("trading_date", "_on_ratio"), on="trading_date", how="left"
            ).sort("ts_utc")
            ogate = (
                pl.col("_on_ratio").is_not_null()
                & (pl.col("_on_ratio") > on_lo)
                & (pl.col("_on_ratio") <= on_hi)
            )
            out = out.with_columns(
                (pl.col("enter_long") & ogate).alias("enter_long"),
                (pl.col("enter_short") & ogate).alias("enter_short"),
            ).drop("_on_ratio")

        # --- Prior-day ending structure regime ---
        allow = p.get("allow_regimes") or ""
        if isinstance(allow, str) and allow.strip():
            allow_set = {x.strip() for x in allow.split(",") if x.strip()}
            struct = structure_regime(df, pivot_n=int(p["pivot_n"]))
            # last regime per trading_date, then shift to prior day
            day_reg = (
                struct.group_by("trading_date")
                .agg(pl.col("structure_regime").last().alias("_reg_eod"))
                .sort("trading_date")
                .with_columns(pl.col("_reg_eod").shift(1).alias("prior_regime"))
                .select("trading_date", "prior_regime")
            )
            out = out.join(day_reg, on="trading_date", how="left").sort("ts_utc")
            rgate = pl.col("prior_regime").is_in(sorted(allow_set)).fill_null(False)
            out = out.with_columns(
                (pl.col("enter_long") & rgate).alias("enter_long"),
                (pl.col("enter_short") & rgate).alias("enter_short"),
            ).drop("prior_regime")

        # --- Inside-day flag from prior day ---
        if p.get("skip_inside_day") or p.get("only_inside_day"):
            ctx = prev_day_context(df, vol_ref_days=int(p["vol_ref_days"]))
            out = out.join(
                ctx.select("trading_date", "inside_flag"), on="trading_date", how="left"
            ).sort("ts_utc")
            if p.get("skip_inside_day"):
                igate = ~pl.col("inside_flag").fill_null(False)
            else:
                igate = pl.col("inside_flag").fill_null(False)
            out = out.with_columns(
                (pl.col("enter_long") & igate).alias("enter_long"),
                (pl.col("enter_short") & igate).alias("enter_short"),
            ).drop("inside_flag")

        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return super().overfit_prone_params() + [
            "vix_min", "vix_max", "on_range_min_ratio", "on_range_max_ratio",
            "allow_regimes", "pivot_n",
        ]

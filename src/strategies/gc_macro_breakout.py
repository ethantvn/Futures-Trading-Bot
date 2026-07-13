"""Macro-release range breakout for gold (Phase 11).

Trades ONLY on scheduled macro days (NFP/CPI @ 8:30 ET, FOMC @ 14:00 ET).
Range = `pre_range_minutes` ending at `release_minute`; OCO breakout after
the release window completes. Sized via optional max_risk_points cap.
"""
from __future__ import annotations

from datetime import date

import polars as pl

from src.data.macro_calendar import cpi_dates, fomc_dates, nfp_dates
from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import minute_of_day


def _macro_dates_for_kind(start: date, end: date, kind: str) -> set[date]:
    if kind == "nfp":
        return nfp_dates(start, end)
    if kind == "cpi":
        return cpi_dates(start, end)
    if kind == "nfp_cpi":
        return nfp_dates(start, end) | cpi_dates(start, end)
    if kind == "fomc":
        return fomc_dates(start, end)
    if kind == "all":
        return nfp_dates(start, end) | cpi_dates(start, end) | fomc_dates(start, end)
    raise ValueError(f"unknown macro kind {kind!r}")


class GcMacroBreakout(Strategy):
    name = "gc_macro_breakout"
    timeframe_minutes = 5
    default_params = {
        "macro_kind": "nfp_cpi",       # nfp | cpi | nfp_cpi | fomc | all
        "release_minute": 8 * 60 + 30, # 8:30 ET for NFP/CPI; use 840 for FOMC
        "pre_range_minutes": 30,
        "post_delay_minutes": 0,       # wait N min after release before arming
        "target_r": 1.0,
        "expire_minutes": 90,
        "tick": 0.10,
        "max_risk_points": 4.0,        # default $400 @ $100/pt
        "min_range_points": 0.0,       # skip if pre-release range too tight
        "long_only": False,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        mod = minute_of_day()
        release = int(p["release_minute"])
        pre = int(p["pre_range_minutes"])
        delay = int(p.get("post_delay_minutes", 0))
        anchor = release - pre
        range_end = release
        emit_mod = release + delay - self.timeframe_minutes

        dates = df["trading_date"]
        d0, d1 = dates.min(), dates.max()
        macro_days: set[date] = set()
        if d0 is not None and d1 is not None:
            macro_days = _macro_dates_for_kind(
                d0 if isinstance(d0, date) else d0,
                d1 if isinstance(d1, date) else d1,
                p["macro_kind"],
            )

        in_range = (mod >= anchor) & (mod < range_end)
        df = df.sort("ts_utc").with_columns(
            pl.when(in_range).then(pl.col("high_adj")).alias("_or_h"),
            pl.when(in_range).then(pl.col("low_adj")).alias("_or_l"),
            mod.alias("_mod"),
            pl.col("trading_date").is_in(sorted(macro_days)).alias("_macro"),
        )
        df = df.with_columns(
            pl.col("_or_h").max().over("trading_date").alias("or_high"),
            pl.col("_or_l").min().over("trading_date").alias("or_low"),
        )
        risk = pl.col("or_high") - pl.col("or_low")
        min_rng = float(p.get("min_range_points", 0.0))
        emit_bar = (
            pl.col("_macro")
            & (pl.col("_mod") == emit_mod)
            & pl.col("or_high").is_not_null()
            & (risk >= min_rng)
        )
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
        ).drop("_mod", "_or_h", "_or_l", "_macro")

        cap = p.get("max_risk_points")
        if cap is not None:
            cap = float(cap)
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
        if p["long_only"]:
            df = df.with_columns(pl.lit(False).alias("enter_short"))
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return [
            "release_minute", "pre_range_minutes", "post_delay_minutes",
            "target_r", "max_risk_points", "min_range_points",
        ]

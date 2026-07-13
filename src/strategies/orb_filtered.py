"""ORB with consistency filters (Phase 7).

Same core as OpeningRangeBreakout; adds day-level gates and an optional
intraday time exit, all OFF by default so the base behavior is unchanged:

- Width band: only trade when (opening range width / vol_ref) is inside
  (min_width_ratio, max_width_ratio]. vol_ref is an EWM of PRIOR daily RTH
  ranges. Rationale (Phase 7 baseline analysis on the WF OOS ledger): ratios
  <= 0.25 were net losers (noise breakouts), ratios > ~0.5 carried twice the
  daily variance for little P&L — both tails hurt Lucid MLL survival.
- skip_weekdays: ISO weekday numbers (1=Mon) to stand aside (Phase 6b found
  Monday negative and skip-Monday held on the 2026 holdout).
- exit_minute: force-flat at this ET minute-of-day (e.g. 810 = 13:30) via
  signal exits, cutting the long afternoon drift tail.
- max_risk_points (Phase 8): cap the protective-stop distance at this many
  points from entry (tighter of range stop vs cap). At $2/point per micro,
  200/250/300 points = $400/$500/$600 max gross loss per trade; with one
  trade per day this caps the daily loss. Targets stay anchored to the
  RANGE risk (the breakout structure), only the stop is tightened.
- long_only (Phase 9): disable short breakouts (equity-index drift bias).
- skip_macro_days + macro_events (Phase 9): stand aside on NFP / CPI / FOMC
  release days (see src/data/macro_calendar.py).

Days with insufficient vol_ref history (warmup) do not trade.
"""
from __future__ import annotations

from datetime import date

import polars as pl

from src.data.macro_calendar import macro_event_dates
from src.strategies.base import with_signal_defaults
from src.strategies.indicators import minute_of_day, prev_day_context
from src.strategies.opening_range import OpeningRangeBreakout


class FilteredOrb(OpeningRangeBreakout):
    name = "orb_filtered"
    timeframe_minutes = 5
    default_params = {
        **OpeningRangeBreakout.default_params,
        "min_width_ratio": 0.0,       # 0 = gate off
        "max_width_ratio": 1e9,       # huge = gate off
        "vol_ref_days": 14,
        "skip_weekdays": (),          # ISO: 1=Mon .. 5=Fri
        "exit_minute": None,          # ET minute-of-day; None = hold to flat_time
        "max_risk_points": None,      # stop-distance cap in points; None = off
        "long_only": False,           # Phase 9: no short entries
        "skip_macro_days": False,     # Phase 9: skip NFP/CPI/FOMC days
        "macro_events": "all",        # 'all' | 'nfp' | 'cpi' | 'fomc'
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        out = super().prepare(df)

        ctx = prev_day_context(df, vol_ref_days=p["vol_ref_days"])
        out = out.join(
            ctx.select("trading_date", "vol_ref"), on="trading_date", how="left"
        ).sort("ts_utc")

        ratio = (pl.col("or_high") - pl.col("or_low")) / pl.col("vol_ref")
        gate = (
            (ratio > p["min_width_ratio"])
            & (ratio <= p["max_width_ratio"])
        ).fill_null(False)
        if p["skip_weekdays"]:
            gate = gate & ~pl.col("trading_date").dt.weekday().is_in(
                list(p["skip_weekdays"])
            )
        if p["skip_macro_days"]:
            dates = out["trading_date"]
            d0, d1 = dates.min(), dates.max()
            if d0 is not None and d1 is not None:
                skip = macro_event_dates(
                    d0 if isinstance(d0, date) else d0,
                    d1 if isinstance(d1, date) else d1,
                    p["macro_events"],
                )
                if skip:
                    gate = gate & ~pl.col("trading_date").is_in(sorted(skip))

        out = out.with_columns(
            (pl.col("enter_long") & gate).alias("enter_long"),
            (pl.col("enter_short") & gate).alias("enter_short"),
        )
        if p["long_only"]:
            out = out.with_columns(pl.lit(False).alias("enter_short"))
        if p["exit_minute"] is not None:
            # a 5m bar opening at exit_minute - tf completes AT exit_minute,
            # so its exit signal fills on the first 1m bar >= exit_minute
            past_exit = minute_of_day() >= (p["exit_minute"] - self.timeframe_minutes)
            out = out.with_columns(
                (pl.col("exit_long") | past_exit).alias("exit_long"),
                (pl.col("exit_short") | past_exit).alias("exit_short"),
            )
        if p["max_risk_points"] is not None:
            cap = float(p["max_risk_points"])
            out = out.with_columns(
                pl.max_horizontal(
                    pl.col("stop_long_adj"),
                    pl.col("entry_price_long_adj") - cap,
                ).alias("stop_long_adj"),
                pl.min_horizontal(
                    pl.col("stop_short_adj"),
                    pl.col("entry_price_short_adj") + cap,
                ).alias("stop_short_adj"),
            )
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return [
            "range_minutes", "target_r", "expire_minutes",
            "min_width_ratio", "max_width_ratio", "exit_minute",
            "max_risk_points",
        ]

"""Volume-spike momentum scalp — Phase 15.

Trigger: volume z-score vs rolling baseline exceeds threshold AND bar range
exceeds rolling median range. Enter market in the direction of the bar
(close > open → long). Stop beyond trigger bar extreme; target target_r × risk.
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, minute_of_day


class VolumeSpikeScalp(Strategy):
    name = "volume_spike_scalp"
    timeframe_minutes = 1
    default_params = {
        "vol_lookback": 20,
        "z_threshold": 2.0,
        "range_mult": 1.0,            # bar range vs rolling median range
        "target_r": 1.0,
        "expire_minutes": 15,
        "buffer_ticks": 1,
        "tick": 0.25,
        "entry_start_minute": 9 * 60 + 35,
        "entry_end_minute": 15 * 60,
        "max_risk_points": None,
        "min_stop_points": 10.0,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        n = int(p["vol_lookback"])
        tick = float(p["tick"])
        buf = float(p["buffer_ticks"]) * tick
        mod = minute_of_day()

        bar_range = pl.col(ADJ["high"]) - pl.col(ADJ["low"])
        df = df.sort("ts_utc").with_columns(
            pl.col("volume").rolling_mean(n).alias("_vmean"),
            pl.col("volume").rolling_std(n).alias("_vstd"),
            bar_range.rolling_median(n).alias("_rmed"),
            bar_range.alias("_rng"),
            mod.alias("_mod"),
        )
        z = (pl.col("volume") - pl.col("_vmean")) / pl.col("_vstd")
        spike = (z >= float(p["z_threshold"])) & (pl.col("_vstd") > 0)
        wide = pl.col("_rng") >= (float(p["range_mult"]) * pl.col("_rmed"))
        window = (
            (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
        )
        bull = spike & wide & window & (pl.col(ADJ["close"]) > pl.col(ADJ["open"]))
        bear = spike & wide & window & (pl.col(ADJ["close"]) < pl.col(ADJ["open"]))

        # Market entry at next bar — engine fills on open after signal completes.
        # Use close as reference for stop/target placement (causal).
        long_stop = pl.col(ADJ["low"]) - buf
        short_stop = pl.col(ADJ["high"]) + buf
        # Risk measured from close (proxy for next-open entry under flat markets)
        long_risk = pl.max_horizontal(
            pl.col(ADJ["close"]) - long_stop,
            pl.lit(float(p["min_stop_points"])),
        )
        short_risk = pl.max_horizontal(
            short_stop - pl.col(ADJ["close"]),
            pl.lit(float(p["min_stop_points"])),
        )
        if p.get("max_risk_points") is not None:
            cap = float(p["max_risk_points"])
            long_risk = pl.min_horizontal(long_risk, pl.lit(cap))
            short_risk = pl.min_horizontal(short_risk, pl.lit(cap))
            long_stop = pl.col(ADJ["close"]) - long_risk
            short_stop = pl.col(ADJ["close"]) + short_risk

        df = df.with_columns(
            rising_edge(bull).alias("enter_long"),
            rising_edge(bear).alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            long_stop.alias("stop_long_adj"),
            short_stop.alias("stop_short_adj"),
            (pl.col(ADJ["close"]) + float(p["target_r"]) * long_risk).alias(
                "target_long_adj"
            ),
            (pl.col(ADJ["close"]) - float(p["target_r"]) * short_risk).alias(
                "target_short_adj"
            ),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_vmean", "_vstd", "_rmed", "_rng", "_mod")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["z_threshold", "vol_lookback", "target_r", "expire_minutes"]

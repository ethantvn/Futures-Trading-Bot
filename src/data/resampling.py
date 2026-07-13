"""Resample 1-minute bars to N-minute bars, session-aware and DST-correct.

Buckets are anchored to NY wall-clock time (truncation happens on the
tz-aware `ts_ny` column), so the 18:00 ET session open and 09:30 RTH open
stay aligned across daylight-saving transitions. Bar timestamps keep the
bar-OPEN convention of the source data.
"""
from __future__ import annotations

import logging

import polars as pl

log = logging.getLogger(__name__)

_AGG = [
    pl.col("ts_utc").first(),
    pl.col("trading_date").first(),
    pl.col("session").first(),
    pl.col("open").first(),
    pl.col("high").max(),
    pl.col("low").min(),
    pl.col("close").last(),
    pl.col("volume").sum(),
]
_AGG_ADJ = [
    pl.col("open_adj").first(),
    pl.col("high_adj").max(),
    pl.col("low_adj").min(),
    pl.col("close_adj").last(),
]


def resample(bars: pl.DataFrame, minutes: int) -> pl.DataFrame:
    """Aggregate sorted 1m bars into `minutes`-minute bars per symbol.

    Grouping additionally splits on `session` so an RTH bucket never absorbs
    ETH minutes (e.g. a 15m bar at 09:15 won't swallow the 09:30 open).
    """
    if bars.height == 0:
        return bars
    agg = list(_AGG) + (_AGG_ADJ if "open_adj" in bars.columns else [])
    out = (
        bars.sort("ts_utc")
        .with_columns(pl.col("ts_ny").dt.truncate(f"{minutes}m").alias("bucket"))
        .group_by("symbol", "trading_date", "session", "bucket", maintain_order=True)
        .agg([a for a in agg if a.meta.output_name() not in ("trading_date", "session")])
        .rename({"bucket": "ts_ny"})
        .sort("ts_utc")
    )
    cols = ["ts_utc", "ts_ny", "trading_date", "session", "symbol",
            "open", "high", "low", "close", "volume"]
    if "open_adj" in bars.columns:
        cols += ["open_adj", "high_adj", "low_adj", "close_adj"]
    return out.select(cols)

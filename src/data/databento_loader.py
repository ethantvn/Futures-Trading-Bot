"""Load Databento GLBX.MDP3 ohlcv-1m CSV.zst batch exports into normalized Polars frames.

Conventions established by inspection of the export (docs/PHASE_1_PLAN.md section 2):
- `ts_event` is the UTC bar-OPEN timestamp in ISO-8601 nanoseconds.
- Prices are decimal ("pretty_px"), unadjusted, tick-aligned to 0.25.
- `symbol` carries raw contract symbols; calendar spreads look like "MNQH0-MNQM0".
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

import polars as pl
import zstandard

log = logging.getLogger(__name__)

NY_TZ = "America/New_York"

# The CME Globex session opens 18:00 ET the prior calendar day and closes
# 17:00 ET, so shifting NY wall-clock time forward 6 hours maps every bar to
# its trading date. This function is the single source of truth for "day"
# across the whole project (drawdown, consistency, daily stats).
TRADING_DATE_SHIFT_HOURS = 6

RTH_START = pl.time(9, 30)
RTH_END = pl.time(16, 0)


def read_raw_csv(path: str | Path) -> pl.DataFrame:
    """Decompress and parse a Databento ohlcv-1m csv.zst file (all rows, as-is)."""
    path = Path(path)
    log.info("reading %s", path)
    dctx = zstandard.ZstdDecompressor()
    with open(path, "rb") as f:
        raw = dctx.stream_reader(f).read()
    df = pl.read_csv(
        io.BytesIO(raw),
        schema_overrides={
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.Int64,
        },
    )
    log.info("parsed %d rows", df.height)
    return df


def normalize(df: pl.DataFrame, drop_spreads: bool = True) -> pl.DataFrame:
    """Normalize a raw frame: UTC + NY timestamps, trading date, session label.

    Keeps the original exchange timestamp as `ts_utc` and adds:
    - `ts_ny`: bar-open in America/New_York (DST-correct)
    - `trading_date`: CME trading date (session starting 18:00 ET belongs to next day)
    - `session`: "rth" for 09:30 <= t < 16:00 ET, else "eth"
    """
    if drop_spreads:
        n = df.height
        df = df.filter(~pl.col("symbol").str.contains("-"))
        log.info("dropped %d calendar-spread rows", n - df.height)

    df = df.with_columns(
        pl.col("ts_event")
        .str.to_datetime(time_unit="ns", time_zone="UTC")
        .alias("ts_utc")
    ).with_columns(
        pl.col("ts_utc").dt.convert_time_zone(NY_TZ).alias("ts_ny")
    ).with_columns(
        (pl.col("ts_ny") + pl.duration(hours=TRADING_DATE_SHIFT_HOURS))
        .dt.date()
        .alias("trading_date"),
        pl.when(pl.col("ts_ny").dt.time().is_between(RTH_START, RTH_END, closed="left"))
        .then(pl.lit("rth"))
        .otherwise(pl.lit("eth"))
        .alias("session"),
    )
    return df.select(
        "ts_utc", "ts_ny", "trading_date", "session", "symbol", "instrument_id",
        "open", "high", "low", "close", "volume",
    ).sort("ts_utc", "symbol")


def load_bars(path: str | Path) -> pl.DataFrame:
    """Read + normalize outright 1-minute bars from a raw export file."""
    return normalize(read_raw_csv(path))

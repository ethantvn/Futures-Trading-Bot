from __future__ import annotations

from datetime import date, datetime, timezone

import polars as pl


def make_bars(rows: list[dict]) -> pl.DataFrame:
    """Build a normalized-bars frame (as produced by databento_loader.normalize)
    from compact row dicts: ts (UTC datetime), symbol, o/h/l/c, v, trading_date."""
    return pl.DataFrame(
        {
            "ts_utc": [r["ts"].replace(tzinfo=timezone.utc) for r in rows],
            "symbol": [r["symbol"] for r in rows],
            "open": [float(r["o"]) for r in rows],
            "high": [float(r["h"]) for r in rows],
            "low": [float(r["l"]) for r in rows],
            "close": [float(r["c"]) for r in rows],
            "volume": [int(r["v"]) for r in rows],
            "trading_date": [r["trading_date"] for r in rows],
        },
        schema_overrides={
            "ts_utc": pl.Datetime("ns", "UTC"),
            "trading_date": pl.Date,
        },
    ).with_columns(
        pl.col("ts_utc").dt.convert_time_zone("America/New_York").alias("ts_ny"),
        pl.lit("rth").alias("session"),
        pl.lit(1).cast(pl.Int64).alias("instrument_id"),
    ).sort("ts_utc")


def bar(ts: datetime, symbol: str, px: float, v: int, td: date, spread: float = 1.0) -> dict:
    return {
        "ts": ts, "symbol": symbol,
        "o": px, "h": px + spread, "l": px - spread, "c": px + spread / 2,
        "v": v, "trading_date": td,
    }

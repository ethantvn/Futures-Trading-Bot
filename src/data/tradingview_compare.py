"""Compare TradingView OHLCV exports against Databento-derived 1m candles.

TradingView export format (verified on a real MNQ1! export, 2026-07-06):
- `time` column: unix epoch seconds, bar-OPEN convention (same as Databento)
- `open/high/low/close` columns; `Volume` only if plotted on the chart
- arbitrary extra indicator/strategy columns, which are ignored
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import polars as pl

log = logging.getLogger(__name__)

PRICE_FIELDS = ("open", "high", "low", "close")


@dataclass
class ComparisonResult:
    tv_bars: int
    db_bars: int
    overlap_bars: int
    tv_only: int
    db_only: int
    pct_candles_matching: float | None
    field_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    volume_compared: bool = False
    tv_range: tuple[str, str] = ("", "")
    db_range: tuple[str, str] = ("", "")
    # Days where TV and our continuous series likely hold different front
    # contracts (TradingView MNQ1! rolls on its own schedule).
    suspected_roll_mismatch_days: list[str] = field(default_factory=list)
    pct_matching_excl_roll_days: float | None = None


def load_tradingview_export(path: str | Path) -> pl.DataFrame:
    """Load a TradingView CSV export, keeping time/OHLC(/volume) only."""
    df = pl.read_csv(path)
    cols = {c.lower().strip(): c for c in df.columns}
    keep = {"time": "epoch_s"}
    for f in PRICE_FIELDS:
        keep[f] = f
    rename = {cols[k]: v for k, v in keep.items() if k in cols}
    missing = [k for k in keep if k not in cols]
    if missing:
        raise ValueError(f"TradingView export missing columns: {missing}")
    out = df.select(list(rename)).rename(rename)
    if "volume" in cols:
        out = out.with_columns(df[cols["volume"]].alias("volume"))
    return out.with_columns(
        pl.from_epoch("epoch_s", time_unit="s")
        .dt.replace_time_zone("UTC")
        .dt.cast_time_unit("ns")  # match the Databento frames' ns precision
        .alias("ts_utc")
    ).sort("ts_utc")


def detect_interval_minutes(tv_bars: pl.DataFrame) -> int:
    """Infer the export's bar interval as the most common timestamp spacing.

    The mode is robust to session halts and weekends, which appear as a small
    number of oversized gaps.
    """
    diffs = (
        tv_bars.sort("ts_utc")
        .select((pl.col("ts_utc").diff().dt.total_seconds() / 60).alias("m"))
        .drop_nulls()
    )
    mode = diffs.group_by("m").len().sort("len", descending=True)["m"][0]
    return int(mode)


def compare(db_bars: pl.DataFrame, tv_bars: pl.DataFrame, tick_size: float = 0.25) -> ComparisonResult:
    """Join on bar-open timestamp and report per-field differences."""
    db_cols = [
        pl.col("ts_utc"),
        *[pl.col(f).alias(f"{f}_db") for f in PRICE_FIELDS],
        pl.col("volume").alias("volume_db"),
    ]
    if "trading_date" in db_bars.columns:
        db_cols.append(pl.col("trading_date"))
    db = db_bars.select(db_cols)
    tv = tv_bars.select(
        pl.col("ts_utc"),
        *[pl.col(f).alias(f"{f}_tv") for f in PRICE_FIELDS],
        *( [pl.col("volume").alias("volume_tv")] if "volume" in tv_bars.columns else [] ),
    )
    joined = db.join(tv, on="ts_utc", how="inner")

    res = ComparisonResult(
        tv_bars=tv.height,
        db_bars=db.height,
        overlap_bars=joined.height,
        tv_only=tv.height - joined.height,
        db_only=db.height - joined.height,
        pct_candles_matching=None,
        tv_range=(str(tv["ts_utc"].min()), str(tv["ts_utc"].max())),
        db_range=(str(db["ts_utc"].min()), str(db["ts_utc"].max())),
    )
    if joined.height == 0:
        return res

    match_all = pl.lit(True)
    for f in PRICE_FIELDS:
        diff = (pl.col(f"{f}_tv") - pl.col(f"{f}_db")).abs()
        stats = joined.select(
            diff.max().alias("max"),
            diff.mean().alias("mean"),
            (diff <= tick_size / 2).mean().alias("pct_exact"),
        ).to_dicts()[0]
        res.field_stats[f] = {
            "max_abs_diff": float(stats["max"]),
            "mean_abs_diff": float(stats["mean"]),
            "pct_within_half_tick": 100.0 * float(stats["pct_exact"]),
        }
        match_all = match_all & ((pl.col(f"{f}_tv") - pl.col(f"{f}_db")).abs() <= tick_size / 2)
    res.pct_candles_matching = 100.0 * float(joined.select(match_all.mean()).item())

    # A whole day of large constant offsets means TV holds a different front
    # contract that day (roll-date difference), not a data problem.
    if "trading_date" in joined.columns:
        daily = joined.group_by("trading_date").agg(
            (pl.col("close_tv") - pl.col("close_db")).abs().mean().alias("mean_close_diff")
        )
        roll_days = daily.filter(pl.col("mean_close_diff") > 40 * tick_size)[
            "trading_date"
        ].sort().to_list()
        res.suspected_roll_mismatch_days = [str(d) for d in roll_days]
        if roll_days:
            ex = joined.filter(~pl.col("trading_date").is_in(roll_days))
            if ex.height:
                res.pct_matching_excl_roll_days = 100.0 * float(
                    ex.select(match_all.mean()).item()
                )

    if "volume_tv" in joined.columns:
        res.volume_compared = True
        vdiff = (pl.col("volume_tv") - pl.col("volume_db")).abs()
        stats = joined.select(vdiff.max().alias("max"), vdiff.mean().alias("mean")).to_dicts()[0]
        res.field_stats["volume"] = {
            "max_abs_diff": float(stats["max"]),
            "mean_abs_diff": float(stats["mean"]),
            "pct_within_half_tick": float("nan"),
        }
    return res


def render_report(res: ComparisonResult) -> str:
    lines = [
        "# TradingView Comparison Report",
        "",
        f"- TradingView bars: {res.tv_bars:,} ({res.tv_range[0]} -> {res.tv_range[1]})",
        f"- Databento bars:   {res.db_bars:,} ({res.db_range[0]} -> {res.db_range[1]})",
        f"- Overlapping bars (timestamp join): {res.overlap_bars:,}",
        f"- TradingView-only bars (missing in Databento series): {res.tv_only:,}",
        f"- Databento-only bars (missing in TradingView export): {res.db_only:,}",
        "",
    ]
    if res.overlap_bars == 0:
        lines += [
            "**No overlapping timestamps — comparison not possible with this export.**",
            "",
            "Likely cause: the TradingView export only contains the bars loaded in",
            "the chart. Scroll the chart back so its history overlaps the Databento",
            "date range, then re-export (and add the Volume indicator so volume is",
            "included).",
            "",
        ]
        return "\n".join(lines)
    lines += [f"- Candles fully matching (all OHLC within half a tick): "
              f"{res.pct_candles_matching:.2f}%"]
    if res.suspected_roll_mismatch_days:
        lines += [
            f"- Suspected roll-date mismatch days (TV front contract differs): "
            f"{', '.join(res.suspected_roll_mismatch_days)}",
        ]
        if res.pct_matching_excl_roll_days is not None:
            lines += [
                f"- Candles fully matching EXCLUDING those days: "
                f"{res.pct_matching_excl_roll_days:.2f}%",
            ]
    lines += ["", "## Per-field differences", ""]
    lines.append("| Field | Max abs diff | Mean abs diff | % within half tick |")
    lines.append("| --- | --- | --- | --- |")
    for f, s in res.field_stats.items():
        pct = "" if f == "volume" else f"{s['pct_within_half_tick']:.2f}%"
        lines.append(f"| {f} | {s['max_abs_diff']:.2f} | {s['mean_abs_diff']:.4f} | {pct} |")
    if not res.volume_compared:
        lines += ["", "Volume was not compared (no volume column in the TradingView export)."]
    lines.append("")
    return "\n".join(lines)

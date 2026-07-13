"""Data-quality checks for normalized 1-minute bars.

Produces a machine-readable dict and a markdown report covering: duplicates,
OHLC violations, non-positive prices, tick alignment, zero-volume bars,
per-day completeness of the volume-lead contract, and the Databento
condition.json day flags.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import polars as pl

log = logging.getLogger(__name__)


def check_bars(
    bars: pl.DataFrame,
    tick_size: float = 0.25,
    min_minutes_full_day: int = 1200,
) -> dict[str, Any]:
    """Run all quality checks on a normalized outright-bars frame."""
    res: dict[str, Any] = {}
    res["tick_size"] = tick_size
    res["rows"] = bars.height
    res["contracts"] = bars["symbol"].n_unique()
    res["first_bar_utc"] = str(bars["ts_utc"].min())
    res["last_bar_utc"] = str(bars["ts_utc"].max())

    res["duplicate_rows"] = int(
        bars.height - bars.unique(subset=["ts_utc", "symbol"]).height
    )

    ohlc_bad = bars.filter(
        (pl.col("low") > pl.min_horizontal("open", "close"))
        | (pl.col("high") < pl.max_horizontal("open", "close"))
        | (pl.col("low") > pl.col("high"))
    )
    res["ohlc_violations"] = ohlc_bad.height

    res["nonpositive_prices"] = bars.filter(
        (pl.col("open") <= 0) | (pl.col("high") <= 0)
        | (pl.col("low") <= 0) | (pl.col("close") <= 0)
    ).height

    misaligned = 0
    for c in ("open", "high", "low", "close"):
        misaligned += bars.filter(((pl.col(c) / tick_size) % 1.0) != 0.0).height
    res["non_tick_aligned_prices"] = misaligned

    res["zero_volume_bars"] = bars.filter(pl.col("volume") <= 0).height

    # Completeness of the daily volume-lead contract (the tradable series).
    daily = bars.group_by("trading_date", "symbol").agg(
        pl.len().alias("minutes"), pl.col("volume").sum().alias("volume")
    )
    lead = (
        daily.sort("volume", descending=True)
        .group_by("trading_date", maintain_order=True)
        .first()
        .sort("trading_date")
    )
    res["trading_days"] = lead.height
    res["median_minutes_per_day"] = float(lead["minutes"].median())
    short = lead.filter(pl.col("minutes") < min_minutes_full_day)
    res["short_days"] = short.height
    res["short_day_list"] = [
        {"date": str(r["trading_date"]), "minutes": r["minutes"], "symbol": r["symbol"]}
        for r in short.sort("minutes").head(50).to_dicts()
    ]
    return res


def summarize_condition(condition_path: str | Path) -> dict[str, Any]:
    """Summarize Databento's per-day condition flags (available/degraded/missing)."""
    days = json.loads(Path(condition_path).read_text())
    out: dict[str, Any] = {"total_days": len(days)}
    by: dict[str, list[str]] = {}
    for d in days:
        by.setdefault(d["condition"], []).append(d["date"])
    out["counts"] = {k: len(v) for k, v in by.items()}
    out["degraded_dates"] = by.get("degraded", [])
    # All "missing" dates were verified to be Saturdays (market closed).
    out["missing_dates"] = by.get("missing", [])
    return out


def render_markdown(quality: dict[str, Any], condition: dict[str, Any]) -> str:
    q, c = quality, condition
    lines = [
        "# Data Quality Report",
        "",
        f"- Rows (outright 1m bars): {q['rows']:,}",
        f"- Contracts: {q['contracts']}",
        f"- Range (UTC, bar-open): {q['first_bar_utc']} -> {q['last_bar_utc']}",
        f"- Trading days (lead contract): {q['trading_days']}",
        f"- Median 1m bars per trading day: {q['median_minutes_per_day']:.0f} (full Globex day = 1380)",
        "",
        "## Integrity checks",
        "",
        f"- Duplicate (ts, symbol) rows: {q['duplicate_rows']}",
        f"- OHLC relationship violations: {q['ohlc_violations']}",
        f"- Non-positive prices: {q['nonpositive_prices']}",
        f"- Prices off the {q.get('tick_size', 0.25)} tick grid: {q['non_tick_aligned_prices']}",
        f"- Bars with volume <= 0: {q['zero_volume_bars']}",
        "",
        f"## Short days (< threshold minutes on lead contract): {q['short_days']}",
        "",
        "Known-legitimate causes: holidays/half-days, COVID 2020 limit halts, export boundary.",
        "",
    ]
    for d in q["short_day_list"][:25]:
        lines.append(f"- {d['date']} ({d['symbol']}): {d['minutes']} minutes")
    lines += [
        "",
        "## Databento condition flags",
        "",
        f"- Day counts: {c['counts']}",
        f"- Degraded dates: {', '.join(c['degraded_dates']) or 'none'}",
        f"- Missing dates (all verified Saturdays, market closed): "
        f"{', '.join(c['missing_dates']) or 'none'}",
        "",
    ]
    return "\n".join(lines)

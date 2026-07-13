"""M0: inspect the raw Databento export and write a schema/coverage report.

Usage:
  .venv/bin/python scripts/inspect_data.py
  .venv/bin/python scripts/inspect_data.py --config config/data_mes.yaml
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import polars as pl
import yaml

from src.data.databento_loader import load_bars, read_raw_csv
from src.logging_setup import setup_logging

log = logging.getLogger("inspect_data")


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--config",
        default="config/data.yaml",
        help="Data config YAML (default: config/data.yaml; MES: config/data_mes.yaml)",
    )
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    raw_dir = Path(cfg["raw"]["dir"])
    bars_path = raw_dir / cfg["raw"]["bars_file"]

    meta = json.loads((raw_dir / cfg["raw"]["metadata_file"]).read_text())
    raw = read_raw_csv(bars_path)
    spreads = raw.filter(pl.col("symbol").str.contains("-"))
    bars = load_bars(bars_path)

    per_contract = (
        bars.group_by("symbol")
        .agg(
            pl.len().alias("bars"),
            pl.col("ts_utc").min().alias("first_bar"),
            pl.col("ts_utc").max().alias("last_bar"),
            pl.col("volume").sum().alias("total_volume"),
        )
        .sort("first_bar")
    )

    q = meta["query"]
    lines = [
        "# Databento Export Inspection Report",
        "",
        f"- Job: {meta['job_id']}",
        f"- Dataset: {q['dataset']}, schema: {q['schema']}, symbols: {q['symbols']} "
        f"(stype_in={q['stype_in']})",
        f"- Encoding: {q['encoding']} + {q['compression']}, pretty_px/pretty_ts/map_symbols on",
        "- Timestamp convention: UTC ISO-8601 ns, bar-OPEN",
        "- Prices: decimal, unadjusted, expected tick 0.25",
        "",
        f"- Total rows: {raw.height:,}",
        f"- Calendar-spread rows (dropped downstream): {spreads.height:,} "
        f"({spreads['symbol'].n_unique()} spread symbols)",
        f"- Outright rows: {bars.height:,} across {bars['symbol'].n_unique()} contracts",
        f"- Range (UTC): {bars['ts_utc'].min()} -> {bars['ts_utc'].max()}",
        f"- Trading days: {bars['trading_date'].n_unique()}",
        "",
        "## Per-contract coverage",
        "",
        "| Contract | Bars | First bar (UTC) | Last bar (UTC) | Total volume |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in per_contract.to_dicts():
        lines.append(
            f"| {r['symbol']} | {r['bars']:,} | {r['first_bar']} | {r['last_bar']} "
            f"| {r['total_volume']:,} |"
        )
    lines.append("")

    out = Path(cfg["reports_dir"]) / "data_inspection.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    log.info("wrote %s", out)


if __name__ == "__main__":
    main()

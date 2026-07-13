"""M5: compare a TradingView OHLCV export against the Databento continuous series.

The export's bar interval is auto-detected (1/3/5/15/30 minutes) and matched
against the corresponding continuous_{N}m.parquet, so deep-history exports on
higher timeframes work around TradingView's 1-minute history limit.

Usage: .venv/bin/python scripts/compare_tradingview.py <tradingview_export.csv>
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import polars as pl
import yaml

from src.data.tradingview_compare import (
    compare,
    detect_interval_minutes,
    load_tradingview_export,
    render_report,
)
from src.logging_setup import setup_logging

log = logging.getLogger("compare_tradingview")


def main() -> None:
    setup_logging()
    cfg = yaml.safe_load(Path("config/data.yaml").read_text())
    tv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if tv_path is None:
        exports = sorted(Path(cfg["tradingview_exports_dir"]).glob("*.csv"))
        if not exports:
            raise SystemExit("no TradingView exports found; pass a CSV path")
        tv_path = exports[-1]
    log.info("comparing against %s", tv_path)

    tv = load_tradingview_export(tv_path)
    minutes = detect_interval_minutes(tv)
    supported = [1] + list(cfg["resample_minutes"])
    if minutes not in supported:
        raise SystemExit(
            f"TradingView export is {minutes}-minute bars; supported: {supported}. "
            "Re-export on a supported timeframe."
        )
    db_file = Path(cfg["processed_dir"]) / f"continuous_{minutes}m.parquet"
    log.info("detected %d-minute bars; comparing against %s", minutes, db_file.name)

    db = pl.read_parquet(db_file)
    res = compare(db, tv, tick_size=cfg["tick_size"])

    out = Path(cfg["reports_dir"]) / f"tradingview_comparison_{minutes}m.md"
    out.write_text(render_report(res))
    log.info("wrote %s", out)
    print(render_report(res))


if __name__ == "__main__":
    main()

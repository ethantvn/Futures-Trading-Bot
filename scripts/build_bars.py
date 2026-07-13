"""M2-M4: build the processed datasets from the raw Databento export.

Outputs (data/processed/):
- bars_1m.parquet            normalized outright 1m bars, all contracts
- roll_calendar.parquet      trading_date -> lead contract
- continuous_1m.parquet      lead-contract splice with *_adj back-adjusted prices
- continuous_{3,5,15,30}m.parquet
Also writes data/reports/data_quality.{md,json}.

Usage:
  .venv/bin/python scripts/build_bars.py
  .venv/bin/python scripts/build_bars.py --config config/data_mes.yaml
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import yaml

from src.data.databento_loader import load_bars
from src.data.resampling import resample
from src.data.rollover import build_continuous, build_roll_calendar
from src.data.validation import check_bars, render_markdown, summarize_condition
from src.logging_setup import setup_logging

log = logging.getLogger("build_bars")


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
    processed = Path(cfg["processed_dir"])
    reports = Path(cfg["reports_dir"])
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    bars = load_bars(raw_dir / cfg["raw"]["bars_file"])
    bars.write_parquet(processed / "bars_1m.parquet")
    log.info("wrote bars_1m.parquet (%d rows)", bars.height)

    quality = check_bars(
        bars,
        tick_size=cfg["tick_size"],
        min_minutes_full_day=cfg["quality"]["min_minutes_full_day"],
    )
    condition = summarize_condition(raw_dir / cfg["raw"]["condition_file"])
    (reports / "data_quality.json").write_text(
        json.dumps({"quality": quality, "condition": condition}, indent=2)
    )
    (reports / "data_quality.md").write_text(render_markdown(quality, condition))
    log.info("wrote data_quality.{md,json}")

    roll_cfg = cfg["rollover"]
    liquid = roll_cfg.get("liquid_month_codes")
    liquid_frozen = frozenset(liquid) if liquid else None
    calendar = build_roll_calendar(
        bars,
        roll_cfg["confirm_sessions"],
        liquid_month_codes=liquid_frozen,
    )
    calendar.write_parquet(processed / "roll_calendar.parquet")

    cont = build_continuous(bars, calendar)
    cont.write_parquet(processed / "continuous_1m.parquet")
    log.info("wrote continuous_1m.parquet (%d rows)", cont.height)

    for m in cfg["resample_minutes"]:
        res = resample(cont, m)
        res.write_parquet(processed / f"continuous_{m}m.parquet")
        log.info("wrote continuous_%dm.parquet (%d rows)", m, res.height)


if __name__ == "__main__":
    main()

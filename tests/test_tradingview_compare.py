from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.data.tradingview_compare import (
    compare,
    detect_interval_minutes,
    load_tradingview_export,
    render_report,
)


def db_frame(epochs: list[int], px: float = 100.0) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "ts_utc": [datetime.fromtimestamp(e, tz=timezone.utc) for e in epochs],
            "open": [px] * len(epochs),
            "high": [px + 1] * len(epochs),
            "low": [px - 1] * len(epochs),
            "close": [px + 0.5] * len(epochs),
            "volume": [10] * len(epochs),
        },
        schema_overrides={"ts_utc": pl.Datetime("ns", "UTC")},
    )


def write_tv_csv(path: Path, epochs: list[int], px: float, with_volume: bool) -> Path:
    cols = ["time,open,high,low,close" + (",Volume" if with_volume else "") + ",RSI"]
    for e in epochs:
        row = f"{e},{px},{px + 1},{px - 1},{px + 0.5}"
        if with_volume:
            row += ",10"
        row += ",55.1"  # indicator column that must be ignored
        cols.append(row)
    path.write_text("\n".join(cols))
    return path


def test_perfect_match(tmp_path: Path):
    epochs = [1700000000 + 60 * i for i in range(10)]
    tv = load_tradingview_export(write_tv_csv(tmp_path / "tv.csv", epochs, 100.0, True))
    res = compare(db_frame(epochs, 100.0), tv)
    assert res.overlap_bars == 10
    assert res.tv_only == 0 and res.db_only == 0
    assert res.pct_candles_matching == 100.0
    assert res.volume_compared
    assert "100.00%" in render_report(res)


def test_mismatch_and_missing_bars(tmp_path: Path):
    db_epochs = [1700000000 + 60 * i for i in range(10)]
    tv_epochs = db_epochs[2:] + [1700000000 + 60 * 20]  # missing 2, one extra
    tv = load_tradingview_export(write_tv_csv(tmp_path / "tv.csv", tv_epochs, 100.25, False))
    res = compare(db_frame(db_epochs, 100.0), tv)
    assert res.overlap_bars == 8
    assert res.tv_only == 1
    assert res.db_only == 2
    assert res.pct_candles_matching == 0.0
    assert res.field_stats["open"]["max_abs_diff"] == 0.25
    assert not res.volume_compared
    assert "Volume was not compared" in render_report(res)


def test_detect_interval_robust_to_gaps(tmp_path: Path):
    # 30m bars with a weekend-sized hole in the middle
    epochs = [1700000000 + 1800 * i for i in range(20)]
    epochs += [epochs[-1] + 2 * 24 * 3600 + 1800 * i for i in range(20)]
    tv = load_tradingview_export(write_tv_csv(tmp_path / "tv.csv", epochs, 100.0, False))
    assert detect_interval_minutes(tv) == 30


def test_no_overlap_reports_cleanly(tmp_path: Path):
    tv = load_tradingview_export(
        write_tv_csv(tmp_path / "tv.csv", [1800000000], 100.0, False)
    )
    res = compare(db_frame([1700000000]), tv)
    assert res.overlap_bars == 0
    assert "No overlapping timestamps" in render_report(res)

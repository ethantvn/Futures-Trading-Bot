from __future__ import annotations

from datetime import date, datetime

from src.data.validation import check_bars
from tests.conftest import bar, make_bars


def test_check_bars_flags_issues():
    d = date(2024, 1, 16)
    rows = [
        bar(datetime(2024, 1, 16, 14, 30), "MNQH4", 100.0, 10, d),
        bar(datetime(2024, 1, 16, 14, 31), "MNQH4", 100.0, 10, d),
        # duplicate timestamp+symbol
        bar(datetime(2024, 1, 16, 14, 31), "MNQH4", 100.25, 10, d),
        # off-tick price
        bar(datetime(2024, 1, 16, 14, 32), "MNQH4", 100.1, 10, d),
        # zero volume
        bar(datetime(2024, 1, 16, 14, 33), "MNQH4", 100.0, 0, d),
    ]
    df = make_bars(rows)
    # inject an OHLC violation: high below open
    df = df.with_columns(
        df["high"].scatter(0, 90.0)
    )
    res = check_bars(df, tick_size=0.25, min_minutes_full_day=3)

    assert res["duplicate_rows"] == 1
    assert res["ohlc_violations"] == 1
    assert res["zero_volume_bars"] == 1
    # 100.1 appears in open and is used to derive h/l/c in the fixture:
    # all four fields of that bar are off-grid
    assert res["non_tick_aligned_prices"] == 4
    assert res["trading_days"] == 1


def test_clean_frame_passes():
    d = date(2024, 1, 16)
    rows = [
        bar(datetime(2024, 1, 16, 14, 30 + i), "MNQH4", 100.0 + 0.25 * i, 10, d)
        for i in range(5)
    ]
    res = check_bars(make_bars(rows), tick_size=0.25, min_minutes_full_day=3)
    assert res["duplicate_rows"] == 0
    assert res["ohlc_violations"] == 0
    assert res["non_tick_aligned_prices"] == 0
    assert res["zero_volume_bars"] == 0
    assert res["short_days"] == 0

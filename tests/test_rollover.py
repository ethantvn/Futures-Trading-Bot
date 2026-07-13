from __future__ import annotations

from datetime import date, datetime, timedelta

import polars as pl

from src.data.rollover import build_continuous, build_roll_calendar, contract_order
from tests.conftest import bar, make_bars


def two_contract_fixture() -> pl.DataFrame:
    """Contract B trades at a constant +50 premium to A.

    Daily volumes: A leads on d1-d2; B's volume exceeds A's on d3, so the roll
    must take effect on d4 (next session), never d3 (look-ahead safety).
    """
    days = [date(2024, 3, 11 + i) for i in range(5)]  # d1..d5, Mon-Fri
    vols_a = [100, 100, 80, 40, 10]
    vols_b = [10, 20, 90, 120, 200]
    rows = []
    for i, d in enumerate(days):
        for minute in range(3):
            ts = datetime(d.year, d.month, d.day, 15, minute)  # 15:0x UTC
            px = 100.0 + i + 0.25 * minute
            rows.append(bar(ts, "MNQH4", px, vols_a[i], d, spread=0.25))
            rows.append(bar(ts, "MNQM4", px + 50.0, vols_b[i], d, spread=0.25))
    # make B expire later than A so expiry order is A -> B; price continues
    # the +1/day drift (B close on d5 is 154.625, so 155.5 + 0.125 = 155.625)
    rows.append(bar(datetime(2024, 3, 18, 15, 0), "MNQM4", 155.5, 100, date(2024, 3, 18), spread=0.25))
    return make_bars(rows)


def test_contract_order_is_data_driven():
    bars = two_contract_fixture()
    assert contract_order(bars) == ["MNQH4", "MNQM4"]


def test_liquid_month_filter_excludes_thin_contracts():
    """GC-style: only G/J/M/Q/V/Z months in roll path."""
    days = [date(2024, 6, 10 + i) for i in range(6)]
    rows = []
    for i, d in enumerate(days):
        ts = datetime(d.year, d.month, d.day, 15, 0)
        rows.append(bar(ts, "GCG4", 100.0, 100 - i * 10, d, spread=0.10))
        rows.append(bar(ts, "GCQ4", 100.0, 50 + i * 20, d, spread=0.10))
        # thin non-standard month — should never become lead
        rows.append(bar(ts, "GCK4", 100.0, 200, d, spread=0.10))
    bars = make_bars(rows)
    cal = build_roll_calendar(
        bars, confirm_sessions=1, liquid_month_codes=frozenset("GJMQVZ")
    )
    months = cal["symbol"].str.slice(-2, 1).unique().to_list()
    assert set(months) <= {"G", "Q"}
    assert "K" not in months


def test_roll_effective_next_session():
    bars = two_contract_fixture()
    cal = build_roll_calendar(bars, confirm_sessions=1)
    lead = {str(r["trading_date"]): r["symbol"] for r in cal.to_dicts()}
    assert lead["2024-03-11"] == "MNQH4"
    assert lead["2024-03-12"] == "MNQH4"
    # B out-trades A on d3 but the roll takes effect on d4
    assert lead["2024-03-13"] == "MNQH4"
    assert lead["2024-03-14"] == "MNQM4"
    assert lead["2024-03-15"] == "MNQM4"


def test_look_ahead_safety():
    """The lead on day T must not change when day T's volumes change."""
    bars = two_contract_fixture()
    cal_before = build_roll_calendar(bars, confirm_sessions=1)
    # Blow up B's volume on d3 only: decision for d3 was made at d2 close, so
    # d3's lead must stay A either way.
    boosted = bars.with_columns(
        pl.when(
            (pl.col("trading_date") == date(2024, 3, 13)) & (pl.col("symbol") == "MNQM4")
        )
        .then(pl.col("volume") * 1000)
        .otherwise(pl.col("volume"))
        .alias("volume")
    )
    cal_after = build_roll_calendar(boosted, confirm_sessions=1)
    d3_before = cal_before.filter(pl.col("trading_date") == date(2024, 3, 13))["symbol"][0]
    d3_after = cal_after.filter(pl.col("trading_date") == date(2024, 3, 13))["symbol"][0]
    assert d3_before == d3_after == "MNQH4"


def test_back_adjustment_removes_roll_gap():
    bars = two_contract_fixture()
    cal = build_roll_calendar(bars, confirm_sessions=1)
    cont = build_continuous(bars, cal).sort("ts_utc")

    # Raw close jumps +50 at the roll (plus the real +1/day drift); adjusted
    # close must show only the real drift.
    daily_close = cont.group_by("trading_date", maintain_order=True).last()
    raw_jumps = daily_close["close"].diff().drop_nulls().to_list()
    adj_jumps = daily_close["close_adj"].diff().drop_nulls().to_list()
    assert max(raw_jumps) > 25.0  # roll gap visible in raw prices
    assert all(abs(j - 1.0) < 1e-9 for j in adj_jumps)  # only the 1 pt/day drift

    # The latest segment is never adjusted; P&L on raw prices stays real.
    last_seg = cont.filter(pl.col("symbol") == "MNQM4")
    assert (last_seg["close_adj"] == last_seg["close"]).all()


def test_forced_roll_when_lead_stops_trading():
    d1, d2 = date(2024, 3, 11), date(2024, 3, 12)
    rows = [
        bar(datetime(2024, 3, 11, 15, 0), "MNQH4", 100.0, 100, d1, spread=0.25),
        bar(datetime(2024, 3, 11, 15, 0), "MNQM4", 150.0, 10, d1, spread=0.25),
        # A disappears entirely on d2
        bar(datetime(2024, 3, 12, 15, 0), "MNQM4", 151.0, 10, d2, spread=0.25),
    ]
    cal = build_roll_calendar(make_bars(rows), confirm_sessions=1)
    lead = {str(r["trading_date"]): r["symbol"] for r in cal.to_dicts()}
    assert lead["2024-03-11"] == "MNQH4"
    assert lead["2024-03-12"] == "MNQM4"

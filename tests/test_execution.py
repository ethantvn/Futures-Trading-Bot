from __future__ import annotations

import pytest

from src.backtest.execution import (
    LONG,
    SHORT,
    OpenPosition,
    PendingEntry,
    check_exit,
    fill_entry,
)

TICK = 0.25
SLIP = 0.25  # 1 tick


def pe(side: int, kind: str, price: float | None) -> PendingEntry:
    return PendingEntry(side=side, kind=kind, price=price, stop=0.0, target=None, qty=1, expire_ts=None)


class TestEntryFills:
    def test_market_fills_at_open_plus_slippage(self):
        assert fill_entry(pe(LONG, "market", None), 100.0, 101, 99, SLIP, TICK) == 100.25
        assert fill_entry(pe(SHORT, "market", None), 100.0, 101, 99, SLIP, TICK) == 99.75

    def test_stop_entry_normal_trigger(self):
        # long stop 100.5; bar trades up through it
        assert fill_entry(pe(LONG, "stop", 100.5), 100.0, 101, 99.9, SLIP, TICK) == 100.75

    def test_stop_entry_gap_through_fills_at_open(self):
        # open already above the stop: worse fill at the open
        assert fill_entry(pe(LONG, "stop", 100.5), 102.0, 103, 101.5, SLIP, TICK) == 102.25

    def test_stop_entry_no_trigger(self):
        assert fill_entry(pe(LONG, "stop", 100.5), 100.0, 100.4, 99.9, SLIP, TICK) is None

    def test_limit_touch_is_not_fill(self):
        # buy limit 100: bar low exactly 100 (touch) -> NO fill
        assert fill_entry(pe(LONG, "limit", 100.0), 100.5, 101, 100.0, SLIP, TICK) is None

    def test_limit_trade_through_fills_at_limit(self):
        # low 99.75 = limit - 1 tick -> fill at limit, no slippage
        assert fill_entry(pe(LONG, "limit", 100.0), 100.5, 101, 99.75, SLIP, TICK) == 100.0

    def test_limit_favorable_gap_fills_at_open(self):
        assert fill_entry(pe(LONG, "limit", 100.0), 99.0, 100.5, 98.5, SLIP, TICK) == 99.0

    def test_short_limit_symmetric(self):
        assert fill_entry(pe(SHORT, "limit", 100.0), 99.5, 100.25, 99.0, SLIP, TICK) == 100.0
        assert fill_entry(pe(SHORT, "limit", 100.0), 99.5, 100.0, 99.0, SLIP, TICK) is None


def pos(side: int, stop: float, target: float | None) -> OpenPosition:
    return OpenPosition(side=side, qty=1, entry_px=100.0, entry_ts=0, stop=stop, target=target)


class TestExits:
    def test_long_stop_normal(self):
        fill, reason, amb = check_exit(pos(LONG, 99.0, None), 100.0, 100.5, 98.9, SLIP, TICK)
        assert (fill, reason, amb) == (98.75, "stop", False)  # stop - slip

    def test_long_stop_gap_through_fills_at_open(self):
        fill, reason, _ = check_exit(pos(LONG, 99.0, None), 98.0, 98.5, 97.5, SLIP, TICK)
        assert fill == 97.75 and reason == "stop"  # open - slip, worse than stop

    def test_long_target_requires_trade_through(self):
        # high exactly at target -> touch, no fill
        assert check_exit(pos(LONG, 98.0, 101.0), 100.0, 101.0, 99.5, SLIP, TICK) is None
        # high 1 tick beyond -> fill at target, no slippage on limit exit
        fill, reason, _ = check_exit(pos(LONG, 98.0, 101.0), 100.0, 101.25, 99.5, SLIP, TICK)
        assert (fill, reason) == (101.0, "target")

    def test_stop_beats_target_same_bar_and_flags_ambiguous(self):
        fill, reason, amb = check_exit(pos(LONG, 99.0, 101.0), 100.0, 101.5, 98.5, SLIP, TICK)
        assert reason == "stop" and amb is True and fill == 98.75

    def test_entry_bar_blocks_target(self):
        res = check_exit(pos(LONG, 98.0, 101.0), 100.0, 101.5, 99.5, SLIP, TICK, entry_bar=True)
        assert res is None  # target reachable but suppressed on entry bar

    def test_short_exits_symmetric(self):
        fill, reason, _ = check_exit(pos(SHORT, 101.0, None), 100.0, 101.2, 99.0, SLIP, TICK)
        assert (fill, reason) == (101.25, "stop")  # stop + slip
        fill, reason, _ = check_exit(pos(SHORT, 102.0, 99.0), 100.0, 100.5, 98.5, SLIP, TICK)
        assert (fill, reason) == (99.0, "target")

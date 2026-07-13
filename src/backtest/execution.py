"""Fill simulation on 1-minute bars, deliberately pessimistic.

Rules (docs/PHASE_1_PLAN.md section 4.4):
- Market orders fill at the bar open +/- slippage.
- Stop entries: if the bar gaps through the stop, fill at the open (worse),
  otherwise at the stop price; slippage applied against the trader.
- Limit orders require the bar to trade THROUGH the limit by >= 1 tick
  (touch != fill). A favorable gap fills at the open. No slippage on limits.
- Protective stops: gap-through fills at the open (worse), else at the stop,
  slippage against the trader.
- Targets are limit orders (trade-through required, favorable gap at open).
- If both stop and target could fill within one bar, the STOP fills
  (pessimistic); such bars are counted as ambiguous.
- On the bar where an entry fills, only the protective stop may also fill
  (pessimistic); the target may not.
"""
from __future__ import annotations

from dataclasses import dataclass

LONG = 1
SHORT = -1


@dataclass
class PendingEntry:
    """An entry order awaiting a fill, prices in RAW contract points."""
    side: int                 # LONG / SHORT
    kind: str                 # "market" | "stop" | "limit"
    price: float | None       # trigger/limit price; None for market
    stop: float               # protective stop (raw)
    target: float | None      # profit target (raw), None = no target
    qty: int
    expire_ts: int | None     # exec-bar ts (ns) at/after which the order dies
    tag: str = ""


@dataclass
class OpenPosition:
    side: int
    qty: int
    entry_px: float
    entry_ts: int             # ns
    stop: float
    target: float | None
    tag: str = ""


def fill_entry(
    pe: PendingEntry, o: float, h: float, l: float, slip: float, tick: float
) -> float | None:
    """Return the raw fill price for this bar, or None if not filled."""
    if pe.kind == "market":
        return o + pe.side * slip
    if pe.kind == "stop":
        if pe.side == LONG:
            if o >= pe.price:
                return o + slip           # gapped through: worse fill
            if h >= pe.price:
                return pe.price + slip
        else:
            if o <= pe.price:
                return o - slip
            if l <= pe.price:
                return pe.price - slip
        return None
    if pe.kind == "limit":
        if pe.side == LONG:
            if o <= pe.price - tick:
                return o                  # favorable gap
            if l <= pe.price - tick:
                return pe.price           # traded through by >= 1 tick
        else:
            if o >= pe.price + tick:
                return o
            if h >= pe.price + tick:
                return pe.price
        return None
    raise ValueError(f"unknown order kind {pe.kind}")


def check_exit(
    pos: OpenPosition,
    o: float,
    h: float,
    l: float,
    slip: float,
    tick: float,
    entry_bar: bool = False,
) -> tuple[float, str, bool] | None:
    """Return (fill_px, reason, ambiguous) if the position exits on this bar.

    reason is "stop" or "target". `entry_bar` disables target fills
    (pessimistic same-bar policy). If both stop and target are reachable in
    the same bar, the stop wins and the bar is flagged ambiguous.
    """
    if pos.side == LONG:
        stop_hit = o <= pos.stop or l <= pos.stop
        stop_px = (o if o <= pos.stop else pos.stop) - slip
        tgt_hit = pos.target is not None and (o >= pos.target or h >= pos.target + tick)
        tgt_px = None if pos.target is None else (o if o >= pos.target else pos.target)
    else:
        stop_hit = o >= pos.stop or h >= pos.stop
        stop_px = (o if o >= pos.stop else pos.stop) + slip
        tgt_hit = pos.target is not None and (o <= pos.target or l <= pos.target - tick)
        tgt_px = None if pos.target is None else (o if o <= pos.target else pos.target)

    if entry_bar:
        tgt_hit = False
    if stop_hit and tgt_hit:
        return stop_px, "stop", True
    if stop_hit:
        return stop_px, "stop", entry_bar
    if tgt_hit:
        return tgt_px, "target", False
    return None

"""Futures rollover: look-ahead-safe volume roll calendar and continuous series.

Design (docs/PHASE_1_PLAN.md section 4.2):
- The lead contract for trading date T is decided using volumes through T-1
  only ("evaluated at session close, effective next session"), so the roll
  never uses future information.
- Two continuous series are produced: raw spliced prices (for fills/P&L) and
  back-adjusted prices (columns *_adj, for indicators), using additive gap
  adjustment measured at the last minute where old and new lead both traded.
"""
from __future__ import annotations

import logging

import polars as pl

log = logging.getLogger(__name__)


MONTH_CODES = {"F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6,
               "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12}


def _month_code(symbol: str) -> str:
    return symbol[-2]


def contract_order(
    bars: pl.DataFrame,
    liquid_month_codes: frozenset[str] | None = None,
) -> list[str]:
    """Contracts ordered by expiry, parsed from the symbol.

    The single year digit (MNQZ6) is ambiguous by itself; it is disambiguated
    with the contract's first trade year: the expiry year is the smallest year
    >= first-trade-year whose last digit matches. (Ordering by last bar
    timestamp instead would break at the export boundary, where several live
    contracts share the same final bar.)
    """
    firsts = (
        bars.group_by("symbol")
        .agg(pl.col("ts_utc").min().alias("first"))
        .to_dicts()
    )

    def expiry(symbol: str, first_year: int) -> tuple[int, int]:
        month = MONTH_CODES[symbol[-2]]
        digit = int(symbol[-1])
        year = first_year
        while year % 10 != digit:
            year += 1
        return year, month

    keyed = [(expiry(r["symbol"], r["first"].year), r["symbol"]) for r in firsts]
    ordered = [s for _, s in sorted(keyed)]
    if liquid_month_codes is not None:
        ordered = [s for s in ordered if _month_code(s) in liquid_month_codes]
    return ordered


def build_roll_calendar(
    bars: pl.DataFrame,
    confirm_sessions: int = 1,
    liquid_month_codes: frozenset[str] | None = None,
) -> pl.DataFrame:
    """Map every trading date to its lead contract, look-ahead-safe.

    Starting from the highest-volume contract on the first date, we advance to
    the next contract in expiry order once its daily volume has exceeded the
    current lead's for `confirm_sessions` consecutive sessions; the roll takes
    effect the FOLLOWING session. If the current lead stops trading, we roll
    immediately.
    """
    order = contract_order(bars, liquid_month_codes=liquid_month_codes)
    if not order:
        raise ValueError("no contracts after liquid_month_codes filter")
    rank = {s: i for i, s in enumerate(order)}

    daily = (
        bars.group_by("trading_date", "symbol")
        .agg(pl.col("volume").sum().alias("volume"))
        .sort("trading_date")
    )
    dates = daily["trading_date"].unique().sort().to_list()
    vol: dict[tuple[object, str], int] = {
        (r["trading_date"], r["symbol"]): r["volume"] for r in daily.to_dicts()
    }

    first_day = daily.filter(
        pl.col("trading_date") == dates[0],
        pl.col("symbol").is_in(order),
    )
    current = first_day.sort("volume", descending=True)["symbol"][0]

    out: list[dict[str, object]] = []
    streak = 0
    pending_roll_to: str | None = None
    for d in dates:
        # A roll decided at the close of the previous session takes effect now.
        if pending_roll_to is not None:
            current = pending_roll_to
            pending_roll_to = None
            streak = 0
        # If the current lead no longer trades at all, jump to the next
        # contract that does (safety for expiry gaps).
        if vol.get((d, current), 0) == 0:
            candidates = [s for s in order if rank[s] > rank[current] and vol.get((d, s), 0) > 0]
            if candidates:
                current = candidates[0]
                streak = 0
        out.append({"trading_date": d, "symbol": current})

        nxt_idx = rank[current] + 1
        nxt = order[nxt_idx] if nxt_idx < len(order) else None
        if nxt is not None and vol.get((d, nxt), 0) > vol.get((d, current), 0):
            streak += 1
        else:
            streak = 0
        if streak >= confirm_sessions:
            pending_roll_to = nxt

    cal = pl.DataFrame(out)
    n_rolls = (cal["symbol"] != cal["symbol"].shift(1)).sum() - 1
    log.info("roll calendar: %d trading days, %d rolls", cal.height, n_rolls)
    return cal


def build_continuous(bars: pl.DataFrame, calendar: pl.DataFrame) -> pl.DataFrame:
    """Splice lead-contract bars into a continuous series with back-adjustment.

    Output columns: the input bar columns (raw, unadjusted prices) plus
    `open_adj/high_adj/low_adj/close_adj` where a cumulative additive offset
    aligns each older segment to the most recent contract's price level.
    """
    cont = bars.join(calendar, on=["trading_date", "symbol"], how="inner").sort("ts_utc")

    # Roll boundaries: dates where the lead changes.
    cal = calendar.sort("trading_date").with_columns(pl.col("symbol").shift(1).alias("prev"))
    rolls = cal.filter(pl.col("symbol") != pl.col("prev")).drop_nulls("prev")

    # Per-roll gap measured on the last session BEFORE the roll takes effect,
    # at the last minute where both contracts traded.
    boundary_dates = rolls["trading_date"].to_list()
    prev_syms = rolls["prev"].to_list()
    new_syms = rolls["symbol"].to_list()
    all_dates = calendar["trading_date"].sort().to_list()
    date_idx = {d: i for i, d in enumerate(all_dates)}

    gaps: list[tuple[object, float]] = []  # (effective_date, new_close - old_close)
    for eff_date, old_sym, new_sym in zip(boundary_dates, prev_syms, new_syms):
        prev_date = all_dates[date_idx[eff_date] - 1]
        day = bars.filter(pl.col("trading_date") == prev_date)
        both = (
            day.filter(pl.col("symbol").is_in([old_sym, new_sym]))
            .group_by("ts_utc")
            .agg(pl.len().alias("n"), pl.col("symbol"), pl.col("close"))
            .filter(pl.col("n") == 2)
            .sort("ts_utc")
        )
        if both.height == 0:
            log.warning("no overlapping minute for roll %s->%s on %s", old_sym, new_sym, prev_date)
            gaps.append((eff_date, 0.0))
            continue
        last = both.tail(1).to_dicts()[0]
        pair = dict(zip(last["symbol"], last["close"]))
        gaps.append((eff_date, float(pair[new_sym] - pair[old_sym])))

    # Cumulative offset: newest segment gets 0; each earlier segment adds the
    # gaps of all rolls that happen after it.
    cum = 0.0
    seg_offsets: dict[object, float] = {}
    for eff_date, gap in reversed(gaps):
        seg_offsets[eff_date] = cum  # segment starting at eff_date
        cum += gap
    # The very first segment (before the first roll) gets the full cumulative gap.
    first_seg_offset = cum

    # Assign per-date offsets.
    boundary_sorted = sorted(seg_offsets.keys())
    def offset_for(d: object) -> float:
        off = first_seg_offset
        for b in boundary_sorted:
            if d >= b:
                off = seg_offsets[b]
            else:
                break
        return off

    off_df = pl.DataFrame(
        {
            "trading_date": all_dates,
            "adj_offset": [offset_for(d) for d in all_dates],
        }
    )
    cont = cont.join(off_df, on="trading_date", how="left")
    cont = cont.with_columns(
        (pl.col("open") + pl.col("adj_offset")).alias("open_adj"),
        (pl.col("high") + pl.col("adj_offset")).alias("high_adj"),
        (pl.col("low") + pl.col("adj_offset")).alias("low_adj"),
        (pl.col("close") + pl.col("adj_offset")).alias("close_adj"),
    )
    return cont

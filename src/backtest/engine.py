"""Event-driven backtest engine: signals on any timeframe, fills on 1m bars.

Look-ahead discipline:
- A signal bar (bar-open ts S, timeframe tf) completes at S + tf. Its signals
  become actionable on the first 1-minute bar whose open ts >= S + tf.
- Strategies express all prices in BACK-ADJUSTED space; the engine converts
  to raw contract prices using the execution bar's `adj_offset` (constant
  within a contract segment; positions never span rolls because every
  position is flat by the session cutoff).

Strategy contract: `Strategy.prepare(signal_df)` returns the frame with these
columns added (all computed causally — using data up to and including each
bar only):
    enter_long, enter_short        bool  (emit on the RISING EDGE of a setup)
    entry_kind                     str   "market" | "stop" | "limit"
    entry_price_long_adj           f64   nullable (None for market)
    entry_price_short_adj          f64   nullable
    stop_long_adj, stop_short_adj  f64   protective stops
    target_long_adj, target_short_adj  f64 nullable
    exit_long, exit_short          bool  close an open position at next open
    expire_minutes                 i64   nullable pending-order lifetime
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import time

import numpy as np
import polars as pl

from src.backtest.execution import LONG, SHORT, OpenPosition, PendingEntry, check_exit, fill_entry
from src.backtest.fees import CostModel

log = logging.getLogger(__name__)

MIN_NS = 60_000_000_000


@dataclass
class EngineConfig:
    qty: int = 1
    flat_time: str = "15:55"          # ET; force-close and stop trading
    no_entry_after: str = "15:30"     # ET; pendings cancelled at this time
    max_trades_per_day: int | None = None
    max_hold_minutes: int | None = None
    daily_loss_stop: float | None = None    # dollars, net
    daily_profit_lock: float | None = None  # dollars, net


@dataclass
class BacktestResult:
    trades: pl.DataFrame
    n_signal_bars: int
    n_exec_bars: int
    ambiguous_bars: int
    forced_session_end_exits: int


def _minute_of_day(ts_ny: pl.Expr) -> pl.Expr:
    # cast first: dt.hour() is Int8 and hour*60 overflows it
    return ts_ny.dt.hour().cast(pl.Int32) * 60 + ts_ny.dt.minute().cast(pl.Int32)


def _parse_hhmm(s: str) -> int:
    t = time.fromisoformat(s)
    return t.hour * 60 + t.minute


def run_backtest(
    exec_bars: pl.DataFrame,
    signal_bars: pl.DataFrame,
    timeframe_minutes: int,
    cost: CostModel,
    cfg: EngineConfig,
    strategy_name: str = "",
) -> BacktestResult:
    """Run one strategy's prepared signal frame against 1-minute execution bars."""
    ex = exec_bars.sort("ts_utc").with_columns(
        _minute_of_day(pl.col("ts_ny")).alias("mod"),
        pl.col("trading_date").cast(pl.Int32).alias("td"),
    )
    ts = ex["ts_utc"].cast(pl.Int64).to_numpy()
    o = ex["open"].to_numpy()
    h = ex["high"].to_numpy()
    l = ex["low"].to_numpy()
    c = ex["close"].to_numpy()
    off = ex["adj_offset"].to_numpy()
    mod = ex["mod"].to_numpy()
    td = ex["td"].to_numpy()
    dates = ex["trading_date"].to_list()
    symbols = ex["symbol"].to_list()

    sg = signal_bars.sort("ts_utc")
    s_end = (sg["ts_utc"].cast(pl.Int64) + timeframe_minutes * MIN_NS).to_numpy()
    s_cols = {
        c: sg[c].to_numpy()
        for c in (
            "enter_long", "enter_short", "exit_long", "exit_short",
            "entry_price_long_adj", "entry_price_short_adj",
            "stop_long_adj", "stop_short_adj",
            "target_long_adj", "target_short_adj",
            "expire_minutes",
        )
    }
    s_kind = sg["entry_kind"].to_list()

    slip = cost.slippage_points
    tick = cost.tick_size
    flat_mod = _parse_hhmm(cfg.flat_time)
    no_entry_mod = _parse_hhmm(cfg.no_entry_after)

    pendings: list[PendingEntry] = []
    pos: OpenPosition | None = None
    trades: list[dict] = []
    ambiguous_bars = 0
    forced_session_end = 0

    cur_td = -1
    day_pnl = 0.0
    day_trades = 0
    day_blocked = False
    signal_exit = False

    j = 0  # next unprocessed signal bar
    n = len(ts)

    def close_position(i: int, px: float, reason: str, ambiguous: bool = False) -> None:
        nonlocal pos, day_pnl, day_trades, day_blocked
        gross, costs, net = cost.trade_pnl(pos.side, pos.entry_px, px, pos.qty)
        trades.append(
            {
                "strategy": strategy_name,
                "trading_date": dates[i],
                "symbol": symbols[i],
                "side": pos.side,
                "qty": pos.qty,
                "entry_ts": pos.entry_ts,
                "exit_ts": ts[i],
                "entry_px": pos.entry_px,
                "exit_px": px,
                "gross_pnl": gross,
                "costs": costs,
                "net_pnl": net,
                "exit_reason": reason,
                "ambiguous": ambiguous,
                "tag": pos.tag,
            }
        )
        day_pnl += net
        day_trades += 1
        pos = None
        if cfg.daily_loss_stop is not None and day_pnl <= -cfg.daily_loss_stop:
            day_blocked = True
        if cfg.daily_profit_lock is not None and day_pnl >= cfg.daily_profit_lock:
            day_blocked = True
        if cfg.max_trades_per_day is not None and day_trades >= cfg.max_trades_per_day:
            day_blocked = True

    for i in range(n):
        # New trading date: reset day state. A still-open position means the
        # previous session ended before flat_time (early close) — force-close
        # it at its last known stop-managed price boundary: previous bar close.
        if td[i] != cur_td:
            if pos is not None:
                close_position(i - 1, c[i - 1], "session_end")
                forced_session_end += 1
            cur_td = td[i]
            day_pnl = 0.0
            day_trades = 0
            day_blocked = False
            pendings.clear()

        # 1) process signal bars completed at or before this bar's open
        signal_exit = False
        while j < len(s_end) and s_end[j] <= ts[i]:
            if pos is not None:
                if (pos.side == LONG and s_cols["exit_long"][j]) or (
                    pos.side == SHORT and s_cols["exit_short"][j]
                ):
                    signal_exit = True
            if not day_blocked and mod[i] < no_entry_mod:
                new: list[PendingEntry] = []
                exp = s_cols["expire_minutes"][j]
                expf = float(exp) if exp is not None else float("nan")
                expire_ts = None if np.isnan(expf) else ts[i] + int(expf) * MIN_NS
                for side, eflag, pcol, scol, tcol in (
                    (LONG, "enter_long", "entry_price_long_adj", "stop_long_adj", "target_long_adj"),
                    (SHORT, "enter_short", "entry_price_short_adj", "stop_short_adj", "target_short_adj"),
                ):
                    if not s_cols[eflag][j]:
                        continue
                    padj = s_cols[pcol][j]
                    tadj = s_cols[tcol][j]
                    new.append(
                        PendingEntry(
                            side=side,
                            kind=s_kind[j],
                            price=None if padj is None or np.isnan(padj) else padj - off[i],
                            stop=s_cols[scol][j] - off[i],
                            target=None if tadj is None or np.isnan(tadj) else tadj - off[i],
                            qty=cfg.qty,
                            expire_ts=expire_ts,
                            tag=f"sig@{s_end[j]}",
                        )
                    )
                if new:
                    pendings = new  # newest setup replaces older pendings (OCO pair allowed)
            j += 1

        at_flat = mod[i] >= flat_mod

        # 2) open-position management at this bar's open
        if pos is not None:
            held_min = (ts[i] - pos.entry_ts) // MIN_NS
            if at_flat or signal_exit or (
                cfg.max_hold_minutes is not None and held_min >= cfg.max_hold_minutes
            ):
                reason = "eod" if at_flat else ("signal" if signal_exit else "max_hold")
                close_position(i, o[i] - pos.side * slip, reason)

        # 3) pending-entry handling
        if pendings:
            if at_flat or day_blocked or mod[i] >= no_entry_mod:
                pendings.clear()
            else:
                pendings = [
                    p for p in pendings if p.expire_ts is None or ts[i] < p.expire_ts
                ]
        if pos is None and pendings and not at_flat and not day_blocked:
            for p in pendings:
                px = fill_entry(p, o[i], h[i], l[i], slip, tick)
                if px is not None:
                    pos = OpenPosition(
                        side=p.side, qty=p.qty, entry_px=px, entry_ts=ts[i],
                        stop=p.stop, target=p.target, tag=p.tag,
                    )
                    pendings.clear()  # OCO: sibling dies with the fill
                    # pessimistic same-bar stop check
                    res = check_exit(pos, o[i], h[i], l[i], slip, tick, entry_bar=True)
                    if res is not None:
                        fill, reason, amb = res
                        ambiguous_bars += int(amb)
                        close_position(i, fill, reason, ambiguous=amb)
                    break

        # 4) stop/target for positions carried into this bar
        elif pos is not None and not at_flat:
            res = check_exit(pos, o[i], h[i], l[i], slip, tick, entry_bar=False)
            if res is not None:
                fill, reason, amb = res
                ambiguous_bars += int(amb)
                close_position(i, fill, reason, ambiguous=amb)

    if pos is not None:
        close_position(n - 1, c[n - 1], "data_end")

    schema = {
        "strategy": pl.Utf8, "trading_date": pl.Date, "symbol": pl.Utf8,
        "side": pl.Int8, "qty": pl.Int32,
        "entry_ts": pl.Int64, "exit_ts": pl.Int64,
        "entry_px": pl.Float64, "exit_px": pl.Float64,
        "gross_pnl": pl.Float64, "costs": pl.Float64, "net_pnl": pl.Float64,
        "exit_reason": pl.Utf8, "ambiguous": pl.Boolean, "tag": pl.Utf8,
    }
    tdf = pl.DataFrame(trades, schema=schema, orient="row") if trades else pl.DataFrame(schema=schema)
    if tdf.height:
        tdf = tdf.with_columns(
            pl.from_epoch("entry_ts", time_unit="ns").dt.replace_time_zone("UTC").alias("entry_ts"),
            pl.from_epoch("exit_ts", time_unit="ns").dt.replace_time_zone("UTC").alias("exit_ts"),
        )
    log.info(
        "%s: %d trades, %d ambiguous bars, %d forced session-end exits",
        strategy_name or "backtest", tdf.height, ambiguous_bars, forced_session_end,
    )
    return BacktestResult(
        trades=tdf,
        n_signal_bars=sg.height,
        n_exec_bars=n,
        ambiguous_bars=ambiguous_bars,
        forced_session_end_exits=forced_session_end,
    )

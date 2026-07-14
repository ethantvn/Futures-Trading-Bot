"""Phase 23 — TradingSim article gold setups (user-override test).

Three causal implementations of the article's testable claims on GC/MGC:

- EmaStochPullback (article #4, + #2 via daily_gate): 20/50 EMA state on the
  signal timeframe, recent pullback touch of the fast EMA, Stochastic %K
  re-cross out of oversold/overbought, ATR stop, R-multiple target. Optional
  daily-trend gate built ONLY from completed prior days (causal multi-TF).
- MomentumReversal50 (article #5, 30m): >= run_n consecutive strong
  same-direction bodies, then an opposite candle closing beyond 50% of the
  final candle's range -> counter-trend entry targeting a 50% retrace of the
  run, stop beyond the run extreme.
- GoldRoundMagnet (article #3): round-number fade/break with levels anchored
  on RAW prices (back-adjusted series shift round levels by roll offsets),
  converted to adj space per bar for the engine.

All signals are computed on completed signal bars; the engine acts on
subsequent execution bars (same pattern as every other strategy here).
"""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import ADJ, atr, ema, minute_of_day, stochastic


def _window(p: dict) -> pl.Expr:
    mod = minute_of_day()
    return (mod >= int(p["entry_start_minute"])) & (mod < int(p["entry_end_minute"]))


def _daily_gate(df: pl.DataFrame, ema_days: int) -> pl.DataFrame:
    """Prior-completed-day close vs daily EMA -> per-date trend flags (causal)."""
    daily = (
        df.sort("ts_utc")
        .group_by("trading_date", maintain_order=True)
        .agg(pl.col(ADJ["close"]).last().alias("dc"))
        .with_columns(pl.col("dc").ewm_mean(span=ema_days).alias("dema"))
        .with_columns(
            (pl.col("dc") > pl.col("dema")).shift(1).alias("day_up"),
            (pl.col("dc") < pl.col("dema")).shift(1).alias("day_dn"),
        )
        .select("trading_date", "day_up", "day_dn")
    )
    return df.join(daily, on="trading_date", how="left").sort("ts_utc")


class EmaStochPullback(Strategy):
    name = "ema_stoch_pullback"
    timeframe_minutes = 5
    default_params = {
        "ema_fast": 20,
        "ema_slow": 50,
        "stoch_k": 14,
        "stoch_d": 3,
        "stoch_os": 20,
        "stoch_ob": 80,
        "touch_bars": 6,        # fast-EMA touch within the last N bars
        "atr_n": 14,
        "stop_atr": 1.25,
        "target_r": 1.5,
        "expire_minutes": 60,
        "entry_start_minute": 8 * 60,
        "entry_end_minute": 12 * 60,
        "daily_gate": False,    # article #2: only trade with the daily trend
        "daily_ema_days": 20,
        "long_only": False,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        k, _ = stochastic(int(p["stoch_k"]), int(p["stoch_d"]))
        out = df.sort("ts_utc").with_columns(
            ema(ADJ["close"], int(p["ema_fast"])).alias("_ef"),
            ema(ADJ["close"], int(p["ema_slow"])).alias("_es"),
            k.alias("_k"),
            atr(int(p["atr_n"])).alias("_atr"),
        )
        if p["daily_gate"]:
            out = _daily_gate(out, int(p["daily_ema_days"]))
        else:
            out = out.with_columns(
                pl.lit(True).alias("day_up"), pl.lit(True).alias("day_dn")
            )

        bull = pl.col("_ef") > pl.col("_es")
        bear = pl.col("_ef") < pl.col("_es")
        touch_lo = (pl.col(ADJ["low"]) <= pl.col("_ef")).cast(pl.Int8)
        touch_hi = (pl.col(ADJ["high"]) >= pl.col("_ef")).cast(pl.Int8)
        n = int(p["touch_bars"])
        touched_lo = touch_lo.rolling_max(window_size=n) == 1
        touched_hi = touch_hi.rolling_max(window_size=n) == 1

        os_, ob = float(p["stoch_os"]), float(p["stoch_ob"])
        k_up = (pl.col("_k") > os_) & (pl.col("_k").shift(1) <= os_)
        k_dn = (pl.col("_k") < ob) & (pl.col("_k").shift(1) >= ob)

        w = _window(p)
        long_sig = (w & bull & touched_lo & k_up & pl.col("day_up")).fill_null(False)
        short_sig = (w & bear & touched_hi & k_dn & pl.col("day_dn")).fill_null(False)
        if p["long_only"]:
            short_sig = pl.lit(False)

        c = pl.col(ADJ["close"])
        sd = float(p["stop_atr"]) * pl.col("_atr")
        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (c - sd).alias("stop_long_adj"),
            (c + sd).alias("stop_short_adj"),
            (c + float(p["target_r"]) * sd).alias("target_long_adj"),
            (c - float(p["target_r"]) * sd).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_ef", "_es", "_k", "_atr", "day_up", "day_dn")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["touch_bars", "stop_atr", "target_r", "daily_gate"]


class MomentumReversal50(Strategy):
    name = "momentum_reversal_50"
    timeframe_minutes = 30
    default_params = {
        "run_n": 3,             # min consecutive strong same-direction candles
        "body_atr_frac": 0.5,   # 'strong' = body >= frac * ATR
        "atr_n": 14,
        "stop_buffer_atr": 0.25,
        "expire_minutes": 60,
        "entry_start_minute": 0,
        "entry_end_minute": 24 * 60,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        c, o = pl.col(ADJ["close"]), pl.col(ADJ["open"])
        h, lo = pl.col(ADJ["high"]), pl.col(ADJ["low"])
        out = df.sort("ts_utc").with_columns(atr(int(p["atr_n"])).alias("_atr"))

        body = c - o
        strong = body.abs() >= float(p["body_atr_frac"]) * pl.col("_atr")
        s = (
            pl.when(strong & (body > 0)).then(1)
            .when(strong & (body < 0)).then(-1)
            .otherwise(0)
        )
        out = out.with_columns(s.alias("_s"))
        grp = (pl.col("_s") != pl.col("_s").shift(1)).fill_null(True).cum_sum()
        out = out.with_columns(grp.alias("_g"))
        out = out.with_columns(
            (pl.int_range(0, pl.len()).over("_g") + 1).alias("_runlen"),
            pl.col(ADJ["open"]).first().over("_g").alias("_run_open"),
            pl.col(ADJ["low"]).min().over("_g").alias("_run_lo"),
            pl.col(ADJ["high"]).max().over("_g").alias("_run_hi"),
        )
        # state of the JUST-COMPLETED run, seen from the current bar
        prev = {
            "s": pl.col("_s").shift(1),
            "runlen": pl.col("_runlen").shift(1),
            "open": pl.col("_run_open").shift(1),
            "lo": pl.col("_run_lo").shift(1),
            "hi": pl.col("_run_hi").shift(1),
            "bar_hi": h.shift(1),
            "bar_lo": lo.shift(1),
        }
        n = int(p["run_n"])
        w = _window(p)
        prev_rng = prev["bar_hi"] - prev["bar_lo"]
        # target: 50% retrace of the run; stop: beyond the run extreme
        tgt_long = prev["lo"] + 0.5 * (prev["open"] - prev["lo"])
        tgt_short = prev["hi"] - 0.5 * (prev["hi"] - prev["open"])
        min_dist = 2 * 0.10  # 2 gold ticks of remaining room to target
        # bearish run then bullish candle closing >= 50% of last candle's range
        long_sig = (
            w
            & (prev["s"] == -1) & (prev["runlen"] >= n)
            & (c > o) & (c >= prev["bar_lo"] + 0.5 * prev_rng)
            & (tgt_long > c + min_dist)
        ).fill_null(False)
        short_sig = (
            w
            & (prev["s"] == 1) & (prev["runlen"] >= n)
            & (c < o) & (c <= prev["bar_hi"] - 0.5 * prev_rng)
            & (tgt_short < c - min_dist)
        ).fill_null(False)

        buf = float(p["stop_buffer_atr"]) * pl.col("_atr")
        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (prev["lo"] - buf).alias("stop_long_adj"),
            (prev["hi"] + buf).alias("stop_short_adj"),
            tgt_long.alias("target_long_adj"),
            tgt_short.alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_atr", "_s", "_g", "_runlen", "_run_open", "_run_lo", "_run_hi")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["run_n", "body_atr_frac"]


class GoldRoundMagnet(Strategy):
    """Round-number fade/break with levels anchored on RAW price."""

    name = "gold_round_magnet"
    timeframe_minutes = 5
    default_params = {
        "mode": "fade",          # fade | break
        "round_step": 10.0,      # $10 / $25 gold increments
        "atr_n": 14,
        "stop_atr": 1.25,
        "target_r": 1.0,
        "expire_minutes": 60,
        "entry_start_minute": 8 * 60,
        "entry_end_minute": 12 * 60,
        "tick": 0.10,
        "touch_ticks": 5,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        step = float(p["round_step"])
        touch = int(p["touch_ticks"]) * float(p["tick"])
        # raw-space round level, mapped into adj space via the per-bar offset
        raw_c = pl.col("close")
        offset = pl.col(ADJ["close"]) - raw_c
        rnd_adj = ((raw_c / step).round(0) * step + offset).alias("_rnd")
        out = df.sort("ts_utc").with_columns(
            rnd_adj, atr(int(p["atr_n"])).alias("_atr")
        )
        w = _window(p)
        c, h, lo = pl.col(ADJ["close"]), pl.col(ADJ["high"]), pl.col(ADJ["low"])
        near = (c - pl.col("_rnd")).abs() <= touch
        sd = float(p["stop_atr"]) * pl.col("_atr")

        if p["mode"] == "break":
            long_sig = w & rising_edge(
                (c > pl.col("_rnd") + touch) & (lo <= pl.col("_rnd") + touch)
            )
            short_sig = w & rising_edge(
                (c < pl.col("_rnd") - touch) & (h >= pl.col("_rnd") - touch)
            )
        else:  # fade: wick through the level, close back on the near side
            long_sig = w & near & rising_edge((lo <= pl.col("_rnd")) & (c > pl.col("_rnd")))
            short_sig = w & near & rising_edge((h >= pl.col("_rnd")) & (c < pl.col("_rnd")))
        long_sig = long_sig.fill_null(False)
        short_sig = short_sig.fill_null(False)

        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (c - sd).alias("stop_long_adj"),
            (c + sd).alias("stop_short_adj"),
            (c + float(p["target_r"]) * sd).alias("target_long_adj"),
            (c - float(p["target_r"]) * sd).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_rnd", "_atr")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["round_step", "touch_ticks", "stop_atr", "target_r", "mode"]

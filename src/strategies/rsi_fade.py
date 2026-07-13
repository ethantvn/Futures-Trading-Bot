"""RSI/Stochastic mean-reversion fade."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, with_signal_defaults
from src.strategies.indicators import ADJ, adx, atr, minute_of_day, rsi, stochastic


class RsiFade(Strategy):
    name = "rsi_fade"
    timeframe_minutes = 5
    default_params = {
        "rsi_n": 14,
        "rsi_ob": 70,
        "rsi_os": 30,
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.0,
        "expire_minutes": 60,
        "adx_n": 14,
        "adx_max": 25.0,
        "entry_start_minute": 10 * 60,
        "entry_end_minute": 14 * 60,
        "skip_weekdays": [],
        "use_stoch": False,
        "stoch_k": 14,
        "stoch_d": 3,
        "stoch_ob": 80,
        "stoch_os": 20,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        k, _d = stochastic(int(p["stoch_k"]), int(p["stoch_d"]))
        osc = k if p["use_stoch"] else rsi(int(p["rsi_n"]))
        ob = float(p["stoch_ob"] if p["use_stoch"] else p["rsi_ob"])
        os = float(p["stoch_os"] if p["use_stoch"] else p["rsi_os"])

        out = df.sort("ts_utc").with_columns(
            osc.alias("_osc"),
            atr(int(p["atr_n"])).alias("_atr"),
            adx(int(p["adx_n"])).alias("_adx"),
            minute_of_day().alias("_mod"),
        )
        adx_gate = (
            pl.lit(True)
            if float(p["adx_max"]) <= 0
            else (pl.col("_adx") < float(p["adx_max"]))
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & adx_gate
            & pl.col("_osc").is_not_null()
        )
        if p["skip_weekdays"]:
            window = window & ~pl.col("trading_date").dt.weekday().is_in(list(p["skip_weekdays"]))

        prev = pl.col("_osc").shift(1)
        long_sig = (window & (pl.col("_osc") > os) & (prev <= os)).fill_null(False)
        short_sig = (window & (pl.col("_osc") < ob) & (prev >= ob)).fill_null(False)

        c = pl.col(ADJ["close"])
        stop_dist = float(p["stop_atr"]) * pl.col("_atr")
        out = out.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit("market").alias("entry_kind"),
            (c - stop_dist).alias("stop_long_adj"),
            (c + stop_dist).alias("stop_short_adj"),
            (c + float(p["target_r"]) * stop_dist).alias("target_long_adj"),
            (c - float(p["target_r"]) * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_osc", "_atr", "_adx", "_mod")
        return with_signal_defaults(out)

    def overfit_prone_params(self) -> list[str]:
        return ["rsi_n", "rsi_ob", "rsi_os", "stop_atr", "use_stoch"]

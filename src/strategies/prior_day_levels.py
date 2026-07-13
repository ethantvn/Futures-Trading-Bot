"""Prior-day high/low break or fade — Phase 16."""
from __future__ import annotations

import polars as pl

from src.strategies.base import Strategy, rising_edge, with_signal_defaults
from src.strategies.indicators import (
    ADJ,
    atr,
    minute_of_day,
    prior_day_hl,
    prior_settle_proxy,
    structure_regime,
)


class PriorDayLevels(Strategy):
    name = "prior_day_levels"
    timeframe_minutes = 5
    default_params = {
        "mode": "break",  # break | fade
        "atr_n": 14,
        "stop_atr": 1.5,
        "target_r": 1.5,
        "expire_minutes": 180,
        "tick": 0.25,
        "entry_start_minute": 9 * 60 + 35,
        "entry_end_minute": 14 * 60,
        "pivot_n": 3,
        "structure_gate": False,
        "allow_regimes": "up,range,down",
        "use_settle_magnet": False,
        "settle_ticks": 20,
    }

    def prepare(self, df: pl.DataFrame) -> pl.DataFrame:
        p = self.params
        tick = float(p["tick"])
        levels = prior_day_hl(df)
        settle = prior_settle_proxy(df)
        struct = structure_regime(df, pivot_n=int(p["pivot_n"]))
        df = (
            df.sort("ts_utc")
            .join(levels, on="trading_date", how="left")
            .join(settle, on="trading_date", how="left")
            .join(struct.select("ts_utc", "structure_regime"), on="ts_utc", how="left")
            .with_columns(
                atr(int(p["atr_n"])).alias("_atr"),
                minute_of_day().alias("_mod"),
            )
        )
        window = (
            (pl.col("session") == "rth")
            & (pl.col("_mod") >= int(p["entry_start_minute"]))
            & (pl.col("_mod") < int(p["entry_end_minute"]))
            & pl.col("pdh").is_not_null()
        )
        if p["structure_gate"]:
            allow = p["allow_regimes"]
            allow_set = (
                {x.strip() for x in allow.split(",") if x.strip()}
                if isinstance(allow, str)
                else set(allow)
            )
            window = window & pl.col("structure_regime").is_in(sorted(allow_set))

        stop_dist = float(p["stop_atr"]) * pl.col("_atr")
        if p["use_settle_magnet"]:
            near_settle_h = (
                pl.col("pdh") - pl.col("prior_settle")
            ).abs() <= int(p["settle_ticks"]) * tick
            near_settle_l = (
                pl.col("pdl") - pl.col("prior_settle")
            ).abs() <= int(p["settle_ticks"]) * tick
        else:
            near_settle_h = pl.lit(True)
            near_settle_l = pl.lit(True)

        if p["mode"] == "fade":
            long_sig = (
                window
                & near_settle_l
                & rising_edge(
                    (pl.col(ADJ["low"]) <= pl.col("pdl"))
                    & (pl.col(ADJ["close"]) > pl.col("pdl"))
                )
            )
            short_sig = (
                window
                & near_settle_h
                & rising_edge(
                    (pl.col(ADJ["high"]) >= pl.col("pdh"))
                    & (pl.col(ADJ["close"]) < pl.col("pdh"))
                )
            )
            entry_l = pl.col("pdl")
            entry_s = pl.col("pdh")
            kind = "limit"
        else:
            # First RTH emit of OCO stop pair (classic PDH/PDL breakout)
            emit = rising_edge(window)
            long_sig = emit & near_settle_h
            short_sig = emit & near_settle_l
            entry_l = pl.col("pdh") + tick
            entry_s = pl.col("pdl") - tick
            kind = "stop"

        df = df.with_columns(
            long_sig.alias("enter_long"),
            short_sig.alias("enter_short"),
            pl.lit(kind).alias("entry_kind"),
            entry_l.alias("entry_price_long_adj"),
            entry_s.alias("entry_price_short_adj"),
            (entry_l - stop_dist).alias("stop_long_adj"),
            (entry_s + stop_dist).alias("stop_short_adj"),
            (entry_l + float(p["target_r"]) * stop_dist).alias("target_long_adj"),
            (entry_s - float(p["target_r"]) * stop_dist).alias("target_short_adj"),
            pl.lit(int(p["expire_minutes"]), dtype=pl.Int64).alias("expire_minutes"),
        ).drop("_atr", "_mod", "structure_regime")
        return with_signal_defaults(df)

    def overfit_prone_params(self) -> list[str]:
        return ["mode", "stop_atr", "target_r", "structure_gate"]

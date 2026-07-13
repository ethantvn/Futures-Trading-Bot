"""Causal indicator expressions on back-adjusted prices.

Every indicator here uses only data up to and including the current bar.
Signals derived from them act on the NEXT bar (engine discipline), so using
the current bar's close is safe.
"""
from __future__ import annotations

import polars as pl

ADJ = {"open": "open_adj", "high": "high_adj", "low": "low_adj", "close": "close_adj"}


def ema(col: str, span: int) -> pl.Expr:
    return pl.col(col).ewm_mean(span=span, adjust=False)


def true_range() -> pl.Expr:
    prev_close = pl.col(ADJ["close"]).shift(1)
    return pl.max_horizontal(
        pl.col(ADJ["high"]) - pl.col(ADJ["low"]),
        (pl.col(ADJ["high"]) - prev_close).abs(),
        (pl.col(ADJ["low"]) - prev_close).abs(),
    )


def atr(n: int) -> pl.Expr:
    return true_range().ewm_mean(alpha=1.0 / n, adjust=False)


def session_vwap() -> pl.Expr:
    """Volume-weighted average of typical price, cumulative within trading date."""
    tp = (pl.col(ADJ["high"]) + pl.col(ADJ["low"]) + pl.col(ADJ["close"])) / 3.0
    pv = (tp * pl.col("volume")).cum_sum().over("trading_date")
    v = pl.col("volume").cum_sum().over("trading_date")
    return pv / v


def bollinger(n: int, k: float) -> tuple[pl.Expr, pl.Expr, pl.Expr]:
    mid = pl.col(ADJ["close"]).rolling_mean(n)
    sd = pl.col(ADJ["close"]).rolling_std(n)
    return mid, mid + k * sd, mid - k * sd


def adx(n: int) -> pl.Expr:
    """Wilder's ADX.

    DX is computed from the smoothed directional movements directly (the TR
    normalization cancels in the ratio), with a zero-denominator guard: a bar
    where both smoothed DMs are zero contributes DX = 0. Without the guard,
    0/0 produces NaN which poisons the recursive EWM smoothing forever.
    """
    up = pl.col(ADJ["high"]) - pl.col(ADJ["high"]).shift(1)
    dn = pl.col(ADJ["low"]).shift(1) - pl.col(ADJ["low"])
    plus_dm = pl.when((up > dn) & (up > 0)).then(up).otherwise(0.0)
    minus_dm = pl.when((dn > up) & (dn > 0)).then(dn).otherwise(0.0)
    a = 1.0 / n
    pdm_s = plus_dm.ewm_mean(alpha=a, adjust=False)
    mdm_s = minus_dm.ewm_mean(alpha=a, adjust=False)
    denom = pdm_s + mdm_s
    dx = pl.when(denom > 0).then(100.0 * (pdm_s - mdm_s).abs() / denom).otherwise(0.0)
    return dx.ewm_mean(alpha=a, adjust=False)


def rsi(n: int) -> pl.Expr:
    """Wilder RSI on adjusted close."""
    d = pl.col(ADJ["close"]) - pl.col(ADJ["close"]).shift(1)
    up = pl.when(d > 0).then(d).otherwise(0.0)
    dn = pl.when(d < 0).then(-d).otherwise(0.0)
    a = 1.0 / n
    avg_up = up.ewm_mean(alpha=a, adjust=False)
    avg_dn = dn.ewm_mean(alpha=a, adjust=False)
    rs = pl.when(avg_dn > 0).then(avg_up / avg_dn).otherwise(None)
    return (
        pl.when((avg_up == 0) & (avg_dn == 0))
        .then(50.0)
        .when(avg_dn == 0)
        .then(100.0)
        .when(avg_up == 0)
        .then(0.0)
        .otherwise(100.0 - (100.0 / (1.0 + rs)))
    )


def stochastic(k_n: int, d_n: int) -> tuple[pl.Expr, pl.Expr]:
    """Stochastic oscillator (%K, %D) on adjusted OHLC."""
    ll = pl.col(ADJ["low"]).rolling_min(k_n)
    hh = pl.col(ADJ["high"]).rolling_max(k_n)
    span = hh - ll
    k = (
        pl.when(span > 0)
        .then(100.0 * (pl.col(ADJ["close"]) - ll) / span)
        .otherwise(50.0)
    )
    d = k.rolling_mean(d_n)
    return k, d


def donchian(n: int) -> tuple[pl.Expr, pl.Expr]:
    """Donchian channel (high, low) over last n bars including current."""
    return pl.col(ADJ["high"]).rolling_max(n), pl.col(ADJ["low"]).rolling_min(n)


def macd(fast: int, slow: int, signal: int) -> tuple[pl.Expr, pl.Expr, pl.Expr]:
    """MACD line, signal line, histogram on adjusted close."""
    macd_line = ema(ADJ["close"], fast) - ema(ADJ["close"], slow)
    signal_line = macd_line.ewm_mean(span=signal, adjust=False)
    return macd_line, signal_line, macd_line - signal_line


def roc(n: int) -> pl.Expr:
    """Percent rate-of-change on adjusted close."""
    prev = pl.col(ADJ["close"]).shift(n)
    return 100.0 * (pl.col(ADJ["close"]) / prev - 1.0)


def minute_of_day() -> pl.Expr:
    # cast first: dt.hour() is Int8 and hour*60 overflows it
    return (
        pl.col("ts_ny").dt.hour().cast(pl.Int32) * 60
        + pl.col("ts_ny").dt.minute().cast(pl.Int32)
    )


def rth_day_high_low(bars: pl.DataFrame) -> pl.DataFrame:
    """Per trading date: RTH high/low (adjusted), for prev-day level strategies."""
    return (
        bars.filter(pl.col("session") == "rth")
        .group_by("trading_date")
        .agg(
            pl.col(ADJ["high"]).max().alias("rth_high"),
            pl.col(ADJ["low"]).min().alias("rth_low"),
        )
        .sort("trading_date")
    )


def prev_day_context(
    bars: pl.DataFrame, vol_ref_days: int = 14, nr_n: int = 7
) -> pl.DataFrame:
    """Per trading date, PRIOR-day session statistics for day-level gates.

    Everything is shifted so each row describes what a trader knows BEFORE
    the session opens (a day's own range only enters the columns of later
    days):
      vol_ref     EWM(1/vol_ref_days) of prior daily RTH ranges
      prev_range  yesterday's RTH range
      nr_flag     yesterday was the narrowest of the last `nr_n` completed days
      inside_flag yesterday's RTH range was inside the prior day's
    """
    d = (
        bars.filter(pl.col("session") == "rth")
        .group_by("trading_date")
        .agg(
            (pl.col(ADJ["high"]).max() - pl.col(ADJ["low"]).min()).alias("_range"),
            pl.col(ADJ["high"]).max().alias("_high"),
            pl.col(ADJ["low"]).min().alias("_low"),
        )
        .sort("trading_date")
    )
    return d.with_columns(
        pl.col("_range").ewm_mean(alpha=1.0 / vol_ref_days, adjust=False)
        .shift(1).alias("vol_ref"),
        pl.col("_range").shift(1).alias("prev_range"),
        (
            pl.col("_range") <= pl.col("_range").rolling_min(nr_n)
        ).shift(1).alias("nr_flag"),
        (
            (pl.col("_high") < pl.col("_high").shift(1))
            & (pl.col("_low") > pl.col("_low").shift(1))
        ).shift(1).alias("inside_flag"),
    ).select("trading_date", "vol_ref", "prev_range", "nr_flag", "inside_flag")


# ---- Phase 16: structure / overnight / profile / MES helpers ---------------

def overnight_levels(bars: pl.DataFrame) -> pl.DataFrame:
    """Per trading_date: overnight high/low completed before RTH (causal).

    Overnight = Globex from 18:00 ET through 09:29 ET only. Afternoon ETH
    (16:00–17:00) on the same trading_date is excluded — including it would
    leak same-day post-RTH extremes into morning signals.
    """
    mod = minute_of_day()
    return (
        bars.sort("ts_utc")
        .with_columns(mod.alias("_mod"))
        .filter(pl.col("session") == "eth")
        .filter((pl.col("_mod") >= 18 * 60) | (pl.col("_mod") < 9 * 60 + 30))
        .group_by("trading_date")
        .agg(
            pl.col(ADJ["high"]).max().alias("on_high"),
            pl.col(ADJ["low"]).min().alias("on_low"),
        )
        .sort("trading_date")
    )


def prior_settle_proxy(bars: pl.DataFrame) -> pl.DataFrame:
    """Prior RTH session last close (settlement proxy; not exchange settle)."""
    return (
        bars.filter(pl.col("session") == "rth")
        .group_by("trading_date")
        .agg(pl.col(ADJ["close"]).last().alias("_settle"))
        .sort("trading_date")
        .with_columns(pl.col("_settle").shift(1).alias("prior_settle"))
        .select("trading_date", "prior_settle")
    )


def prior_day_hl(bars: pl.DataFrame) -> pl.DataFrame:
    """Prior RTH high/low joined as pdh/pdl on trading_date."""
    return (
        rth_day_high_low(bars)
        .with_columns(
            pl.col("rth_high").shift(1).alias("pdh"),
            pl.col("rth_low").shift(1).alias("pdl"),
        )
        .select("trading_date", "pdh", "pdl")
    )


def structure_regime(bars: pl.DataFrame, pivot_n: int = 3) -> pl.DataFrame:
    """Causal swing regime: up / down / range from confirmed N-bar pivots.

    At bar t a swing high at t-n is confirmed iff high[t-n] equals the max of
    highs over [t-2n, t] (window length 2n+1). Same for swing lows. Regime uses
    the last two confirmed swing highs and lows (HH+HL → up, LH+LL → down).
    """
    n = int(pivot_n)
    w = 2 * n + 1
    df = bars.sort("ts_utc").with_columns(
        pl.col(ADJ["high"]).alias("_h"),
        pl.col(ADJ["low"]).alias("_l"),
    )
    conf_ph = pl.col("_h").shift(n) == pl.col("_h").rolling_max(w)
    conf_pl = pl.col("_l").shift(n) == pl.col("_l").rolling_min(w)
    df = df.with_columns(
        pl.when(conf_ph).then(pl.col("_h").shift(n)).otherwise(None).alias("_ph"),
        pl.when(conf_pl).then(pl.col("_l").shift(n)).otherwise(None).alias("_pl"),
    )
    # Running last / prior swing levels via cumulative logic in Python for clarity
    ph = df["_ph"].to_list()
    pl_ = df["_pl"].to_list()
    last_h = prev_h = last_l = prev_l = None
    regimes: list[str | None] = []
    for i in range(len(ph)):
        if ph[i] is not None:
            prev_h, last_h = last_h, float(ph[i])
        if pl_[i] is not None:
            prev_l, last_l = last_l, float(pl_[i])
        if last_h is None or prev_h is None or last_l is None or prev_l is None:
            regimes.append(None)
        elif last_h > prev_h and last_l > prev_l:
            regimes.append("up")
        elif last_h < prev_h and last_l < prev_l:
            regimes.append("down")
        else:
            regimes.append("range")
    return df.drop("_h", "_l", "_ph", "_pl").with_columns(
        pl.Series("structure_regime", regimes, dtype=pl.Utf8)
    )


def session_volume_profile(
    bars: pl.DataFrame,
    bin_size: float = 5.0,
    va_pct: float = 0.70,
    session: str = "rth",
) -> pl.DataFrame:
    """Causal session POC / VAH / VAL from bar typical-price × volume bins.

    Profile includes bars from session open through the *current* bar only.
    Approximation: uses the passed bar timeframe (typically 5m), not tick data.
    """
    import numpy as np

    df = bars.sort("ts_utc")
    poc_out = [None] * df.height
    vah_out = [None] * df.height
    val_out = [None] * df.height
    if df.height == 0:
        return df.with_columns(
            pl.Series("poc", poc_out, dtype=pl.Float64),
            pl.Series("vah", vah_out, dtype=pl.Float64),
            pl.Series("val", val_out, dtype=pl.Float64),
        )

    td = df["trading_date"].to_list()
    sess = df["session"].to_list() if "session" in df.columns else ["rth"] * df.height
    hi = df[ADJ["high"]].to_numpy()
    lo = df[ADJ["low"]].to_numpy()
    cl = df[ADJ["close"]].to_numpy()
    vol = df["volume"].to_numpy().astype(float)
    tp = (hi + lo + cl) / 3.0

    i = 0
    n = df.height
    while i < n:
        day = td[i]
        j = i
        while j < n and td[j] == day:
            j += 1
        # cumulative bins within day for selected session
        bins: dict[int, float] = {}
        for k in range(i, j):
            if sess[k] != session:
                continue
            b = int(np.round(tp[k] / bin_size))
            bins[b] = bins.get(b, 0.0) + vol[k]
            if not bins:
                continue
            # POC = bin with max volume
            poc_b = max(bins, key=bins.get)
            total = sum(bins.values())
            target = total * va_pct
            # Expand around POC until >= va_pct of volume
            keys = sorted(bins)
            lo_i = hi_i = keys.index(poc_b) if poc_b in keys else 0
            covered = bins[poc_b]
            while covered < target and (lo_i > 0 or hi_i < len(keys) - 1):
                left = bins[keys[lo_i - 1]] if lo_i > 0 else -1.0
                right = bins[keys[hi_i + 1]] if hi_i < len(keys) - 1 else -1.0
                if right >= left:
                    hi_i += 1
                    covered += bins[keys[hi_i]]
                else:
                    lo_i -= 1
                    covered += bins[keys[lo_i]]
            poc_out[k] = poc_b * bin_size
            vah_out[k] = keys[hi_i] * bin_size
            val_out[k] = keys[lo_i] * bin_size
        i = j

    return df.with_columns(
        pl.Series("poc", poc_out, dtype=pl.Float64),
        pl.Series("vah", vah_out, dtype=pl.Float64),
        pl.Series("val", val_out, dtype=pl.Float64),
    )


def align_mes_bars(mnq: pl.DataFrame, mes: pl.DataFrame) -> pl.DataFrame:
    """Left-join MES OHLC onto MNQ on ts_utc (MES used as overlay only)."""
    mes_s = mes.select(
        "ts_utc",
        pl.col(ADJ["open"]).alias("mes_open_adj"),
        pl.col(ADJ["high"]).alias("mes_high_adj"),
        pl.col(ADJ["low"]).alias("mes_low_adj"),
        pl.col(ADJ["close"]).alias("mes_close_adj"),
    )
    return mnq.join(mes_s, on="ts_utc", how="left").sort("ts_utc")


def nearest_round(price: pl.Expr, step: float) -> pl.Expr:
    """Nearest psychological round level (e.g. step=50 or 100 on MNQ points)."""
    return (price / step).round() * step

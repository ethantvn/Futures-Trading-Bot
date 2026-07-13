# Phase 18 Scope — Deep Multi-Family Search for Lucid Pass

Date: 2026-07-12.

## Objective

Find any MNQ strategy that **beats ORB-W long-only + skip Monday** on Lucid 25K:

| Metric | Incumbent bar |
| --- | --- |
| WF MC pass @ 1 micro | ~**64%** |
| Pass + first payout | ~**46%** |
| Density | ≳ **4–5 trades/month**, fold+ ≳ 50% |

Train-fold selection uses **`score_upi`** (Ulcer Performance Index + Lucid-hostile
penalties), not Sharpe — then finalists ranked by real MC pass / pass+payout.

## INCLUDE (backtestable with current bars + VIX + MES + macro calendar)

| Family | Class | Notes |
| --- | --- | --- |
| ORB fade (failed breakout) | `OpeningRangeFade` | Highest-EV untested opposite edge |
| VWAP stretch fade | `VwapReversion` | Not the Phase 15 scalp |
| Bollinger + ADX | `BollingerMeanReversion` | Deep grid |
| RSI / Stochastic fade | `RsiFade` | |
| Prior-day H/L fade & break | `PriorDayLevels` | Deeper exits |
| Overnight fade/break | `OvernightLevels` | Causal ON only; expected weak |
| ORB-W control | `FilteredOrb` / `OrbEnhanced` | Incumbent |
| Session TOD ORB | `SessionTodOrb` | first60 / midday / last90 |
| Donchian breakout | `DonchianBreakout` | |
| EMA trend + ADX | `EmaTrend` | Deep grid |
| ATR open breakout | `AtrBreakout` | |
| MACD hist cross | `MacdMomentum` | |
| ROC + volume burst | `RocMomentum` | |
| MES divergence ORB | `MesDivergenceOrb` | Overlay only |
| Macro blackout on ORB-W | `FilteredOrb` skip_macro | Event filter |
| DOW / long-only / risk cap | on families above | Param sweep |

## EXCLUDE (invalid or already dead)

| Family | Reason |
| --- | --- |
| Order book / delta / footprint / tape | No MBP-1 / tick tape |
| Fixed-tick VWAP/POC scalping | Phase 15 REJECT |
| Gold / MGC / Kalshi | Prior phases REJECT / out of scope |
| Overnight fade as “96%” claim | Lookahead bug; causal ~14% |
| ES/MES basis arb | No edge at 1 micro; MES primary failed P10 |
| Earnings calendar | N/A for index futures |

## Param categories swept

Entry structure, stop/target/expire, max trades/day, skip weekdays, TOD windows,
ADX/vol regime, macro blackout, width bands (ORB), RSI/BB thresholds, Donchian N,
ATR multiples — see `config/phase18_deep.yaml`.

## Acceptance

Promote only if: WF pass ≥ incumbent, pass+payout ≥ incumbent − 2pts **or** clear
holdout win with density + fold stability, and not a sparsity trap (<100 OOS trades
or <4 t/mo or fold+ <50%).

# Phase 18 Report — Deep Multi-Family Lucid Pass Search

Date: 2026-07-12.

## TL;DR

**Nothing beat ORB-W.** After ~442 walk-forward combos across 19 families,
UPI-based train selection, 10k Lucid 25K MC, and 2026 holdout:

| Best non-control | WF Pass | Pass+payout | vs incumbent (~64% / ~46%) |
| --- | --- | --- | --- |
| `orb_tod` (TOD window on ORB-W) | 59.2% | 43.5% | worse |
| `mes_diverge_orb` | 58.4% | 38.3% | worse |
| `orb_risk_cap` | 58.3% | 38.5% | worse |
| All fades / Donchian / RSI / BB / MACD | ≤32% | ≤16% | **REJECT** |

**Live recommendation unchanged:** MNQ ORB-W long-only + skip Monday @ 1 micro
(`tradingview/lucid_orb_width_25k.pine`).

## What was tested (valid only)

| Bucket | Families | Result |
| --- | --- | --- |
| Mean reversion | ORB fade, VWAP stretch, Bollinger, RSI, Stoch, prior-day fade, overnight fade | All ≤20% pass; ORB fade ~0% |
| Trend / breakout | Donchian, EMA, ATR open break, prior-day/overnight break | EMA best non-ORB @ 33%; rest fail |
| Momentum | MACD hist, ROC+volume | ≤26% |
| Seasonality / filters | TOD windows, macro skip, risk-cap on ORB-W | Close but **below** control |
| Cross-asset | MES agree/diverge ORB | 58% — no lift |

## Explicitly excluded (no valid backtest)

Order-book / delta / footprint / tape (no MBP-1), fixed-tick scalps (P15 dead),
gold/MGC, Kalshi, ES/MES basis arb at 1 micro.

## Method

- Config: `config/phase18_deep.yaml` (~442 combos)
- Train scorer: **`score_upi`** (Ulcer Performance Index + Lucid-hostile penalties)
- WF 24m/6m on 2019–2025; MC 10k @ Lucid 25K; holdout 2026 H1 frozen
- Density gate: ≥100 OOS trades, ≥4 t/mo, ≥50% positive folds

## Holdout (2026-01-01 → 2026-06-28)

See `data/reports/phase18_holdout.md`. Control remains competitive; no challenger
clears the picky bar on both WF and holdout.

## Deliverables

- New strategies: `orb_fade`, `vwap_reversion`, `donchian_breakout`, `rsi_fade`,
  `atr_breakout`, `macd_momentum`, `roc_momentum`, `session_tod`
- Indicators: RSI, stochastic, Donchian, MACD, ROC
- Runner: `scripts/run_phase18.py`
- Scope: `docs/PHASE_18_SCOPE.md`
- Leaderboard: `data/reports/phase18_leaderboard.md`

## Decision

**Reject all Phase 18 challengers.** ORB-W remains the highest Lucid pass /
pass+payout system found under causal bar data. Further gains likely need a
**true new information set** (paid order flow) or a different account product —
not more OHLCV indicator grids.
